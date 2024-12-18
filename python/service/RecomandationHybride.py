import numpy as np
from service.CacheService import *
from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import accuracy_score
from lightgbm import LGBMClassifier
import ast

def age_to_category(age_range):
    """
    Transformer une plage d'âge en catégorie descriptive.

    Args:
        age_range (str): Plage d'âge sous forme de chaîne de caractères (ex : "21-30").
    
    Returns:
        str: Catégorie correspondant à la plage d'âge (ex : "jeune adulte").
    """
    if "0-10" in age_range:
        return "enfant"
    elif "11-20" in age_range:
        return "adolescent"
    elif "21-30" in age_range:
        return "jeune adulte"
    elif "31-40" in age_range:
        return "adulte"
    elif "41-50" in age_range:
        return "adulte expérimenté"
    elif "51-60" in age_range:
        return "senior"
    elif "61-70" in age_range:
        return "senior confirmé"
    elif "70+" in age_range:
        return "senior âgé"
    else:
        return "inconnu"

class RecomandationHybride:
    """
    Classe pour générer des recommandations hybrides basées sur des embeddings utilisateurs.
    
    Attributes:
        bddservice: Service pour interagir avec la base de données.
        csvservice: Service pour la gestion des fichiers CSV.
        embedding_service: Service pour générer les embeddings textuels.
        cache_service: Service de gestion du cache.
    """

    def __init__(self, bddservice, csvservice, embeddingservice):
        """
        Initialiser les services nécessaires à la recommandation.

        Args:
            bddservice: Instance du service pour interagir avec la base de données.
            csvservice: Instance du service pour manipuler des fichiers CSV.
            embeddingservice: Instance du service pour générer les embeddings.
        """
        self.bddservice = bddservice
        self.csvservice = csvservice
        self.embedding_service = embeddingservice
        self.cache_service = CacheService()
        
    def create_vector_users(self):
        """
        Créer et insérer les vecteurs utilisateur dans la base de données.

        Cette méthode récupère les données utilisateur depuis la base de données,
        génère les embeddings correspondants à leurs profils, puis insère les vecteurs 
        dans la table `library.user_vector`.
        """
        try:
            # Récupération des données des utilisateurs
            users = self.bddservice.cmd_sql("""
                SELECT 
                    u.user_id, 
                    u.age, 
                    u.child, 
                    u.familial_situation, 
                    u.gender, 
                    u.cat_socio_pro, 
                    u.lieu_habitation, 
                    u.frequency, 
                    u.book_size, 
                    ARRAY_AGG(DISTINCT ulg.genre_id ORDER BY ulg.genre_id) AS liked_genres,
                    ARRAY_AGG(DISTINCT ula.author_id ORDER BY ula.author_id) AS liked_authors,
                    ARRAY_AGG(DISTINCT ulb.book_id ORDER BY ulb.book_id) AS liked_books
                FROM 
                    library._Users u
                LEFT JOIN 
                    library.user_liked_genre ulg ON u.user_id = ulg.user_id
                LEFT JOIN 
                    library.liked_author ula ON u.user_id = ula.user_id
                LEFT JOIN
                    library.User_Book_Read ulb ON u.user_id = ulb.user_id
                GROUP BY 
                    u.user_id;
            """)

            # Parcours des utilisateurs pour générer et insérer les vecteurs
            for user in users:
                user_vector = self.get_embeding_user(user)
                self.bddservice.insert_one_sql_with_id("library.user_vector", [user[0], user_vector], user[0])
        
        except Exception as e:
            print(f"Erreur lors de la création des vecteurs utilisateurs : {e}")
            raise

    def get_embeding_user(self, user):
        """
        Générer le vecteur d'embedding pour un utilisateur donné.

        Args:
            user (tuple): Informations utilisateur récupérées depuis la base de données.
        
        Returns:
            list: Vecteur utilisateur sous forme de liste.
        """
        # Conversion de l'âge en catégorie
        age_category = age_to_category(user[1])
        
        # Création d'une description textuelle du profil utilisateur
        user_profile_text = f"{age_category} {user[2]} {user[3]} {user[5]} {user[6]} {user[7]}"
        
        # Génération des embeddings pour le profil utilisateur
        profile_embedding = self.embedding_service.embeddingText(user_profile_text)
        
        # Embedding des auteurs appréciés
        liked_authors = ', '.join(map(str, user[9])) if user[9] else 'No liked authors'
        liked_authors_embedding = self.embedding_service.embeddingText(liked_authors)

        # Embedding des genres appréciés
        liked_genres_embedding = self.embedding_service.embeddingText(user[8])

        # Embedding des livres appréciés
        liked_books = ', '.join(map(str, user[11])) if user[11] else 'No liked books'
        liked_books_embedding = self.embedding_service.embeddingText(liked_books)

        # Fusion de tous les embeddings pour former le vecteur utilisateur final
        full_user_vector = np.concatenate([profile_embedding, liked_authors_embedding, liked_genres_embedding, liked_books_embedding])
        
        return full_user_vector.tolist()
    

    def gbm(self):
        # Récupérer les interactions utilisateur-livre
        query_interactions = """
            SELECT user_id, book_id, is_read, is_liked, is_favorite 
            FROM library.User_Book_Read;
        """
        interactions = self.bddservice.cmd_sql(query_interactions)
        interactions_df = pd.DataFrame(
            interactions, columns=["user_id", "book_id", "is_read", "is_liked", "is_favorite"]
        )

        # Vérification des données
        if interactions_df.empty:
            print("Aucune interaction utilisateur-livre trouvée.")
            return

        # Récupérer les vecteurs utilisateur et livre
        user_vectors_query = "SELECT * FROM library.user_vector;"
        book_vectors_query = "SELECT * FROM library.book_vector;"

        user_vectors = self.bddservice.cmd_sql(user_vectors_query)
        book_vectors = self.bddservice.cmd_sql(book_vectors_query)

        user_vectors_df = pd.DataFrame(user_vectors, columns=["user_id", "vector"])
        book_vectors_df = pd.DataFrame(book_vectors, columns=["book_id", "title", "vector"])

        # Convertir les vecteurs (de chaînes à listes)
        user_vectors_df["vector"] = user_vectors_df["vector"].apply(lambda x: np.array(ast.literal_eval(x)))
        book_vectors_df["vector"] = book_vectors_df["vector"].apply(lambda x: np.array(ast.literal_eval(x)))

        # Fusionner les vecteurs utilisateur et livre avec les interactions
        interactions_df = interactions_df.merge(user_vectors_df, on="user_id", how="left")
        interactions_df = interactions_df.merge(book_vectors_df, on="book_id", how="left")

        # Définir les pondérations
        user_weight = 0.1  # Pondération pour les vecteurs utilisateur
        book_weight = 0.9  # Pondération pour les vecteurs livre

        # Préparer les données pour LightGBM
        # Combiner les vecteurs utilisateur et livre dans les caractéristiques
        features = interactions_df.apply(
            lambda row: np.concatenate([row["vector_x"] * user_weight, row["vector_y"] * book_weight]), axis=1
        ).tolist()
        features = np.array(features)  # Convertir en tableau NumPy
        labels = interactions_df["is_liked"]  # Exemple de label cible

        # Séparer les ensembles d'entraînement et de test
        X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.4, random_state=42)

        # Créer les datasets LightGBM
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

        # Définir les paramètres LightGBM
        params = {
        "objective": "binary",
        "metric": "binary_logloss",
        "boosting_type": "gbdt",
        "learning_rate": 0.03,
        "num_leaves": 31,
        "max_depth": 6,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": -1
    }


        # Entraîner le modèle avec validation
        self.model = lgb.train(
            params,
            train_data,
            valid_sets=[train_data, test_data],  # Ajout des jeux de validation
            valid_names=["train", "valid"],  # Noms des ensembles pour le suivi
            num_boost_round=100 
            
        )

        # Faire des prédictions sur l'ensemble de test
        y_pred = self.model.predict(X_test, num_iteration=self.model.best_iteration)  # Utiliser la meilleure itération
        y_pred_binary = (y_pred > 0.5).astype(int)

        # Évaluer le modèle
        accuracy = accuracy_score(y_test, y_pred_binary)
        print(f"Accuracy: {accuracy:.4f}")



        

    def recommend_books(self, user_id, top_n=5):
        """
        Générer des recommandations de livres pour un utilisateur donné en utilisant le modèle LightGBM.

        Args:
            user_id (int): ID de l'utilisateur.
            top_n (int): Nombre de recommandations à générer.

        Returns:
            list: Liste des IDs des livres recommandés.
        """
        # Récupérer les vecteurs utilisateur et livres
        user_vectors_query = f"SELECT * FROM library.user_vector WHERE id = {user_id};"
        book_vectors_query = "SELECT * FROM library.book_vector;"

        user_vectors = self.bddservice.cmd_sql(user_vectors_query)
        book_vectors = self.bddservice.cmd_sql(book_vectors_query)

        user_vectors_df = pd.DataFrame(user_vectors, columns=["user_id", "vector"])
        book_vectors_df = pd.DataFrame(book_vectors, columns=["book_id", "title", "vector"])

        # Assurer que l'utilisateur a un vecteur dans la base de données
        if user_vectors_df.empty:
            print(f"Utilisateur {user_id} non trouvé dans les vecteurs.")
            return []

        # Extraire le vecteur de l'utilisateur et vérifier sa forme
        user_vector = np.array(ast.literal_eval(user_vectors_df.iloc[0]["vector"]))  # Assurez-vous que c'est une liste numpy
        if user_vector.ndim == 0:
            user_vector = np.expand_dims(user_vector, axis=0)  # S'assurer que c'est un vecteur 1D

        # Préparer les données de test pour tous les livres (ajouter le vecteur de l'utilisateur à chaque livre)
        def concatenate_vectors(book_vector):
            book_vector = np.array(ast.literal_eval(book_vector))  # Convertir le vecteur du livre en numpy array
            if book_vector.ndim == 0:
                book_vector = np.expand_dims(book_vector, axis=0)  # S'assurer que c'est un vecteur 1D
            return np.concatenate([user_vector, book_vector])

        features = book_vectors_df["vector"].apply(concatenate_vectors)
        features = np.array(features.tolist())

        # Faire des prédictions avec le modèle LightGBM
        y_pred = self.model.predict(features)  # Assurez-vous que 'self.model' est le modèle LightGBM entraîné

        # Créer un DataFrame des prédictions avec les book_ids
        predictions_df = pd.DataFrame({"book_id": book_vectors_df["book_id"], "score": y_pred})

        # Trier les livres par score décroissant
        recommendations = predictions_df.sort_values(by="score", ascending=False).head(top_n)

        # Retourner les IDs des livres recommandés
        recommended_books = recommendations["book_id"].tolist()

        # Afficher les titres des livres recommandés
        recommended_titles = recommendations.merge(book_vectors_df, on="book_id", how="left")["title"].tolist()
        return recommended_titles


        

if __name__ == "__main__":
    service = RecomandationHybride()
    service.create_vector_users()
    print("fin")
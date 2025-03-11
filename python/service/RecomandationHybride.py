import numpy as np
import random
from service.CacheService import *
from sklearn.model_selection import train_test_split
#import lightgbm as lgb
from sklearn.metrics import accuracy_score
#from lightgbm import LGBMClassifier
import ast
from service.RecommandationService import RecommendationService
from datetime import datetime

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

    def __init__(self, bddservice, csvservice, embeddingservice,recommandationservice):
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
        self.recommandation_service = recommandationservice
        
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

    def get_embeding_user(self, user, genre_weight=2.0):
        """
        Générer le vecteur d'embedding pour un utilisateur donné.

        Args:
            user (tuple): Informations utilisateur récupérées depuis la base de données.
            genre_weight (float): Facteur de pondération pour l'embedding des genres appréciés.
        
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

        # Embedding des genres appréciés (avec pondération)
        liked_genres_embedding = self.embedding_service.embeddingText(user[8])
        liked_genres_embedding = liked_genres_embedding * genre_weight  # Appliquer la pondération

        # Embedding des livres appréciés
        liked_books = ', '.join(map(str, user[11])) if user[11] else 'No liked books'
        liked_books_embedding = self.embedding_service.embeddingText(liked_books)

        # Fusion de tous les embeddings pour former le vecteur utilisateur final
        full_user_vector = np.concatenate([profile_embedding, liked_authors_embedding, liked_genres_embedding, liked_books_embedding])
        
        return full_user_vector.tolist()

    def insert_vect_user(self, user_id):
        """
        Créer et insérer le vecteur utilisateur dans la base de données.

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
                WHERE 
                    u.user_id = %s
                GROUP BY 
                    u.user_id;
            """, (user_id,))

            # Parcours des utilisateurs pour générer et insérer les vecteurs
            for user in users:
                user_vector = self.get_embeding_user(user)
                self.bddservice.insert_one_sql_with_id("library.user_vector", [user[0], user_vector], user[0])
        
        except Exception as e:
            print(f"Erreur lors de la création du vecteur utilisateur : {e}")
            raise

    def get_similar_users(self, user_id, n=5):
        """
        Rechercher les N users les plus similaires à un user donné en utilisant pgvector.
        """
        # Formater la requête SQL avec les paramètres user_id et n
        query = f"""
        SELECT
            id,
            
            1 - (vector <=> (SELECT vector FROM library.user_vector WHERE id = {user_id})) AS similarity
        FROM
            library.user_vector


        WHERE
            id != {user_id}
        ORDER BY
            similarity DESC
        LIMIT {n};
        """

        # Exécuter la requête SQL
        similar_users = self.bddservice.cmd_sql(query)
        return similar_users
    
    def get_similar_users_debug(self, user_id, n=5):
        """
        Rechercher les N utilisateurs les plus similaires à un utilisateur donné en utilisant pgvector.
        """
        # Formater la requête SQL avec les paramètres user_id et n
        query = f"""
        SELECT
            uv.id,
            us.*,
            ARRAY_AGG(DISTINCT g.name) AS liked_genres,  -- Agrège les genres associés à l'utilisateur
            1 - (vector <=> (SELECT vector FROM library.user_vector WHERE id = {user_id})) AS similarity
        FROM
            library.user_vector uv

        LEFT JOIN
            library._users us ON uv.id = us.user_id

        LEFT JOIN
            library.user_liked_genre lg ON uv.id = lg.user_id

        LEFT JOIN
            library.genre g ON lg.genre_id = g.genre_id

        WHERE
            uv.id != {user_id}  -- Pour exclure l'utilisateur lui-même des résultats

        GROUP BY
            uv.id, us.user_id  -- Groupement par utilisateur pour appliquer ARRAY_AGG

        ORDER BY
            similarity DESC
        LIMIT {n+1};
        """
        
        # Exécuter la requête SQL
        similar_users = self.bddservice.cmd_sql(query)
        for user in similar_users:
            print(user)
        return similar_users

    def get_book(self, book_id):
        query = f"""
        SELECT title
        FROM library.book
        WHERE book_id={book_id} 
        """
        book_title = self.bddservice.cmd_sql(query)
        return book_title
    

    def get_top_books(self, n=10):
        """
        Récupère les N meilleurs livres selon la vue matérialisée library.top_books.

        Args:
            n (int): Nombre de livres à récupérer (par défaut 10).

        Returns:
            list[tuple]: Une liste de tuples contenant les IDs et titres des meilleurs livres.
        """
        # Requête SQL pour récupérer les N meilleurs livres
        query = f"""
        SELECT
            book_id,
            title
        FROM
            library.top_books
        ORDER BY
            score DESC
        LIMIT {n};
        """

        # Exécuter la requête SQL
        top_books = self.bddservice.cmd_sql(query)


        # Retourner les résultats sous forme de liste de tuples
        return [book[0] for book in top_books]

    
    def recommend_books_for_user(self, user_id, n_recommendations=5):
        """
        Recommande les N livres les plus populaires basés sur les utilisateurs les plus similaires à un utilisateur donné.
        """
        self.insert_vect_user(user_id)
        # Récupérer les utilisateurs similaires à l'utilisateur donné
        similar_users = self.get_similar_users(user_id, n=5)
        #print(similar_users)
        # Récupérer les livres que l'utilisateur a aimés ou consultés
        user_books = self.recommandation_service.get_user_books(user_id)
        # Dictionnaire pour stocker les livres recommandés et leur score de similarité total
        recommendations = {}
        
        for similar_user in similar_users:
            
            
            similar_user_id = similar_user[0]
            # Récupérer les livres que cet utilisateur similaire a aimés ou consultés
            similar_user_books = self.recommandation_service.get_user_books(similar_user_id)  # Fonction à implémenter pour obtenir les livres d'un utilisateur
            #print(similar_user_books)
            for book in similar_user_books:
                #print(book)
                book_id = book['book_id']

                # Vérifie si le livre similaire est déjà lu
                if book_id in user_books:
                    continue
                
                similarity_score = similar_user[1]  # Utiliser la similarité calculée pour l'utilisateur similaire
                # Pondération basée sur la note et date de lecture
                weight = 1.0
                if book['note']:
                    weight += book['note'] / 5.0  # Si la note est sur 5
                if book['reading_date']:
                    # Calcul de la différence en années
                    reading_year = book['reading_date'].year
                    current_year = datetime.now().year
                    year_delta = max(current_year - reading_year, 1)  # Éviter division par zéro

                    # Calcul du poids avec logarithme
                    recency_weight = 1 / np.log1p(year_delta)
                    weight *= recency_weight

                #poids par rapport au classement top book / autheur / année de publication
                rank_score = self.recommandation_service.get_ranking_score(book_id)
                if rank_score and rank_score[0]:
                    weight *= 1 + rank_score[0][0]/9000000

                # Calcul du score final
                final_score = similarity_score * weight

                #print(similarity_score,weight)

                # Ajout au dictionnaire des recommandations
                if book_id not in recommendations:
                    
                    recommendations[book_id] = [self.get_book(book_id), final_score, 1] # 1 = count du nombre de score
                    #print(recommendations[book_id])  # Le titre du livre est aussi pris en compte ici
                else:
                    
                    recommendations[book_id][1] += final_score
                    recommendations[book_id][2] += 1
        for reco in recommendations:
            recommendations[reco][1] = recommendations[reco][1]/recommendations[reco][2]

        # Trier les recommandations par score décroissant
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1][1], reverse=True)
        #print(sorted_recommendations)
        # Retourner les N meilleurs
        return sorted_recommendations[:n_recommendations]
    

    def recommandation_hybride(self, user_id, n_recommendations=5):
        """
        Effectue une recommandation hybride de livres en combinant les recommandations basées sur l'utilisateur (user-based)
        et les livres similaires (item-based). Le facteur item_weight_factor permet de donner plus de poids à l'item-based.
        """
        # 1. Recommandations basées sur les utilisateurs similaires (user-based)
        user_based_recommendations = self.recommend_books_for_user(user_id, n_recommendations)

        #print(user_based_recommendations)


        # Dictionnaire pour stocker les livres recommandés de manière hybride et leur score final
        hybrid_recommendations = {}

        # 2. Pour chaque livre recommandé par l'approche user-based, recommander des livres similaires (item-based)
        for book in user_based_recommendations:
            
            book_id = book[0]  # Récupérer le book_id du livre recommandé par l'approche user-based
            #print(f"Recommandations basées sur l'utilisateur : Livre ID {book_id}")
            
            # Récupérer les livres similaires à ce livre (item-based)
            similar_books = self.recommandation_service.get_similar_books_hybrid(book_id, n=n_recommendations)
            
            

            for similar_book in similar_books:
                
                similar_book_id = similar_book[0]  # Récupérer l'ID du livre similaire
                similarity_score = similar_book[2]  # Similarité du livre

                
                
                # Pondération basée sur le score de l'utilisateur
                user_weight = book[1][1]  # Le poids de l'utilisateur pour ce livre recommandé
                
                
                # Appliquer le facteur de poids à l'item-based (augmentation de l'influence de l'item-based)
                final_score = similarity_score * user_weight
                
                # Ajouter ou accumuler les livres recommandés
                if similar_book_id not in hybrid_recommendations:
                    hybrid_recommendations[similar_book_id] = [self.get_book(similar_book_id), final_score, 1]
                else:
                    hybrid_recommendations[similar_book_id][1] += final_score
                    hybrid_recommendations[similar_book_id][2] += 1

        #on récupère les top 1000 livres
        #on prend 20 aléatoire
        #on attribue un poids aléatoire à chaque -> alea20
        aleaN = self.get_top_books(n=1000)
        aleaNlist = random.sample(aleaN,20)
        for idalea in aleaNlist:
            scoreAlea = random.uniform(0.5,1)
            if idalea not in hybrid_recommendations:
                hybrid_recommendations[idalea] = [self.get_book(idalea), scoreAlea, 1]
            else:
                hybrid_recommendations[idalea][1] += scoreAlea
                hybrid_recommendations[idalea][2] += 1


        for reco in hybrid_recommendations:
            hybrid_recommendations[reco][1] = hybrid_recommendations[reco][1]/hybrid_recommendations[reco][2]

        # 3. Trier les recommandations hybrides par score décroissant
        sorted_hybrid_recommendations = sorted(hybrid_recommendations.items(), key=lambda x: x[1][1], reverse=True)

        # 4. Retourner les N meilleurs livres recommandés de manière hybride
        return sorted_hybrid_recommendations[:n_recommendations]


    
    


        


        

if __name__ == "__main__":
    service = RecomandationHybride()
    service.create_vector_users()
    print("fin")
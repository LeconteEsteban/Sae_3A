import numpy as np
from service.CacheService import *



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
    

if __name__ == "__main__":
    service = RecomandationHybride()
    service.create_vector_users()
    print("fin")
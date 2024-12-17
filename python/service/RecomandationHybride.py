import numpy as np
import pandas as pd
import faiss
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from datetime import datetime
from service.CacheService import *

def age_to_category(age_range):
    """Transformer une plage d'âge en catégorie."""
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

    def __init__(self, bddservice, csvservice, embeddingservice):
        self.bddservice = bddservice
        self.csvservice = csvservice
        self.embedding_service = embeddingservice
        self.cache_service = CacheService()
       
        
        
    def create_vector_users(self):
        try:
            # Récupération des utilisateurs
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

            
            for user in users:
                self.bddservice.insert_one_sql_with_id("library.user_vector", [user[0],self.get_embeding_user(user) ], user[0])
       
        
            

        except Exception as e:
            print(f"Erreur lors de la création des vecteurs utilisateurs : {e}")
            raise


    def get_embeding_user(self, user):
        
        age_category = age_to_category(user[1])
        user_profile_text = f"{age_category} {user[2]} {user[3]} {user[5]} {user[6]} {user[7]}"
        # Création de l'embedding du profil utilisateur
        profile_embedding = self.embedding_service.embeddingText(user_profile_text)
        # # Construction des caractéristiques structurées
        liked_authors = ', '.join(map(str, user[9])) if user[9] else 'No liked authors'
        liked_authors_embedding = self.embedding_service.embeddingText(liked_authors)

        liked_genres_embedding = self.embedding_service.embeddingText(user[8])

        liked_books = ', '.join(map(str, user[11])) if user[11] else 'No liked books'
        liked_books_embedding = self.embedding_service.embeddingText(liked_books)

        # Fusion des caractéristiques

        full_user_vector = np.concatenate([profile_embedding, liked_authors_embedding, liked_genres_embedding, liked_books_embedding])
        

        return full_user_vector.tolist()

    

if __name__ == "__main__":
    service = RecomandationHybride()
    service.create_vector_users()
    print("fin")
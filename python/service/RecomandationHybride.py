import numpy as np
import pandas as pd
import faiss
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from datetime import datetime
from service.CacheService import *



class RecomandationHybride:

    def __init__(self, bddservice, csvservice, embeddingservice):
  
        self.bddservice = bddservice
        self.csvservice = csvservice
        self.embedding_service = embeddingservice
        self.cache_service=CacheService()
       
    def create_vector_users(self):
        try:
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
                                                ARRAY_AGG(DISTINCT ula.author_id ORDER BY ula.author_id) AS liked_authors
                                                
                                            FROM 
                                                library._Users u
                                            LEFT JOIN 
                                                library.user_liked_genre ulg ON u.user_id = ulg.user_id
                                            LEFT JOIN 
                                                library.liked_author ula ON u.user_id = ula.user_id
                                            
                                            GROUP BY 
                                                u.user_id;
                                            """)
                                            
                                            
            print("fin de la récupération : ",users[1])
            
            for user in users:
                full_user_vector = self.user_vector(user)
                data = [
                    user[0],
                    full_user_vector
                ]
                #self.cache_service.dict_to_cache("vector_user", data)    
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données de la table : {e}")
            raise
    
    def user_vector(self, user):
        """
        liked_authors = ' '.join(map(str, book[6])) if book[6] else "No settings"

        age_vector = self.embedding_service.embeddingText(user[1])
        child_vector = self.embedding_service.embeddingText(user[2])
        familial_situation_vector = self.embedding_service.embeddingText(user[3])
        gender_vector = self.embedding_service.embeddingText(user[4])
        cat_socio_pro_vector = self.embedding_service.embeddingText(user[5])
        lieu_habitation_vector = self.embedding_service.embeddingText(user[6])
        frequency_vector = self.embedding_service.embeddingText(user[7])
        book_size_vector = self.embedding_service.embeddingText(user[8])
        liked_genres_vector = self.embedding_service.embeddingText(user[9])
        liked_authors_vector = self.embedding_service.embeddingText(liked_authors)


        full_user_vector = np.concatenate((age_vector, child_vector, familial_situation_vector,  gender_vector, cat_socio_pro_vector, lieu_habitation_vector, frequency_vector, book_size_vector, liked_genres_vector, liked_authors_vector))
    
        return full_user_vector"""

if __name__ == "__main__":
    service = RecomandationHybride()
    service.create_vector_users()
    print("fin")
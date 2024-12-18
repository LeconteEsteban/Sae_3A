import numpy as np
import pandas as pd
import faiss
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from datetime import datetime

# CREATE EXTENSION IF NOT EXISTS vector;
# CREATE TABLE Book_vector (
#     id INT PRIMARY KEY,
#     title TEXT,
#     vector VECTOR(300)
# );


class RecommendationService:
    """
    EN DEVELLOPEMENT 
    """
    def __init__(self, bddservice, csvservice, embeddingservice):
        self.bddservice = bddservice
        self.csvservice = csvservice
        self.embedding_service = embeddingservice
    
    def create_book_vector(self):
        """
        Récupère les livres de la base de données, les vectorise, et les stock.
        """
        try:
            print("Début: récupération des livres stockés")
            
            # Récupération des livres
            books = self.bddservice.cmd_sql("""
                SELECT
                    b.book_id, sr.name AS series, b.title, b.description,
                    ARRAY_AGG(DISTINCT g.genre_id) AS genres,
                    ARRAY_AGG(DISTINCT a.author_id) AS authors,
                    ARRAY_AGG(DISTINCT s.settings_id) AS settings
                FROM library.Book b
                LEFT JOIN library.Serie_of_book sb ON b.book_id = sb.book_id
                LEFT JOIN library.Serie sr ON sb.serie_id = sr.serie_id
                LEFT JOIN library.Genre_and_vote gb ON b.book_id = gb.book_id
                LEFT JOIN library.Genre g ON gb.genre_id = g.genre_id
                LEFT JOIN library.Wrote w ON b.book_id = w.book_id
                LEFT JOIN library.Author a ON w.author_id = a.author_id
                LEFT JOIN library.Settings_of_book sb2 ON b.book_id = sb2.book_id
                LEFT JOIN library.Settings s ON sb2.settings_id = s.settings_id
                GROUP BY b.book_id, sr.name
            """)
            
            print("fin de la récupération : ", len(books))

            count = 0
            for book in books:

                full_vector = self.book_vector_simple(book)

                data = [
                    book[0],  # id
                    book[2],  # title
                    full_vector.tolist()  # vector converti en liste
                ]
                # Insertion dans la base de données
                self.bddservice.insert_one_sql_with_id("library.book_vector", data, data[0])

                #permet le suivi
                count += 1
                if count % 10 == 0:
                    print(f"Livres {book[0]} insérés", end="\r")

            print("Fin de la vectorisation et de l'insertion.")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def book_vector(self, book):
        """
        temps de traitement : environs 60 min et 500 Mo
        """
        # Gestion des champs vides

        authors_text = ' '.join(map(str, book[5])) if book[5] else "No authors"

        genres_text = ' '.join(map(str, book[4])) if book[4] else "No genres"

        settings_text = ' '.join(map(str, book[6])) if book[6] else "No settings"
        #print(1)
        # Vectorisation de chaque composant, avec un texte par défaut si le champ est vide
        title_vector = self.embedding_service.embeddingText(book[2] if book[2] else "No title")
        description_vector = self.embedding_service.embeddingText(book[3] if book[3] else "No description")
        series_vector = self.embedding_service.embeddingText(book[1] if book[1] else "No series")

        # Pour les autres informations
        authors_vector = self.embedding_service.embeddingText(authors_text)
        genres_vector = self.embedding_service.embeddingText(genres_text)
        settings_vector = self.embedding_service.embeddingText(settings_text)

        # Fusionner les vecteurs (concatenation ou autre méthode)
        full_vector = np.concatenate([title_vector, description_vector, series_vector,
                                    genres_vector, authors_vector, settings_vector])

        return full_vector

    def book_vector_acp(self, book):
        #ne fonctionne pas car je ne peut pas faire d'acp sur un seul vecteur évidement
        # Gestion des champs vides

        authors_text = ' '.join(map(str, book[5])) if book[5] else "No authors"

        genres_text = ' '.join(map(str, book[4])) if book[4] else "No genres"

        settings_text = ' '.join(map(str, book[6])) if book[6] else "No settings"
        #print(1)
        # Vectorisation de chaque composant, avec un texte par défaut si le champ est vide
        title_vector = self.embedding_service.embeddingText(book[2] if book[2] else "No title")
        description_vector = self.embedding_service.embeddingText(book[3] if book[3] else "No description")
        series_vector = self.embedding_service.embeddingText(book[1] if book[1] else "No series")

        # Pour les autres informations
        authors_vector = self.embedding_service.embeddingText(authors_text)
        genres_vector = self.embedding_service.embeddingText(genres_text)
        settings_vector = self.embedding_service.embeddingText(settings_text)

        # Fusionner les vecteurs (concatenation ou autre méthode)
        full_vector = np.concatenate([title_vector, description_vector, series_vector,
                                    genres_vector, authors_vector, settings_vector])
        
        # Reshaper le vecteur pour qu'il soit en format 2D (1 ligne, n caractéristiques)
        full_vector_2d = full_vector.reshape(1, 2)  # Forme attendue (1, n_features)
        
        # Appliquer l'ACP pour réduire à 300 dimensions
        pca = PCA(n_components=300)
        reduced_vector = pca.fit_transform(full_vector_2d)  

        explained_variance = pca.explained_variance_ratio_

        # Afficher la variance expliquée par chaque composante
        print(f"Variance expliquée par chaque composante : {explained_variance}")

        # Afficher la proportion cumulée de la variance expliquée
        print(f"Proportion cumulée de la variance expliquée : {np.cumsum(explained_variance)}")

        return reduced_vector
    
    def book_vector_simple(self, book):
        """
        temps de traitement : environs 10 min et 50 Mo
        """
        # Gestion des champs vides
        # Création du texte à vectoriser
        text_input = f"Title: {book[2]} Description: {book[3]} " \
            f"Genres: {', '.join(map(str, book[4]))} " \
            f"Authors: {', '.join(map(str, book[5]))} " \
            f"Settings: {', '.join(map(str, book[6]))} Series: {book[1]}"
        #Vectorisation unique
        vector = self.embedding_service.embeddingText(text_input)

        return vector
    
    def get_similar_books(self, book_id, n=5):
        """
        Rechercher les N livres les plus similaires à un livre donné en utilisant pgvector.
        """
        # Formater la requête SQL avec les paramètres book_id et n
        query = f"""
        SELECT
            id,
            title,
            1 - (vector <=> (SELECT vector FROM library.book_vector WHERE id = {book_id})) AS similarity
        FROM
            library.book_vector
        WHERE
            id != {book_id}
        ORDER BY
            similarity DESC
        LIMIT {n};
        """

        # Exécuter la requête SQL
        similar_books = self.bddservice.cmd_sql(query)

        return similar_books

    def recommend_books_for_user(self, user_id, n_recommendations=5):
        """
        Recommande les N livres les plus similaires basés sur les livres déjà appréciés ou consultés par l'utilisateur.
        """
        # Récupérer les livres que l'utilisateur a aimés ou consultés
        user_books = self.get_user_books(user_id)  # Fonction que tu devras implémenter pour obtenir les livres d'un utilisateur
        
        # Dictionnaire pour stocker les livres recommandés et leur score de similarité total
        recommendations = {}

        for book in user_books:
            similar_books = self.get_similar_books(book['book_id'], n=n_recommendations)
            
            for similar_book in similar_books:
                book_id = similar_book[0]
                similarity_score = similar_book[2]

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
                    
                # Calcul du score final
                final_score = similarity_score * weight

                # Ajout au dictionnaire des recommandations
                if book_id not in recommendations:
                    recommendations[book_id] = [similar_book[1],final_score]
                else:
                    recommendations[book_id][1] += final_score

        # Trier les recommandations par score décroissant
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

        # Retourner les N meilleurs
        return sorted_recommendations[:n_recommendations]

    def get_user_books(self, user_id):
        """
        Récupère les livres que l'utilisateur a aimés ou consultés.
        Cela peut inclure des livres dans une table de "livres aimés", "historique de consultation", etc.
        """
        # Exemple de requête pour récupérer les livres de l'utilisateur à partir de la base de données
        query = f"""
        SELECT ubr.book_id, ubr.reading_date, ubn.note
        FROM library.User_Book_Read ubr
        LEFT JOIN library.User_Book_Notation ubn ON ubr.read_id = ubn.read_id
        WHERE user_id = {user_id};
        """
        
        # Exécution de la requête SQL
        books = self.bddservice.cmd_sql(query)
        
        return [{'book_id': book[0], 'reading_date': book[1], 'note': book[2]} for book in books] 


# Exemple d'utilisation
if __name__ == "__main__":
    service = RecommendationService()
    service.create_book_vector()
    print("fin")
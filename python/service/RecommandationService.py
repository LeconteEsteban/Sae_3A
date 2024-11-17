import numpy as np
import pandas as pd
import faiss
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class RecommendationService:
    """
    EN DEVELLOPEMENT NE FONCTIONNE PAS / MAL, résultat incohérent, voir traitement.similarity qui fonctionne
    """
    def __init__(self, bddservice, csvservice):
        self.bddservice = bddservice
        self.csvservice = csvservice
    
    def get_similar_books(self, id_book, n_neighbors=10):
        """
        Récupère les livres similaires au livre avec l'id 'id_book'.
        
        Args:
            id_book (int): ID du livre pour lequel nous cherchons les livres similaires.
            n_neighbors (int): Nombre de voisins à récupérer.
        
        Returns:
            pd.DataFrame: Liste des livres similaires avec leurs distances.
        """
        try:
            print(f"Recherche des livres similaire à id : {id_book} ")
            # Récupérer les données des livres
            books = self.bddservice.cmd_sql("""
                SELECT
                    b.book_id, sb.serie_id,
                    ARRAY_AGG(DISTINCT g.genre_id) AS genres,
                    ARRAY_AGG(DISTINCT a.author_id) AS authors,
                    ARRAY_AGG(DISTINCT s.settings_id) AS settings
                FROM library.Book b
                LEFT JOIN library.Serie_of_book sb ON b.book_id = sb.book_id
                LEFT JOIN library.Genre_and_vote gb ON b.book_id = gb.book_id
                LEFT JOIN library.Genre g ON gb.genre_id = g.genre_id
                LEFT JOIN library.Wrote w ON b.book_id = w.book_id
                LEFT JOIN library.Author a ON w.author_id = a.author_id
                LEFT JOIN library.Settings_of_book sb2 ON b.book_id = sb2.book_id
                LEFT JOIN library.Settings s ON sb2.settings_id = s.settings_id
                GROUP BY b.book_id, sb.serie_id
            """)

            # Transformer les résultats en dictionnaire
            books_data = {}
            for row in books:
                book_id = row[0]
                books_data[book_id] = {
                    'book_id': row[0],
                    'serie_id': row[1],
                    'genres': row[2] if row[2] else [],
                    'authors': row[3] if row[3] else [],
                    'settings': row[4] if row[4] else []
                }
            
            # Vectorisation des caractéristiques
            all_genres = list({genre for book in books_data.values() for genre in book['genres']})
            all_authors = list({author for book in books_data.values() for author in book['authors']})
            all_settings = list({setting for book in books_data.values() for setting in book['settings']})
            
            def vectorize_book_features(books_data):
                vectorized_data = []
                for book_id, book in books_data.items():
                    features = []
                    features.extend([1 if genre in book['genres'] else 0 for genre in all_genres])
                    features.extend([1 if author in book['authors'] else 0 for author in all_authors])
                    features.extend([1 if setting in book['settings'] else 0 for setting in all_settings])
                    vectorized_data.append(features)
                return np.array(vectorized_data)

            book_data = vectorize_book_features(books_data)
            print(f"Données vectorisées : {book_data.shape[0]} livres, {book_data.shape[1]} dimensions.")

            # Rechercher les voisins proches du livre avec id_book
            return self.find_neighbors(book_data, id_book, n_neighbors)

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            return pd.DataFrame()

    
    def find_neighbors(self, data, id_book, n_neighbors):
        """
        Trouve les livres voisins les plus proches pour un livre donné.
        
        Args:
            data (pd.DataFrame): Les données des livres où chaque ligne représente un livre,
                                  et chaque colonne représente une caractéristique (genre, auteur, etc.).
            id_book (int): L'ID du livre de référence pour lequel nous recherchons des voisins.
            n_neighbors (int): Nombre de voisins à retourner.
        
        Returns:
            pd.DataFrame: Liste des voisins similaires avec les distances.
        """
        # Étape 1 : Standardisation des données
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        # Étape 2 : Réduction de dimension avec PCA
        pca = PCA(n_components=50)
        data_reduced = pca.fit_transform(data_scaled)

        # Étape 3 : Indexation avec FAISS
        dimension = data_reduced.shape[1]
        index = faiss.IndexFlatL2(dimension)
        faiss.normalize_L2(np.ascontiguousarray(data_reduced, dtype=np.float32))  # Normalisation des vecteurs

        # Ajouter les données à l'index
        index.add(data_reduced)

        # Étape 4 : Recherche du livre similaire
        query_vector = data_reduced[id_book].reshape(1, -1)
        distances, indices = index.search(query_vector, n_neighbors)

        # Étape 5 : Afficher les voisins similaires et leurs distances
        similar_books = []
        for i, dist in zip(indices[0], distances[0]):
            similar_books.append({
                'book_id': i,
                'similarity': 1 / (1 + dist)  # Convertir la distance en similarité
            })
        
        # Convertir en DataFrame pour un affichage facile
        similar_books_df = pd.DataFrame(similar_books)
        return similar_books_df

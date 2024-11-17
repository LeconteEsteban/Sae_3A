import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import faiss
import re

class traitement:
    """
    Class pour le traitement des données sql

    Gestion des MATERIALIZED VIEW, prétraitement, ...
    """

    def __init__(self, bdd, csvservice):
        self.bddservice = bdd
        self.csvservice = csvservice
        self.csvservice.get_csv_author()
        self.csvservice.get_csv_book()
        self.csvservice.get_csv_questionary()
        return

    def traitementTotal(self):
        """
        Fonction opérationnel pour faire tout les traitements
        """
        try:
            self.MV()
            self.table_book_similarity()

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def MV(self):
        """
        Fonction qui met à jour toutes les MATERIALIZED VIEW
        """
        try:
            self.MV_top_book()

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def MV_top_book(self):
        """
        Met à jour la vue materialisé: top_book
        """
        try:
            print("Début du traitement")

            self.bddservice.cmd_sql("REFRESH MATERIALIZED VIEW CONCURRENTLY library.top_books;")

            print("Fin du traitement")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def table_book_similarity(self):
        self.fill_book_similarity()

    def fill_book_similarity(self):
        """
        Main fonction pour remplir la table book_similarity avec ANN et PCA.
        A améliorer:
            - en prennant en compte le titre et la description par exemple.
            - Utiliser la mise en cache 
            - transpherer dans le service recommandation
        """
        try:
            print("Début du traitement book_similarity ...", end="\r")
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
            
            # Recherche ANN avec PCA
            n_neighbors = 10
            indices, distances = self.build_ann_with_pca(book_data, n_components=50, n_neighbors=n_neighbors)
            
            # Insertion des résultats dans la base
            for book_idx, neighbors in enumerate(indices):
                print(f"book en cours : {book_idx}", end="\r")
                book_id1 = list(books_data.keys())[book_idx]
                for i, neighbor_idx in enumerate(neighbors):
                    if book_idx != neighbor_idx:  # Exclure soi-même
                        book_id2 = list(books_data.keys())[neighbor_idx]
                        similarity_score = 1 - distances[book_idx][i]  # Distance -> Similarité
                        cmd = f"""
                            INSERT INTO library.Book_similarity (book_id1, book_id2, similarity_score) 
                            VALUES ({book_id1}, {book_id2}, {similarity_score})
                            ON CONFLICT (book_id1, book_id2) 
                            DO UPDATE SET similarity_score = EXCLUDED.similarity_score;
                        """
                        self.bddservice.cmd_sql(cmd)

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def build_ann_with_pca(self, data, n_components=50, n_neighbors=10):
        """
        Implémente un système ANN avec réduction de dimension PCA.
        
        Args:
            data (pd.DataFrame): Les données des livres où chaque ligne représente un livre, 
                                et chaque colonne représente une caractéristique (genre, auteur, etc.).
            n_components (int): Le nombre de dimensions à conserver après PCA.
            n_neighbors (int): Le nombre de voisins les plus proches à trouver pour chaque livre.
        
        Returns:
            neighbors (list of list): Liste des indices des voisins proches pour chaque livre.
        """
        # Étape 1 : Standardisation des données
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        # Assurez-vous que les données sont contiguës en mémoire
        data_scaled = np.ascontiguousarray(data_scaled, dtype=np.float32)

        # Étape 2 : Réduction de dimension avec PCA
        pca = PCA(n_components=n_components)
        data_reduced = pca.fit_transform(data_scaled)
        
        print(f"Dimensions réduites à {data_reduced.shape[1]} à partir de {data_scaled.shape[1]}.")

        # Étape 3 : Indexation avec Faiss
        # Initialisation d'un index FAISS basé sur L2 (distance Euclidienne)
        dimension = data_reduced.shape[1]
        index = faiss.IndexFlatL2(dimension)
        print("1")
        # Normalisation des vecteurs pour de meilleures performances
        faiss.normalize_L2(np.ascontiguousarray(data_reduced, dtype=np.float32))
        print("2")
        # Ajouter les données à l'index
        index.add(data_reduced)
        print("3")
        # Étape 4 : Recherche des k-nearest neighbors
        distances, indices = index.search(data_reduced, n_neighbors)

        print(f"Recherche terminée. Trouvé {n_neighbors} voisins pour chaque livre.")
        return indices, distances

    def parse_genre_votes(self, genre_and_votes):
        """
        Fonction pour transformer la colonne 'genre_and_votes' en un dictionnaire {genre: votes}
        """
        # Diviser par '/' pour séparer chaque genre-vote
        genre_votes = genre_and_votes.split('/')
        
        # Extraire le genre et le vote pour chaque segment
        parsed_genre_votes = {}
        for genre_vote in genre_votes:
            genre_vote = genre_vote.strip()  # Supprimer les espaces inutiles
            match = re.match(r'([A-Za-z- ]+)\s(\d+)', genre_vote)
            if match:
                genre = match.group(1).strip()
                vote = int(match.group(2))
                parsed_genre_votes[genre] = vote

        return parsed_genre_votes


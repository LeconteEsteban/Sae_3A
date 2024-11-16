import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import re
from itertools import combinations

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

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def MV(self):
        try:
            self.MV_top_book()

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def MV_top_book(self):
        try:
            print("Début du traitement")

            self.bddservice.cmd_sql("REFRESH MATERIALIZED VIEW CONCURRENTLY library.top_books;")

            print("Fin du traitement")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")


    def similarity(self):
        self.fill_book_similarity()

        
    def calculate_similarity(book1, book2, genre_clusters):
        """
        Fonction de calcul de similarité améliorée
        """
        score = 0

        # Même série
        if book1['serie_id'] == book2['serie_id']:
            score += 2

        # Même genre
        common_genres = set(book1['genres']).intersection(book2['genres'])
        score += len(common_genres) * 1  # 1 point par genre commun

        # Bonus si les genres sont dans le même cluster
        if genre_clusters.get(book1['book_id']) == genre_clusters.get(book2['book_id']):
            score += 1  # Bonus de 1 points pour des genres dans le même cluster

        # Même auteur
        common_authors = set(book1['authors']).intersection(book2['authors'])
        score += len(common_authors) * 1  # 1 point par auteur commun

        # Même personnages
        common_characters = set(book1['characters']).intersection(book2['characters'])
        score += len(common_characters) * 0.4  # 0.4 point par personnage commun

        # Même décors
        common_settings = set(book1['settings']).intersection(book2['settings'])
        score += len(common_settings) * 0.4  # 0.4 point par décor commun

        # Même éditeur
        if book1['publisher_id'] == book2['publisher_id']:
            score += 0.1

        return score


    def fill_book_similarity(self):
        """
        main fonction pour remplir la table book_similarity
        """
        # Récupérer les informations de tous les livres
        books = self.bddservice.cmd_sql("""
            SELECT
                b.book_id, b.publisher_id, sb.serie_id,
                ARRAY_AGG(DISTINCT g.genre_id) AS genres,
                ARRAY_AGG(DISTINCT a.author_id) AS authors,
                ARRAY_AGG(DISTINCT c.characters_id) AS characters,
                ARRAY_AGG(DISTINCT s.settings_id) AS settings
            FROM library.Book b
            LEFT JOIN library.Serie_of_book sb ON b.book_id = sb.book_id
            LEFT JOIN library.Genre_and_vote gb ON b.book_id = gb.book_id
            LEFT JOIN library.Genre g ON gb.genre_id = g.genre_id
            LEFT JOIN library.Wrote w ON b.book_id = w.book_id
            LEFT JOIN library.Author a ON w.author_id = a.author_id
            LEFT JOIN library.Characters_of_book cb ON b.book_id = cb.book_id
            LEFT JOIN library.Characters c ON cb.characters_id = c.characters_id
            LEFT JOIN library.Settings_of_book sb2 ON b.book_id = sb2.book_id
            LEFT JOIN library.Settings s ON sb2.settings_id = s.settings_id
            GROUP BY b.book_id, b.publisher_id, sb.serie_id
        """)

        print(books)

        # Transformer les résultats en dictionnaire
        books_data = {}
        for row in books:
            book_id = row[0]
            books_data[book_id] = {
                'book_id': row[0],
                'publisher_id': row[1],
                'serie_id': row[2],
                'genres': row[3] if row[3] else [],
                'authors': row[4] if row[4] else [],
                'characters': row[5] if row[5] else [],
                'settings': row[6] if row[6] else []
            }

        # Calculer la similarité entre chaque paire de livres et insérer dans la table Book_similarity
        for book_id1, book_id2 in combinations(books_data.keys(), 2):
            book1 = books_data[book_id1]
            book2 = books_data[book_id2]

            similarity_score = self.calculate_similarity(book1, book2, self.cluster_genre())

            # Insérer dans la table Book_similarity si le score est significatif (ex. > 0)
            if similarity_score > 0:
                cmd = f"""
                    INSERT INTO library.Book_similarity (book_id1, book_id2, similarity_score) 
                    VALUES ({book_id1}, {book_id2}, {similarity_score})
                    ON CONFLICT (book_id1, book_id2) 
                    DO UPDATE SET similarity_score = EXCLUDED.similarity_score;
                    """
                self.bddservice.cmd_sql(cmd)

    
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

    def cluster_genre(self):
        """
        return un cluster de livre et de genre
        """
        df_clust = self.csvservice.dataframes["books"].dropna()
        df_genre = df_clust[['genre_and_votes']].copy()

        # Appliquer la fonction à la colonne 'genre_and_votes' pour obtenir une liste de dictionnaires
        df_genre['genre_votes_dict'] = df_genre['genre_and_votes'].apply(self.parse_genre_votes)

        # Obtenir la liste de tous les genres uniques
        all_genres = set()
        df_genre['genre_votes_dict'].apply(lambda x: all_genres.update(x.keys()))

        # Créer un dictionnaire pour stocker les données des nouvelles colonnes
        genre_data = {}
        for genre in all_genres:
            genre_data[genre] = df_genre['genre_votes_dict'].apply(lambda x: x.get(genre, 0))

        # Concaténer les nouvelles colonnes au DataFrame df_genre
        df_genre = pd.concat([df_genre, pd.DataFrame(genre_data)], axis=1)

        # Supprimer la colonne intermédiaire
        df_genre = df_genre.drop(columns=['genre_votes_dict'])

        # Sélectionner les colonnes de genres pour le clustering
        genre_columns = list(all_genres)
        genre_features = df_genre[genre_columns]

        # Standardiser les données
        scaler = StandardScaler()
        genre_features_scaled = scaler.fit_transform(genre_features)

        # Appliquer KMeans pour créer des clusters de genres
        n_clusters = 30  # Choisissez un nombre de clusters pertinent
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        df_genre['genre_cluster'] = kmeans.fit_predict(genre_features_scaled)

        # Stocker les clusters dans une table temporaire
        genre_clusters = dict(zip(df_genre['book_id'], df_genre['genre_cluster']))
        return genre_clusters






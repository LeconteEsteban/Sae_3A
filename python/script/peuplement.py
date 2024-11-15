import sys
import os
import re

# Ajoute le dossier parent au chemin pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.DatabaseService import *
from service.CSVService import *

class peuplement:
    """
    Class pour le peuplement
    """

    def __init__(self, bdd):
        self.bddservice = bdd
        self.csvservice = CSVService()
        self.csvservice.get_csv_author()
        self.csvservice.get_csv_book()
        self.csvservice.get_csv_questionary()
        return

    def table_test(self):
        print("1")

    def table_genre(self):
        """
        Crée la table Genre à partir des données du DataFrame.
        """
        df_clust = self.csvservice.dataframes["books"].dropna()
        df_genre = df_clust[['genre_and_votes']].copy()

        # Extraction des genres et votes
        def parse_genre_votes(genre_and_votes):
            genre_votes = re.findall(r'([\w\s-]+)\s(\d+)', genre_and_votes)
            return {genre.strip(): int(vote) for genre, vote in genre_votes}

        df_genre['genre_votes_dict'] = df_genre['genre_and_votes'].apply(parse_genre_votes)

        # Récupération des genres uniques
        all_genres = set()
        df_genre['genre_votes_dict'].apply(lambda x: all_genres.update(x.keys()))

        # Préparation des données pour l'insertion
        genres_data = [{'name': genre} for genre in all_genres]
        # Insertion dans la base de données
        self.bddservice.insert_sql("Genre", genres_data)

    def table_publisher(self):
        """
        Crée la table Publisher à partir des données du DataFrame.
        """
        publishers_data = [{'name': publisher} for publisher in self.csvservice.dataframes["books"]['publisher'].dropna().unique()]
        self.bddservice.insert_sql("Publisher", publishers_data)
        
    def table_award(self):
        """
        Crée la table Award à partir des données du DataFrame.
        """
        awards_data = [{'name': award} for award in self.csvservice.dataframes["books"]["awards"].dropna().unique()]
        self.bddservice.insert_sql("Award", awards_data)
        
    def table_settings(self):
        """
        Crée la table Settings à partir des données du DataFrame.
        """
        settings_data = [{'description': setting} for setting in self.csvservice.dataframes["books"]["settings"].dropna().unique()]
        self.bddservice.insert_sql("Settings", settings_data)
        
    def table_characters(self):
        """
        Crée la table Characters à partir des données du DataFrame.
        """
        characters_data = [{'name': character} for character in self.csvservice.dataframes["books"]["characters"].dropna().unique()]
        self.bddservice.insert_sql("Characters", characters_data)
        
    def table_series(self):
        """
        Crée la table Series à partir des données du DataFrame.
        """
        series_data = [{'name': series} for series in self.csvservice.dataframes["books"]["series"].dropna().unique()]
        self.bddservice.insert_sql("Serie", series_data)
        
    def table_author(self):
        """
        Crée la table Author à partir des données du DataFrame des auteurs.
        """
        authors_data = self.csvservice.dataframes["authors"][['author_name', 'author_gender', 'birthplace']].dropna()
        authors_data = authors_data.rename(columns={'author_name': 'name', 'author_gender': 'gender'})
        authors_data_dict = authors_data.to_dict(orient='records')
        self.bddservice.insert_sql("Author", authors_data_dict)
        
    def table_book(self):
        """
        Crée la table Book à partir des données du DataFrame.
        """
        # Récupérer uniquement les noms et IDs des éditeurs
        df_publishers_id = self.bddservice.select_sql("publisher")[['name', 'publisher_id']]
        publisher_ids = dict(zip(df_publishers_id['name'], df_publishers_id['publisher_id']))
        books_data_dict = self.csvservice.dataframes["books"].apply(lambda row: {
            "title": row["title"],
            "number_of_pages": row["number_of_pages"] if pd.notna(row["number_of_pages"]) else None,
            "publication_date": pd.to_datetime(row["year_published"], format='%Y', errors='coerce').date() if pd.notna(row["year_published"]) else None,
            "isbn": row["isbn"] if pd.notnull(row["isbn"]) else None,
            "isbn13": row["isbn13"] if pd.notnull(row["isbn13"]) else None,
            "description": row["description"] if pd.notnull(row["description"]) else None,
            "original_title": row["original_title"] if pd.notnull(row["original_title"]) else None,
            "publisher_id": publisher_ids.get(row['publisher'])
        }, axis=1)

        # Convertir en liste de dictionnaires et filtrer les enregistrements valides
        books_data_dict = [
            {key: (value if not pd.isna(value) else None) for key, value in book.items()}
            for book in books_data_dict if book["publisher_id"] is not None
        ]

        # Insertion dans la base de données
        self.bddservice.insert_sql("Book", books_data_dict)
        
    def table_rating_book(self):
        """
        Crée la table Rating_book à partir des données du DataFrame.
        """
        # Récupérer les IDs des livres
        df_books_id = self.bddservice.select_sql("Book")[['title', 'book_id']]
        book_ids = dict(zip(df_books_id['title'], df_books_id['book_id']))
        rating_book_data = self.csvservice.dataframes["books"].apply(lambda row: {
            "book_id": book_ids.get(row["title"]),
            "rating_count": row["rating_count"] if pd.notna(row["rating_count"]) else None,
            "review_count": row["review_count"] if pd.notna(row["review_count"]) else None,
            "average_rating": row["average_rating"] if pd.notna(row["average_rating"]) else None,
            "five_star_rating": row["five_star_ratings"] if pd.notna(row["five_star_ratings"]) else None,
            "four_star_rating": row["four_star_ratings"] if pd.notna(row["four_star_ratings"]) else None,
            "three_star_rating": row["three_star_ratings"] if pd.notna(row["three_star_ratings"]) else None,
            "two_star_rating": row["two_star_ratings"] if pd.notna(row["two_star_ratings"]) else None,
            "one_star_rating": row["one_star_ratings"] if pd.notna(row["one_star_ratings"]) else None
        }, axis=1)

        # Filtrer les enregistrements valides
        rating_book_data = [rating for rating in rating_book_data if rating["book_id"] is not None]

        # Insertion dans la base de données
        self.bddservice.insert_sql("Rating_book", rating_book_data)

    def table_rating_author(self):
        """
        Crée la table Rating_author à partir des données du DataFrame.
        """
        # Récupérer les IDs des auteurs
        df_authors_id = self.bddservice.select_sql("Author")[['name', 'author_id']]
        author_ids = dict(zip(df_authors_id['name'], df_authors_id['author_id']))
        # Préparer les données pour Rating_author avec apply
        rating_author_data = self.csvservice.dataframes["authors"].apply(lambda row: {
            "author_id": author_ids.get(row["author_name"]),  # Assurez-vous d'utiliser author_ids ici
            "average_author_rating": float(row["author_average_rating"].replace(",", ".")) if pd.notna(row["author_average_rating"]) else None,
            "author_rating_count": row["author_rating_count"] if pd.notna(row["author_rating_count"]) else None,
            "author_review_count": row["author_review_count"] if pd.notna(row["author_review_count"]) else None
        }, axis=1)

        # Filtrer les enregistrements pour ne conserver que ceux avec un author_id valide
        rating_author_data = [rating for rating in rating_author_data if rating["author_id"] is not None]

        # Insérer les données dans la table Rating_author
        print("Insertion des données des évaluations des auteurs...")
        self.bddservice.insert_sql("Rating_author", rating_author_data)

    def associate_and_insert(self, table1_name, table2_name, relation_table_name, df, col1_name, col2_name):
        """
        Associe les données entre deux tables via une table de relation.
        """
        try:
            df_table1_id = self.bddservice.select_sql(table1_name)[[col1_name, f'{table1_name.lower()}_id']]
            table1_ids = dict(zip(df_table1_id[col1_name], df_table1_id[f'{table1_name.lower()}_id']))

            df_table2_id = self.bddservice.select_sql(table2_name)[[col2_name, f'{table2_name.lower()}_id']]
            table2_ids = dict(zip(df_table2_id[col2_name], df_table2_id[f'{table2_name.lower()}_id']))

            relation_data_set = set()
            for _, row in df.iterrows():
                if pd.notna(row[col1_name]) and pd.notna(row[col2_name]):
                    table1_id = table1_ids.get(row[col1_name])
                    table2_splits = row[col2_name].split(",")
                    for table2_split in table2_splits:
                        table2_id = table2_ids.get(table2_split.strip())
                        if table1_id and table2_id:
                            relation_data_set.add((table1_id, table2_id))

            relation_data = [{f'{table1_name.lower()}_id': table1_id, f'{table2_name.lower()}_id': table2_id}
                             for table1_id, table2_id in relation_data_set]

            print(f"Insertion des relations {relation_table_name}...")
            self.bddservice.insert_sql(relation_table_name, relation_data)
        except Exception as e:
            print(f"Erreur lors de l'association {table1_name}-{table2_name}: {e}")
    



    def table_characters_of_book(self):
        self.associate_and_insert('Book', 'Characters', 'characters_of_book', self.csvservice.dataframes["books"], 'title', 'name')

    def table_setting_of_book(self):
        self.associate_and_insert('Book', 'Settings', 'setting_of_book', self.csvservice.dataframes["books"], 'title', 'description')

    def table_award_of_book(self):
        self.associate_and_insert('Book', 'Award', 'award_of_book', self.csvservice.dataframes["books"], 'title', 'name')

    def table_serie_of_book(self):
        self.associate_and_insert('Book', 'Serie', 'serie_of_book', self.csvservice.dataframes["books"], 'title', 'name')

    def table_genre_and_vote(self):
        1
    

    def peuplementTotal():
        peuplement1 = peuplement()
        csv_service = CSVService()

        try:
            print("Insertion des données dans les tables principales...")

            # Création des tables
            peuplement1.table_genre()
            print("Table Genre remplie avec succès.")

            peuplement1.table_publisher()
            print("Table Publisher remplie avec succès.")

            peuplement1.table_award()
            print("Table Award remplie avec succès.")

            peuplement1.table_settings()
            print("Table Settings remplie avec succès.")

            peuplement1.table_characters()
            print("Table Characters remplie avec succès.")

            peuplement1.table_series()
            print("Table Series remplie avec succès.")

            peuplement1.table_author()
            print("Table Author remplie avec succès.")

            peuplement1.table_book()
            print("Table Book remplie avec succès.")

            peuplement1.table_rating_book()
            print("Table Rating_book remplie avec succès.")

            peuplement1.table_rating_author()
            print("Table Rating_author remplie avec succès. ")


            
            print("Toutes les données ont été insérées avec succès.")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    peuplement1 = peuplement()
    csv_service = CSVService()

    try:
        print("Insertion des données dans les tables principales...")

        # Peupleument des tables
        peuplement1.table_genre()
        print("Table Genre remplie avec succès.")

        peuplement1.table_publisher()
        print("Table Publisher remplie avec succès.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

"""

"""
import sys
import os

# Ajoute le dossier parent au chemin pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.bdd import *
from service.csv_service import *

class peuplement:
    """
    Gere le peuplement
    """

    def __init__(self):
        return 1

    def table_genre(self, df):
        """
        Crée la table Genre à partir des données du DataFrame.
        """
        df_clust = df.dropna()
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
        self.insert_sql("Genre", genres_data)

    def table_publisher(self, df):
        """
        Crée la table Publisher à partir des données du DataFrame.
        """
        publishers_data = [{'name': publisher} for publisher in df['publisher'].dropna().unique()]
        self.insert_sql("Publisher", publishers_data)
        
    def table_award(self, df):
        """
        Crée la table Award à partir des données du DataFrame.
        """
        awards_data = [{'name': award} for award in df["awards"].dropna().unique()]
        self.insert_sql("Award", awards_data)
        
    def table_settings(self, df):
        """
        Crée la table Settings à partir des données du DataFrame.
        """
        settings_data = [{'description': setting} for setting in df["settings"].dropna().unique()]
        self.insert_sql("Settings", settings_data)
        
    def table_characters(self, df):
        """
        Crée la table Characters à partir des données du DataFrame.
        """
        characters_data = [{'name': character} for character in df["characters"].dropna().unique()]
        self.insert_sql("Characters", characters_data)
        
    def table_series(self, df):
        """
        Crée la table Series à partir des données du DataFrame.
        """
        series_data = [{'name': series} for series in df["series"].dropna().unique()]
        self.insert_sql("Serie", series_data)
        
    def table_author(self, df_author):
        """
        Crée la table Author à partir des données du DataFrame des auteurs.
        """
        authors_data = df_author[['author_name', 'author_gender', 'birthplace']].dropna()
        authors_data = authors_data.rename(columns={'author_name': 'name', 'author_gender': 'gender'})
        authors_data_dict = authors_data.to_dict(orient='records')
        self.insert_sql("Author", authors_data_dict)
        
    def table_book(self, df, publisher_ids):
        """
        Crée la table Book à partir des données du DataFrame.
        """
        books_data_dict = df.apply(lambda row: {
            "title": row["title"],
            "number_of_pages": row["number_of_pages"] if pd.notna(row["number_of_pages"]) else None,
            "publication_date": row["year_published"] if pd.notna(row["year_published"]) else None,
            "isbn": row["isbn"] if pd.notnull(row["isbn"]) else None,
            "isbn13": row["isbn13"] if pd.notnull(row["isbn13"]) else None,
            "description": row["description"] if pd.notnull(row["description"]) else None,
            "original_title": row["original_title"] if pd.notnull(row["original_title"]) else None,
            "publisher_id": publisher_ids.get(row['publisher'])
        }, axis=1)

        # Filtrer les enregistrements valides
        books_data_dict = [book for book in books_data_dict if book["publisher_id"] is not None]

        # Insertion dans la base de données
        self.insert_sql("Book", books_data_dict)
        
    def table_rating_book(self, df, book_ids):
        """
        Crée la table Rating_book à partir des données du DataFrame.
        """
        rating_book_data = df.apply(lambda row: {
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
        self.insert_sql("Rating_book", rating_book_data)

    def associate_and_insert(self, table1_name, table2_name, relation_table_name, df, col1_name, col2_name):
        """
        Associe les données entre deux tables via une table de relation.
        """
        try:
            df_table1_id = self.select_sql(table1_name)[[col1_name, f'{table1_name.lower()}_id']]
            table1_ids = dict(zip(df_table1_id[col1_name], df_table1_id[f'{table1_name.lower()}_id']))

            df_table2_id = self.select_sql(table2_name)[[col2_name, f'{table2_name.lower()}_id']]
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
            self.insert_sql(relation_table_name, relation_data)
        except Exception as e:
            print(f"Erreur lors de l'association {table1_name}-{table2_name}: {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    peuplement1 = peuplement()

    try:
        print("Insertion des données dans les tables principales...")

        # Création des tables
        peuplement1.table_genre(df)
        print("Table Genre créée avec succès.")

        peuplement1.table_publisher(df)
        print("Table Publisher créée avec succès.")

        peuplement1.table_award(df)
        print("Table Award créée avec succès.")

        peuplement1.table_settings(df)
        print("Table Settings créée avec succès.")

        peuplement1.table_characters(df)
        print("Table Characters créée avec succès.")

        peuplement1.table_series(df)
        print("Table Series créée avec succès.")

        peuplement1.table_author(df_authors)
        print("Table Author créée avec succès.")

        peuplement1.table_book(df, publishers_data)
        print("Table Book créée avec succès.")

        peuplement1.table_rating_book(df, rating_book_data)
        print("Table Rating_book créée avec succès.")

        print("Toutes les données ont été insérées avec succès.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

    finally:
        
import sys
import os
import re
import pandas as pd
from service.EmbeddingService import *
from service.CacheService import *
from datetime import datetime

# Ajoute le dossier parent au chemin pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class peuplement:
    """
    Class pour le peuplement
    """

    def __init__(self, bdd, csvservice, parseservice):
        self.bddservice = bdd
        self.csvservice = csvservice
        self.parseservice = parseservice
        self.csvservice.get_csv_author()
        self.csvservice.get_csv_book()
        self.csvservice.get_csv_questionary()
        self.embedding_service=EmbeddingService()
        self.cache_service=CacheService()
        return

    def peuplementTotal(self):
        """
        Fonction opérationnel pour faire tout le peuplement
        """
        try:
            print("Insertion des données dans les tables principales...")
            
            # Création des tables
            self.table_genre()
            self.table_author()
            
            self.table_publisher()
            self.table_award()
            self.table_settings()
            self.table_characters()
            self.table_series()

            self.table_book()

            self.table_user()

            self.table_rating_book()
            self.table_rating_author()

            self.table_characters_of_book()
            self.table_award_of_book()
            self.table_serie_of_book()
            self.table_setting_of_book()

            self.table_genre_and_vote()
            self.table_wrote()

            
            print("Toutes les données ont été insérées avec succès.")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")




    def table_user(self):
        df = self.csvservice.dataframes["questionary"]
        df = df.loc[df["Donnez vous votre consentement à l'utilisation de vos réponses pour un traitement informatique ?"] == "J'accepte"]

        df["Lieu d'habitation"] = df["Lieu d'habitation"].apply(
            lambda x: self.parseservice.clean_string(self.parseservice.replace_with_regex(x, r"\s*\([^)]*\)", ""))
        )

        df["Quel format de lecture / achats préférez-vous ?"] = df["Quel format de lecture / achats préférez-vous ?"].apply(
            lambda x: [self.parseservice.clean_string(item) for item in self.parseservice.split_string(x, delimiter=",")]
        )

        df["Quel genre de livre préférez-vous ?"] = df["Quel genre de livre préférez-vous ?"].apply(
            lambda x: [self.parseservice.clean_string(item) for item in self.parseservice.split_string(x, delimiter=",")]
        )

        df["Dans quel cadre / objectif pratiquez-vous la lecture ?"] = df["Dans quel cadre / objectif pratiquez-vous la lecture ?"].apply(
            lambda x: [self.parseservice.clean_string(item) for item in self.parseservice.split_string(x, delimiter=",")]
        )

        users_data = []
        for _, row in df.iterrows():
            user = {
                "name": None,
                "age": row["Quel âge avez-vous ?"],
                "passwords" : None,
                "child": row["Avez-vous des enfants ?"] == "Oui",
                "familial_situation": row["Situation familiale"],
                "gender": row["Genre"],
                "cat_socio_pro": row["Quelle est votre catégorie socio-professionnelle ?"],
                "lieu_habitation": row["Lieu d'habitation"],
                "frequency": row["À quelle fréquence lisez-vous ?"],
                "book_size": row["Quelle taille de livres préférez vous lire ?"],
                "birth_date": None,
            }
            users_data.append(user)
            
        self.bddservice.insert_sql("_Users", users_data)

        # Récupérer les IDs des genres
        df_genres_id = self.bddservice.select_sql("genre")[['name', 'genre_id']]
        genre_ids = dict(zip(df_genres_id['name'], df_genres_id['genre_id']))

        if self.cache_service.exists_json("genres_embeddings"):
            # Charger le CSV en tant que DataFrame et convertir en dictionnaire
            genres_embeddings = self.cache_service.get_dict_cache("genres_embeddings")
        else:
            # Créer des embeddings pour tous les auteurs
            genres_embeddings = {name: self.embedding_service.embeddingText(name) for name in genre_ids.keys()}
            self.cache_service.dict_to_cache("genres_embeddings", genres_embeddings)

        # Créer le dictionnaire user_id => id_genre
        genre_dict = {}
        for user_id, row in df.iterrows():
            genres = row["Quel genre de livre préférez-vous ?"]
            isnan = True
            if isinstance(genres, float):  # Vérifiez si la valeur est un flottant (NaN)
                isnan = False
            if isnan:
                # Créer un embedding pour l'auteur préféré de l'utilisateur
                for elem in genres:
                    user_genre_embedding = self.embedding_service.embeddingText(elem)
                    similar_genre=False
                    final_genre = ""
                    final_similarity = 0

                    for genre_name,genre_embedding in genres_embeddings.items():
                        similarity = self.embedding_service.compare(user_genre_embedding,genre_embedding)
                        if similarity > 0.4:
                            similar_genre= True
                            if similarity>final_similarity:
                                final_genre = genre_name
                                final_similarity = similarity

                    if similar_genre:
                        if user_id not in genre_dict:
                            genre_dict[user_id] = []
                        genre_dict[user_id].append(genre_ids[final_genre])

        genre_list = []
        for user_id, genre_ids in genre_dict.items():
            for genre_id in genre_ids:
                genre_like = {
                    "user_id" : user_id + 1,
                    "genre_id" : genre_id,
                }
                genre_list.append(genre_like)

        try:
            self.bddservice.insert_sql("user_liked_genre", genre_list)
        except Exception as e:
            print("Aucun auteur n'est identifiable")

        # Récupérer les IDs des auteurs
        author_id = self.bddservice.select_sql("author")[['author_id', 'name']]
        author_ids = dict(zip(author_id['name'], author_id['author_id']))

        if self.cache_service.exists_json("author_embeddings"):
            # Charger le CSV en tant que DataFrame et convertir en dictionnaire
            author_embeddings = self.cache_service.get_dict_cache("author_embeddings")
        else:
            # Créer des embeddings pour tous les auteurs
            author_embeddings = {name: self.embedding_service.embeddingText(name) for name in author_ids.keys()}
            self.cache_service.dict_to_cache("author_embeddings", author_embeddings)

        author_dict = {}
        for user_id, row in df.iterrows():
            authors = row["Quel est votre auteur préféré ?"]
            isnan = True
            if isinstance(authors, float):  # Vérifiez si la valeur est un flottant (NaN)
                isnan = False
            if isnan:
                # Créer un embedding pour l'auteur préféré de l'utilisateur
                user_author_embedding = self.embedding_service.embeddingText(authors.strip())
                similar_authors=False
                final_author = ""
                final_similarity = 0

                for author_name,author_embedding in author_embeddings.items():
                    similarity = self.embedding_service.compare(user_author_embedding,author_embedding)
                    if similarity > 0.7:
                        similar_authors= True
                        if similarity>final_similarity:
                            final_author = author_name
                            final_similarity = similarity

                if similar_authors:
                    if user_id not in author_dict:
                        author_dict[user_id] = []
                    author_dict[user_id].append(author_ids[final_author])

        author_list = []
        for user_id, author_ids in author_dict.items():
            for author_id in author_ids:
                author_like = {
                    "user_id": user_id + 1,
                    "author_id": author_id,
                }
                #print(author_like["user_id"],author_like["author_id"])
                author_list.append(author_like)

        try:
            self.bddservice.insert_sql("liked_author", author_list)
        except Exception as e:
            print("Aucun auteur n'est identifiable")

        format_list = []
        for user_id, row in df.iterrows():
            formats = row["Quel format de lecture / achats préférez-vous ?"]
            if not isinstance(formats, list):
                formats = [formats]  # Convertir en liste si ce n'est pas déjà le cas
            for format in formats:
                format_like = {
                    "user_id": user_id + 1,
                    "format": format
                }
                format_list.append(format_like)

        # Appeler insert_sql une seule fois avec la liste complète
        try:
            self.bddservice.insert_sql("preferred_format_of_reading", format_list)
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'insertion : {e}")

        field_list = []
        for user_id, row in df.iterrows():
            fields = row["Dans quel cadre / objectif pratiquez-vous la lecture ?"]
            if not isinstance(fields, list):
                fields = [fields]  # Convertir en liste si ce n'est pas déjà le cas
            for field in fields:
                field_like = {
                    "user_id": user_id + 1,
                    "field": field
                }
                field_list.append(field_like)

        # Appeler insert_sql une seule fois avec la liste complète
        try:
            self.bddservice.insert_sql("User_field_of_reading", field_list)
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'insertion : {e}")



        df_book = self.bddservice.select_sql("Book")[['title', 'book_id']]
        books_ids = dict(zip(df_book['title'], df_book['book_id']))

        if self.cache_service.exists_json("book_embedding"):
            # Charger le CSV en tant que DataFrame et convertir en dictionnaire
            book_embeddings = self.cache_service.get_dict_cache("book_embedding")
        else:
            # Créer des embeddings pour tous les auteurs
            book_embeddings = {name: self.embedding_service.embeddingText(name) for name in books_ids.keys()}
            self.cache_service.dict_to_cache("book_embedding", book_embeddings)


        book_dict = {}
        for user_id, row in df.iterrows():
            book = row["Quel est votre livre préféré ?"]
            isnan = True
            if isinstance(book, float):  # Vérifiez si la valeur est un flottant (NaN)
                isnan = False
            if isnan:
                # Créer un embedding pour l'auteur préféré de l'utilisateur
                user_book_embedding = self.embedding_service.embeddingText(book.strip())
                similar_book=False
                final_book = ""
                final_similarity = 0

                for book_name,book_embedding in book_embeddings.items():
                    similarity = self.embedding_service.compare(user_book_embedding,book_embedding)
                    if similarity > 0.1:
                        similar_book= True
                        if similarity>final_similarity:
                            final_book = book_name
                            final_similarity = similarity

                if similar_book:
                    if user_id not in book_dict:
                        book_dict[user_id] = []
                    #print("400",final_book)
                    book_dict[user_id].append(books_ids[final_book])

        book_list = []
        for user_id, book_ids in book_dict.items():
            for book_id in book_ids:
                book_like = {
                    "is_read": True,
                    "is_liked": True,
                    "is_favorite": True,
                    "user_id": user_id + 1,
                    "book_id": book_id,
                    "reading_date": datetime.now(),
                    "notation_id": None
                }
                book_list.append(book_like)

        try:
            self.bddservice.insert_sql("User_Book_Read", book_list)
        except Exception as e:
            print("Aucun book n'est identifiable")




    def table_test(self):
        """
        just for testing
        """
        print("1")

    def table_genre(self):
        """
        Crée la table Genre à partir des données du DataFrame.
        """
        print(f"Traitement pour peuplement de la table_genre en cours ... ", end="\r")
        df_clust = self.csvservice.dataframes["books"].dropna()
        df_genre = df_clust[['genre_and_votes']].copy()

        def parse_genre_votes(genre_and_votes):
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
        try:
            print(f"Traitement pour peuplement de la table_publisher en cours ... ", end="\r")
            # Utiliser la fonction générique pour parser la colonne 'publisher'
            unique_publishers = self.parse_and_split_column(
                self.csvservice.dataframes["books"], "publisher", delimiter="/"
            )

            # Préparer les données pour l'insertion
            publishers_data = [{'name': publisher} for publisher in unique_publishers]

            # Insérer dans la base de données
            self.bddservice.insert_sql("Publisher", publishers_data)
        except Exception as e:
            print(f"Erreur lors de la création de la table Publisher : {e}")
        
    def table_award(self):
        """
        Crée la table Award à partir des données du DataFrame.
        """
        try:
            print(f"Traitement pour peuplement de la table_award en cours ... ", end="\r")
            # Utiliser la fonction générique pour parser la colonne 'publisher'
            unique_awards = self.parse_and_split_column(
                self.csvservice.dataframes["books"], "awards", delimiter="/"
            )

            # Préparer les données pour l'insertion
            award_data = [{'name': award} for award in unique_awards]

            # Insérer dans la base de données
            self.bddservice.insert_sql("Award", award_data)
        except Exception as e:
            print(f"Erreur lors de la création de la table Award : {e}")
        
    def table_settings(self):
        """
        Crée la table Settings à partir des données du DataFrame.
        """
        try:
            print(f"Traitement pour peuplement de la table_settings en cours ... ", end="\r")
            # Utiliser la fonction générique pour parser la colonne 'publisher'
            unique_settings = self.parse_and_split_column(
                self.csvservice.dataframes["books"], "settings", delimiter="/"
            )

            # Préparer les données pour l'insertion
            setting_data = [{'description': setting} for setting in unique_settings]

            # Insérer dans la base de données
            self.bddservice.insert_sql("settings", setting_data)
        except Exception as e:
            print(f"Erreur lors de la création de la table setting : {e}")
        
    def table_characters(self):
        """
        Crée la table Characters à partir des données du DataFrame.
        """
        try:
            print(f"Traitement pour peuplement de la table_characters en cours ... ", end="\r")
            # Utiliser la fonction générique pour parser la colonne 'characters'
            unique_characters = self.parse_and_split_column(
                self.csvservice.dataframes["books"], "characters", delimiter="/"
            )

            # Préparer les données pour l'insertion
            characters_data = [{'name': characters} for characters in unique_characters]

            # Insérer dans la base de données
            self.bddservice.insert_sql("characters", characters_data)
        except Exception as e:
            print(f"Erreur lors de la création de la table characters : {e}")
    
    def clean_series_name(self, series_name):
        # Trouver la position de la parenthèse ouvrante et extraire la partie avant
        if '(' in series_name:
            series_name = series_name.split('(')[1].strip()
        # Supprimer le `#` et tout ce qui le suit
        if '#' in series_name:
            series_name = series_name.split('#')[0].strip()
        if ')' in series_name:
            series_name = series_name.split(')')[0].strip()
        return series_name

    def table_series(self):
        """
        Crée la table Series à partir des données du DataFrame, en nettoyant les noms sans regex.
        """
        try:
            print(f"Traitement pour peuplement de la table_series en cours ... ", end="\r")
            # Extraire et nettoyer les séries
            series_cleaned = self.csvservice.dataframes["books"]["series"].dropna()
            series_cleaned = [self.clean_series_name(series) for series in series_cleaned]
            series_cleaned = list(set(series_cleaned))  # Éliminer les doublons

            # Préparer les données pour insertion
            series_data = [{'name': series} for series in series_cleaned]

            # Insérer dans la base de données
            self.bddservice.insert_sql("Serie", series_data)
        except Exception as e:
            print(f"Erreur lors de la création de la table series : {e}")
        
    def process_author_data(self, authors_data):
        """
        Fonction pour nettoyer et préparer les données des auteurs.
        """
        # Nettoyage des données
        authors_data = authors_data.dropna(subset=['author_name'])  # Garder seulement les lignes avec un nom valide
        authors_data['author_name'] = authors_data['author_name'].str.strip()  # Enlever les espaces inutiles
        authors_data['author_gender'] = authors_data['author_gender'].str.strip().str.lower()  # Uniformiser le genre
        authors_data['birthplace'] = authors_data['birthplace'].fillna('Unknown')  # Remplir les lieux de naissance manquants

        # Renommer les colonnes pour correspondre à la table SQL
        authors_data = authors_data.rename(columns={'author_name': 'name', 'author_gender': 'gender'})

        # Suppression des doublons
        #authors_data = authors_data.drop_duplicates(subset=['name','gender','birthplace'])
        
        return authors_data

    def table_author(self):
        """
        Crée la table Author à partir des données du DataFrame des auteurs.
        """
        try:
            print(f"Traitement pour peuplement de la table_author en cours ... ", end="\r")
            # Charger les données nécessaires
            authors_data = self.csvservice.dataframes["authors"][['author_name', 'author_gender', 'birthplace']]

            # Traitement des données des auteurs
            authors_data = self.process_author_data(authors_data)

            # Conversion en dictionnaires
            authors_data_dict = authors_data.to_dict(orient='records')

            # Insertion dans la base de données
            if authors_data_dict:
                self.bddservice.insert_sql("Author", authors_data_dict)
            else:
                print("Aucun auteur valide à insérer.")
        except Exception as e:
            print(f"Erreur lors de la création de la table Author : {e}")

    def table_book(self):
        """
        Crée la table Book à partir des données du DataFrame.
        """
        try:
            print(f"Traitement pour peuplement de la table_book en cours ... ", end="\r")
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
        except Exception as e:
            print(f"Erreur lors de la création de la table Book : {e}")
        
    def table_rating_book(self):
        """
        Crée la table Rating_book à partir des données du DataFrame.
        """
        try:
            print(f"Traitement pour peuplement de la table_rating_book en cours ... ", end="\r")
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
        except Exception as e:
            print(f"Erreur lors de la création de la table rating_book : {e}")

    def table_rating_author(self):
        """
        Crée la table Rating_author à partir des données du DataFrame.
        """
        try:
            print(f"Traitement pour peuplement de la table_rating_author en cours ... ", end="\r")
            # Récupérer les IDs des auteurs
            df_authors_id = self.bddservice.select_sql("Author")[['name', 'author_id']]
            author_ids = dict(zip(df_authors_id['name'], df_authors_id['author_id']))

            # Préparer les données pour Rating_author avec apply
            rating_author_data = self.csvservice.dataframes["authors"].apply(lambda row: {
                "author_id": author_ids.get(row["author_name"].strip()), 
                "average_author_rating": float(row["author_average_rating"].replace(",", ".")) if pd.notna(row["author_average_rating"]) else None,
                "author_rating_count": row["author_rating_count"] if pd.notna(row["author_rating_count"]) else None,
                "author_review_count": row["author_review_count"] if pd.notna(row["author_review_count"]) else None
            }, axis=1)

            # Filtrer les enregistrements pour ne conserver que ceux avec un author_id valide
            rating_author_data = [rating for rating in rating_author_data if rating["author_id"] is not None]

            # Insérer les données dans la table Rating_author
            self.bddservice.insert_sql("Rating_author", rating_author_data)
        except Exception as e:
            print(f"Erreur lors de la création de la table rating_author : {e}")

    def parse_and_split_column(self, dataframe, column_name, delimiter="/"):
        """
        Parse et divise les éléments d'une colonne donnée en utilisant un délimiteur.
        Retourne une liste unique de tous les éléments divisés.

        Args:
            dataframe (pd.DataFrame): Le DataFrame contenant les données.
            column_name (str): Nom de la colonne à parser.
            delimiter (str): Délimiteur utilisé pour séparer les éléments (par défaut : '/').

        Returns:
            list: Une liste de valeurs uniques, nettoyées et triées.
        """
        try:
            # Extraire la colonne, ignorer les valeurs NaN
            column_data = dataframe[column_name].dropna()

            # Diviser les éléments par le délimiteur, puis aplatir la liste
            split_elements = column_data.str.split(delimiter).explode().str.strip()

            # Retirer les doublons et trier les résultats
            unique_elements = split_elements.drop_duplicates().sort_values()

            return unique_elements.tolist()
        except KeyError:
            raise Exception(f"La colonne '{column_name}' est introuvable dans le DataFrame.")
        except Exception as e:
            raise Exception(f"Erreur lors du parsing de la colonne '{column_name}' : {e}")

    def associate_and_insert(self, table1_name, table2_name, relation_table_name, df, col1_name, col2_name, df_table_name):
        """
            Associe les données de deux tables via une table de liaison et insère les associations dans la base de données.
        
            :param table1_name: Nom de la première table (ex: 'Book')
            :param table2_name: Nom de la deuxième table (ex: 'Award')
            :param relation_table_name: Nom de la table de liaison (ex: 'Award_of_book')
            :param df: DataFrame contenant les données à traiter
            :param col1_name: Nom de la colonne de jointure de la première table (ex: 'title' pour 'Book') 
            :param col2_name: Nom de la colonne de jointure de la deuxième table (ex: 'awards' pour 'Award')
            :param df_table_name: Nom de la colonne du csv
            """
        try:
            # Récupérer les IDs des éléments de la première table
            df_table1_id = self.bddservice.select_sql(table1_name)[[col1_name, f'{table1_name.lower()}_id']]
            table1_ids = dict(zip(df_table1_id[col1_name], df_table1_id[f'{table1_name.lower()}_id']))

            # Récupérer les IDs des éléments de la deuxième table
            df_table2_id = self.bddservice.select_sql(table2_name)[[col2_name, f'{table2_name.lower()}_id']]
            table2_ids = dict(zip(df_table2_id[col2_name], df_table2_id[f'{table2_name.lower()}_id']))

            # Créer un ensemble pour stocker les associations uniques
            relation_data_set = set()

            for _, row in df.iterrows():
                if pd.notna(row[col1_name]) and pd.notna(row[df_table_name]):
                    # Récupérer les IDs associés
                    table1_id = table1_ids.get(row[col1_name])
                    table2_splits = row[df_table_name].split("/")  # Séparer les noms par virgule s'il y en a plusieurs

                    for table2_split in table2_splits:
                        table2_id = table2_ids.get(table2_split.strip())  # Enlever les espaces autour du nom
                        if table1_id and table2_id:
                            # Ajouter seulement des paires uniques
                            relation_data_set.add((table1_id, table2_id))

            # Convertir l'ensemble en une liste de dictionnaires pour l'insertion
            relation_data = [{f'{table1_name.lower()}_id': table1_id, f'{table2_name.lower()}_id': table2_id}
                            for table1_id, table2_id in relation_data_set]
            
            # Insertion dans la table de relation
            self.bddservice.insert_sql(relation_table_name, relation_data)
        except Exception as e:
            print(e)

    def associate_and_insert_with_separator(self, table1_name, table2_name, relation_table_name, df, col1_name, col2_name, df_table_name, separator="/"):
        """
        Associe les données de deux tables via une table de liaison et insère les associations avec les votes dans la base de données.

        :param table1_name: Nom de la première table (ex: 'Book')
        :param table2_name: Nom de la deuxième table (ex: 'Genre')
        :param relation_table_name: Nom de la table de liaison (ex: 'Genre_and_vote')
        :param df: DataFrame contenant les données à traiter
        :param col1_name: Nom de la colonne de la première table (ex: 'title' pour 'Book')
        :param col2_name: Nom de la colonne de la deuxième table (ex: 'name' pour 'Genre')
        :param df_table_name: Nom de la colonne contenant les données associées au format genre/vote (ex: 'genre_and_votes')
        :param separator: Caractère séparant les genres et les votes (par défaut : '/')
        """
        try:
            # Récupérer les IDs des éléments de la première table
            df_table1_id = self.bddservice.select_sql(table1_name)[[col1_name, f'{table1_name.lower()}_id']]
            table1_ids = dict(zip(df_table1_id[col1_name], df_table1_id[f'{table1_name.lower()}_id']))

            # Récupérer les IDs des éléments de la deuxième table
            df_table2_id = self.bddservice.select_sql(table2_name)[[col2_name, f'{table2_name.lower()}_id']]
            table2_ids = dict(zip(df_table2_id[col2_name], df_table2_id[f'{table2_name.lower()}_id']))
            
            # Créer un ensemble pour stocker les associations uniques
            relation_data_set = set()
            verif_doublon_set = set()
            
            for _, row in df.iterrows():
                if pd.notna(row[col1_name]) and pd.notna(row[df_table_name]):
                    # Récupérer les IDs associés
                    table1_id = table1_ids.get(row[col1_name])
                    genre_votes = row[df_table_name].split(separator) 
                    
                    for genre_vote in genre_votes:
                        genre_vote = genre_vote.strip()
                        
                        if len(genre_vote.split()) >= 2:
                            *genre_name_parts, vote_count = genre_vote.split()  # Dernier élément est le vote, les autres forment le nom
                            genre_name = " ".join(genre_name_parts).strip()  # Reconstituer le nom du genre sans les votes
                            vote_count = vote_count.strip()

                            # Remplacer '1user' ou des chaînes similaires par un nombre valide
                            if 'user' in vote_count:
                                #print(f"Correction du vote pour le genre '{genre_name}': '{vote_count}' remplacé par '1'")
                                vote_count = '1'  # Vous pouvez remplacer ici par la valeur que vous souhaitez.

                            # Vérification si le vote_count est bien un entier
                            try:
                                vote_count = int(vote_count)  # Conversion en entier
                            except ValueError:
                                print(f"Valeur de vote invalide pour le genre '{genre_name}': '{vote_count}'")
                                continue  # Ignore cette entrée et passe à la suivante

                            table2_id = table2_ids.get(genre_name)  # Enlever les espaces autour du nom

                            if table1_id and table2_id:
                                # Vérifier si la combinaison (table1_id, table2_id) existe déjà dans le set
                                if (table1_id, table2_id) not in verif_doublon_set:
                                    # Ajouter dans le set pour vérifier l'unicité
                                    verif_doublon_set.add((table1_id, table2_id))
                                    
                                    # Ajouter dans le set final avec le vote_count
                                    relation_data_set.add((table1_id, table2_id, vote_count))

                        else:
                            print(f"Format inattendu dans la donnée : {genre_vote}")

            # Convertir l'ensemble en une liste de dictionnaires pour l'insertion
            relation_data = [
                {
                    f'{table1_name.lower()}_id': table1_id,
                    f'{table2_name.lower()}_id': table2_id,
                    'vote_count': vote_count
                }
                for table1_id, table2_id, vote_count in relation_data_set
            ]
            # Insertion dans la table de relation
            self.bddservice.insert_sql(relation_table_name, relation_data)
        except Exception as e:
            print(f"Erreur lors de l'association et de l'insertion : {e}")
            raise
    
    def associate_and_insert_series(self, table1_name, table2_name, relation_table_name, df, col1_name, col2_name, df_table_name):
        """
            Associe les données de deux tables via une table de liaison et insère les associations dans la base de données.
        
            :param table1_name: Nom de la première table 
            :param table2_name: Nom de la deuxième table
            :param relation_table_name: Nom de la table de liaison 
            :param df: DataFrame contenant les données à traiter
            :param col1_name: Nom de la colonne de la première table 
            :param col2_name: Nom de la colonne de la deuxième table 
            """
        try:
            # Récupérer les IDs des éléments de la première table
            df_table1_id = self.bddservice.select_sql(table1_name)[[col1_name, f'{table1_name.lower()}_id']]
            table1_ids = dict(zip(df_table1_id[col1_name], df_table1_id[f'{table1_name.lower()}_id']))

            # Récupérer les IDs des éléments de la deuxième table
            df_table2_id = self.bddservice.select_sql(table2_name)[[col2_name, f'{table2_name.lower()}_id']]
            table2_ids = dict(zip(df_table2_id[col2_name], df_table2_id[f'{table2_name.lower()}_id']))

            # Créer un ensemble pour stocker les associations uniques
            relation_data_set = set()

            for _, row in df.iterrows():
                if pd.notna(row[col1_name]) and pd.notna(row[df_table_name]):
                    # Récupérer les IDs associés
                    table1_id = table1_ids.get(row[col1_name])
                    table2_splits = row[df_table_name].split("/")



                    for table2_split in table2_splits:
                        table2_split = self.clean_series_name(table2_split)
                        table2_id = table2_ids.get(table2_split.strip())  # Enlever les espaces autour du nom
                        if table1_id and table2_id:
                            # Ajouter seulement des paires uniques
                            relation_data_set.add((table1_id, table2_id))

            # Convertir l'ensemble en une liste de dictionnaires pour l'insertion
            relation_data = [{f'{table1_name.lower()}_id': table1_id, f'{table2_name.lower()}_id': table2_id}
                            for table1_id, table2_id in relation_data_set]

            # Insertion dans la table de relation
            self.bddservice.insert_sql(relation_table_name, relation_data)
        except Exception as e:
            print(e)

    def associate_and_insert_wrote(self):
        """
            Associe les données de deux tables via une table de liaison et insère les associations dans la base de données.
        
            :param table1_name: Nom de la première table (ex: 'Book')
            :param table2_name: Nom de la deuxième table (ex: 'Award')
            :param relation_table_name: Nom de la table de liaison (ex: 'Award_of_book')
            :param df: DataFrame contenant les données à traiter
            :param col1_name: Nom de la colonne de jointure de la première table (ex: 'title' pour 'Book') 
            :param col2_name: Nom de la colonne de jointure de la deuxième table (ex: 'awards' pour 'Award')
            :param df_table_name: Nom de la colonne du csv
            """
        table1_name='Book'
        table2_name='Author'
        relation_table_name ='wrote'
        df = self.csvservice.dataframes["books"]
        col1_name = 'title'
        col2_name = 'name'
        df_table_name = 'author'
        try:
            # Récupérer les IDs des éléments de la première table
            df_table1_id = self.bddservice.select_sql(table1_name)[[col1_name, f'{table1_name.lower()}_id']]
            table1_ids = dict(zip(df_table1_id[col1_name], df_table1_id[f'{table1_name.lower()}_id']))

            # Récupérer les IDs des éléments de la deuxième table
            df_table2_id = self.bddservice.select_sql(table2_name)[[col2_name, f'{table2_name.lower()}_id']]
            table2_ids = dict(zip(df_table2_id[col2_name], df_table2_id[f'{table2_name.lower()}_id']))
            #print(table2_ids)
            # Créer un ensemble pour stocker les associations uniques
            relation_data_set = set()

            for _, row in df.iterrows():
                if pd.notna(row[col1_name]) and pd.notna(row[df_table_name]):
                    # Récupérer les IDs associés
                    table1_id = table1_ids.get(row[col1_name])
                    table2_splits = row[df_table_name].split("/")  # Séparer les noms par virgule s'il y en a plusieurs

                    for table2_split in table2_splits:
                        table2_id = table2_ids.get(table2_split.strip())  # Enlever les espaces autour du nom
                        if table1_id and table2_id:
                            # Ajouter seulement des paires uniques
                            relation_data_set.add((table1_id, table2_id))

            # Convertir l'ensemble en une liste de dictionnaires pour l'insertion
            relation_data = [{f'{table1_name.lower()}_id': table1_id, f'{table2_name.lower()}_id': table2_id}
                            for table1_id, table2_id in relation_data_set]

            # Insertion dans la table de relation
            self.bddservice.insert_sql(relation_table_name, relation_data)
        except Exception as e:
            print(e)

    def table_characters_of_book(self):
        """
        Remplie table_characters_of_book à partir du dataframe
        """
        try:
            print(f"Traitement pour peuplement de la table_characters_of_book en cours ... ", end="\r")
            self.associate_and_insert('Book', 'Characters', 'characters_of_book', self.csvservice.dataframes["books"], 'title', 'name', "characters")
        except Exception as e:
            print(f"Erreur lors de la création de la table characters_of_book : {e}")

    def table_setting_of_book(self):
        """
        Remplie table_setting_of_book
        """
        try:
            print(f"Traitement pour peuplement de la table_setting_of_book en cours ... ", end="\r")
            self.associate_and_insert('Book', 'Settings', 'settings_of_book', self.csvservice.dataframes["books"], 'title', 'description', "settings")
        except Exception as e:
            print(f"Erreur lors de la création de la table setting_of_book : {e}")

    def table_award_of_book(self):
        """
        Remplie table_award_of_book
        """
        try:
            print(f"Traitement pour peuplement de la table_award_of_book en cours ... ", end="\r")
            self.associate_and_insert('Book', 'Award', 'award_of_book', self.csvservice.dataframes["books"], 'title', 'name', "awards")
        except Exception as e:
            print(f"Erreur lors de la création de la table award_of_book : {e}")

    def table_serie_of_book(self):
        """
        Remplie table_serie_of_book
        """
        try:
            print(f"Traitement pour peuplement de la table_serie_of_book en cours ... ", end="\r")
            self.associate_and_insert_series('Book', 'Serie', 'serie_of_book', self.csvservice.dataframes["books"], 'title', 'name', "series")
        except Exception as e:
            print(f"Erreur lors de la création de la table serie_of_book : {e}")

    def table_genre_and_vote(self):
        """Remplie la table genre_and_vote"""
        try:
            print(f"Traitement pour peuplement de la table_genre_and_vote en cours ... ", end="\r")
            self.associate_and_insert_with_separator('Book', 'Genre', 'Genre_and_vote', self.csvservice.dataframes["books"], 'title', 'name', "genre_and_votes")
        except Exception as e:
            print(f"Erreur lors de la création de la table genre_and_vote : {e}")

    def table_wrote(self):
        """
        Remplie la table wrote
        """
        try:
            print(f"Traitement pour peuplement de la table_wrote en cours ... ", end="\r")
            self.associate_and_insert_wrote()
        except Exception as e:
            print(f"Erreur lors de la création de la table wrote : {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    peuplement1 = peuplement()
    
    try:
        print("Insertion des données dans les tables principales...")

        # Peupleument des tables
        peuplement1.table_genre()
        print("Table Genre remplie avec succès.")

        peuplement1.table_publisher()
        print("Table Publisher remplie avec succès.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


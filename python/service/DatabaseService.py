# -*- coding: utf-8 -*-
import psycopg2
import csv
import os
import pandas as pd
from .connection_bdd import host, port, user, password, database, connectdb
import requests
from fastapi import HTTPException

class DatabaseService:
    """
    Service pour gérer les interactions avec la base de données.
    """

    def __init__(self):
        self.connection = None
        self.cursor = None

    def initialize_connection(self):
        """
        Initialise la connexion et crée un curseur.
        """
        try:
            self.connection = connectdb()
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def close_connection(self):
        """
        Ferme la connexion et le curseur à la base de données.
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("Connexion à la base de données fermée.")
        except Exception as e:
            print(f"Erreur lors de la fermeture de la connexion : {e}")
            raise
    
    def get_escape_sql(self):

        # URL brute du fichier SQL sur GitHub
        url = "https://raw.githubusercontent.com/LeconteEsteban/Sae_3A/refs/heads/main/escape.sql"

        # Télécharger le fichier SQL
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open("create_table.sql", "w") as file:
                    file.write(response.text)

                print("Le script SQL a été téléchargé et enregistré localement.")
            else:
                print(f"Erreur lors du téléchargement : {response.status_code}")
        except Exception as e:
            print(f"Erreur lors de l'exécution : {e}")
        finally:
            print("Fin du téléchargement du script SQL.")

    def create_database(self):
        """
        Crée les tables dans la base de données à partir d'un script SQL.
        Si le fichier 'create_table.sql' n'existe pas, il est téléchargé.
        """
        try:
            # Vérifier si le fichier 'create_table.sql' existe
            if not os.path.exists("create_table.sql"):
                print("Le fichier 'create_table.sql' n'existe pas. Téléchargement du script SQL...")
                self.get_escape_sql()  # Télécharger le fichier SQL

            # Lire le contenu du fichier SQL
            with open("create_table.sql", "r") as file:
                sql_script = file.read()

            # Exécuter le script SQL
            self.cursor.execute(sql_script)
            self.connection.commit()
            print("Script SQL de création de la base de données exécuté avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution : {e}")
            raise
    
    def insert_sql(self, table, data):
        """
        insert dans table de data : une liste de dictionaire de donnée ex: [{name:x},{},{},{}]
        """
        try:
            print(f"Peuplement de {table} en cours ... ", end="\r")
            # Récupérer les noms de colonnes
            columns = data[0].keys()
            columns_str = ", ".join(columns)
            values_placeholders = ", ".join([f"%({col})s" for col in columns])

            # Créer et exécuter le script SQL
            sql_script = f"INSERT INTO library.{table} ({columns_str}) VALUES ({values_placeholders})"
            self.cursor.executemany(sql_script, data)
            self.connection.commit()
            print(f"Les données ont été insérées avec succès dans: {table}. {len(data)} rows.")
        except Exception as e:
            print(f"Peuplement de {table} échec")
            print(f"Erreur lors de l'insertion dans la table {table} : {e}")
            raise

    def insert_one_sql(self, table, data):
        """
        insert dans table de data : une liste de donnée ex: [l1,l2,l3,l4]
        """
        try:
            # Générer des placeholders pour les valeurs, par exemple : (%s, %s, %s)
            placeholders = ", ".join(["%s"] * len(data))

            # Créer la requête SQL pour insérer une ligne
            query = f"INSERT INTO {table} VALUES ({placeholders})"

            # Exécuter la requête
            self.cursor.execute(query, data)

            # Confirmer la transaction
            self.connection.commit()
            #print("Les données ont été insérées avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'insertion dans la table {table} : {e}")
            raise

    def insert_one_sql_with_id(self, table, data, id):
        """
        insert dans table de data : une liste de donnée ex: [l1,l2,l3,l4]
        """
        try:
             # Vérifier si l'ID existe déjà dans la table
            query_check = f"SELECT 1 FROM {table} WHERE id = %s"
            self.cursor.execute(query_check, (id,))
            result = self.cursor.fetchone()
            
            if result:
                # Si l'ID existe déjà, vous pouvez choisir de mettre à jour la ligne ou de l'ignorer
                print(f"ID {data[0]} exist", end="\r")
            else:
                # Générer des placeholders pour les valeurs, par exemple : (%s, %s, %s)
                placeholders = ", ".join(["%s"] * len(data))

                # Créer la requête SQL pour insérer une ligne
                query = f"INSERT INTO {table} VALUES ({placeholders})"

                # Exécuter la requête
                self.cursor.execute(query, data)

                # Confirmer la transaction
                self.connection.commit()
                #print("Les données ont été insérées avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'insertion dans la table {table} : {e}")
            raise

    def select_sql(self, query, params=None, as_dataframe=False):
        """
        Exécute une requête SELECT et retourne les résultats.

        Args:
            query (str): La requête SQL à exécuter.
            params (tuple, optional): Les paramètres pour la requête SQL.
            as_dataframe (bool, optional): Retourner un DataFrame si True, sinon une liste.

        Returns:
            list | pd.DataFrame: Résultats sous forme de liste de tuples ou de DataFrame.
        """
        try:
            self.cursor.execute(query, params or ())
            rows = self.cursor.fetchall()
            
            if as_dataframe:
                columns = [desc[0] for desc in self.cursor.description]
                return pd.DataFrame(rows, columns=columns)
            
            return rows  # Retourne une liste de tuples si as_dataframe=False
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de la requête : {e}")
            raise


    def execute_query(self, query, values):
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.fetchall()

    def execute_update(self, query, values):
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
            self.connection.commit()

    # def cmd_sql(self, query):
    #     """
    #     Exécute une commande SQL.
    #     - Pour les commandes `SELECT`, retourne les résultats.
    #     - Pour les autres commandes (`INSERT`, `UPDATE`, `DELETE`), effectue la commande sans attendre de résultat.
    #     """
    #     try:
    #         self.cursor.execute(query)
            
    #         # Vérifie si la requête est une commande `SELECT`
    #         if query.strip().lower().startswith("select"):
    #             results = self.cursor.fetchall()
    #             return results
            
    #         # Pour les autres requêtes (DELETE, INSERT, etc.)
    #         self.connection.commit()
    #         #print("Commande SQL exécutée avec succès.")
    #     except Exception as e:
    #         print(f"Erreur lors de l'exécution de la commande SQL : {e}")
    #         raise
    
    def cmd_sql(self, query, params=None):
        """
        Exécute une commande SQL avec un timeout.
        """
        try:
            if params:
                # Exécute la requête avec des paramètres
                self.cursor.execute(query, params)
            else:
                # Exécute la requête sans paramètres
                self.cursor.execute(query)
            
            # Vérifie si la requête est une commande `SELECT`
            if query.strip().lower().startswith("select"):
                results = self.cursor.fetchall()
                return results
            if query.strip().lower().startswith("with"):
                return self.cursor.fetchall()
            # Pour les autres requêtes (DELETE, INSERT, etc.)
            self.connection.commit()
            print("Commande SQL exécutée avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande SQL : {e}")
            raise
        
    def get_user_by_id(self, user_id: int):
        """
        Récupère les informations d'un utilisateur par son ID.
        """
        try:
            if not self.connection:  # Vérifie que la connexion est bien initialisée
                raise HTTPException(status_code=500, detail="Connexion à la base de données non établie.")

            cursor = self.connection.cursor()  
            cursor.execute("""
                SELECT user_id, name, age, child, familial_situation, gender, 
                    cat_socio_pro, lieu_habitation, frequency, book_size, birth_date 
                FROM library._Users WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()
            cursor.close() 

            if not user:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            return user
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None

    def get_all_user_ids(self):
        """
        Récupère la liste de tous les ID des utilisateurs.
        """
        try:
            if not self.connection:
                raise HTTPException(status_code=500, detail="Connexion à la base de données non établie.")

            with self.connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM library._Users")
                users = cursor.fetchall()  # Récupérer tous les utilisateurs sous forme de liste de tuples

            return [user[0] for user in users]  # Extraire uniquement les ID sous forme de liste
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs : {e}")
            return None




    def create_user(self, user: dict):
        """
        Crée un nouvel utilisateur dans la base de données.
        Si le nom d'utilisateur est déjà pris, renvoie une exception.
        """
        if not self.connection:
            raise HTTPException(status_code=500, detail="La connexion à la base de données n'est pas établie.")
        
        # Vérification si le nom d'utilisateur existe déjà
        check_query = """
        SELECT user_id
        FROM library._Users
        WHERE name = %s;
        """
        
        try:
            # Vérifier si l'utilisateur existe déjà
            self.cursor.execute(check_query, (user["username"],))
            existing_user = self.cursor.fetchone()
            
            if existing_user:
                # Si l'utilisateur existe déjà, lever une exception
                raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris.")
            
            # Si l'utilisateur n'existe pas, insérer le nouvel utilisateur
            insert_query = """
            INSERT INTO library._Users
            (name, age, passwords, child, familial_situation, gender, cat_socio_pro, lieu_habitation, frequency, book_size, birth_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id;
            """
            values = [
                user["username"],
                user["age"],
                user["password"],
                user["child"],
                user["familial_situation"],
                user["gender"],
                user["cat_socio_pro"],
                user["lieu_habitation"],
                user["frequency"],
                user["book_size"],
                user["birth_date"]
            ]
            
            # Exécution de la requête d'insertion
            self.cursor.execute(insert_query, values)
            self.connection.commit()
            
            # Récupérer l'ID du nouvel utilisateur
            result = self.cursor.fetchone()
            return result  # Retourner l'ID du nouvel utilisateur
        except HTTPException as http_exc:
            raise http_exc  
        except Exception as e:
            # Annuler la transaction en cas d'erreur
            self.connection.rollback()
            print(f"Erreur lors de la création de l'utilisateur : {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la création de l'utilisateur.")
        finally:
            # Optionnel: fermer le curseur si nécessaire
            pass

    def add_author(self, author: dict):
        """
        Crée un nouvel auteur dans la base de données.
        """
        if not self.connection:
            raise HTTPException(status_code=500, detail="La connexion à la base de données n'est pas établie.")
        
        # Vérifier si l'auteur existe déjà
        check_query = """
        SELECT author_id
        FROM library.author
        WHERE name = %s AND birthplace = %s;
        """
        try:
            self.cursor.execute(check_query, (author["name"], author["birthplace"]))
            existing_author = self.cursor.fetchone()
            
            if existing_author:
                raise HTTPException(status_code=400, detail="L'auteur existe déjà.")

            # Si l'auteur n'existe pas, insérer un nouvel auteur
            insert_query = """
            INSERT INTO library.author (name, birthplace)
            VALUES (%s, %s)
            RETURNING author_id;
            """
            values = [author["name"], author["birthplace"]]
            
            # Exécuter la requête d'insertion
            self.cursor.execute(insert_query, values)
            self.connection.commit()

            # Récupérer l'ID de l'auteur inséré
            result = self.cursor.fetchone()
            return result[0]  # Retourner l'ID de l'auteur créé

        except HTTPException as http_exc:
            raise http_exc  
        
        except Exception as e:
            # Annuler la transaction en cas d'erreur
            self.connection.rollback()
            print(f"Erreur lors de l'ajout de l'auteur : {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de l'ajout de l'auteur.")



    def authenticate_user(self, username: str, password: str):
        """
        Authentifie un utilisateur en vérifiant les informations de connexion.
        """
        if not self.connection:
            raise HTTPException(status_code=500, detail="La connexion à la base de données n'est pas établie.")
        
        query = """
        SELECT * FROM library._Users
        WHERE name = %s AND passwords = %s;
        """
        values = [username, password]
        
        try:
            # Exécution de la requête pour récupérer l'utilisateur
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result:
                return result  # Renvoie l'utilisateur si trouvé
            else:
                return None  # Sinon, renvoie None si pas d'utilisateur trouvé
        except Exception as e:
            print(f"Erreur lors de l'authentification de l'utilisateur : {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de l'authentification.")
        finally:
            # Optionnel, tu pourrais fermer le curseur ici, mais cela dépend de ta gestion des connexions.
            pass

    def add_book(self, book: dict):
        """
        Ajoute un livre dans la base de données, ainsi que ses relations avec les auteurs, genres, et prix.
        """
        if not self.connection:
            raise HTTPException(status_code=500, detail="La connexion à la base de données n'est pas établie.")
        
        try:
            print(f"Vérification de l'existence du livre : {book['title']}, {book['isbn']}")
            # Vérifier si le livre existe déjà
            check_query = """
            SELECT book_id FROM library.book WHERE title = %s AND isbn = %s;
            """
            self.cursor.execute(check_query, (book["title"], book["isbn"]))
            existing_book = self.cursor.fetchone()
            
            if existing_book:
                print(f"Le livre existe déjà : {book['title']}, {book['isbn']}")
                raise HTTPException(status_code=400, detail="Le livre existe déjà.")
            
            # Insérer le livre dans la table book
            print(f"Insérer le livre dans la base de données : {book['title']}, {book['isbn']}")
            insert_query = """
            INSERT INTO library.book (title, isbn, isbn13, description, number_of_pages, publisher_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING book_id;
            """
            values = [
                book["title"], 
                book["isbn"], 
                book["isbn13"], 
                book["description"], 
                book["number_of_pages"], 
                book["publisher_name"]
            ]
            
            self.cursor.execute(insert_query, values)
            self.connection.commit()
            
            # Récupérer l'ID du livre
            result = self.cursor.fetchone()
            book_id = result[0]  # ID du livre inséré
            print(f"Livre inséré avec succès, ID : {book_id}")

            # Ajouter les auteurs, genres et awards
            if book["author_name"]:
                print(f"Ajout des auteurs pour le livre ID : {book_id}")
                self.add_authors_to_book(book_id, book["author_name"])
            
            if book["genre_names"]:
                print(f"Ajout des genres pour le livre ID : {book_id}")
                self.add_genres_to_book(book_id, book["genre_names"])
            
            if book["award_names"]:
                print(f"Ajout des awards pour le livre ID : {book_id}")
                self.add_awards_to_book(book_id, book["award_names"])

            return book_id

        except HTTPException as http_exc:
            print(f"Erreur HTTP : {http_exc.detail}")
            raise http_exc  
        
        except Exception as e:
            self.connection.rollback()
            print(f"Erreur lors de l'ajout du livre : {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de l'ajout du livre.")

        
    def add_authors_to_book(self, book_id, author_names):
        """
        Ajoute les auteurs au livre dans la table `wrote`.
        """
        for author_name in author_names:
            author_query = """
            INSERT INTO library.wrote (book_id, author_id)
            SELECT %s, author_id FROM library.author WHERE name = %s
            """
            self.cursor.execute(author_query, (book_id, author_name))
            self.connection.commit()

    def add_genres_to_book(self, book_id, genre_names):
        """
        Ajoute les genres au livre dans la table `genre_and_vote`.
        """
        for genre_name in genre_names:
            genre_query = """
            INSERT INTO library.genre_and_vote (book_id, genre_id)
            SELECT %s, genre_id FROM library.genre WHERE name = %s
            """
            self.cursor.execute(genre_query, (book_id, genre_name))
            self.connection.commit()

    def add_awards_to_book(self, book_id, award_names):
        """
        Ajoute les awards au livre dans la table `Award_of_book`.
        """
        for award_name in award_names:
            award_query = """
            INSERT INTO library.Award_of_book (book_id, award_id)
            SELECT %s, award_id FROM library.award WHERE name = %s
            """
            self.cursor.execute(award_query, (book_id, award_name))
            self.connection.commit()
       
    def get_book_cover_url(self, book_id: int, isbn: str):
        try:
            if isbn is None or isbn.strip() == "":
                return "-1"

            # Vérifier si une couverture existe déjà
            cover_query = """
                SELECT cover_url
                FROM library.Book_Cover
                WHERE book_id = %s;
            """
            cover_res = self.execute_query(cover_query, (book_id,))
    
            if cover_res:  # Si une couverture existe déjà
                return cover_res[0][0]
    
            # Si aucune couverture n'existe, appeler l'API Google Books
            api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            response = requests.get(api_url)
            data = response.json()
    
            cover_url = "-1"  # Valeur par défaut si aucune couverture n'est trouvée
    
            if "items" in data and len(data["items"]) > 0:
                cover_url = data["items"][0]["volumeInfo"].get("imageLinks", {}).get("thumbnail", "-1")
    
            # Insérer ou mettre à jour l'URL de la couverture dans la base de données
            insert_query = """
                INSERT INTO library.Book_Cover (book_id, isbn13, cover_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (book_id) 
                DO UPDATE SET cover_url = %s;
            """
            self.execute_update(insert_query, (book_id, isbn, cover_url, cover_url))
    
            return cover_url
        except Exception as e:
            print(f"Erreur lors de la récupération ou de l'insertion de la couverture: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération ou de l'insertion de la couverture")
        
    def fill_book_cover_from_csv(self, csv_file_path: str = "books_with_cover.csv"):
        """
        Remplit la base de données avec les URLs des couvertures à partir d'un fichier CSV.
        
        Args:
            csv_file_path (str): Chemin du fichier CSV contenant les URLs des couvertures.
        """
        try:
            # Lire le fichier CSV avec pandas
            df = pd.read_csv(csv_file_path, dtype={'isbn13': str})  # Forcer isbn13 en type str
            
            # Parcourir chaque ligne du DataFrame
            for index, row in df.iterrows():
                isbn13 = row['isbn13']  # Récupérer l'ISBN13 du livre
                cover_link = row['cover_link']  # Récupérer l'URL de la couverture
                
                # Vérifier si isbn13 est nul (NaN ou chaîne vide)
                if pd.isna(isbn13) or isbn13.strip() == "":
                    #print(f"ISBN13 manquant ou invalide à la ligne {index + 1}. Ignorer cette ligne.")
                    continue  # Passer à la ligne suivante
                
                # Récupérer le book_id correspondant à l'isbn13
                book_id_query = """
                    SELECT book_id
                    FROM library.Book
                    WHERE isbn13 = %s;
                """
                book_id_res = self.execute_query(book_id_query, (isbn13,))

                if not book_id_res:
                    #print(f"Aucun livre trouvé avec l'ISBN13 {isbn13}.")
                    continue  # Passer à la ligne suivante

                book_id = book_id_res[0][0]  # Récupérer le book_id

                # Vérifier si une couverture existe déjà dans la base de données
                cover_query = """
                    SELECT cover_url
                    FROM library.Book_Cover
                    WHERE book_id = %s;
                """
                cover_res = self.execute_query(cover_query, (book_id,))

                # Si une couverture existe et qu'elle n'est pas égale à "-1", passer à la ligne suivante
                if cover_res and cover_res[0][0] and cover_res[0][0] != "-1":
                    print(f"Couverture déjà existante pour le livre {book_id} avec ISBN13 {isbn13}.")
                    continue

                # Vérifier si cover_link est NaN
                if pd.isna(cover_link) or cover_link.strip() == "":
                    cover_url = "-1"  # Si cover_link est NaN ou vide, utiliser "-1"
                else:
                    cover_url = cover_link  # Sinon, utiliser l'URL du CSV

                # Insérer ou mettre à jour l'URL de la couverture dans la base de données
                insert_query = """
                    INSERT INTO library.Book_Cover (book_id, isbn13, cover_url)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (book_id) 
                    DO UPDATE SET cover_url = %s;
                """
                self.execute_update(insert_query, (book_id, isbn13, cover_url, cover_url))

                #print(f"Couverture mise à jour pour le livre avec ISBN13 {isbn13} : {cover_url}")
        
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la base de données à partir du fichier CSV : {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    db_service = DatabaseService()

    try:
        # Initialiser la connexion
        db_service.initialize_connection()
        
        # Créer la base de données
        db_service.get_escape_sql()
        db_service.create_database()

        # Insérer des données
        table_name = "Award"
        user_data = [{"name": "Alice"}, {"name": "Bob"}]
        db_service.insert_sql(table_name, user_data)

        # Récupérer les données
        award = db_service.select_sql(table_name)
        print(award)

        # Exécuter une commande personnalisée
        cmd = "SELECT name FROM library.Award;"
        result = db_service.cmd_sql(cmd)
        print(result)

    finally:
        # Fermer la connexion
        db_service.close_connection()

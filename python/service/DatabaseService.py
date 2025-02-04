# -*- coding: utf-8 -*-
import psycopg2
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

    def select_sql(self, table):
        """
        Récupère les données d'une table et les retourne sous forme de DataFrame.
        """
        try:
            # Exécuter la requête SQL
            self.cursor.execute(f"SELECT * FROM library.{table}")
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]

            # Convertir en DataFrame
            df = pd.DataFrame(rows, columns=columns)
            #print(f"Données récupérées depuis la table {table}.")
            return df
        except Exception as e:
            print(f"Erreur lors de la récupération des données de la table {table} : {e}")
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
        Exécute une commande SQL.
        - Pour les commandes `SELECT`, retourne les résultats.
        - Pour les autres commandes (`INSERT`, `UPDATE`, `DELETE`), effectue la commande sans attendre de résultat.
        - `params` : Un tuple ou une liste de paramètres pour les requêtes paramétrées.
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
            
            # Pour les autres requêtes (DELETE, INSERT, etc.)
            self.connection.commit()
            #print("Commande SQL exécutée avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande SQL : {e}")
            raise

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

    def get_book_cover_url(self, book_id: int, isbn: str):
        try:
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

import psycopg2
import os
import pandas as pd
from .connection_bdd import host, port, user, password, database, connectdb
import requests

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
            print("Les données ont été insérées avec succès.")
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

    def cmd_sql(self, query):
        """
        Exécute une commande SQL.
        - Pour les commandes `SELECT`, retourne les résultats.
        - Pour les autres commandes (`INSERT`, `UPDATE`, `DELETE`), effectue la commande sans attendre de résultat.
        """
        try:
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

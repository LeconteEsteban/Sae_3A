import psycopg2
import pandas as pd
from connection_bdd import host, port, user, password, database, connectdb
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
        self.connection = connectdb()
        self.cursor = self.connection.cursor()

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
    
    def get_escape_sql():
        #import de github
        # URL brute du fichier SQL sur GitHub
        url = "https://raw.githubusercontent.com/LeconteEsteban/Sae_3A/refs/heads/main/escape.sql"

        # Télécharger le fichier SQL
        try:
            response = requests.get(url)
            with open("create_table.sql", "w") as file:
                file.write(response.text)

            print("Le script SQL a été téléchargé et enregistré localement.")
        except Exception as e:
            print(f"Erreur lors de l'exécution : {e}")

        finally:
            print("fin")

    def create_database(self):
        """
        Crée les tables dans la base de données à partir d'un script SQL.
        """
        try:
            # Lire le contenu du fichier SQL
            with open("create_table.sql", "r") as file:
                sql_script = file.read()

            # Exécuter le script SQL
            self.cursor.execute(sql_script)
            self.connection.commit()
            print("Script SQL exécuté avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution : {e}")
            raise

    def insert_sql(self, table, data):
        """
        Insère des données dans une table spécifique.
        """
        try:
            # Récupérer les noms de colonnes
            columns = data[0].keys()
            columns_str = ", ".join(columns)
            values_placeholders = ", ".join([f"%({col})s" for col in columns])

            # Créer et exécuter le script SQL
            sql_script = f"INSERT INTO library.{table} ({columns_str}) VALUES ({values_placeholders})"
            self.cursor.executemany(sql_script, data)
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
            print(f"Données récupérées depuis la table {table}.")
            return df
        except Exception as e:
            print(f"Erreur lors de la récupération des données de la table {table} : {e}")
            raise

    def cmd_sql(self, cmd):
        """
        Exécute une commande SQL personnalisée et retourne les résultats sous forme de DataFrame.
        """
        try:
            self.cursor.execute(cmd)
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]

            # Convertir en DataFrame
            df = pd.DataFrame(rows, columns=columns)
            print("Commande SQL exécutée avec succès.")
            return df
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
        user_data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        db_service.insert_sql(table_name, user_data)

        # Récupérer les données
        users = db_service.select_sql(table_name)
        print(users)

        # Exécuter une commande personnalisée
        cmd = "SELECT name FROM library.users WHERE age > 20;"
        result = db_service.cmd_sql(cmd)
        print(result)

    finally:
        # Fermer la connexion
        db_service.close_connection()

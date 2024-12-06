import psycopg2
from psycopg2 import sql

# Paramètres de connexion à la base de données
host = "localhost"         # Adresse du serveur
port = 5432               # Port de la base de données
user = "melvin" # Nom d'utilisateur
password = "mdp" # Mot de passe
database = "postgres" # Nom de la base de données

def connectdb():
    """
    Établit une connexion à la base de données PostgreSQL.
    
    Returns:
        connection (psycopg2.connection): Connexion active à la base de données.
    Raises:
        Exception: Si une erreur survient lors de la connexion.
    """
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print("Connexion à la base de données réussie.")
        return connection
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        print("Assurez vous de la validité des informations de connexion à la bdd dans service.connection_bdd.py")
        raise

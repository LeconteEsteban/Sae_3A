import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()
# Paramètres de connexion à la base de données postgresql basique
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

# Paramètres de connexion à la base de données kerboros
host_ker = "" # Adresse du serveur
port_ker = "" # Port de la base de données
database_ker = "" # Nom de la base de données
# Pas besoin d'utilisateur n'y de mdp, modalité à voir dans info_connection_bdd.txt


def connectdb():
    """
    Tente une connexion à la base de données PostgreSQL en mode classique
    puis en mode Kerberos si la première échoue.
    
    Returns:
        connection (psycopg2.connection): Connexion active à la base de données.
    """
    try:
        print("Tentative de connexion classique...")
        connection = connect_postgress()
        print(f"Connexion classique réussie à : {host}")
        return connection
    except Exception as e1:
        print("Échec de la connexion classique. Tentative avec Kerberos...")
        try:
            connection = connect_kerberos()
            return connection
        except Exception as e2:
            print(f"Impossible de se connecter à la base de données : {e1} /////// {e2}")
            raise

def connect_postgress():
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        raise

def connect_kerberos():
    """
    Tente une connexion à PostgreSQL en utilisant l'authentification Kerberos (GSSAPI).
    
    Returns:
        connection (psycopg2.connection): Connexion active à la base de données.
    Raises:
        Exception: Si une erreur survient lors de la connexion.
    """
    try:
        connection = psycopg2.connect(
            host=host_ker,
            port=port_ker,
            database=database_ker,
            options="-c gssencmode=prefer",  # Permet d'utiliser GSSAPI si disponible
        )
        print("Connexion Kerberos réussie.")
        return connection
    except Exception as e:
        print(f"Erreur lors de la connexion Kerberos : {e}")
        raise


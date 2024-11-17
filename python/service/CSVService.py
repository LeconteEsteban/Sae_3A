import os
import requests
import pandas as pd
from io import StringIO
from .CacheService import *


class CSVService:
    """
    Service pour télécharger et gérer des fichiers CSV à partir d'URLs.

    Fonction utile : get_csv_book, get_csv_author, get_csv_questionary
    """

    def __init__(self):
        self.dataframes = {}
        self.cache_service = CacheService()

    def get_csv(self, url, key, usecols=None, max_columns=None, force_download=False):
        """
        Récupère un CSV depuis un cache ou le télécharge.

        Args:
            key (str): Clé unique pour identifier le cache.
            url (str): URL du fichier CSV.
            max_columns (int, optional): Limite le nombre de colonnes du DataFrame.
            force_download (bool): Forcer le téléchargement.

        Returns:
            pd.DataFrame: DataFrame contenant les données du CSV.
        """
        try:
            if self.cache_service.exists(key) and not force_download:
                self.dataframes[key] = self.cache_service.get_csv_cache(key)
                print(f"csv '{key}' récuperé du cache.")
                return self.dataframes[key]
                
            else:
                df = self.download_csv(url, key, usecols=usecols, max_columns=max_columns)
                self.cache_service.csv_to_cache(key,df)
                self.dataframes[key] = df
                #print(f"CSV téléchargé et chargé avec succès pour '{key}'.")
                return df
            
        except Exception as e:
            print(f"Erreur du get_csv : {e}")
            raise

    def download_csv(self, url, key, usecols=None, max_columns=None):
        """
        Télécharge un fichier CSV à partir d'une URL.

        Args:
            url (str): URL du fichier CSV.
            key (str): Clé pour identifier le DataFrame (ex: 'books', 'authors').
            usecols (list[int] or range, optional): Colonnes à lire. Si None, toutes les colonnes sont lues.
            max_columns (int, optional): Limite au nombre de colonnes à importer, si applicable.

        Returns:
            pd.DataFrame: Le DataFrame chargé, ou None si le téléchargement échoue.
        """
        try:
            print("Downloading of", key,".csv")
            # Télécharger le fichier CSV depuis l'URL
            response = requests.get(url)
            if response.status_code == 200:
                # Traiter le contenu CSV
                csv_data = StringIO(response.content.decode('utf-8'))

                # Lire le CSV dans un DataFrame avec les options fournies
                df = pd.read_csv(csv_data, low_memory=False, usecols=usecols)

                # Restreindre le nombre de colonnes si max_columns est défini
                if max_columns is not None:
                    df = df[df.columns[:max_columns]]
                return df
            else:
                print(f"Erreur lors du téléchargement de '{key}' : {response.status_code}")
                return None
        except Exception as e:
            print(f"Erreur lors du traitement de l'URL '{url}' : {e}")
            return None

    def get_dataframe(self, key):
        """
        Récupère un DataFrame chargé par sa clé.

        Args:
            key (str): Clé identifiant le DataFrame.

        Returns:
            pd.DataFrame: Le DataFrame correspondant, ou None si absent.
        """
        return self.dataframes.get(key, None)


    def get_csv_book(self):
        """
        Get le csv et retourne le DataFrame des livres.

        Returns:
            pd.DataFrame: DataFrame des livres.
        """
        try:
            books_url = "https://docs.google.com/spreadsheets/d/1cWkVcuw_wTQxqTgJcRfCZTweSb06tzfHVbuAd73owNw/export?format=csv&gid=1613894920"
            df = self.dataframes.get("books")
            if df is not None:
                return df
            else:
                return self.get_csv(books_url, key="books", max_columns=25)
        
        except Exception as e:
                print(f"Erreur get_csv_book : {e}")
                raise


    def get_csv_author(self):
        """
        Télécharge ou retourne le DataFrame des auteurs.

        Returns:
            pd.DataFrame: DataFrame des auteurs.
        """
        try:
            authors_url = "https://docs.google.com/spreadsheets/d/1cWkVcuw_wTQxqTgJcRfCZTweSb06tzfHVbuAd73owNw/export?format=csv&gid=818727220"
            df = self.dataframes.get("authors")
            if df is not None:
                return df
            else:
                return self.get_csv(authors_url, key="authors", usecols=range(18))
        except Exception as e:
                print(f"Erreur get_csv_author : {e}")
                raise



    def get_csv_questionary(self):
        """
        Télécharge ou retourne le DataFrame du questionnaire.

        Returns:
            pd.DataFrame: DataFrame du questionnaire.
        """
        questionary_url = "https://docs.google.com/spreadsheets/d/1dqgFu3AlBIqRN6ZS95s2WKxgi5oCoqF9XRZ_M1XSueY/export?format=csv"
        try:
            df = self.dataframes.get("questionary")
            if df is not None:
                return df
            else:
                return self.get_csv(questionary_url, key="questionary", usecols=range(17))
        except Exception as e:
                print(f"Erreur get_csv_questionary : {e}")
                raise


    def list_dataframes(self):
        """
        Liste toutes les clés des DataFrames chargés.

        Returns:
            list[str]: Liste des clés disponibles.
        """
        return list(self.dataframes.keys())

    

# Exemple d'utilisation
if __name__ == "__main__":
    csv_service = CSVService()

    # Récupérer les fichiers CSV avec les fonctions simplifiées
    books_df = csv_service.get_csv_book()
    authors_df = csv_service.get_csv_author()
    questionary_df = csv_service.get_csv_questionary()

    # Afficher les DataFrames importés
    if books_df is not None:
        print("Books DataFrame :")
        print(books_df.head())
    
    if authors_df is not None:
        print("Authors DataFrame :")
        print(authors_df.head())
    
    if questionary_df is not None:
        print("Questionary DataFrame :")
        print(questionary_df.head())

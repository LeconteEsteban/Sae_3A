import requests
import pandas as pd
from io import StringIO

class CSVService:
    """
    Service pour télécharger et gérer des fichiers CSV à partir d'URLs.
    """

    def __init__(self):
        self.dataframes = {}

    def download_csv(self, url, key, usecols=None, max_columns=None):
        """
        Télécharge un fichier CSV à partir d'une URL et le charge dans un DataFrame.

        Args:
            url (str): URL du fichier CSV.
            key (str): Clé pour identifier le DataFrame (ex: 'books', 'authors').
            usecols (list[int] or range, optional): Colonnes à lire. Si None, toutes les colonnes sont lues.
            max_columns (int, optional): Limite au nombre de colonnes à importer, si applicable.

        Returns:
            pd.DataFrame: Le DataFrame chargé, ou None si le téléchargement échoue.
        """
        try:
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

                # Sauvegarder dans le dictionnaire
                self.dataframes[key] = df
                print(f"CSV téléchargé et chargé avec succès pour '{key}'.")
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
        Télécharge ou retourne le DataFrame des livres.

        Returns:
            pd.DataFrame: DataFrame des livres.
        """
        books_url = "https://docs.google.com/spreadsheets/d/1cWkVcuw_wTQxqTgJcRfCZTweSb06tzfHVbuAd73owNw/export?format=csv&gid=1613894920"
        return self.dataframes.get("books") or self.download_csv(books_url, key="books", max_columns=25)

    def get_csv_author(self):
        """
        Télécharge ou retourne le DataFrame des auteurs.

        Returns:
            pd.DataFrame: DataFrame des auteurs.
        """
        authors_url = "https://docs.google.com/spreadsheets/d/1cWkVcuw_wTQxqTgJcRfCZTweSb06tzfHVbuAd73owNw/export?format=csv&gid=818727220"
        return self.dataframes.get("authors") or self.download_csv(authors_url, key="authors", usecols=range(18))

    def get_csv_questionary(self):
        """
        Télécharge ou retourne le DataFrame du questionnaire.

        Returns:
            pd.DataFrame: DataFrame du questionnaire.
        """
        questionary_url = "https://docs.google.com/spreadsheets/d/1dqgFu3AlBIqRN6ZS95s2WKxgi5oCoqF9XRZ_M1XSueY/export?format=csv"
        return self.dataframes.get("questionary") or self.download_csv(questionary_url, key="questionary", usecols=range(17))

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

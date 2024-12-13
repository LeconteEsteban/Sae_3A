import os
import pandas as pd
import json

class CacheService:
    def __init__(self, cache_dir="cache"):
        """
        Initialise le gestionnaire de cache.

        Args:
            cache_dir (str): Répertoire de stockage des fichiers cache.
        """
        self.cache_dir = cache_dir
        try:
            os.makedirs(cache_dir, exist_ok=True)  # Crée le répertoire s'il n'existe pas
        except Exception as e:
            print(f"Problème lors de la création du dossier cache: {e}")

    def get_cache_path(self, key):
        """
        Génère le chemin complet pour un fichier cache basé sur une clé unique.

        Args:
            key (str): Clé unique pour identifier le fichier cache.

        Returns:
            str: Chemin du fichier cache.
        """
        return os.path.join(self.cache_dir, f"{key}.cache")

    def exists(self, key):
        """
        Vérifie si un cache existe pour une clé donnée.

        Args:
            key (str): Clé unique pour identifier le fichier cache.

        Returns:
            bool: True si le cache existe, False sinon.
        """
        return os.path.exists(self.get_cache_path(key))

    def get_cache_path_json(self, key):
        """
        Génère le chemin complet pour un fichier json cache basé sur une clé unique.

        Args:
            key (str): Clé unique pour identifier le fichier json cache.

        Returns:
            str: Chemin du fichier json cache.
        """
        return os.path.join(self.cache_dir, f"{key}.json")

    def exists_json(self, key):
        """
        Vérifie si un json cache existe pour une clé donnée.

        Args:
            key (str): Clé unique pour identifier le fichier json cache.

        Returns:
            bool: True si le json cache existe, False sinon.
        """
        return os.path.exists(self.get_cache_path_json(key))
    
    def csv_to_cache(self, key, csv, cache_dir="cache"):
        """
        Enregistre un DataFrame ou du contenu CSV brut dans le cache.

        Args:
            key (str): Clé unique pour identifier le fichier cache.
            csv (str | pd.DataFrame): Contenu CSV (chaine brute) ou DataFrame à enregistrer.
            cache_dir (str): Répertoire de stockage des fichiers cache (par défaut : 'cache').

        Returns:
            str: Chemin complet du fichier cache créé.
        """
        cache_path = None  # Initialisation pour éviter des problèmes de portée
        try:
            # Convertir le chemin en absolu
            cache_path = os.path.join(cache_dir, f"{key}.cache")
            #os.makedirs(cache_dir, exist_ok=True)  # Crée le répertoire de cache s'il n'existe pas

            if isinstance(csv, pd.DataFrame):
                # Enregistrer le DataFrame dans un fichier CSV
                csv.to_csv(cache_path, index=False)
            elif isinstance(csv, str):
                # Enregistrer une chaîne brute dans un fichier CSV
                with open(cache_path, "w", encoding="utf-8") as file:
                    file.write(csv)
            else:
                raise ValueError("Le paramètre 'csv' doit être un DataFrame ou une chaîne brute CSV.")

            print(f"Le fichier cache a été créé : {cache_path}")
            return cache_path
        except PermissionError as e:
            raise Exception(f"Erreur de permission pour créer ou écrire dans le répertoire : {cache_dir}. Détails : {e}")
        except Exception as e:
            raise Exception(f"Erreur lors de l'enregistrement dans le cache '{cache_path}' : {e if cache_path else 'Cache path non défini'}")

    def get_csv_cache(self, key, cache_dir="cache"):
        """
        Retourne un DataFrame à partir du fichier CSV en cache pour une clé donnée.

        Args:
            key (str): Clé unique pour identifier le fichier cache.
            cache_dir (str): Répertoire de stockage des fichiers cache (par défaut : 'cache').

        Returns:
            pd.DataFrame: DataFrame des données si le cache existe.

        Raises:
            FileNotFoundError: Si le fichier cache n'existe pas.
            Exception: Si une erreur survient lors de la lecture du fichier.
        """
        os.makedirs(cache_dir, exist_ok=True)  # Crée le répertoire de cache s'il n'existe pas
        cache_path = os.path.join(cache_dir, f"{key}.cache")
        
        if not os.path.exists(cache_path):
            raise FileNotFoundError(f"Le fichier cache pour la clé '{key}' est introuvable : {cache_path}")
        
        try:
            return pd.read_csv(cache_path)
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du fichier cache '{cache_path}' : {e}")

    def dict_to_cache(self, key, data_dict, cache_dir="cache"):
        cache_path = os.path.join(cache_dir, f"{key}.json")
        try:
            os.makedirs(cache_dir, exist_ok=True)
            # Conversion des Tensors en listes
            serializable_dict = {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in data_dict.items()}
            with open(cache_path, "w", encoding="utf-8") as file:
                json.dump(serializable_dict, file, ensure_ascii=False, indent=4)
            print(f"Le fichier cache a été créé : {cache_path}")
            return cache_path
        except PermissionError as e:
            raise Exception(f"Erreur de permission pour créer ou écrire dans le répertoire : {cache_dir}. Détails : {e}")
        except Exception as e:
            raise Exception(f"Erreur lors de l'enregistrement du dictionnaire dans le cache '{cache_path}' : {e}")


    def get_dict_cache(self, key, cache_dir="cache"):
        cache_path = os.path.join(cache_dir, f"{key}.json")
        if not os.path.exists(cache_path):
            raise FileNotFoundError(f"Le fichier cache pour la clé '{key}' est introuvable : {cache_path}")
        try:
            with open(cache_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération du dictionnaire depuis le cache '{cache_path}' : {e}")

    def invalidate(self, key):
        """
        Supprime un cache spécifique.

        Args:
            key (str): Clé unique pour identifier le fichier cache.
        """
        cache_path = self.get_cache_path(key)
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"Cache supprimé : {cache_path}")

    def clear(self):
        """
        Supprime tous les fichiers dans le répertoire de cache.
        """
        for file in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, file)
            os.remove(file_path)
        print(f"Tous les caches ont été supprimés dans le répertoire {self.cache_dir}.")


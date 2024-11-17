import os
import shutil

from python.service.CacheService import *

def supprimer_caches():
    """
    fonction qui supprime tout les caches
    """
    #Supprime les caches du service
    cache = CacheService()
    cache.clear()

    #Supprime les caches __pycache__
    # Parcourir récursivement le répertoire courant
    for root, dirs, files in os.walk('.'):
        # Vérifier et supprimer '__pycache__'
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"Deleted: {pycache_path}")
            except Exception as e:
                print(f"Failed to delete {pycache_path}: {e}")
        if 'create_table.sql' in files:  # Vérifiez les fichiers, pas les répertoires
            ct = os.path.join(root, 'create_table.sql')
            try:
                os.remove(ct)  # Supprimer le fichier
                print(f"Deleted: {ct}")
            except Exception as e:
                print(f"Failed to delete {ct}: {e}")


if __name__ == "__main__":
    supprimer_caches()
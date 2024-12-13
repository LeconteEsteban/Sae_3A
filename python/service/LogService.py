import os
from datetime import datetime

class LogService:
    """
    Service pour gérer les logs.

    Les logs sont stockés dans le dossier log/
    """

    def __init__(self):
        self.log_dir = "log"
        os.makedirs(self.log_dir, exist_ok=True)
        print("Service log initialized")

    def exists(self, key):
        """
        Vérifie si le fichier key existe dans le dossier log/
        """
        return os.path.isfile(os.path.join(self.log_dir, key))

    def createLog(self, key, log):
        """
        Crée un nouveau fichier log avec key comme nom dans log/ et y insère le log
        """
        with open(os.path.join(self.log_dir, key), "w") as file:
            file.write(log + "\n")
        print(f"Log créé : {key}")

    def newLog(self, key, log):
        """
        Si le fichier key n'existe pas, il le crée, sinon, il l'ouvre et insère à la suite le nouveau log
        """
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_entry = f"{timestamp} {log}"
        file_path = os.path.join(self.log_dir, key)
        mode = "a" if self.exists(key) else "w"
        with open(file_path, mode) as file:
            file.write(log_entry + "\n")
        print(f"Log mis à jour : {key}")

    def deleteLog(self, key):
        """
        Supprime le fichier log avec key comme nom dans log/
        """
        file_path = os.path.join(self.log_dir, key)
        if self.exists(key):
            os.remove(file_path)
            print(f"Log supprimé : {key}")
        else:
            print(f"Log non trouvé : {key}")


# Exemple d'utilisation
if __name__ == "__main__":
    service = LogService()
    service.deleteLog("log1.txt")
    service.newLog("log1.txt", "coucou j'adore les phrases. je décoche avec mon arc")
    service.newLog("log1.txt", "Bonjour j'aime les mots. Je tire des flèches")
    service.newLog("log2.txt", "Bonjour j'aime les mots. Je tire des flèches")

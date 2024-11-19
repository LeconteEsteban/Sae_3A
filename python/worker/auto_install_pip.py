import subprocess
import sys
import os

def install_pip_if_missing():
    """Installe pip si ce n'est pas déjà disponible."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
        print("Pip est déjà installé.")
    except Exception:
        print("Pip n'est pas installé. Téléchargement de get-pip.py pour l'installation.")
        try:
            import urllib.request
            urllib.request.urlretrieve(
                "https://bootstrap.pypa.io/get-pip.py", "get-pip.py"
            )
            subprocess.check_call([sys.executable, "get-pip.py"])
            print("Pip a été installé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'installation de pip : {e}")
            sys.exit(1)

def install_requirements():
    """Installe les dépendances à partir du fichier requirements.txt ligne par ligne."""
    # Obtenez le chemin absolu du fichier requirements.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_dir, 'requirements.txt')

    if not os.path.exists(requirements_path):
        print(f"Erreur : Le fichier requirements.txt est introuvable au chemin {requirements_path}")
        return  # Continue le script même si le fichier est manquant.

    print("Début de l'installation des dépendances...")
    # Essayez de lire avec l'encodage UTF-8, sinon tombez sur UTF-16.
    try:
        with open(requirements_path, 'r', encoding='utf-8') as req_file:
            lines = req_file.readlines()
    except UnicodeDecodeError:
        print("Encodage en UTF-8 échoué. Essai avec UTF-16...")
        with open(requirements_path, 'r', encoding='utf-16') as req_file:
            lines = req_file.readlines()

    for line in lines:
        dependency = line.strip()
        if not dependency or dependency.startswith('#'):
            continue

        try:
            print(f"Installation de la dépendance : {dependency}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dependency])
            print(f"Succès : {dependency} a été installé.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur : Impossible d'installer {dependency}. Détails : {e}")
            # Ne pas lever d'exception pour permettre de continuer avec les autres dépendances

    print("Installation des dépendances terminée (avec ou sans erreurs).")



if __name__ == "__main__":
    # Étape 1 : Vérifiez que pip est installé, sinon installez-le.
    install_pip_if_missing()
    # Étape 2 : Installez les dépendances à partir du fichier requirements.txt.
    install_requirements()

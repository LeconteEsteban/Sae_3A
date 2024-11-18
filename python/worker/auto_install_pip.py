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

import os

def install_requirements():
    """Installe les dépendances à partir du fichier requirements.txt."""
    # Obtenez le chemin absolu du fichier requirements.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_dir, 'requirements.txt')

    if not os.path.exists(requirements_path):
        print(f"Erreur : Le fichier requirements.txt est introuvable au chemin {requirements_path}")
        sys.exit(1)

    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
        print("Toutes les dépendances ont été installées avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'installation des dépendances : {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Étape 1 : Vérifiez que pip est installé, sinon installez-le.
    install_pip_if_missing()
    # Étape 2 : Installez les dépendances à partir du fichier requirements.txt.
    install_requirements()

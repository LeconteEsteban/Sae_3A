import re
import unicodedata

class ParsingService:
    def __init__(self):
        """
        Initialise le service de parsing.
        """
        print("Service de parsing initialisé.")

    def split_string(self, text, delimiter=" "):
        """
        Divise une chaîne de caractères en une liste en fonction d'un délimiteur.

        Args:
            text (str): La chaîne de caractères à diviser.
            delimiter (str): Le délimiteur utilisé pour le découpage (par défaut : espace).

        Returns:
            list: Une liste contenant les segments de la chaîne.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        if not isinstance(delimiter, str) or not delimiter:
            raise ValueError("'delimiter' doit être une chaîne non vide.")
        return text.split(delimiter)

    def replace_characters(self, text, old, new):
        """
        Remplace un ou plusieurs caractères ou sous-chaînes dans une chaîne.

        Args:
            text (str): La chaîne de caractères à modifier.
            old (str): Le ou les caractères/sous-chaînes à remplacer.
            new (str): Le ou les caractères/sous-chaînes de remplacement.

        Returns:
            str: La chaîne modifiée.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        if not isinstance(old, str) or not isinstance(new, str):
            raise ValueError("'old' et 'new' doivent être des chaînes de caractères.")
        return text.replace(old, new)

    def clean_string(self, text):
        """
        Nettoie une chaîne en supprimant les espaces inutiles et en la normalisant.

        Args:
            text (str): La chaîne à nettoyer.

        Returns:
            str: La chaîne nettoyée.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        return " ".join(text.split())

    def replace_with_regex(self, text, pattern, replacement):
        """
        Remplace les occurrences d'un motif regex dans une chaîne.

        Args:
            text (str): La chaîne cible.
            pattern (str): L'expression régulière à rechercher.
            replacement (str): La chaîne de remplacement.

        Returns:
            str: La chaîne modifiée.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        if not isinstance(pattern, str) or not isinstance(replacement, str):
            raise ValueError("'pattern' et 'replacement' doivent être des chaînes.")
        return re.sub(pattern, replacement, text)

    def split_with_regex(self, text, pattern):
        """
        Divise une chaîne en utilisant un motif regex comme séparateur.

        Args:
            text (str): La chaîne à diviser.
            pattern (str): Le motif regex pour la division.

        Returns:
            list: La liste des segments.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        if not isinstance(pattern, str):
            raise ValueError("'pattern' doit être une chaîne représentant une regex.")
        return re.split(pattern, text)

    def count_occurrences(self, text, substring):
        """
        Compte les occurrences d'un sous-texte dans une chaîne.

        Args:
            text (str): La chaîne cible.
            substring (str): Le sous-texte à compter.

        Returns:
            int: Le nombre d'occurrences.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        if not isinstance(substring, str):
            raise ValueError("Le paramètre 'substring' doit être une chaîne.")
        return text.count(substring)

    def normalize_unicode(self, text):
        """
        Normalise une chaîne en Unicode (supprime les accents, etc.).

        Args:
            text (str): La chaîne cible.

        Returns:
            str: La chaîne normalisée.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

    def reverse_string(self, text):
        """
        Inverse une chaîne de caractères.

        Args:
            text (str): La chaîne à inverser.

        Returns:
            str: La chaîne inversée.
        """
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        return text[::-1]

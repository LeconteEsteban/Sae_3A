#à revoir
import pandas as pd
import re
import ftfy

Fonction pour détecter des caractères non-ASCII
def contains_non_ascii(text):
    return bool(re.search(r'[^\x00-\x7F]', str(text)))

Fonction pour ré-encoder les titres en UTF-8
def reencode_to_utf8(text):
    try:
        # Essayer de décoder en UTF-8 directement
        return text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        try:
            # Essayer de décoder en UTF-8 après avoir encodé en latin1
            return text.encode('utf-8').decode('latin1')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text

Fonction pour corriger les erreurs d'encodage avec ftfy
def fix_encoding(text):
    return ftfy.fix_text(text)

Lire le fichier CSV
df = pd.read_csv('../default_data/bigboss_book.csv')

Colonnes à traiter
columns_to_fix = ['title', 'publisher', 'series', 'author', 'original_title', 'genre_and_votes', 'settings', 'characters', 'awards', 'description']

Appliquer les fonctions sur les colonnes spécifiées
for column in columns_to_fix:
    df_with_non_ascii = df[df[column].apply(contains_non_ascii)]
    df_with_non_ascii[column] = df_with_non_ascii[column].apply(reencode_to_utf8)
    df_with_non_ascii[column] = df_with_non_ascii[column].apply(fix_encoding)
    df.update(df_with_non_ascii)

Sauvegarder le fichier CSV corrigé
df.to_csv('../new_data/books_corrected.csv', index=False)

Afficher les lignes contenant des caractères non-ASCII pour chaque colonne
for column in columns_to_fix:
    print(f"Non-ASCII characters in column '{column}':")
    print(df[df[column].apply(contains_non_ascii)][column])
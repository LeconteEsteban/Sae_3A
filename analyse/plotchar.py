#Leconte Esteban
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
import requests
from io import StringIO

#Import For the author sheet
url = 'https://docs.google.com/spreadsheets/d/1cWkVcuw_wTQxqTgJcRfCZTweSb06tzfHVbuAd73owNw/export?format=csv&gid=818727220'
response = requests.get(url)
if response.status_code == 200:
     # Convert the content to a string and use StringIO to handle it as a file-like object
    csv_data = StringIO(response.content.decode('utf-8'))

    # Read the CSV into a DataFrame with low_memory=False to avoid mixed dtype warnings and range for the number of columns to import
    df_author = pd.read_csv(csv_data, low_memory=False, usecols=range(18))

else:
    print(f"ERROR WHILE DOWNLOADING THE FILE: {response.status_code}")


# Remplacer les virgules par des points et convertir en valeurs numériques
df_author['author_average_rating'] = pd.to_numeric(df_author['author_average_rating'].str.replace(',', '.'), errors='coerce')
df_author['book_average_rating'] = pd.to_numeric(df_author['book_average_rating'].str.replace(',', '.'), errors='coerce')

# Vérifier qu'il ne reste pas de valeurs non converties
print(df_author[pd.to_numeric(df_author['author_average_rating'], errors='coerce').isna()])
print(df_author[pd.to_numeric(df_author['book_average_rating'], errors='coerce').isna()])

# Calcul de la moyenne et de l'écart type après conversion
df_mean = df_author.groupby('author_average_rating')['book_average_rating'].mean()
df_std = df_author.groupby('author_average_rating')['book_average_rating'].std()

# Taille de l'échantillon
n = df_author.groupby('author_average_rating')['book_average_rating'].count()

# Calcul de l'intervalle de confiance
ci = 1.96 * df_std / np.sqrt(n)

# Préparation des données pour le graphique
x = df_mean.index
y = df_mean.values

# Créer le graphique
plt.figure(figsize=(32, 8))  # Taille du plot

# Tracé de la moyenne et de l'intervalle de confiance
plt.plot(x, y, label='Mean average rating')
plt.fill_between(x, (y - ci), (y + ci), color='#ff2515', alpha=0.7, label='95% CI')

# Ajuster les labels des axes et le titre
plt.xlabel("author_average_rating", fontsize=14)
plt.ylabel("book_average_rating", fontsize=14)
plt.title("Plot of author_average_rating as a function of book_average_rating with 95% CI", fontsize=16)

plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.legend()
plt.show()

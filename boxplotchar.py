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

# URL of Google Sheets about books
url = 'https://docs.google.com/spreadsheets/d/1cWkVcuw_wTQxqTgJcRfCZTweSb06tzfHVbuAd73owNw/export?format=csv&gid=1613894920'

# download the CSV file
response = requests.get(url)

# Check if it succed
if response.status_code == 200:
     # Convert the content to a string and use StringIO to handle it as a file-like object
    csv_data = StringIO(response.content.decode('utf-8'))

    # Read the CSV into a DataFrame with low_memory=False to avoid mixed dtype warnings and range for the number of columns to import
    df = pd.read_csv(csv_data, low_memory=False)
    df = df[df.columns[:25]]
else:
    print(f"ERROR WHILE DOWNLOADING THE FILE: {response.status_code}")


# Retirer les lignes où 'year_published' est inférieur à 1500
df_year = df[df['year_published'] >= -850]
#[df['year_published'] >= 1900]
# Calculer les quantiles basés sur les années
NbQuantiles = 4
# Calculer les quantiles et laisser qcut générer les intervalles comme labels
df_year['year_group'] = pd.qcut(df_year['year_published'], q=NbQuantiles)

# Réorganiser les données pour le boxplot
df_melted = pd.melt(df_year, id_vars='year_group',  # Utilise 'year_group' ici
                    value_vars=['five_star_ratings', 'four_star_ratings',
                                'three_star_ratings', 'two_star_ratings',
                                'one_star_ratings'],
                    var_name='rating', value_name='value')

# Créer le boxplot avec Seaborn
plt.figure(figsize=(16, 8))
sns.boxplot(x='year_group', y='value', hue='rating', data=df_melted)

# Ajouter un titre et des étiquettes
plt.title("Box plot of ratings by year group")
plt.xlabel('Year Group (by Quartiles)')  # Étiquette de l'axe des x
plt.ylabel('Rating Values')              # Étiquette de l'axe des y

plt.legend(title='Rating Type')          # Ajouter une légende
plt.yscale('log')                        # Utiliser une échelle logarithmique si nécessaire
plt.show()                               # Afficher le graphique
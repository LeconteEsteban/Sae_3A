##Creer par Mohamed

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
from sklearn.cluster import KMeans
from io import StringIO
from mca import MCA
import pycountry
import pycountry_convert as pc
from adjustText import adjust_text

# Load the dataset from a CSV file
df = pd.read_csv("Big_boss_authors.csv", low_memory=False)

# Remove rows with missing values
df.dropna(inplace=True)

def get_continent(country_name):
    # Handle empty or whitespace-only country names
    country_name = country_name.split("\n")[0].strip()  # Keep only the first line and strip whitespace
    if not country_name:  # Check if country_name is empty or whitespace-only
        return None  # Return None for missing data

    try:
        country = pycountry.countries.lookup(country_name)  # Look up the country using its name
        country_code = country.alpha_2  # Get the 2-letter country code
        continent_code = pc.country_alpha2_to_continent_code(country_code)  # Convert the country code to a continent code
        return continent_code  # Return the continent code

    except LookupError:
        return None  # Return None if the country cannot be found

# Apply the get_continent function to create a new column for continent
df['continent'] = df['birthplace'].apply(get_continent)

# Create a new DataFrame for analysis containing selected columns
dfACMD = df[['author_gender', 'genre_1', "continent"]]

# Count the occurrences of each continent
continets_counts = dfACMD['continent'].value_counts().reset_index()
continets_counts.columns = ['continent', 'count']  # Rename columns for clarity

# Count the occurrences of each genre
genre_counts = dfACMD['genre_1'].value_counts().reset_index()
genre_counts.columns = ['genre_1', 'count']

# Set a threshold to filter main genres
threshold = 300
main_genres = [genre_1 for genre_1, count in genre_counts.set_index('genre_1')['count'].items() if count >= threshold]

# Filter the DataFrame to include only rows with main genres
dfACMPRE = dfACMD[dfACMD['genre_1'].isin(main_genres)]
# Also filter the DataFrame to include only valid continents
dfACMPRE = dfACMD[dfACMD['continent'].isin(continets_counts['continent'])]

# Transform qualitative variables into a complete disjunctive table (One-Hot Encoding)
dc = pd.DataFrame(pd.get_dummies(dfACMPRE))

# Perform Multiple Correspondence Analysis (MCA)
mcaFic = MCA(dc, benzecri=False)

# Set the figure size to very large dimensions
plt.figure(figsize=(150, 110))
plt.scatter(mcaFic.fs_c()[:, 0], mcaFic.fs_c()[:, 1], s=150)  # Scatter plot for MCA dimensions

# Create a list to store text objects for the labels
texts = []

# Adjust the positions of the texts based on the figure size
for i, j, nom in zip(mcaFic.fs_c()[:, 0], mcaFic.fs_c()[:, 1], dc.columns):
    # Adjust position to fit the large figure
    text = plt.text(i + 0.05, j + 0.05, nom, fontsize=30, ha='right')
    texts.append(text)

# Use adjust_text to avoid overlap of labels
adjust_text(texts,
            force_text=10.0,    # Increased force to move text
            force_points=1.0,  # Increased force to spread points and text
            expand_text=(1.5, 1.5),  # Increased expansion to separate text
            lim=10000,  # Limit on the number of adjustment iterations
            arrowprops=dict(arrowstyle="-", color='grey', lw=1.5,
                            connectionstyle="arc3,rad=0",  # Straight lines for connections
                            shrinkA=0, shrinkB=5))  # Adjust length of arrows

# Set the title and labels with larger fonts
plt.title("ACM", fontsize=70)
plt.xlabel("Dimension 1", fontsize=50)
plt.ylabel("Dimension 2", fontsize=50)
plt.show()  # Display the plot

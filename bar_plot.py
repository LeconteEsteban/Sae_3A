# from sklearn.datasets import load_iris
# from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
#from sklearn.cluster import KMeans
import pandas as pd
import numpy as np


#dfAuthors = pd.read_csv("Big_boss_authors.csv",delimiter=",")
#dfAuthors


#-------------------------------------------------------------
#Bar Chart of Book Ratings by Year of Publication

# Loading the data
dfBook = pd.read_csv("bigboss_book - bigboss_book.csv", delimiter=",", low_memory=False)

# Cleaning the data: converting the years to numeric and removing invalid ones
dfBook['year_published'] = pd.to_numeric(dfBook['year_published'], errors='coerce')
dfBook_cleaned = dfBook.dropna(subset=['year_published'])
dfBook_cleaned['year_published'] = dfBook_cleaned['year_published'].astype(int)

# Generate the range of valid years (include years with no ratings)
min_year = dfBook['year_published'].min()
max_year = dfBook['year_published'].max()
all_years = pd.DataFrame({'year_published': np.arange(min_year, max_year + 1)})

# Merge the data to include all missing years
dfBook_complete = pd.merge(all_years, dfBook_cleaned, on='year_published', how='left')

# Replace NaN values (for ratings) with 0 for calculation or NaN if you want to exclude them from averages
dfBook_complete[['one_star_ratings', 'two_star_ratings', 'three_star_ratings', 'four_star_ratings', 'five_star_ratings']] = \
    dfBook_complete[['one_star_ratings', 'two_star_ratings', 'three_star_ratings', 'four_star_ratings', 'five_star_ratings']].fillna(0)

# Divide the years into quartile classes including all years (even those without ratings)
year_bins = 4
dfBook_complete['year_published_class'] = pd.qcut(dfBook_complete['year_published'], q=year_bins, duplicates='drop')

# Group by year classes and calculate the average ratings for all years, even if some are 0
y1 = dfBook_complete.groupby('year_published_class')['one_star_ratings'].mean()
y2 = dfBook_complete.groupby('year_published_class')['two_star_ratings'].mean()
y3 = dfBook_complete.groupby('year_published_class')['three_star_ratings'].mean()
y4 = dfBook_complete.groupby('year_published_class')['four_star_ratings'].mean()
y5 = dfBook_complete.groupby('year_published_class')['five_star_ratings'].mean()

# Creating the chart
x = np.arange(len(y1))
width = 0.15
dist = width

# Labels for year classes for xticks (all years)
xtick_labels = [f"{int(interval.left)} - {int(interval.right)}" for interval in dfBook_complete['year_published_class'].cat.categories]

plt.bar(x - 2*dist, y1, width, color='#F28E2B', label="1★")  # Bright orange
plt.bar(x - dist, y2, width, color='#3D85C6', label="2★")   # Bright blue
plt.bar(x, y3, width, color='#A6D785', label="3★")          # Pastel green
plt.bar(x + dist, y4, width, color='#D94D25', label="4★")   # Bright red
plt.bar(x + 2*dist, y5, width, color='#6D3D99', label="5★") # Purple

plt.xticks(x, xtick_labels)
plt.xlabel("Year of Publication")
plt.ylabel("Rating")
plt.legend(["1★", "2★", "3★", "4★", "5★"])
plt.title("Bar Chart of Book Ratings by Year of Publication")
plt.tight_layout()
plt.show()


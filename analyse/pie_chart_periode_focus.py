
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("bigboss_book.csv", delimiter=",")

df['year_group'] = pd.cut(df['year_published'], bins=[1995, 2000,2005,2010,2015,2020,2024],
                           labels=["1995-2000", "2000-2005", "2005-2010","2010-2015","2015-2020","2020-2023"])

year_count = df['year_group'].value_counts()

def afficher_nombre(pct):
    total = sum(year_count)
    print(total)
    valeur = int(round(pct*total/100))
    return f'{valeur}'

plt.pie(year_count, labels=year_count.index, startangle=90, autopct=afficher_nombre)
plt.title("Repartition and number of book per periode")
plt.axis('equal')
plt.show()
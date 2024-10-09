import pandas as pd
import matplotlib.pyplot as plt
import re
df = pd.read_csv("bigboss_book.csv", delimiter=",")
df = df.dropna(subset=['genre_and_votes'])

df_after_1995 = df[df['year_published'] < 1995]
# df_after_1995 = df[df['year_published'] > 1995]

def parse_genre_votes(genre_and_votes):
    genre_votes = re.findall(r'([\w\s-]+)\s(\d+)', genre_and_votes)
    return {genre.strip(): int(vote) for genre, vote in genre_votes}

df_genre = df_after_1995[['genre_and_votes']].copy()

df_genre['genre_votes_dict'] = df_genre['genre_and_votes'].apply(parse_genre_votes)

all_genres = set()
df_genre['genre_votes_dict'].apply(lambda x: all_genres.update(x.keys()))

genre_data = {}
for genre in all_genres:
    genre_data[genre] = df_genre['genre_votes_dict'].apply(lambda x: x.get(genre, 0))

df_genre = pd.concat([df_genre, pd.DataFrame(genre_data)], axis=1)

df_genre = df_genre.drop(columns=['genre_votes_dict'])

genre_columns = list(all_genres)
genre_counts = df_genre[genre_columns].sum().reset_index()
genre_counts.columns = ['genre', 'count']

top_50_genres = genre_counts.sort_values(by='count', ascending=False).head(50)

total_votes_top_50 = top_50_genres['count'].sum()

top_50_genres['percentage'] = (top_50_genres['count'] / total_votes_top_50) * 100

top_genres_above_3 = top_50_genres[top_50_genres['percentage'] >= 1]
top_genres_below_3 = top_50_genres[top_50_genres['percentage'] < 1]

other_genre_row = pd.DataFrame({
    'genre': ['Autre'],
    'count': [top_genres_below_3['count'].sum()],
    'percentage': [top_genres_below_3['percentage'].sum()]
})

final_genre_counts = pd.concat([top_genres_above_3, other_genre_row], ignore_index=True)

plt.figure(figsize=(10, 10))
plt.pie(final_genre_counts['count'], labels=final_genre_counts['genre'], autopct='%1.1f%%', startangle=90)
plt.axis('equal')
plt.title('Repartition of all books per genre before 1995')
# plt.title('Repartition of all books per genre after 1995')
plt.show()

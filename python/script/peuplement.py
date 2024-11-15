

class peuplement:
    """
    Gere le peuplement
    """

    def __init__(self):
        return 1

    def Table_genre(self):
        df_clust = df.dropna()
        df_genre = df_clust[['genre_and_votes']].copy()


        def parse_genre_votes(genre_and_votes):
            genre_votes = re.findall(r'([\w\s-]+)\s(\d+)', genre_and_votes)
            return {genre.strip(): int(vote) for genre, vote in genre_votes}

        df_genre['genre_votes_dict'] = df_genre['genre_and_votes'].apply(parse_genre_votes)


        all_genres = set()
        df_genre['genre_votes_dict'].apply(lambda x: all_genres.update(x.keys()))


        genre_data = {}
        for genre in all_genres:
            genre_data[genre] = df_genre['genre_votes_dict'].apply(lambda x: x.get(genre, 0))



        genres_data = [{'name': genre} for genre in all_genres]
        print("Insertion des genres...")
        insert_sql("Genre", genres_data)


# Exemple d'utilisation
if __name__ == "__main__":
    peuplement1 = peuplement()

    try:
        

    finally:
        
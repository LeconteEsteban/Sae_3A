from service.DatabaseService import *
from service.CSVService import CSVService
#from script.peuplement import *
#from script.traitement import *
#from service.CacheService import *
from service.RecommandationService import * 
#from service.ParseService import *
from service.EmbeddingService import *
from datetime import datetime

def test_data(bdd):
    """
    Remplit la base de données de données de test pour la recommandation item base à minima
    """
    # Insertion dans la table User_Book_Read
    query = """
        INSERT INTO library.User_Book_Read 
        (user_id, book_id, is_read, is_liked, is_favorite, reading_date, notation_id) 
        VALUES 
        (1, 154, TRUE, TRUE, TRUE, '2024-12-17', NULL),
        (1, 155, TRUE, TRUE, TRUE, '2024-12-17', NULL),
        (1, 156, TRUE, TRUE, TRUE, '2024-12-17', NULL),
        (1, 157, TRUE, TRUE, TRUE, '2024-12-17', NULL),
        (1, 158, TRUE, TRUE, TRUE, '2024-12-17', NULL),
        (2, 6452, TRUE, TRUE, TRUE, '2024-12-17', NULL),
        (2, 11570, TRUE, TRUE, TRUE, '2024-12-17', NULL),
        (2, 16586, TRUE, TRUE, TRUE, '2023-12-17', NULL),
        (2, 37980, TRUE, TRUE, TRUE, '2023-12-17', NULL),
        (2, 38052, TRUE, TRUE, TRUE, '2022-12-17', NULL);
    """
    bdd.cmd_sql(query)

    # Insertion dans la table User_Book_Notation
    query = """
        INSERT INTO library.User_Book_Notation 
        (note, review_id, read_id) 
        VALUES 
        (5, NULL, 38),
        (4, NULL, 39),
        (3, NULL, 40),
        (5, NULL, 41),
        (1, NULL, 42),
        (5, NULL, 43),
        (4, NULL, 44),
        (3, NULL, 45),
        (5, NULL, 46),
        (1, NULL, 47);
    """
    bdd.cmd_sql(query)

#main pour les tests pls
if __name__ == "__main__":
    #cache_service  = CacheService()
    bddservice = DatabaseService()
    csv_service = CSVService()
    #parseservice = ParsingService()
    embservice = EmbeddingService()
    #peuplement1 = peuplement(bddservice, csv_service, parseservice)
    #traitement1 = traitement(bddservice, csv_service)
    recommandation1 = RecommendationService(bddservice, csv_service, embservice)

    try:
        # Initialiser la connexion à garder
        bddservice.initialize_connection()
        print(datetime.now())

        #print(bddservice.get_book_cover_url(1,'9781416950417'))

        #Créer la base de donnée
        #bddservice.create_database()
        #remplie la base de donnée des tables
        #peuplement1.peuplementTotal()
        #Effectue les traitements: vue matérialisé, pré-traitement, ...
        #traitement1.traitementTotal()

        # bddservice.cmd_sql("TRUNCATE TABLE library.friends RESTART IDENTITY CASCADE ;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.User_Book_Read RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.User_field_of_reading RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.preferred_format_of_reading RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.liked_author RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.user_liked_genre RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library._Users RESTART IDENTITY CASCADE;")

        # test_data(bddservice)
        # peuplement1.table_user()
        #recommandation1.create_book_vector()

        # #similar_books = recommandation1.get_similar_books(1, 5)

        # similar_books = recommandation1.get_user_books(1)
        # # Affichage des livres similaires
        # for book in similar_books:
        #     print(book)

        # recommanded_book = recommandation1.recommend_books_for_user(2,200)
        # # # Affichage des livres recommandé
        # for book in recommanded_book:
        #      print(book)
        # print(len(recommanded_book))

        #bddservice.cmd_sql("TRUNCATE TABLE library.book_vector;")

    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        bddservice.close_connection()






     
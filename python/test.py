from service.DatabaseService import *
from service.CSVService import CSVService
from script.peuplement import *
from script.traitement import *
from service.CacheService import *
from service.RecommandationService import * 
from service.ParseService import *
from service.EmbeddingService import *


#main pour les tests pls
if __name__ == "__main__":
    cache_service  = CacheService()
    bddservice = DatabaseService()
    csv_service = CSVService()
    parseservice = ParsingService()
    embservice = EmbeddingService()
    peuplement1 = peuplement(bddservice, csv_service, parseservice)
    traitement1 = traitement(bddservice, csv_service)
    recommandation1 = RecommendationService(bddservice, csv_service, embservice)

    try:
        # Initialiser la connexion
        bddservice.initialize_connection()
        #Créer la base de donnée
        #bddservice.create_database()
        #remplie la base de donnée des tables
        #peuplement1.peuplementTotal()
        #Effectue les traitements: vue matérialisé, pré-traitement, ...

        # bddservice.cmd_sql("TRUNCATE TABLE library.friends RESTART IDENTITY CASCADE ;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.User_Book_Read RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.User_field_of_reading RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.preferred_format_of_reading RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.liked_author RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.user_liked_genre RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library._Users RESTART IDENTITY CASCADE;")

        # peuplement1.table_user()
        recommandation1.create_book_vector()
        #similar_books = recommandation1.get_similar_books(1, 5)

        # Affichage des livres similaires
        # for book in similar_books:
        #     print(f"ID: {book[0]}, Titre: {book[1]}, Similarité: {book[2]}")


        #bddservice.cmd_sql("TRUNCATE TABLE library.book_vector;")

    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        bddservice.close_connection()



def test_data():
     """
     remplie la bdd de donnée de testpour la recommandation
     """
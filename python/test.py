# -*- coding: utf-8 -*-
from service.DatabaseService import *
from service.CSVService import CSVService
from script.peuplement import *
from script.traitement import *
from service.CacheService import *
from service.RecommandationService import * 
from service.RecomandationHybride import * 
from service.ParseService import *
from service.EmbeddingService import *
import csv


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
    recommandationhybride = RecomandationHybride(bddservice, csv_service, embservice,recommandation1)

    try:
        # Initialiser la connexion
        bddservice.initialize_connection()
        #Créer la base de donnée
        #bddservice.create_database()
        #remplie la base de donnée des tables
        #peuplement1.peuplementTotal()
        #Effectue les traitements: vue matérialisé, pré-traitement, ...

        #recommandation1.create_book_vector()
        #recommandationhybride.create_vector_users()
        

        # bddservice.cmd_sql("TRUNCATE TABLE library.friends RESTART IDENTITY CASCADE ;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.User_Book_Read RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.User_field_of_reading RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.preferred_format_of_reading RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.liked_author RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library.user_liked_genre RESTART IDENTITY CASCADE;")
        # bddservice.cmd_sql("TRUNCATE TABLE library._Users RESTART IDENTITY CASCADE;")

        # peuplement1.table_user()
        #recommandation1.create_book_vector()
        #similar_books = recommandation1.get_similar_books(1, 5)
        #recommandationhybride.get_similar_users_debug(26,5)
        #print(recommandationhybride.recommend_books_for_user(26,5))
        #bddservice.cmd_sql("TRUNCATE TABLE library.user_vector;")
        #recommandationhybride.create_vector_users()
        #print(recommandationhybride.recommend_books_for_user(25,5))
        #print(recommandationhybride.get_top_books(20))
        #print(recommandationhybride.recommandation_hybride(25,20))

        #print(bddservice.update_book_cover_from_csv("9780385618953", csv_file_path="books_with_cover.csv"))
        print(bddservice.fill_book_cover_from_csv(csv_file_path="books_with_cover.csv"))

        # # Affichage des livres similaires
        # for book in similar_books:
        #      print(f"ID: {book[0]}, Titre: {book[1]}, Similarité: {book[2]}")


        #bddservice.cmd_sql("TRUNCATE TABLE library.book_vector;")

    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        # bddservice.close_connection()
        print("fin")



def test_data():
     """
     remplie la bdd de donnée de testpour la recommandation
     """
     return 0

     
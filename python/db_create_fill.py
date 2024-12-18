from service.DatabaseService import *
from service.CSVService import CSVService
from script.peuplement import *
from script.traitement import *
from service.CacheService import *
from service.RecommandationService import * 
from service.RecomandationHybride import * 
from service.ParseService import *
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
        (1, 158, TRUE, TRUE, TRUE, '2024-12-17', NULL);
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
        (1, NULL, 42);
    """
    bdd.cmd_sql(query)

#main pour les tests pls
if __name__ == "__main__":
    cache_service  = CacheService()
    bddservice = DatabaseService()
    csv_service = CSVService()
    parseservice = ParsingService()
    embservice = EmbeddingService()
    peuplement1 = peuplement(bddservice, csv_service, parseservice)
    traitement1 = traitement(bddservice, csv_service)
    recommandationItemBased = RecommendationService(bddservice, csv_service, embservice)
    recommandationHybride = RecomandationHybride(bddservice, csv_service, embservice, recommandationItemBased)

    try:
        print(datetime.now())
        # Initialiser la connexion
        bddservice.initialize_connection()
        #Créer la base de donnée
        bddservice.create_database()
        #remplie la base de donnée des tables
        peuplement1.peuplementTotal()
        #Effectue les traitements: vue matérialisé, pré-traitement, ...
        traitement1.traitementTotal()
        #fait les vecteurs des book et les stock en bdd
        recommandationItemBased.create_book_vector()
        #pareille avec les vecteurs des users
        recommandationHybride.create_vector_users()

        print("fin :)")


    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        bddservice.close_connection()
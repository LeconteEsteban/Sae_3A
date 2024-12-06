from service.DatabaseService import *
from service.CSVService import CSVService
from script.peuplement import *
from script.traitement import *
from service.CacheService import *
from service.RecommandationService import * 
from service.ParseService import *


#main pour les tests pls
if __name__ == "__main__":
    cache_service  = CacheService()
    bddservice = DatabaseService()
    csv_service = CSVService()
    parseservice = ParsingService()
    peuplement1 = peuplement(bddservice, csv_service, parseservice)
    traitement1 = traitement(bddservice, csv_service)
    recommandation1 = RecommendationService(bddservice, csv_service)

    try:
        # Initialiser la connexion
        bddservice.initialize_connection()
        #Créer la base de donnée
        #bddservice.create_database()
        #remplie la base de donnée des tables
        peuplement1.peuplementTotal()
        #Effectue les traitements: vue matérialisé, pré-traitement, ...

        #bddservice.cmd_sql("delete from library.book_similarity")

        #traitement1.traitementTotal()
        #traitement1.similarity()
        #print(traitement1.cluster_genre())

        #print(recommandation1.get_similar_books(1))

    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        bddservice.close_connection()
from service.DatabaseService import *
from service.CSVService import CSVService
from script.peuplement import *
from script.traitement import *
from service.CacheService import *
from service.RecommandationService import * 
from service.ParseService import *
from service.RecomandationHybride import *


#main pour les tests pls
if __name__ == "__main__":
    cache_service  = CacheService()
    bddservice = DatabaseService()
    csv_service = CSVService()
    parseservice = ParsingService()
    embeddingservice = EmbeddingService()
    peuplement1 = peuplement(bddservice, csv_service, parseservice)
    traitement1 = traitement(bddservice, csv_service)
    recommandation1 = RecommendationService(bddservice, csv_service)
    recommandationHybride1 = RecomandationHybride(bddservice, csv_service, embeddingservice)

    try:
       
         bddservice.initialize_connection()
         bddservice.create_database()
         peuplement1.peuplementTotal()
    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        bddservice.close_connection()
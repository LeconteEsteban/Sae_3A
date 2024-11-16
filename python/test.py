from service.DatabaseService import *
from service.CSVService import CSVService
from script.peuplement import *
from script.traitement import *
from service.CacheService import *

#main pour les tests pls
if __name__ == "__main__":
    cache_service  = CacheService()
    bddservice = DatabaseService()
    csv_service = CSVService()
    peuplement1 = peuplement(bddservice, csv_service)
    traitement1 = traitement(bddservice, csv_service)

    try:
        # Initialiser la connexion
        bddservice.initialize_connection()
        #Créer la base de donnée
        #bddservice.create_database()
        #remplie la base de donnée des tables
        #peuplement1.peuplementTotal()
        #Effectue les traitements: vue matérialisé, pré-traitement, ...

        #bddservice.cmd_sql("delete from library.top_books")

        #traitement1.traitementTotal()
        traitement1.similarity()

    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        bddservice.close_connection()
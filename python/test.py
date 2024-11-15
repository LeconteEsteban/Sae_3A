from service.DatabaseService import *
from service.CSVService import CSVService
from script.peuplement import *
from service.CacheService import *

#main pour les tests pls
if __name__ == "__main__":
    cache_service  = CacheService()
    bddservice = DatabaseService()
    csv_service = CSVService()
    peuplement1 = peuplement(bddservice)

    try:
        # Initialiser la connexion
        bddservice.initialize_connection()

        #db_service.create_database()

        #bddservice.cmd_sql("delete from library.book;")
        #print(bddservice.cmd_sql("SELECT COUNT(*) FROM library.book;"))
        
        peuplement1.table_characters_of_book()

    except Exception as e:
            print(f"Erreur dans le main : {e}")
    finally:
        # Fermer la connexion
        bddservice.close_connection()
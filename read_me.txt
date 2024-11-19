Bonjour à tous

worker disponible :
    - installation de tout les dépendances automatiques : auto_install_pip.py
    - si vous avez des erreurs qui ne sont pas lier aux droit de l'environement, vous pouvez rexecuter le script plusieurs fois, ça fonctionnera

service disponible :
    -DatabaseService, remplir connection_bdd pour renseigner les infos de connection à la bdd
    -CSVService : pour la gestion des csv, 
    -CacheService 


script disponible :
    script de création de la base de donnée: DatabaseService.create_database()
    script de peuplement de la bdd: Peuplement.peuplementTotal()
    script de Traitement de la bdd: Traitement.traitementTotal()


main disponible :
    db_create_fill.py pour créer, remplir et traiter la bdd automatiquement


test disponible : 
    utilisé librement test.py ou créer d'autre fichier test, pour effectuer vos tests !
    grace à la mise en cache, vous optimiser les temps d'executions pour les tests !

Spécificité : 
    
    - escape.sql est le script sql de création de base de donnée, il ne faut le modifier que si vous êtes
    sûr des changements, create_table.sql est le script qui sera executer par DatabaseService.create_database(),
    create_table.sql est téléchargé à partir git main s'il n'existe pas, donc vous devez faire vos tests sql dessus.

    

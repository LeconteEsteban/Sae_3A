Bonjour à tous
Lisez bien la mention IMPORTANT svp

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


!!!!!!!!!! IMPORTANT, SVP, Pour git, supprimer votre dossier cache ainsi que tout les __pycache__ (utilisez si possible avant_de_push.py qui automatise) !!!!!!!!!!!
Nettoyer localement : Si vous voulez supprimer les __pycache__ de votre répertoire local avant le push :
python : executer avant_de_push.py situé à la racine du projet
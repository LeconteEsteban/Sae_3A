from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import Optional
from models.schemas import  AuthorReponse
from services.servicebdd import bddservice




router = APIRouter()



@router.get("/all", response_model=List[AuthorReponse])
def get_all_authors():
    """
    Endpoint pour obtenir tous les auteurs de la base de données.

    Cette fonction exécute une requête SQL complexe pour récupérer les informations de base
    des auteurs, agrège les livres écrits par chaque auteur, joint les tables `wrote` et
    `Rating_author`, et calcule la note moyenne des auteurs. Les résultats sont groupés par
    auteur. Si aucun auteur n'est trouvé, une exception HTTP 404 est levée.

    Returns:
        List[AuthorReponse]: Une liste de tous les auteurs avec leurs informations et les livres écrits.
    """
    
    # Requête SQL
    query = """SELECT
                Author.author_id,
                Author.name,
                Author.birthplace,
                Rating_author.average_author_rating,
                ARRAY_AGG(DISTINCT wrote.book_id) AS BooksWritten
            FROM
                library.Author
            LEFT JOIN library.wrote ON wrote.author_id = Author.author_id
            LEFT JOIN library.Rating_author ON Rating_author.author_id = Author.author_id
            GROUP BY
                Author.author_id, Author.name, Author.birthplace, Rating_author.average_author_rating
            ;
                """
    authors = bddservice.cmd_sql(query)
    
    # Gestion d'erreur si aucun auteur trouvé
    if not authors:
        raise HTTPException(status_code=404, detail="No authors found in the database")

    
    authors_data = [
        {
        "id": author[0],
        "name": author[1],
        "birthplace": author[2],
        "authorRating": author[3],
        "BooksWritten": author[4]
        }
        for author in authors
    ]

    return authors_data


@router.get("/{id_author}", response_model=AuthorReponse)
def get_author(id_author: int):
    """
    Endpoint pour obtenir les informations d'un auteur donné.

    Cette fonction prend en paramètre l'identifiant d'un auteur (id_author) et exécute une
    requête SQL pour récupérer les informations de l'auteur, y compris les livres écrits et
    la note moyenne. La requête est une version filtrée de la requête principale, avec un
    filtrage par ID d'auteur. Si l'auteur n'est pas trouvé, une exception HTTP 404 est levée.

    Args:
        id_author (int): L'identifiant de l'auteur.

    Returns:
        AuthorReponse: Les informations de l'auteur avec les livres écrits et la note moyenne.
    """

    # Requête pour filtrer par ID
    query = f"""SELECT
                Author.author_id,
                Author.name,
                Author.birthplace,
                Rating_author.average_author_rating,
                ARRAY_AGG(DISTINCT wrote.book_id) AS BooksWritten
            FROM
                library.Author
            LEFT JOIN library.wrote ON wrote.author_id = Author.author_id
            LEFT JOIN library.Rating_author ON Rating_author.author_id = Author.author_id
            WHERE Author.author_id = {id_author}
            GROUP BY
                Author.author_id, Author.name, Author.birthplace, Rating_author.average_author_rating
            ;
                """
    author = bddservice.cmd_sql(query)
    
    
    if not author:
        raise HTTPException(status_code=404, detail="Author not found in the database")
    author = author[0]
    
    
    author_data = {
        "id": author[0],
        "name": author[1],
        "birthplace": author[2].strip(),  
        "authorRating": author[3],
        "BooksWritten": author[4]
    }

    return author_data
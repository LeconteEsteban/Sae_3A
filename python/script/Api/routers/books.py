from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import Optional
from models.schemas import BookResponse
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride
from datetime import date
import random



router = APIRouter()


@router.get("/all", response_model=List[BookResponse])
def get_all_books():
    """
    Endpoint pour obtenir tous les livres de la base de données.

    Cette fonction exécute une requête SQL pour récupérer tous les livres avec leurs détails,
    y compris les informations sur les auteurs, les genres, les récompenses, et les notes.
    Si aucun livre n'est trouvé, une exception HTTP 404 est levée.

    Returns:
        List[BookResponse]: Une liste de livres avec leurs détails.
    
    """
    query = f"""
        WITH book_data AS (
            SELECT 
                b.book_id,
                b.title,
                b.isbn,
                b.isbn13,
                a.name AS author_name,
                b.description,
                b.number_of_pages,
                p.name AS publisher_name,
                array_agg(DISTINCT g.name) AS genre_names,
                array_agg(DISTINCT aw.name) AS award_names,
                rb.rating_count,
                rb.average_rating
            FROM library.book b
            JOIN library.wrote w ON b.book_id = w.book_id
            JOIN library.author a ON w.author_id = a.author_id
            JOIN library.publisher p ON b.publisher_id = p.publisher_id
            left join library.genre_and_vote Gav on b.book_id = Gav.book_id
            LEFT JOIN library.genre g ON Gav.genre_id = g.genre_id
            LEFT JOIN library.Award_of_book ba ON b.book_id = ba.book_id
            LEFT JOIN library.award aw ON ba.award_id = aw.award_id
            left join library.rating_book rb on b.book_id = rb.book_id
            GROUP BY b.book_id, b.title, b.isbn, b.isbn13, a.name, b.description,
                     b.number_of_pages, p.name, rb.rating_count, rb.average_rating
        )
        SELECT * FROM book_data;
    """
    books = bddservice.cmd_sql(query)
    if not books:
        raise HTTPException(status_code=404, detail="No books found in the database")

    return [
        {
            "id": book[0],
            "title": book[1],
            "isbn": book[2],
            "isbn13": book[3],
            "author_name": book[4],
            "description": book[5],
            "number_of_pages": book[6],
            "publisher_name": book[7],
            "genre_names": book[8],
            "award_names": book[9],  
            "rating_count": book[10],
            "average_rating": book[11],
        }
        for book in books
    ]


import logging

logging.basicConfig(level=logging.DEBUG)

@router.get("/search", response_model=List[BookResponse])
def search_books(query: Optional[str] = None, skip: int = 0, limit: int = 10):
    """
    Endpoint pour rechercher des livres par titre.

    Cette fonction prend en paramètre une chaîne de recherche (query) et exécute une requête SQL
    pour trouver les livres dont le titre correspond à la recherche. Les résultats peuvent être
    paginés en utilisant les paramètres `skip` et `limit`. Si aucun livre n'est trouvé, une
    exception HTTP 404 est levée.

    Args:
        query (Optional[str]): La chaîne de recherche.
        skip (int): Le nombre de livres à sauter pour la pagination.
        limit (int): Le nombre maximum de livres à retourner.

    Returns:
        List[BookResponse]: Une liste de livres correspondant à la recherche.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    #logging.debug(f"Search query: {query}")

    query_sql = """
        SELECT
            bv.book_id,
            bv.title,
            bv.isbn13,
            bv.description,
            a.name        
        FROM
            library.book bv
        JOIN library.wrote w ON bv.book_id = w.book_id 
        JOIN library.author a ON w.author_id = a.author_id 
        WHERE
            bv.title ILIKE CONCAT('%%', %s, '%%')  
        LIMIT %s OFFSET %s;
    """

    books = bddservice.cmd_sql(query_sql, (query, limit, skip))
    
    #logging.debug(f"Books found: {books}")

    if not books:
        raise HTTPException(status_code=404, detail="No books found matching the query")

    books_data = [
        {
            "id": book[0],
            "title": book[1],
            "isbn13": book[2],
            "description": book[3],
            "author_name": book[4],
            "url": bddservice.get_book_cover_url(book[0], book[2])
        }
        for book in books
    ]

    return books_data



@router.get('/{id_book}', response_model=BookResponse)
def get_book(id_book: int):
    """
    Endpoint pour obtenir un livre par son identifiant.

    Cette fonction prend en paramètre l'identifiant d'un livre (id_book) et exécute une requête SQL
    pour récupérer les détails du livre correspondant. Si le livre n'est pas trouvé, une exception
    HTTP 404 est levée.

    Args:
        id_book (int): L'identifiant du livre.

    Returns:
        BookResponse: Les détails du livre.
    """
    # Formattage direct de la requête avec l'id_book
    query = f"""SELECT
                bv.book_id,
                bv.title,
                bv.isbn13,
                bv.description
            FROM
                library.book bv
            WHERE
                bv.book_id = {id_book}"""
    
    # Exécution de la requête
    book = bddservice.cmd_sql(query)
    
    if not book:
        raise HTTPException(status_code=404, detail="No book found in the database")

    #print(book)
    #print(book[0][0])

    book_data = book[0]
    response_data = {
            "id": book_data[0],
            "title": book_data[1],
            "isbn13": book_data[2],
            "description": book_data[3],
    }
    
    return response_data


@router.get("/topbook/{nbook}", response_model=List[BookResponse])
def get_top_books(nbook: int):
    """
    Endpoint pour obtenir des livres aléatoires parmi les meilleurs livres.

    Cette fonction prend en paramètre le nombre de livres à retourner (nbook) et exécute une
    requête SQL pour récupérer une sélection aléatoire de livres parmi les meilleurs livres.
    Si aucun livre n'est trouvé, une exception HTTP 404 est levée.

    Args:
        nbook (int): Le nombre de livres à retourner.

    Returns:
        List[BookResponse]: Une liste de livres parmi les meilleurs.
    """
    query = """
            WITH top_books_filtered AS (
            SELECT book_id
            FROM library.top_books
            LIMIT 2000
        )
        SELECT
            bv.book_id,
            bv.title,
            bv.isbn13,
            bv.author_name,
            bv.description,
            bv.number_of_pages,
            bv.publisher_name,
            array_agg(DISTINCT bv.genre_name) AS genre_names,
            array_agg(DISTINCT bv.award_name) AS award_names,
            bv.average_rating
        FROM
            top_books_filtered tbf
        JOIN
            library.book_view bv ON tbf.book_id = bv.book_id
        GROUP BY
            bv.book_id,
            bv.title,
            bv.isbn13,
            bv.author_name,
            bv.description,
            bv.number_of_pages,
            bv.publisher_name,
            bv.average_rating;
    """

    #print("Executing query...")
    top_books = bddservice.cmd_sql(query)
    #print(f"Query executed. {len(top_books)} top books found.")

    if not top_books:
        raise HTTPException(status_code=404, detail="No top books found in the database")

    # Sélection aléatoire des livres
    sampled_books = random.sample(top_books, min(nbook, len(top_books)))
    #print(f"Sampled {len(sampled_books)} books.")

    # Transformation des données pour correspondre au schéma BookResponse
    books_data = [
        {
            "id": book[0],
            "title": book[1],
            "isbn13": book[2],
            "author_name": book[3],
            "description": book[4],
            "number_of_pages": book[5],
            "publisher_name": book[6],
            "genre_names": book[7],
            "award_names": book[8],
            "average_rating": book[9],
            "url": bddservice.get_book_cover_url(book[0], book[2])
        }
        for book in sampled_books
    ]

    #print(f"Returning {len(books_data)} books.")
    return books_data
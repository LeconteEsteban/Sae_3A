from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import Optional
from models.schemas import BookResponse
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride, decodeur
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
    -- Utilise LEFT JOIN pour inclure tous les livres, même sans données associées
    LEFT JOIN library.wrote w ON b.book_id = w.book_id
    LEFT JOIN library.author a ON w.author_id = a.author_id
    LEFT JOIN library.publisher p ON b.publisher_id = p.publisher_id
    LEFT JOIN library.genre_and_vote Gav ON b.book_id = Gav.book_id
    LEFT JOIN library.genre g ON Gav.genre_id = g.genre_id
    LEFT JOIN library.Award_of_book ba ON b.book_id = ba.book_id
    LEFT JOIN library.award aw ON ba.award_id = aw.award_id
    LEFT JOIN library.rating_book rb ON b.book_id = rb.book_id
    -- Regroupe par les colonnes de livre, sans les relations "many-to-many"
    GROUP BY 
        b.book_id, 
        b.title, 
        author_name,
        b.isbn, 
        b.isbn13, 
        b.description,
        b.number_of_pages, 
        p.name, 
        rb.rating_count, 
        rb.average_rating
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
            "url": bddservice.get_book_cover_url(book[0], book[2])
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
        LEFT JOIN library.wrote w ON bv.book_id = w.book_id 
        LEFT JOIN library.author a ON w.author_id = a.author_id 
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
   
    query = f"""SELECT 
                book_id,
                title,
                isbn,
                isbn13,
                STRING_AGG(DISTINCT author_name, ', ') FILTER (WHERE author_name IS NOT NULL) AS author_name,
                description,
                number_of_pages,
                publisher_name,
                array_agg(DISTINCT genre_name) FILTER (WHERE genre_name IS NOT NULL) AS genre_names,
                array_agg(DISTINCT award_name) FILTER (WHERE award_name IS NOT NULL) AS award_names,
                rating_count,
                average_rating
            FROM library.book_view
            WHERE book_id = {id_book}
            GROUP BY 
                book_id, title, isbn, isbn13, description, 
                number_of_pages, publisher_name, rating_count, average_rating;
           """
    
    books = bddservice.cmd_sql(query)
    if not books:
        raise HTTPException(status_code=500, detail="Livre non trouvé")

    book = books[0] 

    return {
        "id": book[0],
        "title": decodeur.decode(book[1]),
        "isbn13": book[3],  
        "author_name": decodeur.decode(book[4]),
        "description": decodeur.decode(book[5]),
        "number_of_pages": book[6],
        "publisher_name": decodeur.decode(book[7]),
        "genre_names": book[8],
        "award_names": decodeur.decode(book[9]),
        "rating_count": book[10],
        "average_rating": book[11],  
        "url": bddservice.get_book_cover_url(book[0], book[3]),
    }


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
    bddservice.initialize_connection()
    #print("Executing query...")
    top_books = bddservice.cmd_sql(query)
    #print(f"Query executed. {len(top_books)} top books found.")

    MAX_ATTEMPTS = 3
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        top_books = bddservice.cmd_sql(query)
        if top_books:
            break  # Sortie de la boucle si des livres sont trouvés
        attempts += 1

    if not top_books:
        raise HTTPException(status_code=500, detail="No top books found in the database")

    # Sélection aléatoire des livres
    sampled_books = random.sample(top_books, min(nbook, len(top_books)))
    #print(f"Sampled {len(sampled_books)} books.")

    # Transformation des données pour correspondre au schéma BookResponse
    books_data = [
        {
            "id": book[0],
            "title": decodeur.decode(book[1]),
            "isbn13": book[2],
            "author_name": decodeur.decode(book[3]),
            "description": decodeur.decode(book[4]),
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
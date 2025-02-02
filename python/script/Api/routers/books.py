from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import Optional
from models.schemas import BookResponse
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride
from datetime import date



router = APIRouter()

# @router.get("/all", response_model=List[BookResponse])
# def get_all_books():
#     """
#     Endpoint pour obtenir tous les livres de la base de données.
#     """

#     query = """SELECT
#                 bv.book_id,
#                 bv.title,
#                 bv.isbn,
#                 bv.isbn13,
#                 bv.author_name,
#                 bv.description,
#                 bv.number_of_pages,
#                 bv.publisher_name,
#                 array_agg(DISTINCT bv.genre_name) AS genre_names,
#                 array_agg(DISTINCT bv.award_name) AS award_names,
#                 bv.rating_count,
#                 bv.average_rating
#             FROM
#                 library.book_view bv
#             GROUP BY
#                 bv.book_id, bv.title, bv.isbn, bv.isbn13,
#                 bv.author_name, bv.description, bv.number_of_pages,
#                 bv.publisher_name, bv.rating_count, bv.average_rating
                
#             ;
#                 """
# #SELECT book_id, title, publication_date, isbn, isbn13, description, 
#             #           publisher_name, genre_name, award_name, serie_name, 
#             #           rating_count, average_rating, author_name 
#             #    FROM library.book_view;
#     books = bddservice.cmd_sql(query)
#     if not books:
#         raise HTTPException(status_code=404, detail="No books found in the database")

#     books_data = [
#         {
#         "id": book[0],
#         "title": book[1],
#         "isbn": book[2],
#         "isbn13": book[3],
#         "author_name": book[4],
#         "description": book[5],
#         "number_of_pages": book[6],
#         "publisher_name": book[7],
#         "genre_names": book[8],
#         "award_names": book[9],  
#         "rating_count": book[10],
#         "average_rating": book[11],
#     }
#         for book in books
#     ]

#     return books_data


@router.get("/all", response_model=List[BookResponse])
def get_all_books(skip: int = 0, limit: int = 10):
    """
    Endpoint pour obtenir tous les livres de la base de données avec pagination.
    """
    query = f"""SELECT
                bv.book_id,
                bv.title,
                bv.isbn,
                bv.isbn13,
                bv.author_name,
                bv.description,
                bv.number_of_pages,
                bv.publisher_name,
                array_agg(DISTINCT bv.genre_name) AS genre_names,
                array_agg(DISTINCT bv.award_name) AS award_names,
                bv.rating_count,
                bv.average_rating
            FROM
                library.book_view bv
            GROUP BY
                bv.book_id, bv.title, bv.isbn, bv.isbn13,
                bv.author_name, bv.description, bv.number_of_pages,
                bv.publisher_name, bv.rating_count, bv.average_rating
            LIMIT {limit} OFFSET {skip};
            """
    books = bddservice.cmd_sql(query)
    if not books:
        raise HTTPException(status_code=404, detail="No books found in the database")

    books_data = [
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

    return books_data

import logging

logging.basicConfig(level=logging.DEBUG)

@router.get("/search", response_model=List[BookResponse])
def search_books(query: Optional[str] = None, skip: int = 0, limit: int = 10):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    logging.debug(f"Search query: {query}")

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
    
    logging.debug(f"Books found: {books}")

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
    """
    # Formattage direct de la requête avec l'id_book
    query = f"""SELECT
                bv.book_id,
                bv.title,
                bv.isbn,
                bv.isbn13,
                bv.author_name,
                bv.description,
                bv.number_of_pages,
                bv.publisher_name,
                array_agg(DISTINCT bv.genre_name) AS genre_names,
                array_agg(DISTINCT bv.award_name) AS award_names,
                bv.rating_count,
                bv.average_rating
            FROM
                library.book_view bv
            WHERE
                bv.book_id = {id_book}
            GROUP BY
                bv.book_id, bv.title, bv.isbn, bv.isbn13,
                bv.author_name, bv.description, bv.number_of_pages,
                bv.publisher_name, bv.rating_count, bv.average_rating;"""
    
    # Exécution de la requête (en supposant que tu utilises une méthode pour ça)
    book = bddservice.cmd_sql(query)
    
    if not book:
        raise HTTPException(status_code=404, detail="No book found in the database")

    book_data = book[0]
    response_data = {
        "id": book_data[0],
        "title": book_data[1],
        "isbn": book_data[2],
        "isbn13": book_data[3],
        "author_name": book_data[4],
        "description": book_data[5],
        "number_of_pages": book_data[6],
        "publisher_name": book_data[7],
        "genre_names": book_data[8],
        "award_names": book_data[9],  
        "rating_count": book_data[10],
        "average_rating": book_data[11],
    }
    
    return response_data



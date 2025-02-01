from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import BookResponse
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride
import random


router = APIRouter()



@router.get("/all", response_model=List[BookResponse])
def get_all_books():
    """
    Endpoint pour obtenir tous les livres de la base de données.
    """

    query = """SELECT book_id, title, publication_date, isbn, isbn13, description, 
                      publisher_name, genre_name, award_name, serie_name, 
                      rating_count, average_rating, author_name 
               FROM library.book_view;"""
    books = bddservice.cmd_sql(query)
    if not books:
        raise HTTPException(status_code=404, detail="No books found in the database")

    return books



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
    }
    
    return response_data
@router.get("/topbook/{nbook}", response_model=List[BookResponse])
def get_top_books(nbook: int):
    """
    Endpoint pour obtenir des livres aléatoires parmi les meilleurs livres.
    """
    query = """
                SELECT
                    bv.book_id, bv.title, bv.isbn13, bv.author_name,
                    bv.description, bv.number_of_pages, bv.publisher_name,
                    array_agg(DISTINCT bv.genre_name) AS genre_names,
                    array_agg(DISTINCT bv.award_name) AS award_names,
                    bv.average_rating
                FROM library.top_books tb
                JOIN library.book_view bv ON tb.book_id = bv.book_id
                GROUP BY
                            bv.book_id, bv.title, bv.isbn, bv.isbn13, bv.author_name,
                            bv.description, bv.number_of_pages, bv.publisher_name,
                            bv.rating_count, bv.average_rating
                LIMIT 100;
    """
    
    top_books = bddservice.cmd_sql(query)

    if not top_books:
        raise HTTPException(status_code=404, detail="No top books found in the database")
    
    # Sélection aléatoire des livres
    sampled_books = random.sample(top_books, min(nbook, len(top_books)))

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
        }
        for book in sampled_books
    ]

    return books_data

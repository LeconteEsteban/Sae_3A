from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import BookResponse
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride



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



from fastapi import HTTPException
from typing import Optional
from datetime import date

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



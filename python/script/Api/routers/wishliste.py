from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import BookResponse
from services.servicebdd import bddservice
from datetime import date

router = APIRouter()

@router.post("/wishlist/add/{user_id}/{book_id}")
def add_to_wishlist(user_id: int, book_id: int):
    """
    Ajoute un livre à la wishlist d'un utilisateur.
    """
    query = """
        INSERT INTO WishListe (user_id, book_id, add_date)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, book_id) DO NOTHING;
    """
    bddservice.cmd_sql(query, (user_id, book_id, date.today()))
    return {"message": "Livre ajouté à la wishlist"}

@router.get("/wishlist/{user_id}", response_model=List[BookResponse])
def get_wishlist(user_id: int):
    """
    Récupère la wishlist d'un utilisateur avec une seule entrée par livre.
    """
    query = """
        SELECT DISTINCT ON (b.book_id) 
               b.book_id, b.title, b.isbn13, a.name AS author_name, b.description
        FROM WishListe w
        JOIN Book b ON w.book_id = b.book_id
        LEFT JOIN Wrote wr ON b.book_id = wr.book_id
        LEFT JOIN Author a ON wr.author_id = a.author_id
        WHERE w.user_id = %s;
    """
    books = bddservice.cmd_sql(query, (user_id,))
    
    if not books:
        raise HTTPException(status_code=404, detail="Aucun livre trouvé dans la wishlist")
    
    return [
        {
            "id": book[0],
            "title": book[1],
            "isbn13": book[2],
            "author_name": book[3] if book[3] else "Auteur inconnu",
            "description": book[4] if book[4] else "Pas de description",
            "url": bddservice.get_book_cover_url(book[0], book[2])  # Récupération de l'URL de l'image
        }
        for book in books
    ]

@router.delete("/wishlist/remove/{user_id}/{book_id}")
def remove_from_wishlist(user_id: int, book_id: int):
    """
    Supprime un livre de la wishlist d'un utilisateur.
    """
    query = """
        DELETE FROM WishListe WHERE user_id = %s AND book_id = %s;
    """
    bddservice.cmd_sql(query, (user_id, book_id))
    return {"message": "Livre retiré de la wishlist"}

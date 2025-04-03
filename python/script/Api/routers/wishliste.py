from fastapi import APIRouter, HTTPException, Depends, Cookie
from typing import List
from models.schemas import BookResponse
from services.servicebdd import bddservice
from datetime import date

router = APIRouter()

@router.post("/wishlist/add/{book_id}/{user_id}")
def add_to_wishlist(book_id: int, user_id: int):
    """
    Ajoute un livre à la wishlist d'un utilisateur.
    """
    query = """
        INSERT INTO library.WishListe (user_id, book_id, add_date)
        SELECT %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM library.WishListe WHERE user_id = %s AND book_id = %s
        );

    """
    bddservice.initialize_connection()
    bddservice.cmd_sql(query, (user_id, book_id, date.today(), user_id, book_id))

    return {"message": "Livre ajouté à la wishlist"}

@router.get("/wishlist/{user_id}")
def get_wishlist(user_id: int):
    """
    Récupère la liste des livres présents dans la wishlist d'un utilisateur.
    Renvoie uniquement les ID des livres.
    """
    bddservice.initialize_connection()
    query = f"""
        SELECT book_id
        FROM library.WishListe
        WHERE user_id = {user_id};
    """

    books = bddservice.cmd_sql(query)


    if books is None or len(books) == 0:
        raise HTTPException(status_code=404, detail="Aucun livre trouvé dans la wishlist")

    return [book[0] for book in books]


@router.delete("/wishlist/remove/{book_id}/{user_id}")
def remove_from_wishlist(book_id: int, user_id: int):
    """
    Supprime un livre de la wishlist d'un utilisateur.
    """
    query = """
        DELETE FROM library.WishListe WHERE user_id = %s AND book_id = %s;
    """
    bddservice.initialize_connection()
    bddservice.cmd_sql(query, (user_id, book_id))
    return {"message": "Livre retiré de la wishlist"}

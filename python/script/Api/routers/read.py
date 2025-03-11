from fastapi import APIRouter, HTTPException
from typing import List
from services.servicebdd import bddservice


router = APIRouter()


@router.get("/{id_user}")
def book_read(id_user:int):
    """
    Endpoint pour récupérer les livres lus par un utilisateur.

    Cette fonction prend en paramètre l'identifiant de l'utilisateur (id_user) et renvoie
    la liste des livres lus par cet utilisateur.

    Args:
        id_user (int): L'identifiant de l'utilisateur.

    Returns:
        list: La liste des livres lus par l'utilisateur.
    """
    bddservice.initialize_connection()
    query = f"""
    SELECT book_id FROM library.User_Book_Read WHERE user_id = {id_user} AND is_read = TRUE
    """
    result = bddservice.cmd_sql(query)
    return result

@router.post("/{id_user}/{id_book}")
def add_book_read(id_user:int , id_book:int):
    """
    Endpoint pour marquer un livre comme lu par un utilisateur.

    Cette fonction prend en paramètre l'identifiant de l'utilisateur (id_user) et l'identifiant
    du livre (id_book) et marque le livre comme lu par l'utilisateur. Si le livre est déjà marqué
    comme lu, une exception HTTP 400 est levée.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        id_book (int): L'identifiant du livre.

    Returns:
        dict: Un message de confirmation.
    """
    bddservice.initialize_connection()
    query = f"""
    INSERT INTO library.User_Book_Read (user_id, book_id, is_read, is_liked, is_favorite, reading_date, notation_id)
    VALUES ({id_user}, {id_book}, TRUE, FALSE, FALSE, CURRENT_DATE, NULL)

    """
    bddservice.cmd_sql(query)
    return {"message": "Book marked as read."}

@router.delete("/{id_user}/{id_book}")
def delete_book_read(id_user:int , id_book:int):
    """
    Endpoint pour supprimer un livre lu par un utilisateur.

    Cette fonction prend en paramètre l'identifiant de l'utilisateur (id_user) et l'identifiant
    du livre (id_book) et supprime le livre de la liste des livres lus par l'utilisateur.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        id_book (int): L'identifiant du livre.

    Returns:
        dict: Un message de confirmation.
    """
    bddservice.initialize_connection()
    query = f"""
    DELETE FROM library.User_Book_Read WHERE user_id = {id_user} AND book_id = {id_book}
    """
    bddservice.cmd_sql(query)
    return {"message": "Book removed from read list."}

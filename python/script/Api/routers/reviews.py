from fastapi import APIRouter, HTTPException
from typing import List
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride, decodeur


router = APIRouter()


@router.post("/{id_user}/{id_book}")
def book_is_read(id_user:int , id_book:int):
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
    query = f"""
    INSERT INTO library.User_Book_Read (user_id, book_id, is_read, is_liked, is_favorite, reading_date, notation_id)
    VALUES ({id_user}, {id_book}, TRUE, FALSE, FALSE, CURRENT_DATE, NULL)

    """
    bddservice.cmd_sql(query)
    return {"message": "Book marked as read."}


@router.post("/{id_user}/{id_book}/{note}")
def post_review(id_user:int , id_book:int, note:int):
    """
    Endpoint pour ajouter une critique à un livre.

    Cette fonction prend en paramètre l'identifiant de l'utilisateur (id_user), l'identifiant
    du livre (id_book) et le texte de la critique (review). Elle ajoute la critique à la base
    de données. Si une critique existe déjà pour ce livre et cet utilisateur, une exception
    HTTP 400 est levée.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        id_book (int): L'identifiant du livre.
        note (int): La note attribuée au livre.

    Returns:
        dict: Un message de confirmation.
    """
    query = f"""
    INSERT INTO library.User_Book_Notation (note, review_id, read_id)
    VALUES ({note}, NULL, (SELECT read_id FROM library.User_Book_Read WHERE user_id = {id_user} AND book_id = {id_book}))
    """
    bddservice.cmd_sql(query)

    query = f"""
    UPDATE library.User_Book_Read SET notation_id = (SELECT MAX(notation_id) FROM library.User_Book_Notation)
    WHERE user_id = {id_user} AND book_id = {id_book}
    """
    bddservice.cmd_sql(query)

    return {"message": "Review added successfully."}
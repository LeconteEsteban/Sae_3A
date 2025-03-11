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
    bddservice.initialize_connection()
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
    bddservice.initialize_connection()
    query = f"""
    INSERT INTO library.User_Book_Notation (note, review_id, read_id)
    VALUES ({note}, NULL, (SELECT read_id FROM library.User_Book_Read WHERE user_id = {id_user} AND book_id = {id_book}))
    """
    bddservice.cmd_sql(query)

    query = f"""
    UPDATE library.User_Book_Read SET notation_id = (SELECT MAX(notation_id) FROM library.User_Book_Notation)
    WHERE user_id = {id_user} AND book_id = {id_book}
    """
    bddservice.initialize_connection()
    bddservice.cmd_sql(query)

    return {"message": "Review added successfully."}

@router.get("/user/{id_user}/{id_book}")
def get_review_user_book(id_user: int, id_book: int):
    """
    Endpoint pour obtenir la note d'un utilisateur pour un livre.
    """
    query = f"""
    SELECT UBN.note
    FROM library.User_Book_Read UBR
    JOIN library.User_Book_Notation UBN ON UBR.read_id = UBN.read_id
    WHERE UBR.user_id = {id_user} AND UBR.book_id = {id_book}
    """
    reviews = bddservice.cmd_sql(query)

    if not reviews:
        return {"note": None}
    
    return {"note": reviews[0][0]}


@router.put("/{id_user}/{id_book}/{note}")
def update_review(id_user:int , id_book:int, note:int):
    """
    Endpoint pour mettre à jour la critique d'un utilisateur pour un livre.

    Cette fonction prend en paramètre l'identifiant de l'utilisateur (id_user), l'identifiant
    du livre (id_book) et le texte de la critique (review). Elle met à jour la critique de
    l'utilisateur pour ce livre. Si aucune critique n'est trouvée, une exception HTTP 404 est levée.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        id_book (int): L'identifiant du livre.
        note (int): La note attribuée au livre.

    Returns:
        dict: Un message de confirmation.
    """
    query = f"""
    UPDATE library.User_Book_Notation UBN
    SET note = {note}
    FROM library.User_Book_Read UBR
    WHERE UBR.read_id = UBN.read_id
    AND UBR.user_id = {id_user}
    AND UBR.book_id = {id_book}
    """
    bddservice.cmd_sql(query)

    return {"message": "Review updated successfully."}


@router.delete("/{id_user}/{id_book}")
def delete_review(id_user:int , id_book:int):
    """
    Endpoint pour supprimer la critique d'un utilisateur pour un livre.

    Cette fonction prend en paramètre l'identifiant de l'utilisateur (id_user) et l'identifiant
    du livre (id_book) et supprime la critique de l'utilisateur pour ce livre. Si aucune critique
    n'est trouvée, une exception HTTP 404 est levée.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        id_book (int): L'identifiant du livre.

    Returns:
        dict: Un message de confirmation.
    """
    query = """
    DELETE FROM library.User_Book_Notation 
    USING library.User_Book_Read 
    WHERE library.User_Book_Read.read_id = library.User_Book_Notation.read_id
    AND library.User_Book_Read.user_id = %s
    AND library.User_Book_Read.book_id = %s
    """
    bddservice.cmd_sql(query, (id_user, id_book))
    delete_reads = "DELETE FROM library.User_Book_Read WHERE User_Book_Read.book_id = %s AND User_Book_Read.user_id = %s"
    bddservice.cmd_sql(delete_reads, (id_book, id_user)) 


    return {"message": "Review deleted successfully."}
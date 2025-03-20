from fastapi import APIRouter, HTTPException
from typing import List
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride, decodeur


router = APIRouter()


@router.get("/{id_user}/noted-books")
def get_noted_books(id_user: int):
    """
    Endpoint pour obtenir les livres notés par un utilisateur.

    Args:
        id_user (int): L'identifiant de l'utilisateur.

    Returns:
        list: La liste des livres notés par l'utilisateur.
    """
    query = f"""
    SELECT B.*
    FROM library.User_Book_Notation UBN
    JOIN library.User_Book_Read UBR ON UBN.read_id = UBR.read_id
    JOIN library.Book B ON UBR.book_id = B.book_id
    WHERE UBR.user_id = {id_user}
    """
    books = bddservice.cmd_sql(query)
    return books





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

@router.post("/{id_user}/{id_book}/{note}")
def add_or_update_review(id_user: int, id_book: int, note: int):
    """
    Ajoute ou met à jour la note d'un utilisateur pour un livre.

    - Si une note existe déjà, elle est mise à jour.
    - Sinon, une nouvelle note est ajoutée.

    Args:
        id_user (int): L'ID de l'utilisateur.
        id_book (int): L'ID du livre.
        note (int): La note attribuée.

    Returns:
        dict: Un message de confirmation.
    """
    bddservice.initialize_connection()

    # Vérifier si une note existe déjà pour cet utilisateur et ce livre
    query_check = """
    SELECT UBN.notation_id 
    FROM library.User_Book_Notation UBN
    JOIN library.User_Book_Read UBR ON UBN.read_id = UBR.read_id
    WHERE UBR.user_id = %s AND UBR.book_id = %s
    """
    result = bddservice.select_sql(query_check, (id_user, id_book))

    print(result)


    if result:
        notation_id = result[0][0]
        query_update = """
        UPDATE library.User_Book_Notation 
        SET note = %s
        WHERE notation_id = %s
        """
        bddservice.cmd_sql(query_update, (note, notation_id))
        return {"message": "Note mise à jour avec succès."}
    else:
        query_insert = """
        INSERT INTO library.User_Book_Notation (note, review_id, read_id)
        VALUES (%s, NULL, (SELECT read_id FROM library.User_Book_Read WHERE user_id = %s AND book_id = %s LIMIT 1));
        """
        bddservice.cmd_sql(query_insert, (note, id_user, id_book))

        query_update_read = """
        UPDATE library.User_Book_Read 
        SET notation_id = (SELECT MAX(notation_id) FROM library.User_Book_Notation)
        WHERE user_id = %s AND book_id = %s
        """
        bddservice.cmd_sql(query_update_read, (id_user, id_book))

        return {"message": "Note ajoutée avec succès."}


    


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

    
    delete_reads = " UPDATE library.User_Book_Read SET notation_id = NULL WHERE user_id = %s AND book_id = %s "
    bddservice.cmd_sql(delete_reads, (id_book, id_user)) 


    return {"message": "Review deleted successfully."}
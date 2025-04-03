from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import Optional
from models.schemas import BookResponse, BookRequest
from sqlalchemy.sql import text
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride, decodeur
from psycopg2 import DatabaseError
from datetime import date
import random
import logging




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

@router.get("/genre/{genre_name}", response_model=List[BookResponse])
def get_books_by_genre(genre_name: str, limit: int = Query(30, ge=1, le=100)):
    """
    Endpoint pour obtenir un nombre limité de livres d'un genre spécifique.

    Cette fonction exécute une requête SQL pour récupérer les livres qui appartiennent
    à un genre donné, avec une limite sur le nombre de livres retournés.

    Args:
        genre_name (str): Le nom du genre recherché.
        limit (int): Le nombre maximum de livres à récupérer (par défaut 30, min 1, max 100).

    Returns:
        List[BookResponse]: Une liste de livres correspondant au genre.
    """

    if not genre_name or genre_name.strip() == "":
        raise HTTPException(status_code=400, detail="Le nom du genre ne peut pas être vide.")

    query = """
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
            LEFT JOIN library.wrote w ON b.book_id = w.book_id
            LEFT JOIN library.author a ON w.author_id = a.author_id
            LEFT JOIN library.publisher p ON b.publisher_id = p.publisher_id
            LEFT JOIN library.genre_and_vote Gav ON b.book_id = Gav.book_id
            LEFT JOIN library.genre g ON Gav.genre_id = g.genre_id
            LEFT JOIN library.Award_of_book ba ON b.book_id = ba.book_id
            LEFT JOIN library.award aw ON ba.award_id = aw.award_id
            LEFT JOIN library.rating_book rb ON b.book_id = rb.book_id
            WHERE g.name ILIKE %s
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
        SELECT * FROM book_data
        LIMIT %s;
    """

    try:
        books = bddservice.cmd_sql(query, (genre_name, limit))
        
        if not books:
            raise HTTPException(status_code=404, detail=f"Aucun livre trouvé pour le genre : {genre_name}")

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
    
    except DatabaseError as e:
        logging.error(f"Erreur SQL lors de la récupération des livres par genre {genre_name}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur lors de la récupération des livres.")

    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue est survenue.")




logging.basicConfig(level=logging.DEBUG)


@router.post("/add")
def add_book(book: BookRequest):
    """
    Endpoint pour ajouter un livre dans la base de données.
    """
    try:
        print(f"Initialisation de la connexion à la base de données")
        bddservice.initialize_connection()

        # Vérifier si le livre existe déjà
        check_query = """
        SELECT book_id FROM library.book WHERE title = %s AND isbn = %s
        """
        print(f"Vérification de l'existence du livre : {book.title}, {book.isbn}")
        existing_book = bddservice.cmd_sql(check_query, (book.title, book.isbn))
        if existing_book:
            print(f"Le livre existe déjà : {book.title}, {book.isbn}")
            raise HTTPException(status_code=400, detail="Le livre existe déjà.")

        # Insérer le livre dans la base de données
        insert_book_query = """
            INSERT INTO library.book (title, isbn, isbn13, description, number_of_pages, publisher_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        print(f"Exécution de l'insertion du livre : {book.title}, {book.isbn}")
        # Insère aussi publisher_id si disponible
        bddservice.cmd_sql(insert_book_query, (book.title, book.isbn, book.isbn13, book.description, book.number_of_pages, book.publisher_ids[0] if book.publisher_ids else None))


        # Récupérer l'ID du livre inséré
        select_book_id_query = """
        SELECT book_id FROM library.book WHERE isbn = %s AND title = %s
        """
        print(f"Récupération de l'ID du livre après insertion : {book.title}, {book.isbn}")
        book_id_result = bddservice.cmd_sql(select_book_id_query, (book.isbn, book.title))
        print(book_id_result)

        if not book_id_result or not book_id_result[0]:
            print(f"Erreur lors de la récupération de l'ID du livre : {book.title}")
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'ID du livre.")

        book_id = book_id_result[0][0]
        print(f"Livre inséré avec succès, ID : {book_id}")


        # Ajouter les auteurs
        if book.author_ids:
            print(f"Ajout des auteurs pour le livre ID : {book_id}")
            for author_id in book.author_ids:
                # Vérification de l'existence de l'auteur pour éviter l'ajout de doublons
                check_author_query = """
                SELECT 1 FROM library.wrote WHERE book_id = %s AND author_id = %s
                """
                existing_author = bddservice.cmd_sql(check_author_query, (book_id, author_id))
                if not existing_author:  # Si l'auteur n'est pas déjà lié au livre
                    author_query = """
                    INSERT INTO library.wrote (book_id, author_id)
                    VALUES (%s, %s)
                    """
                    bddservice.cmd_sql(author_query, (book_id, author_id))
                else:
                    print(f"L'auteur ID {author_id} est déjà associé au livre {book_id}")


        # Ajouter les genres
        if book.genre_ids:
            print(f"Ajout des genres pour le livre ID : {book_id}")
            for genre_id in book.genre_ids:
                genre_query = """
                INSERT INTO library.genre_and_vote (book_id, genre_id)
                SELECT %s, genre_id FROM library.genre WHERE genre_id = %s
                """
                bddservice.cmd_sql(genre_query, (book_id, genre_id))

        # Vérification des awards
        if isinstance(book.award_ids, str):
            award_ids = [int(book.award_ids)]  # Convertir en liste d'entiers
        else:
            award_ids = [int(award_id) for award_id in book.award_ids]

        if award_ids:
            print(f"Ajout des awards pour le livre ID : {book_id}")
            for award_id in award_ids:
                award_query = """
                INSERT INTO library.Award_of_book (book_id, award_id)
                SELECT %s, award_id FROM library.award WHERE award_id = %s
                """
                bddservice.cmd_sql(award_query, (book_id, award_id))

        print(f"Livre ajouté avec succès : {book.title}")
        return {
            "book_id": book_id,
            "title": book.title,
            "isbn": book.isbn,
            "message": "Livre ajouté avec succès"
        }

    except Exception as e:
        print(f"Erreur lors de l'ajout du livre: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {str(e)}")






@router.get("/search/{search_term}", response_model=List[BookResponse])
def search_books(search_term: str, limit: int = Query(30, ge=1, le=100)):
    """
    Endpoint pour rechercher des livres en fonction d'un terme dans le titre ou le nom de l'auteur.
    """
    query = """
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
        LEFT JOIN library.wrote w ON b.book_id = w.book_id
        LEFT JOIN library.author a ON w.author_id = a.author_id
        LEFT JOIN library.publisher p ON b.publisher_id = p.publisher_id
        LEFT JOIN library.genre_and_vote Gav ON b.book_id = Gav.book_id
        LEFT JOIN library.genre g ON Gav.genre_id = g.genre_id
        LEFT JOIN library.Award_of_book ba ON b.book_id = ba.book_id
        LEFT JOIN library.award aw ON ba.award_id = aw.award_id
        LEFT JOIN library.rating_book rb ON b.book_id = rb.book_id
        WHERE b.title ILIKE %s OR a.name ILIKE %s
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
        LIMIT %s;
    """
    search_pattern = f"%{search_term}%"
    
    try:
        books = bddservice.cmd_sql(query, (search_pattern, search_pattern, limit))
        
        if not books:
            raise HTTPException(status_code=404, detail=f"Aucun livre trouvé pour le terme : {search_term}")

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

    except DatabaseError as e:
        logging.error(f"Erreur SQL lors de la recherche de livres pour le terme {search_term}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur lors de la recherche des livres.")

    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue est survenue.")

@router.get("/{id_book}", response_model=BookResponse)
def get_book(id_book: int):
    """
    Endpoint pour obtenir les détails d'un livre spécifique par son ID.
    """

    query = """
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
            LEFT JOIN library.wrote w ON b.book_id = w.book_id
            LEFT JOIN library.author a ON w.author_id = a.author_id
            LEFT JOIN library.publisher p ON b.publisher_id = p.publisher_id
            LEFT JOIN library.genre_and_vote Gav ON b.book_id = Gav.book_id
            LEFT JOIN library.genre g ON Gav.genre_id = g.genre_id
            LEFT JOIN library.Award_of_book ba ON b.book_id = ba.book_id
            LEFT JOIN library.award aw ON ba.award_id = aw.award_id
            LEFT JOIN library.rating_book rb ON b.book_id = rb.book_id
            WHERE b.book_id = %s
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

    try:
        books = bddservice.cmd_sql(query, (id_book,))

        if not books:
            raise HTTPException(status_code=404, detail=f"Aucun livre trouvé avec l'ID : {id_book}")

        book = books[0]  # Un seul livre retourné

        return {
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

    except DatabaseError as e:
        logging.error(f"Erreur SQL lors de la récupération du livre {id_book}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur lors de la récupération du livre.")

    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue est survenue.")


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

    MAX_ATTEMPTS = 4
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        bddservice.initialize_connection()
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
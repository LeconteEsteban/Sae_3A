from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import Optional
from models.schemas import  SeriesReponse
from services.servicebdd import bddservice




router = APIRouter()


@router.get("/all", response_model=List[SeriesReponse])
def get_all_series():
    """
    Endpoint pour obtenir toutes les séries de la base de données.

    Cette fonction exécute une requête SQL pour récupérer toutes les séries avec les livres
    associés. Si aucune série n'est trouvée, une exception HTTP 404 est levée.

    Returns:
        List[SeriesReponse]: Une liste de toutes les séries avec leurs livres associés.
    """

    query = """SELECT
    Serie.serie_id,
    Serie.name,
    ARRAY_AGG(DISTINCT (book.book_id)) AS BooksInSeries
        FROM
            library.Serie
        LEFT JOIN library.serie_of_book ON serie_of_book.serie_id = Serie.serie_id
        LEFT JOIN library.book ON book.book_id = serie_of_book.book_id
        GROUP BY
            Serie.serie_id, Serie.name;

                """
    bddservice.initialize_connection()
    series = bddservice.cmd_sql(query)

    

    if not series:
        raise HTTPException(status_code=404, detail="No series found in the database")

    series_data = [
        {
        "id": serie[0],
        "name": serie[1],
        "BooksSeries": serie[2]
        }
        for serie in series
    ]

    return series_data

@router.get("/{id_serie}", response_model=List[SeriesReponse])
def get_serie(id_serie: int):
    """
    Endpoint pour obtenir les informations d'une série donnée.

    Cette fonction prend en paramètre l'identifiant d'une série (id_serie) et exécute une
    requête SQL pour récupérer les informations de la série ainsi que les livres associés.
    Si la série n'est pas trouvée, une exception HTTP 404 est levée.

    Args:
        id_serie (int): L'identifiant de la série.

    Returns:
        List[SeriesReponse]: Les informations de la série avec les livres associés.
    """

    query = f"""SELECT
    Serie.serie_id,
    Serie.name,
    ARRAY_AGG(DISTINCT (book.book_id)) AS BooksInSeries
        FROM
            library.Serie
        LEFT JOIN library.serie_of_book ON serie_of_book.serie_id = Serie.serie_id
        LEFT JOIN library.book ON book.book_id = serie_of_book.book_id
        WHERE Serie.serie_id = {id_serie}
        GROUP BY
            Serie.serie_id, Serie.name;

                """
    bddservice.initialize_connection()
    series = bddservice.cmd_sql(query)
    if not series:
        raise HTTPException(status_code=404, detail="No series found in the database")
    
    series_data = [
        {
        "id": serie[0],
        "name": serie[1],
        "BooksSeries": serie[2]
        }
        for serie in series
    ]

    return series_data
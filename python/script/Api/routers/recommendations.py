from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import RecommendationReponse
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride
import random
router = APIRouter()

# Fonction utilitaire pour récupérer les genres d'un livre
def get_book_genres(book_id: int) -> List[str]:
    """
    Récupère les genres associés à un livre donné.

    Cette fonction exécute une requête SQL pour récupérer les genres associés à un livre
    en utilisant son identifiant (book_id). Elle retourne une liste de noms de genres.

    Args:
        book_id (int): L'identifiant du livre.

    Returns:
        List[str]: Une liste de noms de genres associés au livre.
    """
    query = f"""
    SELECT g.name
    FROM library.book b
    INNER JOIN library.Genre_and_vote gv ON b.book_id = gv.book_id
    INNER JOIN library.Genre g ON gv.genre_id = g.genre_id
    WHERE b.book_id = {book_id}
    """
    book_genres = bddservice.cmd_sql(query)
    return [genre[0] for genre in book_genres]

@router.get("/user/{id_user}/{nbook}", response_model=List[RecommendationReponse])
def get_recommendations(id_user: int, nbook: int):
    """
    Endpoint pour obtenir des recommandations pour un utilisateur.

    Cette fonction prend en paramètre l'identifiant d'un utilisateur (id_user) et le nombre
    de recommandations souhaitées (nbook). Elle utilise un service de recommandation hybride
    pour obtenir des recommandations personnalisées pour l'utilisateur. Si aucune recommandation
    n'est trouvée, une exception HTTP 404 est levée.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        nbook (int): Le nombre de recommandations souhaitées.

    Returns:
        List[RecommendationReponse]: Une liste de recommandations de livres pour l'utilisateur.
    """
    recommandations = recommendation_hybride.recommandation_hybride(id_user, nbook)
    if not recommandations:
        raise HTTPException(status_code=404, detail="No recommendations found for the given user")

    return [
        {"id": rec[0], "title": rec[1][0][0][0], "genres": get_book_genres(rec[0])}
        for rec in recommandations
    ]

@router.get("/book/{id_book}/{nbook}", response_model=List[RecommendationReponse])
def get_book_recommendations(id_book: int, nbook: int):
    """
    Endpoint pour obtenir des recommandations de livres similaires.

    Cette fonction prend en paramètre l'identifiant d'un livre (id_book) et le nombre
    de recommandations souhaitées (nbook). Elle utilise un service de recommandation pour
    obtenir des livres similaires au livre donné. Si aucun livre similaire n'est trouvé,
    une exception HTTP 404 est levée.

    Args:
        id_book (int): L'identifiant du livre.
        nbook (int): Le nombre de recommandations souhaitées.

    Returns:
        List[RecommendationReponse]: Une liste de livres similaires au livre donné.
    """
    similar_books = recommendation_service.get_similar_books(id_book, nbook)
    if not similar_books:
        raise HTTPException(status_code=404, detail="No similar books found for the given book ID")

    return [
        {"id": book[0], "title": book[1], "genres": get_book_genres(book[0])}
        for book in similar_books
    ]

@router.get("/user/book/{id_user}/{nbook}", response_model=List[RecommendationReponse])
def get_book_recommendations_user(id_user: int, nbook: int):
    """
    Endpoint pour obtenir des recommandations de livres pour un utilisateur.

    Cette fonction prend en paramètre l'identifiant d'un utilisateur (id_user) et le nombre
    de recommandations souhaitées (nbook). Elle utilise un service de recommandation pour
    obtenir des recommandations de livres pour l'utilisateur. Si aucune recommandation
    n'est trouvée, une exception HTTP 404 est levée.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        nbook (int): Le nombre de recommandations souhaitées.

    Returns:
        List[RecommendationReponse]: Une liste de recommandations de livres pour l'utilisateur.
    """
    recommend_books_for_user = recommendation_service.recommend_books_for_user(id_user, nbook)
    if not recommend_books_for_user:
        raise HTTPException(status_code=404, detail="No recommendations found for the given user")

    return [
        {"id": book[0], "title": book[1][0], "genres": get_book_genres(book[0])}
        for book in recommend_books_for_user
    ]


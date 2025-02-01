import sys
from pathlib import Path

# Ajouter le chemin parent au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

from service.DatabaseService import DatabaseService
from service.CSVService import CSVService
from service.EmbeddingService import EmbeddingService
from service.RecommandationService import RecommendationService
from service.RecomandationHybride import RecomandationHybride

class RecommendationResponse(BaseModel):
    """
    Modèle de réponse pour les recommandations.

    Attributes:
        id (int): Identifiant de la recommandation.
        title (str): Titre de la recommandation.
        genres (List[str]): Liste des genres associés à la recommandation.
    """
    id: int
    title: str
    genres: List[str]

# Ajouter le chemin parent au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Initialisation des services
bddservice = DatabaseService()
csv_service = CSVService()
embservice = EmbeddingService()
bddservice.initialize_connection()
recommendation_service = RecommendationService(bddservice, csv_service, embservice)
recommendation_hybride = RecomandationHybride(bddservice, csv_service, embservice, recommendation_service)

# Fonction utilitaire pour récupérer les genres d'un livre
def get_book_genres(book_id: int, bddservice: DatabaseService) -> List[str]:
    """
    Récupère les genres associés à un livre donné.

    Args:
        book_id (int): Identifiant du livre.
        bddservice (DatabaseService): Instance du service de base de données.

    Returns:
        List[str]: Liste des genres associés au livre.
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

# Création de l'application FastAPI
app = FastAPI()

# Monter le dossier des fichiers statiques (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="../../frontend/public"), name="static")

@app.get("/")
def home():
    return FileResponse("../../frontend/public/index.html")



@app.get("/recommandation/user/{id_user}/{nbook}", response_model=List[RecommendationResponse])
def get_recommendations(id_user: int, nbook: int):
    """
    Endpoint pour obtenir des recommandations pour un utilisateur.

    Args:
        id_user (int): Identifiant de l'utilisateur.
        nbook (int): Nombre de recommandations souhaitées.

    Returns:
        List[RecommendationResponse]: Liste des recommandations pour l'utilisateur.

    Raises:
        HTTPException: Si aucune recommandation n'est trouvée pour l'utilisateur.
    """
    # Appeler la fonction de recommandation
    recommandations = recommendation_hybride.recommandation_hybride(id_user, nbook)

    if not recommandations:
        raise HTTPException(status_code=404, detail="No recommendations found for the given user")

    # Extraire uniquement les champs souhaités
    filtered_recommendations = []
    for rec in recommandations:
        rec_id = rec[0]  # ID de la recommandation
        rec_data = rec[1]  # Liste contenant les titres et genres
        rec_title = rec_data[0][0][0]  # Le premier titre
        rec_genres = get_book_genres(rec_id, bddservice)  # Utiliser la fonction utilitaire
        filtered_recommendations.append({
            "id": rec_id,
            "title": rec_title,
            "genres": rec_genres
        })

    return filtered_recommendations

@app.get("/recommandation/book/{id_book}/{nbook}", response_model=List[RecommendationResponse])
def get_book_recommendations(id_book: int, nbook: int):
    """
    Endpoint pour obtenir des recommandations de livres similaires.

    Args:
        id_book (int): Identifiant du livre.
        nbook (int): Nombre de recommandations souhaitées.

    Returns:
        List[RecommendationResponse]: Liste des livres similaires.

    Raises:
        HTTPException: Si aucun livre similaire n'est trouvé pour l'identifiant du livre donné.
    """
    # Appeler la fonction de recommandation
    similar_books = recommendation_service.get_similar_books(id_book, nbook)

    if not similar_books:
        raise HTTPException(status_code=404, detail="No similar books found for the given book ID")

    # Formater les données pour répondre au modèle RecommendationResponse
    formatted_recommendations = []
    for book in similar_books:
        book_id, book_title, _ = book  # Nous utilisons uniquement l'ID et le titre pour l'instant
        book_genres = get_book_genres(book_id, bddservice)  # Utiliser la fonction utilitaire

        formatted_recommendations.append({
            "id": book_id,
            "title": book_title,
            "genres": book_genres
        })

    return formatted_recommendations

@app.get("/recommandation/user/book/{id_user}/{nbook}", response_model=List[RecommendationResponse])
def get_book_recommendations_user(id_user: int, nbook: int):
    """
    Endpoint pour obtenir des recommandations de livres pour un utilisateur.

    Args:
        id_user (int): Identifiant de l'utilisateur.
        nbook (int): Nombre de recommandations souhaitées.

    Returns:
        List[RecommendationResponse]: Liste des recommandations de livres pour l'utilisateur.

    Raises:
        HTTPException: Si aucune recommandation n'est trouvée pour l'utilisateur.
    """
    # Récupérer les recommandations pour l'utilisateur
    recommend_books_for_user = recommendation_service.recommend_books_for_user(id_user, nbook)
    print(f"Recommendations for user {id_user}: {recommend_books_for_user}")  # Debugging

    if not recommend_books_for_user:
        raise HTTPException(status_code=404, detail="No recommendations found for the given user")

    # Formater les données pour répondre au modèle RecommendationResponse
    formatted_recommendations = []
    for book in recommend_books_for_user:
        # Déstructuration correcte
        book_id = book[0]
        book_title = book[1][0]  # Titre du livre
        book_genres = get_book_genres(book_id, bddservice)  # Utiliser la fonction utilitaire
        print(f"Genres for book {book_id}: {book_genres}")  # Debugging

        # Ajouter les données formatées à la réponse
        formatted_recommendations.append({
            "id": book_id,
            "title": book_title,
            "genres": book_genres
        })

    return formatted_recommendations

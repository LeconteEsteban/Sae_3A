import sys
from pathlib import Path

# Ajouter le chemin parent au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))



from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from service.DatabaseService import DatabaseService
from service.CSVService import CSVService
from service.EmbeddingService import EmbeddingService
from service.RecommandationService import RecommendationService
from service.RecomandationHybride import RecomandationHybride

class RecommendationResponse(BaseModel):
    id: int
    title: str
    genres: List[str]

# Initialisation des services
bddservice = DatabaseService()
csv_service = CSVService()
embservice = EmbeddingService()
bddservice.initialize_connection()
recommendation_service = RecommendationService(bddservice, csv_service, embservice)
recommendation_hybride = RecomandationHybride(bddservice, csv_service, embservice, recommendation_service)

# Création de l'application FastAPI
app = FastAPI()

@app.get("/", response_model=dict)
def root():
    return {"message": "c'est la api hinhihnhin"}
@app.get("/recomandation/{book_id}/{nbook}", response_model=List[RecommendationResponse])
def get_recommendations(book_id: int, nbook: int):
    # Appeler la fonction de recommandation
    recommandations = recommendation_hybride.recommandation_hybride(book_id, nbook)

    # Extraire uniquement les champs souhaités
    filtered_recommendations = []
    for rec in recommandations:
        rec_id = rec[0]  # ID de la recommandation
        rec_data = rec[1]  # Liste contenant les titres et genres
        rec_title = rec_data[0][0][0]  # Le premier titre
        rec_genres = [genre[1] for genre in rec_data[0]]  # Extraire tous les genres
        filtered_recommendations.append({
            "id": rec_id,
            "title": rec_title,
            "genres": rec_genres
        })

    return filtered_recommendations


@app.get("/book/recomandation/{book_id}/{nbook}", response_model=List[RecommendationResponse])
def get_recommendations_book(book_id: int, nbook: int):
    try:
        # Appeler la fonction de recommandation
        recommandations = recommendation_service.get_similar_books(book_id, nbook)

        # Vérifier si les recommandations sont vides
        if not recommandations:
            raise HTTPException(status_code=404, detail="No recommendations found")

        return recommandations
    except Exception as e:
        # Log the exception
        print(f"Error in get_recommendations_book: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

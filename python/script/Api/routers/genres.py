from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import Optional
from models.schemas import GenreResponse
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride, decodeur
from datetime import date
import random



router = APIRouter()


@router.get("/all", response_model=List[GenreResponse])
def get_all_genres():
    """
    Endpoint pour obtenir tous les genres de la base de données.

    Cette fonction exécute une requête SQL pour récupérer tous les genres.
    Si aucun genre n'est trouvé, une exception HTTP 404 est levée.

    Returns:
        List[GenreResponse]: Une liste de genres.
    
    """
    query = f"""
    SELECT *
    FROM library.Genre ;
    """
    genres = bddservice.cmd_sql(query)
    if not genres:
        raise HTTPException(status_code=404, detail="No genres found in the database")

    return [
        {
            "id": genre[0],
            "name": genre[1]
        }
        for genre in genres
    ]

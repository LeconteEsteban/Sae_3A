from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import AwardResponse
from services.servicebdd import bddservice

router = APIRouter()

@router.get("/all", response_model=List[AwardResponse])
def get_all_awards():
    """
    Endpoint pour obtenir tous les awards de la base de données.

    Returns:
        List[AwardResponse]: Une liste des awards.
    """
    query = """
    SELECT award_id, name
    FROM library.award;
    """
    awards = bddservice.cmd_sql(query)

    if not awards:
        raise HTTPException(status_code=404, detail="No awards found in the database")

    return [
        {
            "id": award[0],
            "name": award[1]
        }
        for award in awards
    ]

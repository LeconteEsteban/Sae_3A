from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import PublisherResponse
from services.servicebdd import bddservice

router = APIRouter()

@router.get("/all", response_model=List[PublisherResponse])
def get_all_publishers():
    """
    Endpoint pour obtenir tous les publishers de la base de données.

    Returns:
        List[PublisherResponse]: Une liste des publishers.
    """
    query = """
    SELECT publisher_id, name
    FROM library.publisher;
    """
    publishers = bddservice.cmd_sql(query)

    if not publishers:
        raise HTTPException(status_code=404, detail="No publishers found in the database")

    return [
        {
            "id": publisher[0],
            "name": publisher[1]
        }
        for publisher in publishers
    ]

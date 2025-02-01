from fastapi import APIRouter, HTTPException
from typing import List

from pydantic import BaseModel
from models.schemas import RecommendationReponse
from service.DatabaseService import *

router = APIRouter()

# Modèle Pydantic pour la création d'un utilisateur
class UserCreate(BaseModel):
    username: str
    password: str
    age: int
    child: bool
    familial_situation: str
    gender: str
    cat_socio_pro: str
    lieu_habitation: str
    frequency: int
    book_size: int
    birth_date: str

# Modèle pour la connexion
class UserLogin(BaseModel):
    username: str
    password: str

bddservice = DatabaseService()

# Route pour créer un nouvel utilisateur
@router.post("/api/register")
def register(user: UserCreate):
    try:
        bddservice.initialize_connection()
        new_user = bddservice.create_user(user.dict())  # Conversion en dict
        bddservice.close_connection()
        return {"message": "Utilisateur créé avec succès", "userId": new_user["user_id"]}
    except Exception as e:
        bddservice.close_connection()
        print(e)
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'utilisateur")

# Route pour se connecter
@router.post("/api/login")
def login(user: UserLogin):
    try:
        bddservice.initialize_connection()
        authenticated_user = bddservice.authenticate_user(user.username, user.password)
        bddservice.close_connection()
        if authenticated_user:
            return {
                "message": "Connexion réussie",
                "user": {
                    "user_id": authenticated_user[0],
                    "name": authenticated_user[1]
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Nom ou mot de passe incorrect")
    except Exception as e:
        bddservice.close_connection()
        print(e)
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")
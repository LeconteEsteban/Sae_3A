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
    age: str
    child: bool
    familial_situation: str
    gender: str
    cat_socio_pro: str
    lieu_habitation: str
    frequency: str
    book_size: str
    birth_date: str

# Modèle pour la connexion
class UserLogin(BaseModel):
    username: str
    password: str

bddservice = DatabaseService()

@router.post("/api/register")
def register(user: UserCreate):
    try:
        bddservice.initialize_connection()
        new_user = bddservice.create_user(user.model_dump())
        return {"message": "Utilisateur créé avec succès", "userId": new_user[0]}
    
    except HTTPException as http_exc:
        raise http_exc  
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'utilisateur: {str(e)}")
    
    finally:
        bddservice.close_connection()

# Route pour se connecter
@router.post("/api/login")
def login(user: UserLogin):
    try:
        bddservice.initialize_connection()
        authenticated_user = bddservice.authenticate_user(user.username, user.password)
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
        print(e)
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")
    finally:
        bddservice.close_connection()
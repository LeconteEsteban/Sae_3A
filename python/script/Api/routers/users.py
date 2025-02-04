from fastapi import APIRouter, HTTPException
from typing import List

from pydantic import BaseModel
from models.schemas import UserCreate, UserLogin
from services.servicebdd import bddservice

router = APIRouter()



@router.post("/api/register")
def register(user: UserCreate):
    """
    Endpoint pour enregistrer un nouvel utilisateur.

    Cette fonction prend en paramètre un objet `UserCreate` contenant les informations
    nécessaires pour créer un nouvel utilisateur. Elle initialise une connexion à la base
    de données, crée l'utilisateur, et retourne un message de succès avec l'identifiant
    de l'utilisateur créé. Si une erreur survient, une exception HTTP est levée.

    Args:
        user (UserCreate): Les informations de l'utilisateur à créer.

    Returns:
        dict: Un message de succès avec l'identifiant de l'utilisateur créé.

    Raises:
        HTTPException: En cas d'erreur lors de la création de l'utilisateur.
    """
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
    """
    Endpoint pour authentifier un utilisateur.

    Cette fonction prend en paramètre un objet `UserLogin` contenant le nom d'utilisateur
    et le mot de passe. Elle initialise une connexion à la base de données, vérifie les
    informations d'identification, et retourne un message de succès avec les informations
    de l'utilisateur authentifié. Si les informations d'identification sont incorrectes
    ou si une erreur survient, une exception HTTP est levée.

    Args:
        user (UserLogin): Les informations d'identification de l'utilisateur.

    Returns:
        dict: Un message de succès avec les informations de l'utilisateur authentifié.

    Raises:
        HTTPException: En cas d'erreur lors de l'authentification de l'utilisateur.
    """
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
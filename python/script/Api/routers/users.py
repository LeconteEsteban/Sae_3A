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
        if authenticated_user and authenticated_user[12] == "user": 
            return {
                "message": "Connexion réussie",
                "user": {
                    "user_id": authenticated_user[0],
                    "name": authenticated_user[1],
                    "role": authenticated_user[12],
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Nom ou mot de passe incorrect")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")

@router.post("/api/admin/login")
def admin_login(user: UserLogin):
    """
    Endpoint pour authentifier un administrateur.

    Args:
        user (UserLogin): Les informations de connexion de l'administrateur.

    Returns:
        dict: Un message de succès avec les informations de l'administrateur authentifié.

    Raises:
        HTTPException: Si l'utilisateur n'est pas admin ou si les identifiants sont incorrects.
    """
    try:
        bddservice.initialize_connection()
        authenticated_user = bddservice.authenticate_user(user.username, user.password)

        if authenticated_user and authenticated_user[12] == "admin": 
            return {
                "message": "Connexion admin réussie",
                "user": {
                    "user_id": authenticated_user[0],
                    "name": authenticated_user[1],
                    "role": authenticated_user[12],
                }
            }
        else:
            raise HTTPException(status_code=403, detail="Accès refusé : droits administrateur requis")

    except Exception as e:
        print(f"Erreur lors de la connexion admin: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion admin")



@router.get("/api/user/{user_id}")
def get_user_info(user_id: int):
    try:
        user_data = bddservice.get_user_by_id(user_id)

        if not user_data:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")

        return {
            "user_id": user_data[0],
            "name": user_data[1],
            "age": user_data[2],
            "child": user_data[3],
            "familial_situation": user_data[4],
            "gender": user_data[5],
            "cat_socio_pro": user_data[6],
            "lieu_habitation": user_data[7],
            "frequency": user_data[8],
            "book_size": user_data[9],
            "birth_date": user_data[10],
        }

    except Exception as e:
        print(f"Erreur API get_user_info: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'utilisateur")
    
@router.get("/api/users")
def get_user_ids():
    try:
        user_ids = bddservice.get_all_user_ids()

        if not user_ids:
            raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé")

        return {"user_ids": user_ids}

    except Exception as e:
        print(f"Erreur API get_user_ids: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des IDs utilisateurs")

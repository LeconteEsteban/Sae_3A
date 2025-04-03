from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from typing import List, Dict, Union
from models.schemas import BookResponse
from sqlalchemy.sql import text
from services.servicebdd import bddservice, recommendation_service, recommendation_hybride, decodeur
from psycopg2 import DatabaseError
from datetime import date
import random
import logging
import requests
from collections import defaultdict

BASE_URL = "http://145.239.177.192:1000"
API_USERS_URL = f"{BASE_URL}/api/users"
API_RECOMMENDATION_URL = f"{BASE_URL}/recommandations/item"
API_WISHLIST_URL = f"{BASE_URL}/wishlist"
API_RECOMMENDATION_HYBRID_URL = f"{BASE_URL}/recommandations/hybrid"
    
router = APIRouter()


@router.get("/book")
def get_book_reco():
    """
    Récupère les livres recommandés et calcule leur pondération ajustée.
    """
    try:
        user_response = requests.get(API_USERS_URL)
        user_response.raise_for_status()
        user_ids = user_response.json().get("user_ids", [])

        if not user_ids:
            raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé.")

        book_counts = defaultdict(int)
        book_details = {}
        genre_counts = defaultdict(int)

        for user_id in user_ids:
            try:
                books = []

                reco_response = requests.get(f"{API_RECOMMENDATION_URL}/{user_id}/30")
                reco_response.raise_for_status()
                books.extend(reco_response.json())

                
                try:
                    hybrid_response = requests.get(f"{API_RECOMMENDATION_HYBRID_URL}/{user_id}/30")
                    hybrid_response.raise_for_status()
                    if hybrid_response.status_code == 200:
                        books.extend(hybrid_response.json())

                except requests.RequestException:
                    pass 

                wishlist_books = set()
                try:
                    wishlist_response = requests.get(f"{API_WISHLIST_URL}/{user_id}")
                    if wishlist_response.status_code == 200:
                        wishlist_books = set(wishlist_response.json())
                except requests.RequestException:
                    pass 

                for book in books:
                    book_id = book.get("id")
                    if book_id is not None:
                        weight = 2 if book_id in wishlist_books else 1
                        book_counts[book_id] += weight
                        genres = book.get("genre_names", [])
                        rating = book.get("average_rating", 2.5)

                        book_details[book_id] = {
                            "title": book.get("title", "Titre inconnu"),
                            "genres": genres,
                            "rating": rating,
                            "url": book.get("url", "URL inconnu"),
                        }
    
                        for genre in genres:
                            genre_counts[genre] += weight

            except requests.RequestException as e:
                print(f"Erreur pour l'utilisateur {user_id} : {e}")

        # Calcul des proportions des genres
        total_genre_count = sum(genre_counts.values())
        genre_proportions = {
            genre: count / total_genre_count for genre, count in genre_counts.items()
        }

        # Calcul des pondérations ajustées
        book_adjusted_weights = {}

        for book_id, count in book_counts.items():
            genres = book_details[book_id]["genres"]
            rating = book_details[book_id]["rating"]
            adjusted_weight = sum(
                count * (1 / genre_proportions.get(genre, 1)) * (rating if rating is not None else 2.5)
                for genre in genres
            )
            book_adjusted_weights[book_id] = adjusted_weight

        # Formatage des résultats
        book_list = [
            {
                "id": book_id,
                "title": book_details[book_id]["title"],
                "genres": book_details[book_id]["genres"],
                "url": book_details[book_id]["url"],
                "rating": book_details[book_id]["rating"],
                "adjusted_weight": book_adjusted_weights[book_id],
            }
            for book_id in book_adjusted_weights
        ]

        # Tri par ordre décroissant de pondération ajustée
        book_list.sort(key=lambda x: x["adjusted_weight"], reverse=True)

        return {"books": book_list}

    except requests.RequestException as e:
        print(f"Erreur API : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des données")



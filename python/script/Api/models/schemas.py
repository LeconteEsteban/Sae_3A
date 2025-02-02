from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class BookResponse(BaseModel):
    id: int
    title: str
    isbn13: Optional[str] = None
    author_name: Optional[str] = None
    description: Optional[str] = None
    number_of_pages: Optional[int] = None
    publisher_name: Optional[str] = None
    genre_names: Optional[List[Optional[str]]] = None
    award_names: Optional[List[Optional[str]]] = None
    average_rating: Optional[float] = None
    url: Optional[str] = None

class RecommendationReponse(BaseModel):
    id: int
    title: str
    genres: List[str] = []


class AuthorReponse(BaseModel):
    id: int
    name: str
    birth_date: Optional[date] = None
    biography: Optional[str] = None


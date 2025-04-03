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


class BookRequest(BaseModel):
    title: str
    isbn: str
    isbn13: Optional[str] = None
    description: Optional[str] = None
    number_of_pages: Optional[int] = None
    publisher_ids: Optional[List[int]] = [] 
    author_ids: Optional[List[int]] = []
    genre_ids: Optional[List[int]] = []    
    award_ids: Optional[List[int]] = []    



class RecommendationReponse(BaseModel):
    id: int
    title: str
    genres: List[str] = []

class GenreResponse(BaseModel):
    id: int
    name: str

class AuthorReponse(BaseModel):
    id: int
    name: str
    birthplace: Optional[str] = None
    authorRating: Optional[float] = None
    BooksWritten: Optional[List[Optional[int]]] = None

class AuthorRequest(BaseModel):
    name: str
    birthplace: Optional[str] = None


class SeriesReponse(BaseModel):
    id: int
    name: Optional[str] = None
    BooksSeries: Optional[List[Optional[int]]] = None

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

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    name: str
    age: str
    child: bool
    familial_situation: str
    gender: str
    cat_socio_pro: str
    lieu_habitation: str
    frequency: str
    book_size: str
    birth_date: date


class PublisherResponse(BaseModel):
    id: int
    name: str

class AwardResponse(BaseModel):
    id: int
    name: str

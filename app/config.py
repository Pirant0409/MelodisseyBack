from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime
import os
from app.today_singleton import TodaySingleton

#load_dotenv("./app/var.env")  # Load environment variables from a .env file

SECRET_KEY = os.getenv("SECRET_KEY")
API_KEY = os.getenv("TMDB_API_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
HASHED_PWD = os.getenv("ADMIN_PASSWORD")
MULTI_URL = os.getenv("MULTIURL")
DISCOVER_MOVIES_URL = os.getenv("DISCOVERMOVIESURL")
DISCOVER_TV_URL = os.getenv("DISCOVERTVURL")
FIND_MOVIE_URL = os.getenv("FINDMOVIEURL")
FIND_TV_URL = os.getenv("FINDTVURL")
TODAY = TodaySingleton()

class PasswordRequest(BaseModel):
    password: str

class Day(BaseModel):
    ytbid: str
    media: str
    available_date: datetime
    tmdbid: int
    id:int

class Movie(BaseModel):
    tmdbid: int
    original_title: str
    media: str
    overview: str
    actor1: str
    actor2: str
    actor3: str
    collection: str
    release_date: str
    poster_path: str
    director: str

class RoomData(BaseModel):
    tmdbid:int
    media: str
    ytbid: str
    poster_path: str
    original_title: str
    release_date: str
    collection: str
    hint1: str
    hint2: str
    hint3: str
    hint4: str
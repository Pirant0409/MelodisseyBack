from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models, database
from .services import tmdbServices as tmdb
from .utils import cacheUtils, gameUtils
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.auth import verify_admin_token
import os
import jwt

load_dotenv("var.env")

router= APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordRequest(BaseModel):
    password: str

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def read_root():
    return {"detail": "Bienvenue sur mon API FastAPI !"}

@router.get("/days/")
def get_days(db: Session = Depends(get_db)):
    today = datetime.today().date()
    days = db.query(models.Days).filter(models.Days.available_date <= today).all()
    # return only the days' ids
    daysIDS = [day.id for day in days]
    return JSONResponse(daysIDS)

@router.get("/allDays/")
def get_all_days(db: Session = Depends(get_db), token:str=Depends(verify_admin_token)):
    days = db.query(models.Days).all()
    days = [{"id": day.id, 
             "ytbid": day.ytbid,
             "media":day.media,
             "available_date": day.available_date.strftime("%Y-%m-%d"),
             "tmdbid":day.tmdbid} for day in days]
    return JSONResponse(days)

@router.get("/days/{day_id}")
def get_day(day_id: int, db: Session = Depends(get_db)):
    today = datetime.today().date()
    day = db.query(models.Days).filter(models.Days.id == day_id and models.Days.available_date <= today).first()
    if day is None:
        raise HTTPException(status_code=404, detail="Day not found")
    else :
        message = {
            "dayID": day.id,
            "ytbID": day.ytbid,
        }
    return JSONResponse(content=message)

@router.get("/allMovies/")
def get_all_movies(db: Session = Depends(get_db), token:str=Depends(verify_admin_token)):
    movies = db.query(models.Movies).all()
    movies = [{"tmdbid": movie.tmdbid, 
               "original_title": movie.original_title,
               "media": movie.media,
               "overview": movie.overview,
               "actor1": movie.actor1,
               "actor 2": movie.actor2,
               "actor3": movie.actor3,
               "collection": movie.collection,
               "release_date": movie.release_date,
               "poster_path": movie.poster_path,
               "director":movie.director} for movie in movies]
    return JSONResponse(movies)

@router.get("/check/{day_id}/")
def check_answer(day_id: int, db: Session = Depends(get_db), media:str =None, collection:str=None,tmdbid:int=None,hint:int=None):
    today = datetime.today().date()
    param = {"day_id":day_id,
             "media": media,
             "collection": collection,
             "tmdbid":tmdbid,
             "hint":hint
             }
    day = db.query(models.Days).filter(models.Days.id == day_id and models.Days.available_date <= today).first()
    paramResponse = gameUtils.check_param(day,param)
    if paramResponse["isValid"] is False:
        raise HTTPException(status_code=404, detail=paramResponse["detail"])
    else:
        message = gameUtils.message_to_send(day.movie,day_id,param)
    return JSONResponse(content=message)
    
@router.get("/search/{movie}")
def search_movie(movie:str):
    response = cacheUtils.get_from_cache(movie)
    if (response == False):
        response = tmdb.search_movies(movie+"&append_to_response=credits")
        cacheUtils.save_on_cache(movie,response)
    return response

@router.get("/routes/")
def get_routes(db: Session = Depends(get_db)):
    #get ids from all days in the database
    days = db.query(models.Days).all()
    #create a list of the ids
    idsList =[day.id for day in days]
        
    return idsList

@router.get("/stats/{day_id}")
def get_stats(day_id):
    db = database.SessionLocal()
    stats = db.query(models.Stats).filter(models.Stats.day_id == day_id).first()
    if stats is None:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    if stats.total_guesses != 0:
        message = {"first_guess": round(stats.first_guess/stats.total_guesses*100, 1),
                    "second_guess": round(stats.second_guess/stats.total_guesses*100, 1),
                    "third_guess": round(stats.third_guess/stats.total_guesses*100, 1),
                    "fourth_guess": round(stats.fourth_guess/stats.total_guesses*100, 1),
                    "fifth_guess": round(stats.fifth_guess/stats.total_guesses*100, 1),
                    "lost": round(stats.lost/stats.total_guesses*100, 1),
                    "total": stats.total_guesses,
                    "day_id": stats.day_id}
    else:
        message = {"first_guess": 0,
                    "second_guess": 0,
                    "third_guess": 0,
                    "fourth_guess": 0,
                    "fifth_guess": 0,
                    "lost": 0,
                    "total": 0,
                    "day_id": stats.day_id}
    return JSONResponse(message)



@router.get("/random")
def get_random(include_adults:bool=False,include_videos:bool=False,language:str="en-US",page:int=5,primary_release_date_gte:str="1970-01-01",primary_release_date_lte:str="1990-01-01",sort_by:str="popularity.desc",vote_count_gte:int=5000):
    #get all tmdbIds from the database
    db = database.SessionLocal()
    days = db.query(models.Days).all()
    tmdbIds = [day.tmdbid for day in days]
    answer=tmdb.get_random_movie(tmdbIds,include_adults,include_videos,language,page,primary_release_date_gte,primary_release_date_lte,sort_by,vote_count_gte)
    gameUtils.push_media_to_db(answer)
    return JSONResponse(answer)

@router.post("/admin/login")
def admin(request:PasswordRequest):
    HASHED_PWD = os.getenv("ADMIN_PASSWORD")
    if not pwd_context.verify(request.password,HASHED_PWD):
        raise HTTPException(status_code=401, detail="Password incorrect")
    
    token_data = {
        "sub": "admin",
        "exp": datetime.now() + timedelta(minutes=30)
    }

    token = jwt.encode(token_data, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
    return {"detail":"Access granted", "token": token}

@router.get("/admin/protected")
def protected_admin_route(token:str=Depends(verify_admin_token)):
    return {"detail":"Access granted"}



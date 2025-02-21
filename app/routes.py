from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import models, database
from .services import tmdbServices as tmdb
from .utils import cacheUtils, gameUtils
from passlib.context import CryptContext
from app.auth import verify_admin_token
from app.config import SECRET_KEY, ALGORITHM, HASHED_PWD, DBData, PasswordRequest, Day, Movie, RoomData
from app.config import TODAY
import jwt
import json


router= APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    try:
        today = date.today()
        if today != TODAY.get_today():
            gameUtils.delete_old_rooms()
            TODAY.set_today()
        today = datetime.today().date()
        days = db.query(models.Days).filter(models.Days.available_date <= today ).all()
        # return only the days' ids
        daysIDS = [day.id for day in days]
        return JSONResponse(daysIDS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/allDays/")
def get_all_days(db: Session = Depends(get_db), token:str=Depends(verify_admin_token)):
    try:
        days = db.query(models.Days).all()
        days = [{"id": day.id, 
                "ytbid": day.ytbid,
                "media":day.media,
                "available_date": day.available_date.strftime("%Y-%m-%d"),
                "tmdbid":day.tmdbid} for day in days]
        return JSONResponse(days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/days/{day_id}")
def get_day(day_id: int, db: Session = Depends(get_db)):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/allMovies/")
def get_all_movies(db: Session = Depends(get_db), token:str=Depends(verify_admin_token)):
    try:
        movies = db.query(models.Movies).all()
        movies = [{"tmdbid": movie.tmdbid, 
                "original_title": movie.original_title,
                "media": movie.media,
                "overview": movie.overview,
                "actor1": movie.actor1,
                "actor2": movie.actor2,
                "actor3": movie.actor3,
                "collection": movie.collection,
                "release_date": movie.release_date,
                "poster_path": movie.poster_path,
                "director":movie.director} for movie in movies]
        return JSONResponse(movies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/check/{day_id}/")
def check_answer(day_id: int, db: Session = Depends(get_db), media:str =None, collection:str=None,tmdbid:int=None,hint:int=None):
    try:
        today = datetime.today().date()
        param = {"day_id":day_id,
                "media": media,
                "collection": collection,
                "tmdbid":tmdbid,
                "hint":hint
                }
        day = db.query(models.Days).filter(models.Days.id == day_id and models.Days.available_date <= today).first()
        paramResponse = gameUtils.check_param(day,param,"day")
        if paramResponse["isValid"] is False:
            raise HTTPException(status_code=404, detail=paramResponse["detail"])
        else:
            message = gameUtils.message_to_send(day.movie,day_id,param)
        return JSONResponse(content=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/checkRoom/{room_id}/")
def check_room(room_id: str, db: Session = Depends(get_db), media:str =None, collection:str=None,tmdbid:int=None,hint:int=None):
    try:
        room = db.query(models.Rooms).filter(models.Rooms.id == room_id).first()
        param = {"media": media,
                "collection": collection,
                "tmdbid":tmdbid,
                "hint":hint
                }
        paramResponse = gameUtils.check_param(room,param,"room")
        if paramResponse["isValid"] is False:
            raise HTTPException(status_code=404, detail=paramResponse["detail"])
        else:
            message = gameUtils.message_to_send(room,None,param)
        return JSONResponse(content=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/search/{movie}")
def search_movie(movie:str):
    try:
        response = cacheUtils.get_from_cache(movie)
        if (response == False):
            response = tmdb.search_movies(movie+"&append_to_response=credits")
            cacheUtils.save_on_cache(movie,response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/stats/{day_id}")
def get_stats(day_id):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.get("/random")
def get_random(token:str=Depends(verify_admin_token), include_adults:bool=False,include_videos:bool=False,language:str="en-US",page:int=5,primary_release_date_gte:str="1970-01-01",primary_release_date_lte:str="1990-01-01",sort_by:str="popularity.desc",vote_count_gte:int=5000):
    try:
        #get all tmdbIds from the database
        db = database.SessionLocal()
        days = db.query(models.Days).all()
        tmdbIds = [day.tmdbid for day in days]
        answer=tmdb.get_random_movie(tmdbIds,include_adults,include_videos,language,page,primary_release_date_gte,primary_release_date_lte,sort_by,vote_count_gte)
        gameUtils.push_media_to_db(answer)
        return JSONResponse(answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.post("/admin/login")
def admin(request:PasswordRequest):
    try:
        if not pwd_context.verify(request.password,HASHED_PWD):
            raise HTTPException(status_code=401, detail="Password incorrect")
        
        token_data = {
            "sub": "admin",
            "exp": datetime.now() + timedelta(minutes=30)
        }

        token = jwt.encode(token_data, SECRET_KEY, ALGORITHM)
        return {"detail":"Access granted", "token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/admin/protected")
def protected_admin_route(token:str=Depends(verify_admin_token)):
    return {"detail":"Access granted"}

@router.post("/createRoom/")
def createRoom(roomData: RoomData, db: Session = Depends(get_db)):
    try:
        db = database.SessionLocal()
        #Get a list of all ids of private table
        ids = db.query(models.Rooms).all()
        if (len(ids) != 0):
            ids = [room.id for room in ids]
        #Create a new id
        new_id = gameUtils.create_id(ids)
        newRoom = models.Rooms(id=new_id,
                                creation_date=datetime.today().date(),
                                tmdbid=roomData.tmdbid,
                                media=roomData.media,
                                ytbid=roomData.ytbid,
                                poster_path=roomData.poster_path,
                                original_title=roomData.original_title,
                                release_date=roomData.release_date,
                                collection=roomData.collection,
                                hint1=roomData.hint1,
                                hint2=roomData.hint2,
                                hint3=roomData.hint3,
                                hint4=roomData.hint4)
        db.add(newRoom)
        db.commit()
        db.close()
        gameUtils.save_db()
        return {"detail": "Room created", "roomID": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/rooms/")
def get_rooms(token:str=Depends(verify_admin_token), db: Session = Depends(get_db)):
    try:
        rooms = db.query(models.Rooms).all()
        rooms = [room.id for room in rooms]
        return JSONResponse(rooms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/rooms/{room_id}")
def get_room(room_id: str, db: Session = Depends(get_db)):
    try:
        room = db.query(models.Rooms).filter(models.Rooms.id == room_id).first()
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")
        else:
            message = {
                "roomID": room.id,
                "ytbID": room.ytbid,
            }
        return JSONResponse(content=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/days/")
def update_day(day: Day, db: Session = Depends(get_db), token:str=Depends(verify_admin_token)):
    try:
        db = database.SessionLocal()
        day_db = db.query(models.Days).filter(models.Days.id == day.id).first()
        if day_db is None:
            raise HTTPException(status_code=404, detail="Day does not exist")
        print(day_db.available_date)
        day_db.ytbid = day.ytbid
        day_db.media = day.media
        day_db.available_date = day.available_date
        day_db.tmdbid = day.tmdbid
        db.commit()
        db.refresh(day_db)
        db.close()
        gameUtils.save_db()
        return {"detail": "Day updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/movies/")
def update_movie(movie: Movie, db: Session = Depends(get_db), token:str=Depends(verify_admin_token)):
    try:
        db = database.SessionLocal()
        movie_db = db.query(models.Movies).filter(models.Movies.tmdbid == movie.tmdbid and models.Movies.media == movie.media).first()
        if movie_db is None:
            raise HTTPException(status_code=404, detail="Movie does not exist")
        movie_db.original_title = movie.original_title
        movie_db.media = movie.media
        movie_db.overview = movie.overview
        movie_db.actor1 = movie.actor1
        movie_db.actor2 = movie.actor2
        movie_db.actor3 = movie.actor3
        movie_db.collection = movie.collection
        movie_db.release_date = movie.release_date
        movie_db.poster_path = movie.poster_path
        movie_db.director = movie.director
        movie_db.tmdbid = movie.tmdbid
        db.commit()
        db.refresh(movie_db)
        db.close()
        gameUtils.save_db()
        return {"detail": "Movie updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/timer/")
def get_timer():
    try:
        now = datetime.now()
        next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time_remaining = next_day - now
        if(time_remaining.seconds //3600 <10):
            hours= "0"+str(time_remaining.seconds // 3600)
        else:
            hours= str(time_remaining.seconds // 3600)
        if((time_remaining.seconds // 60) % 60 <10):
            minutes= "0"+str((time_remaining.seconds // 60) % 60)
        else:
            minutes= str((time_remaining.seconds // 60) % 60)
        if(time_remaining.seconds % 60 <10):
            seconds= "0"+str(time_remaining.seconds % 60)
        else:
            seconds= str(time_remaining.seconds % 60)
        
        return {"detail":"sucess","hours": hours, "minutes":minutes, "seconds": seconds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
#Route to restore db from received json file
@router.post("/restoreDB/")
def restore_db(file: DBData, token: str = Depends(verify_admin_token)):
    try:
        # Store received json file in a variable
        gameUtils.restore_db(file)
        return {"detail": "DB Restored"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



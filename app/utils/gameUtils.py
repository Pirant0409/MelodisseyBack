import os
from app import database, models
from datetime import datetime, timedelta
import json, random

def is_it_guess(media,tmdbid):
    if media is not None and tmdbid is not None:
        return True
    else:
        return False

def is_guess_right(movie,id,media,collection):
    if movie.tmdbid == id and movie.media == media or movie.collection == collection and collection is not None and movie.media == media:
        return True

def check_param(game, param, room_type):
    response = {"isValid": False, "detail":""}
    isGuess = is_it_guess(param["media"],param["tmdbid"])
    if game is None:
        response["detail"]="Day not found"
    elif room_type == "day" and game.movie is None:
        response["detail"]="Movie not found"
    elif param["media"] is None and param["tmdbid"] is not None:
        response["detail"]= "Missing media parameter"
    elif param ["media"] is not None and param["tmdbid"] is None:
        response["detail"]="Missing tmdbid parameter"
    elif (param["media"] is None and param["tmdbid"] is None) and param["hint"] is None:
        response["detail"] = "Missing media, tmdbid or hint parameter(s)"
    elif isGuess and param["hint"] is None or isGuess and param["hint"] > 4:
        response["detail"]="Missing or invalid hint parameter"
    else:
        response["isValid"]=True
    return response

def message_to_send(movie,day_id,param):
    message={}
    isRight = is_guess_right(movie,param["tmdbid"],param["media"],param["collection"])
    if isRight:
        message["original_title"]= movie.original_title
        message["release_date" ]= movie.release_date
        message["poster_path"]= movie.poster_path
        message["media"]= movie.media
        message["isRight"]= True
        if day_id is not None:
            process_stats(day_id,param["hint"],True)
    else:
        match param["hint"]:
            case 0:
                
                message["hint"]= movie.hint1 if hasattr(movie,"hint1") else movie.media
            case 1:
                message["hint"]= movie.hint2 if hasattr(movie,"hint2") else [movie.actor1,movie.actor2,movie.actor3]
            case 2:
                message["hint"]= movie.hint3 if hasattr(movie,"hint3") else movie.director
            case 3:
                message["hint"] = movie.hint4 if hasattr(movie,"hint4") else movie.overview
            case _:
                message["original_title"]= movie.original_title
                message["release_date"]= movie.release_date
                message["poster_path"] =movie.poster_path
                message["media"] = movie.media
                message["isRight"] = False
                if day_id is not None:
                    process_stats(day_id,4,False)
    return message

def process_stats(day_id,hint,is_right):
    db = database.SessionLocal()
    stats = db.query(models.Stats).filter(models.Stats.day_id == day_id).first()
    if stats is None:
        stats = models.Stats(day_id=day_id,first_guess=0,second_guess=0,third_guess=0,fourth_guess=0,fifth_guess=0,lost=0,total_guesses=0)
        db.add(stats)
    if hint == 0:
        stats.first_guess += 1
    elif hint == 1:
        stats.second_guess += 1
    elif hint == 2:
        stats.third_guess += 1
    elif hint == 3:
        stats.fourth_guess += 1
    elif hint == 4 and is_right is True:
        stats.fifth_guess += 1
    elif hint == 4 and is_right is False:
        stats.lost += 1
    stats.total_guesses += 1
    db.commit()
    db.close()
    save_db()

def push_media_to_db(medias,is_it_restore=False):
    db = database.SessionLocal()
    if len(medias)>0:
        for media in medias:
            # check if movie with tmdbid and same media type already exists
            new_movie = {}
            db_movie = db.query(models.Movies).filter(models.Movies.tmdbid == media["tmdbID"], models.Movies.media == media["media"]).first()
            #get last id from days
            if db_movie is None:
                #setup date
                last_day = db.query(models.Days).order_by(models.Days.id.desc()).first()
                last_date = last_day.available_date
                new_last_date = last_date + timedelta(days=1)

                #setup hints
                if media.get("mainCast"):
                    media["actor1"] = media["mainCast"][0] if len(media["mainCast"])>=1 else "No actors"
                    media["actor2"] = media["mainCast"][1] if len(media["mainCast"])>=2 and not media.get("actor2") else "No actors"
                    media["actor3"] = media["mainCast"][2] if len(media["mainCast"])>=3 and not media.get("actor3") else "No actors"
                    del media["mainCast"]

                #rename tmdbID to tmdbid
                media["tmdbid"] = media["tmdbID"]
                del media["tmdbID"]

                #removing movie name and key characters from overview
                new_movie["overview"] = remove_banned_words(media)

                new_movie = models.Movies(**media)
                new_day = models.Days(tmdbid=new_movie.tmdbid,media=new_movie.media,ytbid="No ytbid",available_date=new_last_date)
                new_stats = models.Stats(day_id=last_day.id+1,first_guess=0,second_guess=0,third_guess=0,fourth_guess=0,fifth_guess=0,lost=0,total_guesses=0)
                db.add(new_movie)
                db.add(new_stats)
                db.add(new_day)
                db.commit()
                print(media["original_title"] + " added to database")
        db.close()
        if not is_it_restore:
            save_db()
    else:
        print("No media to push to database")

def remove_banned_words(media):
    #trouver les mots en communs entre titre et collection
    common_words = set(media["original_title"].split()).intersection(set(media["collection"].split()))
    new_overview = media["overview"]
    if len(common_words)>0:
        #if there are articles inside common_words, remove them
        banned_words = ["the","a","an","of","in","on","at","for","to","from","by","with","about","as","into","through","during","before","after","above","below","under","over","between","among","along","around","behind","beneath","beside","beyond","inside","outside","underneath","within","without"]
        common_words = [word for word in common_words if word not in banned_words]
        for word in common_words:
            new_overview = new_overview.replace(word,"______")
    return new_overview

def create_id(idsUnavailable):
    #generate a random string of 5 alphanumerical characters
    isAvailable = False
    while not isAvailable:
        id = ''.join(random.choices("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
        if id not in idsUnavailable:
            isAvailable = True
    return id
#save db in json file
def save_db():
    db = database.SessionLocal()
    days = db.query(models.Days).all()
    stats = db.query(models.Stats).all()
    movies = db.query(models.Movies).all()
    rooms = db.query(models.Rooms).all()
    db.close()
    days_dict = [day.__dict__ for day in days]
    stats_dict = [stat.__dict__ for stat in stats]
    movies_dict = [movie.__dict__ for movie in movies]
    rooms_dict = [room.__dict__ for room in rooms]
    
    # Remove the '_sa_instance_state' key from the dictionaries
    for day in days_dict:
        day["available_date"] = day["available_date"].strftime("%Y-%m-%d")
        day.pop('_sa_instance_state', None)
    for stat in stats_dict:
        stat.pop('_sa_instance_state', None)
    for movie in movies_dict:
        movie.pop('_sa_instance_state', None)
    for room in rooms_dict:
        room["creation_date"] = room["creation_date"].strftime("%Y-%m-%d")
        room.pop('_sa_instance_state', None)
    
    with open("db.json","w") as f:
        json.dump({"days":days_dict,"stats":stats_dict,"movies":movies_dict,"rooms":rooms_dict},f,indent=4)
        print("Database saved in db.json")

#load db from json file
def load_db():
    if "db.json" not in os.listdir():
        print("No database to load")
        return
    else:
        db = database.SessionLocal()
        with open("db.json","r", encoding='utf8') as f:
            data = json.load(f)
            if data.get("days") is not None:
                for day in data["days"]:
                    day["available_date"] = datetime.strptime(day["available_date"],"%Y-%m-%d").date()
                    new_day = models.Days(**day)
                    db.add(new_day)
            if data.get("stats") is not None:
                for stat in data["stats"]:
                    new_stat = models.Stats(**stat)
                    db.add(new_stat)
            if data.get("movies") is not None:
                for movie in data["movies"]:
                    new_movie = models.Movies(**movie)
                    db.add(new_movie)
            if data.get("rooms") is not None:
                for room in data["rooms"]:
                    room["creation_date"] = datetime.strptime(room["creation_date"],"%Y-%m-%d").date()
                    new_room = models.Rooms(**room)
                    db.add(new_room)
            db.commit()
        print("Database loaded from json")
        db.close()

def delete_old_rooms():
    db = database.SessionLocal()
    changes_made = False
    rooms = db.query(models.Rooms).all()
    for room in rooms:
        print(room.creation_date)
        print(datetime.today().date() - timedelta(days=7))
        if room.creation_date <= (datetime.today().date() - timedelta(days=7)):
            print("Old room deleted")
            changes_made = True
            db.delete(room)
            db.commit()
    if changes_made:
        print("Old rooms deleted")
        save_db()
    db.close()

def restore_db(data):
    db = database.SessionLocal()
    clear_db(db)
    # Add the data from the json file
    if hasattr(data, "days") and len(data.days) > 0:
        for day in data.days:
            day["available_date"] = datetime.strptime(day["available_date"], "%Y-%m-%d").date()
            new_day = models.Days(**day)
            db.add(new_day)
    if hasattr(data, "stats") and len(data.stats) > 0:
        for stat in data.stats:
            new_stat = models.Stats(**stat)
            db.add(new_stat)
    if hasattr(data, "movies") and len(data.movies) > 0:
        for movie in data.movies:
            new_movie = models.Movies(**movie)
            db.add(new_movie)
    if hasattr(data, "rooms") and len(data.rooms) > 0:
        for room in data.rooms:
            room["creation_date"] = datetime.strptime(room["creation_date"], "%Y-%m-%d").date()
            new_room = models.Rooms(**room)
            db.add(new_room)
    db.commit()
    save_db()
    db.close()

def clear_db(db):
    db.query(models.Stats).delete()
    db.query(models.Movies).delete()
    db.query(models.Days).delete()
    db.query(models.Rooms).delete()
    db.commit()
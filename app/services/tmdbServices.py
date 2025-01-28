import requests, random
import os
from dotenv import load_dotenv
from app import models

load_dotenv("./app/var.env")

MULTI_URL = os.getenv("MULTIURL")
DISCOVER_MOVIES_URL = os.getenv("DISCOVERMOVIESURL")
DISCOVER_TV_URL = os.getenv("DISCOVERTVURL")
FIND_MOVIE_URL = os.getenv("FINDMOVIEURL")
FIND_TV_URL = os.getenv("FINDTVURL")
API_KEY = os.getenv("TMDB_API_KEY")


headers = {
    "accept": "application/json",
    "Authorization": API_KEY
}


def search_movies(query):
    querriedURL = MULTI_URL+"?query="+query
    response = requests.get(querriedURL, headers=headers)
    return format_movies(response.json())

def format_movies(results):
    formatted_results = []
    max_results = 10
    if results.get("results"):
        only_movies = results["results"]
    else:
        only_movies = [results]
    if len(only_movies)<10:
            max_results = len(only_movies)

    for i in range(max_results):
        movie=only_movies[i]
        if(movie and movie.get("media_type") in ["movie","tv"]):
            details = get_cast_crew_collection(movie["id"],movie["media_type"])
            formattedMovie = setup_data(movie, details)
            formatted_results.append(formattedMovie)
    return formatted_results


def get_cast_crew_collection(id,media):
    querriedURL = "https://api.themoviedb.org/3/"+media+"/"+str(id)+"?append_to_response=credits"
    response = requests.get(querriedURL,headers=headers)
    response = response.json()
    sortedCast = sorted(response["credits"]["cast"], key=lambda x:x["order"], reverse=True)
    directors = [member for member in response["credits"]["crew"] if member["known_for_department"] == "Directing"]
    sortedDirectors = sorted(directors,key=lambda x:x["popularity"], reverse=True)
    director = sortedDirectors[0] if len(sortedDirectors)>0 else {"name":"Unknown"}
    mainCast = sortedCast[:3]
    collection = response["belongs_to_collection"]["name"] if response.get("belongs_to_collection") else "None"
    director = director["name"]
    return {"director":director,
            "mainCast":[member["name"] for member in mainCast],
            "collection":collection}

def setup_data(movie, details):
    formattedMovie = {}
    formattedMovie["tmdbID"] = movie["id"]
    formattedMovie["overview"] = movie["overview"] if movie.get("overview") else "No overview"
    formattedMovie["poster_path"] = "https://image.tmdb.org/t/p/w500"+ movie["poster_path"] if movie.get("poster_path") else ""
    formattedMovie["mainCast"] = details["mainCast"] if details.get("mainCast") else "No main cast"
    formattedMovie["collection"] = details["collection"] if details.get("collection") else "No collection"
    formattedMovie["director"] = details["director"] if details.get("director") else "No director"
    formattedMovie["media"] = movie["media_type"] if movie.get("media_type") else "No media type"

    if movie.get("original_title"):
       formattedMovie["original_title"] = movie["original_title"]
    elif movie.get("name"):
        formattedMovie["original_title"] = movie["name"]
    else:
        formattedMovie["original_title"] = "Unknown"
    if movie.get("release_date"):
       formattedMovie["release_date"] = movie["release_date"]
    elif movie.get("first_air_date"):
        formattedMovie["release_date"] = movie["first_air_date"]
    else:
        formattedMovie["release_date"] = "Unknown"

    return formattedMovie

def get_random_movie(allIDS,include_adults:bool,include_videos:bool,language:str,page:int,release_date_gte:str,release_date_lte:str,sort_by:str,vote_count_gte:int):
    randomMovies = []
    for i in range(page):
        loop_limit = 10
        can_be_added = True 
        urlParams=f'?include_adult{include_adults}&include_video={include_videos}&language={language}&page={i+1}&primary_release_date.gte={release_date_gte}&primary_release_date.lte={release_date_lte}&sort_by={sort_by}&vote_count.gte={vote_count_gte}'
        querriedURL = DISCOVER_MOVIES_URL+urlParams
        while(can_be_added and loop_limit>0):
            print("de")
            response = requests.get(querriedURL,headers=headers)
            response = response.json()
            #sort by popularity from highest to lowest

            print(response)
            if len(response["results"])>0:
                print("i'm in")
                randomNum = random.randint(0,len(response["results"])-1)
                randomMovie= response["results"][randomNum]
                if randomMovie["id"] in allIDS or randomMovie["original_title"] in ["Star Wars", "Back to the Future" ]:
                    loop_limit-=1
                else:
                    can_be_added = False
                    allIDS.append(randomMovie["id"])
                    randomMovie["media_type"]="movie"
                    formatted_random_movie = format_movies(randomMovie)
                    randomMovies.append(formatted_random_movie[0])
            elif len(response["results"]) == 0:
                print("ok c 0")
                can_be_added = False
        if loop_limit == 0:
            print("No more movies to add")        
        
    return(randomMovies)



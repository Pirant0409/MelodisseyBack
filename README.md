# Movie Blind Test API

This project is a **Movie Blind Test** web application backend built with **FastAPI** inspired by [Themely](https://themely.se/days).<br>
It allows players to guess the movie or series from a piece of music each day, with dynamic hints and limited attempts. It includes an admin panel for managing the game, movies, and statistics.<br>
🔗 The frontend repository is available here: [Melodissey's frontend](https://github.com/Pirant0409/Melodissey-front)

## 🚀Features

- 🎶 **Daily blind test Game**: Players are presented with a movie/series soundtrack every day and must guess the movie.
- 🧩 **Progressive Hints** – The more attempts, the more clues
- 👥 **Private Rooms** – Play with friends in custom rooms
- 🔧 **Admin Panel**: Admin users can add, edit, or delete (comming soon) movies and view game statistics.
- 🏆 **Leaderboard**: Track the performance of all players (comming soon).
- 📊 **Statistics**: Track guesses, total guesses, and success/failure for each day.

## 🛠Technologies Used

- **FastAPI**: For building the backend REST API.
- **SQLAlchemy**: ORM for interacting with the database.
- **Pydantic**: For request validation and response models.
- **JWT Authentication**: For securing admin routes.
- **Bcrypt**: For hashing and validating admin passwords.
- **SQLite** (or your chosen DB): For storing movies, guesses, and stats.
- [**TMDB API**](https://developer.themoviedb.org/reference/intro/getting-started) : Getting movies and tv shows' data

## ⚙️Installation

### 1. Prerequisites

Ensure you have **Python 3.7+** installed on your machine.

### 2. Steps

1. Clone the repository:

```bash
git clone https://github.com/Pirant0409/MelodisseyBack.git
cd MelodisseyBack
```
2. Install dependencies in a venv
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Update your environment variables. The app is currently build to fetch them from a var.env file under app folder.
```env
ADMIN_PASSWORD=SOME_BCRYPT_PASSWORD
TMDB_API_KEY=Bearer YOUR_TMDB_API_KEY
SECRET_KEY= YOUR_SERVER_SECRET_KEY
ALGORITHM= SOME_HASHING_ALGORITHM
SQLALCHEMY_DATABASE_URL="sqlite:///./test.db"
MULTIURL=https://api.themoviedb.org/3/search/multi
DISCOVERMOVIESURL=https://api.themoviedb.org/3/discover/movie
DISCOVERTVURL=https://api.themoviedb.org/3/discover/tv
FINDMOVIEURL=https://api.themoviedb.org/3/movie/
FINDTVURL=https://api.themoviedb.org/3/tv/
```
5. Run FastAPI
```bash
uvicorn main:app --reload
```


## 🛣️ Endpoints

### 1. Fetching TMDB API
- **GET** `/search/{movie}` : Fetchs server cache or tmdb API. Returns a list of different movies' data whose english title (partialy)matches the title send.<br>
  Example Response:
  ```json
  [{"tmdbID": 807,
    "overview": "Two homicide detectives are on a desperate hunt for a serial killer whose crimes are based on the \"seven deadly sins\" in this dark and haunting film that takes viewers from the tortured remains of one victim to the next. The seasoned Det. Sommerset researches each sin in an effort to get inside the killer's mind, while his novice partner, Mills, scoffs at his efforts to unravel the case.",
    "poster_path": "https://image.tmdb.org/t/p/w500/191nKfP0ehp3uIvWqgPbFmI4lv9.jpg",
    "mainCast": ["Morgan Freeman","Brad Pitt","Gwyneth Paltrow"],
    "collection": "None",
    "director": "David Fincher",
    "media": "movie",
    "original_title": "Se7en",
    "release_date": "1995-09-22"}]
  ```
  
### 2. Days data
- **GET** `/days/` : Returns a list of all available days' ID.
- **GET** `/days/{day_id}/` : From a day's ID, returns the associated ytbid.<br>
  Example response:
  ```json
  {"dayID":238,
   "ytbID":"Flb01Ni3p3M"}
  ```
- **GET** `/check/{day_id}?media={media}&tmdbid={tmdbID}&collection=${collection}&hint=${hint}/` : Checks if a guess is right. If it is, returns an object with some answers' data. If not, returns a hint.<br>
  If guess is right:
  ```json
  {"isRight": true,
   "original_title": "The Godfather",
   "release_date": "1971-03-14",
   "poster_path": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
   "media": "movie"}
  ```
  If not
  ```json
  {"hint": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American ______ crime family."}
  ```
### 3. Stats
- **GET** `/stats/{day_id}` : Returns stats for the provided day id. (guess stats are expressed in %)
  ```json
  {"first_guess": 25,
   "second_guess": 0,
   "third_guess": 25,
   "fourth_guess": 0,
   "fifth_guess": 25,
   "lost": 25,
   "total": 4,
   "day_id": 1}
  ```

  
### 4. Private room
- **POST** `/createRoom/` : Create a private room with the information given in the headers and returns the roomID.<br>
  Example response:
  ```json
  {"detail": "Room created",
   "roomID": "P7ed3"}
  ```
- **GET** `/rooms/{room_id}/` : From a room's ID, returns the associated ytbid.<br>
  Example response:
  ```json
  {"roomID":"P7ed3",
   "ytbID":"Flb01Ni3p3M"}
  ```
- **GET** `/checkRoom/{room_id}?media={media}&tmdbid={tmdbID}&collection=${collection}&hint=${hint}/` : Similar to third route of [this section](#2-days-data)

  

### 5. Admin protected routes
- **POST** `/admin/login/` : Check if the admin password is correct and returns the JWT token if it is.<br>
  Example response:
  ```json
  {"detauk":"Acces granted",
   "token":"BQDoolbkB18rSSdjZnbcd6ew0yIM8YBRyS-xUB_T7LGtZIBQeHsxbzU6-ugCyOlZFbr1zu_x-fQoqZAL0ab_M6oQ88jQKOSqtny_WuC4pKk6DUOCQ7gQUWxPCtjW-1F2sINlzwuLgODg0vAuer0eSU_cwWM6Tl8bSwvM1TyJmYhosFv0h3-8svcX2SzkZ8OJA7XMbnR2"}
  ```
- **PUT** `/days/` : Updates the day according to the data sent in the headers.
- **PUT** `/movies/` : Updates the movie/tv show according to the data sent in the headers.
- **GET** `/admin/protected/` : Checks if the JWT token provided in the headers
- **GET** `/admin/protected/` : Checks if the JWT token provided in the headers is valid.
- **GET** `/allDays/` : Returns a list of every days object.<br>
  Example response:
  ```json
    [{"tmdbid": 238,
      "id": 1,
      "ytbid": "Flb01Ni3p3M",
      "available_date": "2025-01-15",
      "media": "movie"}]
  ```
- **GET** `/rooms/` : Returns a list of every rooms' id.<br>
  Example response:
  ```json
  ["P7ed3","D1eaf","mced4"]
  ```
- **GET** `/allMovies/` : Returns a list of every shows object.<br>
  Example response:
  ```json
  {"tmdbid": 238,
    "original_title": "The Godfather",
    "media": "movie",
    "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American ______ crime family.",
    "actor1": "Marlon Brando",
    "actor2": "Al Pacino",
    "actor3": "James Caan",
    "collection": "The Godfather Collection",
    "release_date": "1971-03-14",
    "poster_path": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
    "director": "Francis Ford Coppola"}
  ```
- **GET** `/random?pages{pages}&primary_release_date_gte={prdgte}&primary_release_date_lte={prdlte}&vote_count_gte={vote_count_gte}` : Get one random movie matching release dates and vote count filters from page 1 to page {pages} and return them on a list.<br>
  Example response:
  ```json
  {"overview": "In the post-apocalyptic future, reigning tyrannical supercomputers teleport a cyborg assassin known as the \"Terminator\" back to 1984 to kill Sarah Connor, whose unborn son is destined to lead insurgents against 21st century mechanical hegemony. Meanwhile, the human-resistance movement dispatches a lone warrior to safeguard Sarah. Can he stop the virtually indestructible killing machine?",
  "poster_path": "https://image.tmdb.org/t/p/w500/hzXSE66v6KthZ8nPoLZmsi2G05j.jpg",
  "collection": "The Terminator Collection",
  "director": "James Cameron",
  "media": "movie",
  "original_title": "The Terminator",
  "release_date": "1984-10-26",
  "actor1": "Arnold Schwarzenegger",
  "actor2": "Michael Biehn",
  "actor3": "Linda Hamilton",
  "tmdbid": 218}
  ```

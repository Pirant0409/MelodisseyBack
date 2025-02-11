# Movie Blind Test API

This project is a **Movie Blind Test** web application backend built with **FastAPI**. It allows players to guess the movie or series from a piece of music each day, with dynamic hints and limited attempts. It includes an admin panel for managing the game, movies, and statistics.

## Features

- **Movie Guessing Game**: Players are presented with a movie/series soundtrack every day and must guess the movie.
- **Admin Panel**: Admin users can add, edit, or delete movies and view game statistics.
- **Leaderboard**: Track the performance of all players.
- **Statistics**: Track guesses, total guesses, and success/failure for each day.

## Technologies Used

- **FastAPI**: For building the backend REST API.
- **SQLAlchemy**: ORM for interacting with the database.
- **Pydantic**: For request validation and response models.
- **JWT Authentication**: For securing admin routes.
- **Bcrypt**: For hashing and validating admin passwords.
- **SQLite** (or your chosen DB): For storing movies, guesses, and stats.
- [**TMDB API**](https://developer.themoviedb.org/reference/intro/getting-started) : Getting movies and tv shows' data

## Installation

### 1. Prerequisites

Ensure you have **Python 3.7+** installed on your machine.

### 2. Steps

1. Clone the repository:

```bash
git clone <repository-url>
cd <project-directory>
```
2. Install dependencies in a venv
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Run FastAPI
```bash
uvicorn main:app --reload
```

## Endpoints

### 1. Days data
- **GET** `/days/` : Returns a list of all available days' ID.
- **GET** `/days/{day_id}/` : From a day's ID, returns the associated ytbid <br>
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
### 2. Private room
- **GET** `/checkRoom/{room_id}?media={media}&tmdbid={tmdbID}&collection=${collection}&hint=${hint}/` : Similar to [`third route of this section`](1.-days-data)
- 

  
  

### 3. Admin protected routes
- **GET** `/allDays/` : Returns a list of every days object.<br>
  Example response:
  ```json
    [{"tmdbid": 238,
      "id": 1,
      "ytbid": "Flb01Ni3p3M",
      "available_date": "2025-01-15",
      "media": "movie"}]
  ```
- **GET** `/allMovies/` : Returns a list of every shows object.<br>
  Example response:
  ```json
  {"release_date": "1971-03-14",
   "poster_path": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
   "actor2": "Al Pacino",
   "director": "Francis Ford Coppola",
   "original_title": "The Godfather",
   "tmdbid": 238,
   "media": "movie",
   "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American ______ crime family.",
   "actor1": "Marlon Brando",
   "actor3": "James Caan",
   "collection": "The Godfather Collection"}
  ```

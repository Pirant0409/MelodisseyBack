from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app import models, database, routes
import diskcache

    
app = FastAPI()

database.init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200","http://127.0.0.1:4200","https://melodissey.e-kot.be","https://melodissey.e-kot.be/"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization","Accept"]
)

models.Base.metadata.create_all(bind=database.engine)

app.include_router(routes.router)

cache = diskcache.Cache('cache_dir')

cache.size_limit = 2 ** 30  # Limite la taille du cache à 1 Go



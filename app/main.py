from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database, routes
import diskcache

app = FastAPI()

database.init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200","http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

models.Base.metadata.create_all(bind=database.engine)

app.include_router(routes.router)

cache = diskcache.Cache('cache_dir')

cache.size_limit = 2 ** 30  # Limite la taille du cache à 1 Go
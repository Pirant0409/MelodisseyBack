from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from app.utils import gameUtils

import os 

load_dotenv("./app/var.env")
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)  # Crée les tables de la base de données

    # Ajout de données par défaut
    db = SessionLocal()
    try:

        gameUtils.load_db()
    except IntegrityError:
        db.rollback()  # En cas de duplication, annule les changements
    finally:
        db.close()
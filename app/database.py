from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.utils import gameUtils
from app.config import SQLALCHEMY_DATABASE_URL


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
    
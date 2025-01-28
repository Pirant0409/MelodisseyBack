from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Integer,String, Enum, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from datetime import datetime 
from app.enums import MediaType
from app.database import Base

class Days(Base):
    __tablename__ = "days"

    id = Column(Integer, primary_key= True, index = True)
    # use Movies's tmdbid and media as foreign key
    tmdbid = Column(Integer,nullable=False)
    media = Column(Enum(MediaType), nullable=False)
    ytbid = Column(String, nullable=False)
    available_date = Column(Date, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tmdbid", "media"],  # Colonnes locales
            ["movies.tmdbid", "movies.media"]  # Colonnes distantes
        ),
    )

    # Relation avec Movies
    movie = relationship("Movies", back_populates="days")
    stats = relationship("Stats", back_populates="day", uselist=False)

class Stats(Base):
    __tablename__ = "stats"

    day_id = Column(Integer,ForeignKey("days.id"), primary_key=True, nullable=False)
    first_guess = Column(Integer,nullable=True)
    second_guess = Column(Integer,nullable=True)
    third_guess = Column(Integer,nullable=True)
    fourth_guess = Column(Integer,nullable=True)
    fifth_guess = Column(Integer,nullable=True)
    lost = Column(Integer,nullable=True)
    total_guesses = Column(Integer,nullable=True)

    day = relationship("Days", back_populates="stats")
    
class Movies(Base):
    __tablename__ = "movies"
    tmdbid = Column(Integer, nullable=False, primary_key=True)
    media = Column(Enum(MediaType), nullable=False,primary_key=True)
    original_title = Column(String, nullable=False)
    release_date = Column(String, nullable=False)
    overview = Column(String,nullable=False)
    poster_path = Column(String,nullable=False)
    actor1 = Column(String,nullable=False)
    actor2 = Column(String, nullable=True)
    actor3 = Column(String,nullable=True)
    director = Column(String,nullable=False)
    collection = Column(String, nullable=True)

    
    __table_args__ = (UniqueConstraint("tmdbid", "media", name="unique_tmdb_media"),)
    days = relationship("Days", back_populates="movie")


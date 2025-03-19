from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import os

Base = declarative_base()

# Many-to-many relationship tables
video_genre = Table(
    'video_genre', Base.metadata,
    Column('video_id', Integer, ForeignKey('videos.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

video_actor = Table(
    'video_actor', Base.metadata,
    Column('video_id', Integer, ForeignKey('videos.id'), primary_key=True),
    Column('actor_id', Integer, ForeignKey('actors.id'), primary_key=True)
)

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True, nullable=False)
    original_name = Column(String, nullable=False)
    official_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    subtitles = relationship("Subtitle", back_populates="video", cascade="all, delete-orphan")
    movie_info = relationship("MovieInfo", back_populates="video", uselist=False, cascade="all, delete-orphan")
    genres = relationship("Genre", secondary=video_genre, back_populates="videos")
    actors = relationship("Actor", secondary=video_actor, back_populates="videos")

class Subtitle(Base):
    __tablename__ = 'subtitles'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    language = Column(String)
    source_type = Column(String)  # embedded, external, ocr
    content_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    video = relationship("Video", back_populates="subtitles")

class MovieInfo(Base):
    __tablename__ = 'movie_info'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), unique=True, nullable=False)
    title = Column(String)
    original_title = Column(String)
    release_date = Column(String)
    runtime = Column(Integer)
    overview = Column(String)
    poster_path = Column(String)
    tmdb_id = Column(String)
    imdb_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    video = relationship("Video", back_populates="movie_info")

class Genre(Base):
    __tablename__ = 'genres'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    videos = relationship("Video", secondary=video_genre, back_populates="genres")

class Actor(Base):
    __tablename__ = 'actors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    profile_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    videos = relationship("Video", secondary=video_actor, back_populates="actors")

def init_db(database_url=None):
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///./videos.db')
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine 
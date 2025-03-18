from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# Many-to-many relationship tables
video_genre = Table(
    'video_genre', Base.metadata,
    Column('video_id', Integer, ForeignKey('videos.video_id')),
    Column('genre_id', Integer, ForeignKey('genres.genre_id'))
)

video_actor = Table(
    'video_actor', Base.metadata,
    Column('video_id', Integer, ForeignKey('videos.video_id')),
    Column('actor_id', Integer, ForeignKey('actors.actor_id'))
)

class Video(Base):
    __tablename__ = 'videos'
    
    video_id = Column(Integer, primary_key=True)
    file_path = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    official_name = Column(String(255))
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    subtitles = relationship("Subtitle", back_populates="video")
    metadata = relationship("Metadata", back_populates="video")
    genres = relationship("Genre", secondary=video_genre, back_populates="videos")
    actors = relationship("Actor", secondary=video_actor, back_populates="videos")

class Subtitle(Base):
    __tablename__ = 'subtitles'
    
    subtitle_id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.video_id'))
    language = Column(String(50))
    format = Column(String(20))  # SRT, VTT, ASS, etc.
    content = Column(Text)
    
    video = relationship("Video", back_populates="subtitles")

class Metadata(Base):
    __tablename__ = 'metadata'
    
    metadata_id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.video_id'))
    api_source = Column(String(50))  # TMDB, OMDb, etc.
    data = Column(JSON)  # Store raw API response
    
    video = relationship("Video", back_populates="metadata")

class Genre(Base):
    __tablename__ = 'genres'
    
    genre_id = Column(Integer, primary_key=True)
    genre_name = Column(String(100), unique=True)
    
    videos = relationship("Video", secondary=video_genre, back_populates="genres")

class Actor(Base):
    __tablename__ = 'actors'
    
    actor_id = Column(Integer, primary_key=True)
    actor_name = Column(String(100), unique=True)
    
    videos = relationship("Video", secondary=video_actor, back_populates="actors")

def init_db(db_url):
    """Initialize the database with tables"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine 
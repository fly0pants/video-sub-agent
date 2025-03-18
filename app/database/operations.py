from sqlalchemy.orm import sessionmaker
from .models import Video, Subtitle, Metadata, Genre, Actor

class DatabaseOperations:
    def __init__(self, engine):
        """Initialize database operations with an engine"""
        self.Session = sessionmaker(bind=engine)
    
    def add_video(self, file_path, original_name, official_name=None):
        """Add a new video to the database"""
        session = self.Session()
        try:
            video = Video(
                file_path=file_path,
                original_name=original_name,
                official_name=official_name
            )
            session.add(video)
            session.commit()
            return video.video_id
        finally:
            session.close()
    
    def update_video_official_name(self, video_id, official_name):
        """Update the official name of a video"""
        session = self.Session()
        try:
            video = session.query(Video).filter(Video.video_id == video_id).first()
            if video:
                video.official_name = official_name
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def add_subtitle(self, video_id, language, format, content):
        """Add a subtitle to a video"""
        session = self.Session()
        try:
            subtitle = Subtitle(
                video_id=video_id,
                language=language,
                format=format,
                content=content
            )
            session.add(subtitle)
            session.commit()
            return subtitle.subtitle_id
        finally:
            session.close()
    
    def add_metadata(self, video_id, api_source, data):
        """Add metadata to a video"""
        session = self.Session()
        try:
            metadata = Metadata(
                video_id=video_id,
                api_source=api_source,
                data=data
            )
            session.add(metadata)
            session.commit()
            return metadata.metadata_id
        finally:
            session.close()
    
    def get_or_create_genre(self, genre_name):
        """Get a genre by name or create if it doesn't exist"""
        session = self.Session()
        try:
            genre = session.query(Genre).filter(Genre.genre_name == genre_name).first()
            if not genre:
                genre = Genre(genre_name=genre_name)
                session.add(genre)
                session.commit()
            return genre
        finally:
            session.close()
    
    def get_or_create_actor(self, actor_name):
        """Get an actor by name or create if it doesn't exist"""
        session = self.Session()
        try:
            actor = session.query(Actor).filter(Actor.actor_name == actor_name).first()
            if not actor:
                actor = Actor(actor_name=actor_name)
                session.add(actor)
                session.commit()
            return actor
        finally:
            session.close()
    
    def add_genres_to_video(self, video_id, genre_names):
        """Add genres to a video"""
        session = self.Session()
        try:
            video = session.query(Video).filter(Video.video_id == video_id).first()
            if not video:
                return False
            
            for genre_name in genre_names:
                genre = self.get_or_create_genre(genre_name)
                if genre not in video.genres:
                    video.genres.append(genre)
            
            session.commit()
            return True
        finally:
            session.close()
    
    def add_actors_to_video(self, video_id, actor_names):
        """Add actors to a video"""
        session = self.Session()
        try:
            video = session.query(Video).filter(Video.video_id == video_id).first()
            if not video:
                return False
            
            for actor_name in actor_names:
                actor = self.get_or_create_actor(actor_name)
                if actor not in video.actors:
                    video.actors.append(actor)
            
            session.commit()
            return True
        finally:
            session.close()
    
    def get_video_by_id(self, video_id):
        """Get a video by id with all related data"""
        session = self.Session()
        try:
            video = session.query(Video).filter(Video.video_id == video_id).first()
            return video
        finally:
            session.close()
    
    def get_videos_by_genre(self, genre_name):
        """Get videos by genre"""
        session = self.Session()
        try:
            genre = session.query(Genre).filter(Genre.genre_name == genre_name).first()
            if genre:
                return genre.videos
            return []
        finally:
            session.close()
    
    def get_videos_by_actor(self, actor_name):
        """Get videos by actor"""
        session = self.Session()
        try:
            actor = session.query(Actor).filter(Actor.actor_name == actor_name).first()
            if actor:
                return actor.videos
            return []
        finally:
            session.close() 
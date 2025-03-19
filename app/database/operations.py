from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from .models import Video, Subtitle, MovieInfo, Genre, Actor

class DatabaseOperations:
    def __init__(self, session: Session):
        self.session = session

    def create_video(self, file_path: str, original_name: str, official_name: Optional[str] = None) -> Video:
        video = Video(
            file_path=file_path,
            original_name=original_name,
            official_name=official_name
        )
        self.session.add(video)
        self.session.commit()
        return video

    def get_video(self, video_id: int) -> Optional[Video]:
        return self.session.query(Video).filter(Video.id == video_id).first()

    def get_video_by_path(self, file_path: str) -> Optional[Video]:
        return self.session.query(Video).filter(Video.file_path == file_path).first()

    def list_videos(self, skip: int = 0, limit: int = 100) -> List[Video]:
        return self.session.query(Video).offset(skip).limit(limit).all()

    def add_subtitle(self, video_id: int, language: str, source_type: str, content_path: str) -> Subtitle:
        subtitle = Subtitle(
            video_id=video_id,
            language=language,
            source_type=source_type,
            content_path=content_path
        )
        self.session.add(subtitle)
        self.session.commit()
        return subtitle

    def update_movie_info(self, video_id: int, **kwargs) -> MovieInfo:
        movie_info = self.session.query(MovieInfo).filter(MovieInfo.video_id == video_id).first()
        if not movie_info:
            movie_info = MovieInfo(video_id=video_id, **kwargs)
            self.session.add(movie_info)
        else:
            for key, value in kwargs.items():
                setattr(movie_info, key, value)
        self.session.commit()
        return movie_info

    def get_or_create_genre(self, name: str) -> Genre:
        genre = self.session.query(Genre).filter(Genre.name == name).first()
        if not genre:
            genre = Genre(name=name)
            self.session.add(genre)
            self.session.commit()
        return genre

    def get_or_create_actor(self, name: str, profile_path: Optional[str] = None) -> Actor:
        actor = self.session.query(Actor).filter(Actor.name == name).first()
        if not actor:
            actor = Actor(name=name, profile_path=profile_path)
            self.session.add(actor)
            self.session.commit()
        return actor

    def add_genres_to_video(self, video_id: int, genre_names: List[str]):
        video = self.get_video(video_id)
        if not video:
            raise ValueError(f"Video with id {video_id} not found")
        
        for name in genre_names:
            genre = self.get_or_create_genre(name)
            if genre not in video.genres:
                video.genres.append(genre)
        
        self.session.commit()

    def add_actors_to_video(self, video_id: int, actor_data: List[dict]):
        video = self.get_video(video_id)
        if not video:
            raise ValueError(f"Video with id {video_id} not found")
        
        for data in actor_data:
            actor = self.get_or_create_actor(data['name'], data.get('profile_path'))
            if actor not in video.actors:
                video.actors.append(actor)
        
        self.session.commit()

    def delete_video(self, video_id: int) -> bool:
        video = self.get_video(video_id)
        if video:
            self.session.delete(video)
            self.session.commit()
            return True
        return False 
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

class SubtitleResponse(BaseModel):
    path: str
    format: str
    language: str
    content: Optional[str] = None

class MetadataResponse(BaseModel):
    api_source: str
    data: Dict[str, Any]

class VideoDetail(BaseModel):
    video_id: int
    file_path: str
    original_name: str
    official_name: Optional[str] = None
    upload_date: datetime
    subtitles: List[SubtitleResponse] = []
    metadata: List[MetadataResponse] = []
    genres: List[str] = []
    actors: List[str] = []

class VideoList(BaseModel):
    video_id: int
    original_name: str
    official_name: Optional[str] = None
    upload_date: datetime

class VideosResponse(BaseModel):
    count: int
    videos: List[VideoList]

class ProcessResult(BaseModel):
    video_path: str
    original_name: str
    official_name: Optional[str] = None
    subtitles: List[Dict[str, Any]] = []
    db_id: Optional[int] = None
    error: Optional[str] = None

class ProcessRequest(BaseModel):
    video_path: str
    extract_hardcoded: bool = False

class BatchProcessRequest(BaseModel):
    video_paths: List[str]
    extract_hardcoded: bool = False

class ErrorResponse(BaseModel):
    detail: str

class GenreList(BaseModel):
    genre_id: int
    genre_name: str

class ActorList(BaseModel):
    actor_id: int
    actor_name: str

class RecognizeNameRequest(BaseModel):
    name: str

class RecognizeNameResponse(BaseModel):
    original_name: str
    official_name: str 
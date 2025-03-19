from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import shutil
import logging
from typing import List, Optional
from pathlib import Path

from ..database import DatabaseOperations
from .. import processor
from .models import (
    VideoDetail, VideoList, VideosResponse, ProcessResult, 
    ProcessRequest, BatchProcessRequest, ErrorResponse,
    GenreList, ActorList, RecognizeNameRequest, RecognizeNameResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get database operations
def get_db_operations(request: Request):
    return request.app.state.db_operations

# Dependency to get video processor
def get_video_processor(request: Request):
    return request.app.state.video_processor

@router.get("/videos", response_model=VideosResponse)
def list_videos(
    db_operations: DatabaseOperations = Depends(get_db_operations),
    skip: int = 0,
    limit: int = 100
):
    """List all videos in the database"""
    # Implementation would fetch videos from database
    pass

@router.get("/videos/{video_id}", response_model=VideoDetail)
def get_video(
    video_id: int,
    db_operations: DatabaseOperations = Depends(get_db_operations)
):
    """Get details of a specific video"""
    # Implementation would fetch video details from database
    pass

@router.post("/videos/process", response_model=ProcessResult)
def process_video(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    video_processor: processor.VideoProcessor = Depends(get_video_processor)
):
    """Process a video file to extract subtitles, recognize name, and fetch metadata"""
    try:
        # Check if file exists
        if not os.path.exists(request.video_path):
            raise HTTPException(status_code=404, detail=f"Video file not found: {request.video_path}")
        
        # Process the video (can be moved to background task for long processing)
        result = video_processor.process_video(
            video_path=request.video_path
        )
        
        return result
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/videos/process/batch", response_model=List[ProcessResult])
def process_videos_batch(
    request: BatchProcessRequest,
    video_processor: processor.VideoProcessor = Depends(get_video_processor)
):
    """Process multiple video files in batch"""
    try:
        # Check if all files exist
        for path in request.video_paths:
            if not os.path.exists(path):
                raise HTTPException(status_code=404, detail=f"Video file not found: {path}")
        
        # Process videos
        results = video_processor.batch_process_videos(
            video_paths=request.video_paths,
            extract_hardcoded=request.extract_hardcoded
        )
        
        return results
    except Exception as e:
        logger.error(f"Error processing videos batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/videos/upload", response_model=ProcessResult)
async def upload_and_process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    extract_hardcoded: bool = Form(False),
    video_processor: processor.VideoProcessor = Depends(get_video_processor)
):
    """Upload and process a video file"""
    try:
        # Create temp directory for uploads if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the video (can be moved to background task for long processing)
        result = video_processor.process_video(
            video_path=file_path
        )
        
        return result
    except Exception as e:
        logger.error(f"Error processing uploaded video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres", response_model=List[GenreList])
def list_genres(
    db_operations: DatabaseOperations = Depends(get_db_operations)
):
    """List all genres in the database"""
    # Implementation would fetch genres from database
    pass

@router.get("/actors", response_model=List[ActorList])
def list_actors(
    db_operations: DatabaseOperations = Depends(get_db_operations)
):
    """List all actors in the database"""
    # Implementation would fetch actors from database
    pass

@router.post("/recognize/name", response_model=RecognizeNameResponse)
def recognize_movie_name(
    request: RecognizeNameRequest,
    video_processor: processor.VideoProcessor = Depends(get_video_processor)
):
    """Recognize official movie name from a filename or partial name"""
    try:
        official_name = video_processor.movie_name_recognizer.recognize_movie_name(request.name)
        
        return {
            "original_name": request.name,
            "official_name": official_name
        }
    except Exception as e:
        logger.error(f"Error recognizing movie name: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
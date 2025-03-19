import argparse
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from .database import init_db
from .database.operations import DatabaseOperations
from .processor import VideoProcessor
from .movie_name import MovieNameRecognizer
from config.settings import setup_logging

# Set up logging
logger = setup_logging()

def get_db_session() -> Session:
    engine = init_db()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def process_video(file_path: str, db_ops: DatabaseOperations, processor: VideoProcessor) -> bool:
    try:
        # Check if video already exists in database
        existing_video = db_ops.get_video_by_path(file_path)
        if existing_video:
            logger.info(f"Video already processed: {file_path}")
            return True

        # Process the video
        result = processor.process_video(file_path)
        if result:
            logger.info(f"Successfully processed video: {file_path}")
            return True
        else:
            logger.error(f"Failed to process video: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error processing video {file_path}: {str(e)}")
        return False

def delete_video(file_path: str, db_ops: DatabaseOperations) -> bool:
    try:
        # Get video from database
        video = db_ops.get_video_by_path(file_path)
        if not video:
            logger.error(f"Video not found in database: {file_path}")
            return False
            
        # Delete video and related data
        db_ops.delete_video(video.id)
        logger.info(f"Successfully deleted video: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting video {file_path}: {str(e)}")
        return False

def batch_process_videos(directory: str, db_ops: DatabaseOperations, processor: VideoProcessor) -> None:
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv'}
    path = Path(directory)
    
    if not path.exists():
        logger.error(f"Directory not found: {directory}")
        return

    if path.is_file():
        if path.suffix.lower() in video_extensions:
            process_video(str(path), db_ops, processor)
        return

    for file_path in path.rglob('*'):
        if file_path.suffix.lower() in video_extensions:
            process_video(str(file_path), db_ops, processor)

def recognize_movie_name(name: str) -> Optional[str]:
    recognizer = MovieNameRecognizer()
    try:
        result = recognizer.recognize(name)
        if result:
            logger.info(f"Recognized name: {result}")
            return result
        else:
            logger.error(f"Could not recognize movie name: {name}")
            return None
    except Exception as e:
        logger.error(f"Error recognizing movie name: {str(e)}")
        return None

def list_videos(db_ops: DatabaseOperations) -> None:
    try:
        videos = db_ops.list_videos()
        if not videos:
            logger.info("No videos found in database")
            return

        for video in videos:
            print(f"\nVideo ID: {video.id}")
            print(f"Original Name: {video.original_name}")
            print(f"Official Name: {video.official_name or 'Not recognized'}")
            print(f"File Path: {video.file_path}")
            print(f"Subtitles: {len(video.subtitles)}")
            if video.movie_info:
                print("Movie Info:")
                print(f"  Title: {video.movie_info.title}")
                print(f"  Release Date: {video.movie_info.release_date}")
                print(f"  Runtime: {video.movie_info.runtime} minutes")
            print("Genres:", ", ".join(genre.name for genre in video.genres))
            print("Actors:", ", ".join(actor.name for actor in video.actors))
            print("-" * 80)
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")

def parse_args():
    parser = argparse.ArgumentParser(description="Video Analysis and Metadata Management CLI")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Process single video
    process_parser = subparsers.add_parser('process', help='Process a single video')
    process_parser.add_argument('file_path', help='Path to the video file')

    # Delete video
    delete_parser = subparsers.add_parser('delete', help='Delete a video from the database')
    delete_parser.add_argument('file_path', help='Path to the video file')

    # Batch process videos
    batch_parser = subparsers.add_parser('batch', help='Process multiple videos')
    batch_parser.add_argument('directory', help='Directory containing videos')

    # Recognize movie name
    recognize_parser = subparsers.add_parser('recognize', help='Recognize movie name')
    recognize_parser.add_argument('name', help='Movie name or filename to recognize')

    # List videos
    subparsers.add_parser('list', help='List all processed videos')

    return parser.parse_args()

def main():
    args = parse_args()
    if not args.command:
        print("Please specify a command. Use -h for help.")
        return 1

    try:
        session = get_db_session()
        db_ops = DatabaseOperations(session)
        
        if args.command == 'process':
            processor = VideoProcessor(db_ops)
            success = process_video(args.file_path, db_ops, processor)
            return 0 if success else 1
            
        elif args.command == 'delete':
            success = delete_video(args.file_path, db_ops)
            return 0 if success else 1
        
        elif args.command == 'batch':
            processor = VideoProcessor(db_ops)
            batch_process_videos(args.directory, db_ops, processor)
            return 0
        
        elif args.command == 'recognize':
            result = recognize_movie_name(args.name)
            return 0 if result else 1
        
        elif args.command == 'list':
            list_videos(db_ops)
            return 0

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    finally:
        session.close()

if __name__ == '__main__':
    sys.exit(main()) 
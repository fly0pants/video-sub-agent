import argparse
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import click

from .database import init_db
from .database.operations import DatabaseOperations
from .processor import VideoProcessor
from .movie_name import MovieNameRecognizer
from config.settings import setup_logging
from .log import logger

# Set up logging
logger = setup_logging()

def get_db_session() -> Session:
    engine = init_db()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def process_video(file_path: str, db_ops: DatabaseOperations, processor: VideoProcessor, force: bool = False) -> bool:
    try:
        # Check if video already exists in database
        existing_video = db_ops.get_video_by_path(file_path)
        if existing_video and not force:
            logger.info(f"Video already processed: {file_path}")
            return True
            
        # If force flag is set and video exists, delete it first
        if existing_video and force:
            logger.info(f"Force flag set, reprocessing video: {file_path}")
            db_ops.delete_video(existing_video.id)

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
    process_parser.add_argument('--force', '-f', action='store_true', help='Force reprocessing even if video is already processed')

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
            processor = VideoProcessor()
            success = process_video(args.file_path, db_ops, processor, args.force)
            return 0 if success else 1
            
        elif args.command == 'delete':
            success = delete_video(args.file_path, db_ops)
            return 0 if success else 1
        
        elif args.command == 'batch':
            processor = VideoProcessor()
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

@click.group()
def cli():
    """Video subtitle extraction and management tool."""
    pass

@cli.command()
@click.argument("video_path", type=click.Path(exists=True))
@click.option("--force", "-f", is_flag=True, help="Force reprocessing even if video was already processed")
def process(video_path: str, force: bool = False):
    """Process a video file to extract subtitles and metadata."""
    processor = VideoProcessor()
    
    # Check if video already exists and force flag is not set
    if not force and processor.db_manager.is_video_processed(video_path):
        logger.info(f"Video already processed: {video_path}")
        return
        
    # If force flag is set and video exists, delete it first
    if force and processor.db_manager.is_video_processed(video_path):
        logger.info(f"Force flag set, reprocessing video: {video_path}")
        processor.db_manager.delete_video(video_path)
    
    result = processor.process_video(video_path)
    
    if "error" in result:
        logger.error(f"Failed to process video: {result['error']}")
        return
        
    logger.info("Video processing completed successfully:")
    logger.info(f"  File: {result['file_path']}")
    logger.info(f"  Name: {result['official_name']}")
    
    if result['subtitle_info'].get('subtitles'):
        logger.info("  Subtitles:")
        for sub in result['subtitle_info']['subtitles']:
            logger.info(f"    - {sub['language']}: {sub['content_path']}")
    else:
        logger.info("  No subtitles found")
    
    if result['metadata']:
        logger.info("  Metadata:")
        logger.info(f"    Title: {result['metadata'].get('title')}")
        logger.info(f"    Year: {result['metadata'].get('release_date', '').split('-')[0]}")
        logger.info(f"    Genres: {', '.join(result['metadata'].get('genres', []))}")
    else:
        logger.info("  No metadata found")

@cli.command()
def list():
    """List all processed videos."""
    processor = VideoProcessor()
    videos = processor.db_manager.list_videos()
    
    if not videos:
        logger.info("No processed videos found")
        return
        
    logger.info(f"Found {len(videos)} processed videos:")
    for video in videos:
        logger.info(f"\nFile: {video['file_path']}")
        logger.info(f"Name: {video['official_name']}")
        
        if video['subtitle_info'].get('subtitles'):
            logger.info("Subtitles:")
            for sub in video['subtitle_info']['subtitles']:
                logger.info(f"  - {sub['language']}: {sub['content_path']}")
        else:
            logger.info("No subtitles found")
        
        if video['metadata']:
            logger.info("Metadata:")
            logger.info(f"  Title: {video['metadata'].get('title')}")
            logger.info(f"  Year: {video['metadata'].get('release_date', '').split('-')[0]}")
            logger.info(f"  Genres: {', '.join(video['metadata'].get('genres', []))}")
        else:
            logger.info("No metadata found")

@cli.command()
@click.argument("video_path", type=click.Path(exists=True))
def delete(video_path: str):
    """Delete video information from database."""
    processor = VideoProcessor()
    if processor.db_manager.delete_video(video_path):
        logger.info(f"Successfully deleted video info: {video_path}")
    else:
        logger.error(f"Failed to delete video info: {video_path}")

if __name__ == '__main__':
    sys.exit(main()) 
import argparse
import os
import sys
import logging
import glob
from pathlib import Path

from .database import init_db, DatabaseOperations
from .processor import VideoProcessor
from config.settings import CONFIG, setup_logging

# Set up logging
logger = setup_logging()

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Video Analysis and Metadata Management System"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process a video file")
    process_parser.add_argument("path", help="Path to the video file")
    process_parser.add_argument("--ocr", action="store_true", help="Extract hardcoded subtitles using OCR")
    process_parser.add_argument("--output-dir", help="Directory to save extracted subtitles")
    
    # Batch process command
    batch_parser = subparsers.add_parser("batch", help="Process multiple video files")
    batch_parser.add_argument("path", help="Path to directory or glob pattern for video files")
    batch_parser.add_argument("--ocr", action="store_true", help="Extract hardcoded subtitles using OCR")
    batch_parser.add_argument("--output-dir", help="Directory to save extracted subtitles")
    
    # Recognize command
    recognize_parser = subparsers.add_parser("recognize", help="Recognize official movie name")
    recognize_parser.add_argument("name", help="Movie name or filename to recognize")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List processed videos")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of videos to list")
    
    # Initialize database command
    init_parser = subparsers.add_parser("init", help="Initialize database")
    
    return parser.parse_args()

def process_video(args, processor):
    """Process a single video file"""
    try:
        if not os.path.exists(args.path):
            logger.error(f"File not found: {args.path}")
            return 1
        
        output_dir = args.output_dir or CONFIG["output_dir"]
        
        logger.info(f"Processing video: {args.path}")
        result = processor.process_video(
            video_path=args.path,
            output_dir=output_dir,
            extract_hardcoded=args.ocr
        )
        
        logger.info(f"Video processed successfully: {args.path}")
        logger.info(f"Original name: {result['original_name']}")
        logger.info(f"Official name: {result['official_name']}")
        logger.info(f"Subtitles extracted: {len(result['subtitles'])}")
        
        return 0
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return 1

def batch_process_videos(args, processor):
    """Process multiple video files"""
    try:
        # Get video files from path
        if os.path.isdir(args.path):
            # If path is a directory, get all video files
            video_extensions = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]
            video_paths = []
            for ext in video_extensions:
                video_paths.extend(glob.glob(os.path.join(args.path, f"*{ext}")))
        else:
            # Treat as glob pattern
            video_paths = glob.glob(args.path)
        
        if not video_paths:
            logger.error(f"No video files found at: {args.path}")
            return 1
        
        logger.info(f"Found {len(video_paths)} video files")
        
        output_dir = args.output_dir or CONFIG["output_dir"]
        
        # Process videos
        results = processor.batch_process_videos(
            video_paths=video_paths,
            output_dir=output_dir,
            extract_hardcoded=args.ocr
        )
        
        # Print summary
        successful = sum(1 for r in results if "error" not in r)
        failed = len(results) - successful
        
        logger.info(f"Batch processing completed: {successful} successful, {failed} failed")
        
        return 0
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        return 1

def recognize_movie_name(args, processor):
    """Recognize official movie name"""
    try:
        logger.info(f"Recognizing movie name: {args.name}")
        official_name = processor.movie_name_recognizer.recognize_movie_name(args.name)
        
        logger.info(f"Recognized '{args.name}' as '{official_name}'")
        
        return 0
    except Exception as e:
        logger.error(f"Error recognizing movie name: {e}")
        return 1

def list_videos(args, db_operations):
    """List processed videos from database"""
    try:
        # Implementation would fetch videos from database
        # For now, just print a message
        logger.info("Listing videos is not implemented yet")
        
        return 0
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return 1

def init_database():
    """Initialize database"""
    try:
        logger.info(f"Initializing database at {CONFIG['database_url']}")
        db_engine = init_db(CONFIG["database_url"])
        logger.info("Database initialized successfully")
        
        return 0
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return 1

def main():
    """Main entry point for CLI"""
    args = parse_args()
    
    if args.command is None:
        logger.error("No command specified. Use -h for help.")
        return 1
    
    # Initialize database for commands that need it
    if args.command in ["process", "batch", "recognize", "list"]:
        try:
            db_engine = init_db(CONFIG["database_url"])
            db_operations = DatabaseOperations(db_engine)
            
            # Initialize video processor
            processor = VideoProcessor(db_operations=db_operations, config=CONFIG)
        except Exception as e:
            logger.error(f"Error initializing system: {e}")
            return 1
    
    # Execute command
    if args.command == "process":
        return process_video(args, processor)
    elif args.command == "batch":
        return batch_process_videos(args, processor)
    elif args.command == "recognize":
        return recognize_movie_name(args, processor)
    elif args.command == "list":
        return list_videos(args, db_operations)
    elif args.command == "init":
        return init_database()
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
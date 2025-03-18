import os
import logging
import tempfile
from pathlib import Path

from .subtitle import SubtitleExtractor, OCRSubtitleExtractor
from .movie_name import MovieNameRecognizer
from .metadata import MetadataFetcher
from .database.operations import DatabaseOperations

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Main class for processing videos and coordinating all modules"""
    
    def __init__(self, db_operations, config=None):
        """
        Initialize with database operations and configuration
        
        Args:
            db_operations: DatabaseOperations instance
            config: Optional configuration dictionary
        """
        self.db_operations = db_operations
        self.config = config or {}
        
        # Initialize subtitle extractors
        self.subtitle_extractor = SubtitleExtractor(
            ffmpeg_path=config.get("ffmpeg_path", "ffmpeg"),
            ffprobe_path=config.get("ffprobe_path", "ffprobe"),
            ccextractor_path=config.get("ccextractor_path", "ccextractor")
        )
        
        self.ocr_subtitle_extractor = OCRSubtitleExtractor(
            ffmpeg_path=config.get("ffmpeg_path", "ffmpeg"),
            tesseract_cmd=config.get("tesseract_cmd")
        )
        
        # Initialize movie name recognizer
        self.movie_name_recognizer = MovieNameRecognizer(
            api_key=config.get("deepseek_api_key"),
            api_base=config.get("deepseek_api_base"),
            model=config.get("deepseek_model", "deepseek-coder")
        )
        
        # Initialize metadata fetcher
        self.metadata_fetcher = MetadataFetcher(
            tmdb_api_key=config.get("tmdb_api_key"),
            omdb_api_key=config.get("omdb_api_key")
        )
    
    def process_video(self, video_path, output_dir=None, extract_hardcoded=False):
        """
        Process a video file to extract subtitles, identify movie name, and fetch metadata
        
        Args:
            video_path: Path to the video file
            output_dir: Directory to save extracted subtitles
            extract_hardcoded: Whether to attempt OCR extraction of hardcoded subtitles
            
        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        os.makedirs(output_dir, exist_ok=True)
        
        # Get original file name for movie name recognition
        file_name = Path(video_path).stem
        
        result = {
            "video_path": video_path,
            "original_name": file_name,
            "official_name": None,
            "subtitles": [],
            "metadata": {},
            "db_id": None
        }
        
        # Step 1: Extract subtitles
        try:
            logger.info(f"Extracting subtitles from {video_path}")
            extracted_subtitles = self.subtitle_extractor.extract_subtitles(
                video_path,
                output_dir=output_dir
            )
            result["subtitles"].extend(extracted_subtitles)
            
            # If no subtitles found and hardcoded extraction is enabled, try OCR
            if not extracted_subtitles and extract_hardcoded:
                logger.info(f"No embedded subtitles found, trying OCR extraction for {video_path}")
                ocr_subtitle = self.ocr_subtitle_extractor.extract_hardcoded_subtitles(
                    video_path,
                    output_path=os.path.join(output_dir, f"{file_name}_ocr.srt")
                )
                if ocr_subtitle:
                    result["subtitles"].append(ocr_subtitle)
        except Exception as e:
            logger.error(f"Error extracting subtitles: {e}")
        
        # Step 2: Recognize official movie name
        try:
            logger.info(f"Recognizing official name for {file_name}")
            official_name = self.movie_name_recognizer.recognize_movie_name(file_name)
            result["official_name"] = official_name
        except Exception as e:
            logger.error(f"Error recognizing movie name: {e}")
        
        # Step 3: If official name was recognized, fetch metadata
        if result["official_name"]:
            try:
                logger.info(f"Fetching metadata for {result['official_name']}")
                metadata = self.metadata_fetcher.fetch_metadata(result["official_name"])
                result["metadata"] = metadata
                
                # Extract common metadata fields
                result["common_metadata"] = self.metadata_fetcher.extract_common_metadata(metadata)
            except Exception as e:
                logger.error(f"Error fetching metadata: {e}")
        
        # Step 4: Store everything in the database
        try:
            # Add video to database
            video_id = self.db_operations.add_video(
                file_path=video_path,
                original_name=result["original_name"],
                official_name=result["official_name"]
            )
            result["db_id"] = video_id
            
            # Add subtitles to database
            for subtitle in result["subtitles"]:
                self.db_operations.add_subtitle(
                    video_id=video_id,
                    language=subtitle.get("language", "unknown"),
                    format=subtitle.get("format", "srt"),
                    content=subtitle.get("content", "")
                )
            
            # Add metadata to database
            for source, data in result["metadata"].items():
                self.db_operations.add_metadata(
                    video_id=video_id,
                    api_source=source,
                    data=data
                )
            
            # Add genres and actors if available in common metadata
            if "common_metadata" in result and result["common_metadata"]:
                common = result["common_metadata"]
                
                if common.get("genres"):
                    self.db_operations.add_genres_to_video(video_id, common["genres"])
                
                if common.get("actors"):
                    self.db_operations.add_actors_to_video(video_id, common["actors"])
        except Exception as e:
            logger.error(f"Error storing data in database: {e}")
        
        return result
    
    def batch_process_videos(self, video_paths, output_dir=None, extract_hardcoded=False):
        """
        Process multiple video files
        
        Args:
            video_paths: List of paths to video files
            output_dir: Base directory to save extracted subtitles
            extract_hardcoded: Whether to attempt OCR extraction of hardcoded subtitles
            
        Returns:
            List of dictionaries with processing results
        """
        results = []
        
        for video_path in video_paths:
            try:
                # Create a specific output directory for each video
                video_name = Path(video_path).stem
                video_output_dir = os.path.join(output_dir, video_name) if output_dir else None
                
                result = self.process_video(video_path, video_output_dir, extract_hardcoded)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing video {video_path}: {e}")
                results.append({
                    "video_path": video_path,
                    "error": str(e)
                })
        
        return results 
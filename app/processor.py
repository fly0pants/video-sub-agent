import os
import json
import requests
from typing import Dict, Any, Optional, List
from .database.manager import DatabaseManager
from .subtitle import SubtitleExtractor
from .metadata import MetadataManager
from .log import logger

class VideoProcessor:
    def __init__(self):
        """Initialize the video processor."""
        self.db_manager = DatabaseManager()
        self.subtitle_extractor = SubtitleExtractor()
        self.metadata_manager = MetadataManager()

    def _fetch_subtitles_from_web(self, video_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Fetch subtitles from OpenSubtitles API.
        
        Args:
            video_info: Dictionary containing video information
            
        Returns:
            Dictionary containing subtitle information if successful, None otherwise
        """
        try:
            # Get API key from environment
            api_key = os.getenv("OPENSUBTITLES_API_KEY")
            if not api_key or api_key == "your_opensubtitles_api_key":
                logger.warning(
                    "OpenSubtitles API key not found or invalid. To use online subtitle search:"
                    "\n1. Get a VIP membership at https://www.opensubtitles.com/en/vip"
                    "\n2. Get an API key at https://www.opensubtitles.com/en/consumers"
                    "\n3. Add your API key to the .env file"
                )
                return None
                
            # Get movie name from video info
            movie_name = video_info.get("name")
            if not movie_name:
                logger.error("Movie name not found in video info")
                return None
                
            # Get metadata from video info
            metadata = video_info.get("metadata", {})
            if not metadata:
                logger.warning("No metadata found in video info")
                
            # Try to get IMDb ID from metadata
            imdb_id = metadata.get("imdb_id")
            
            # Get movie's original language from metadata
            original_language = metadata.get("language", "").lower() if metadata else ""
            languages_to_download = ["en"]
            
            # Add movie's original language if available and not English
            if original_language and original_language != "english" and original_language != "en":
                # Convert common language names to ISO codes
                language_map = {
                    "korean": "ko",
                    "chinese": "zh",
                    "japanese": "ja",
                    "french": "fr",
                    "spanish": "es",
                    "german": "de",
                    "italian": "it",
                    "russian": "ru"
                }
                lang_code = language_map.get(original_language.lower(), original_language[:2].lower())
                if lang_code != "en":
                    languages_to_download.append(lang_code)
            
            languages_str = ",".join(languages_to_download)
            logger.info(f"Searching for subtitles in languages: {languages_str}")
            
            if imdb_id:
                logger.info(f"Using IMDb ID for subtitle search: {imdb_id}")
                search_params = {
                    "imdb_id": imdb_id.replace("tt", ""),
                    "languages": languages_str
                }
            else:
                # Try to get English title from metadata
                english_title = metadata.get("title")
                if english_title:
                    logger.info(f"Using English title for subtitle search: {english_title}")
                    search_params = {
                        "query": english_title,
                        "languages": languages_str
                    }
                else:
                    logger.info(f"Using original title for subtitle search: {movie_name}")
                    search_params = {
                        "query": movie_name,
                        "languages": languages_str
                    }
                    
            # Search for subtitles
            headers = {
                "Api-Key": api_key,
                "Content-Type": "application/json"
            }
            
            logger.info("Searching for subtitles on OpenSubtitles...")
            response = requests.get(
                "https://api.opensubtitles.com/api/v1/subtitles",
                params=search_params,
                headers=headers
            )
            
            if response.status_code == 401:
                logger.error("OpenSubtitles API key is invalid or expired")
                return None
            elif response.status_code == 403:
                logger.error("OpenSubtitles API access denied. Make sure you have a VIP membership")
                return None
            elif response.status_code != 200:
                logger.error(f"Failed to search subtitles: {response.text}")
                return None
                
            data = response.json()
            if not data.get("data"):
                logger.info("No subtitles found on OpenSubtitles")
                return None
                
            # Group subtitles by language
            subtitles_by_lang = {}
            for sub in data.get("data", []):
                lang = sub.get("attributes", {}).get("language")
                if lang in languages_to_download and lang not in subtitles_by_lang:
                    subtitles_by_lang[lang] = sub
            
            if not subtitles_by_lang:
                logger.info("No subtitles found in the requested languages")
                # Fall back to first subtitle if available
                if data.get("data"):
                    subtitles_by_lang = {data["data"][0].get("attributes", {}).get("language"): data["data"][0]}
                else:
                    return None
            
            downloaded_subtitles = []
            
            # Download each language subtitle
            for lang, subtitle in subtitles_by_lang.items():
                file_id = subtitle.get("attributes", {}).get("files", [{}])[0].get("file_id")
                
                if not file_id:
                    logger.error(f"No file ID found for {lang} subtitle")
                    continue
                    
                # Download subtitle
                logger.info(f"Downloading {lang} subtitle file...")
                response = requests.post(
                    "https://api.opensubtitles.com/api/v1/download",
                    headers=headers,
                    json={"file_id": file_id}
                )
                
                if response.status_code == 406:
                    logger.error("Daily download limit exceeded. Please wait 24 hours or upgrade your plan")
                    continue
                elif response.status_code != 200:
                    logger.error(f"Failed to download {lang} subtitle: {response.text}")
                    continue
                    
                download_link = response.json().get("link")
                if not download_link:
                    logger.error(f"No download link in response for {lang} subtitle")
                    continue
                    
                # Download and save subtitle file
                response = requests.get(download_link)
                if response.status_code != 200:
                    logger.error(f"Failed to download {lang} subtitle file")
                    continue
                    
                # Save subtitle file
                output_dir = "output/subtitles"
                os.makedirs(output_dir, exist_ok=True)
                
                output_path = os.path.join(
                    output_dir,
                    f"{os.path.splitext(os.path.basename(video_info['path']))[0]}_{lang}.srt"
                )
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                    
                logger.info(f"Successfully downloaded {lang} subtitle to: {output_path}")
                
                downloaded_subtitles.append({
                    "language": lang,
                    "content_path": output_path
                })
            
            if not downloaded_subtitles:
                logger.error("Failed to download any subtitles")
                return None
                
            return {
                "source_type": "web",
                "subtitles": downloaded_subtitles
            }
            
        except Exception as e:
            logger.error(f"Error fetching subtitles from web: {str(e)}")
            return None
            
    def process_video(self, video_path: str) -> Dict[str, Any]:
        """
        Process a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing video information and processing results
        """
        try:
            # Check if video has already been processed
            if self.db_manager.is_video_processed(video_path):
                logger.info(f"Video already processed: {video_path}")
                return self.db_manager.get_video_info(video_path)
                
            # Get movie name from parent directory
            parent_dir = os.path.basename(os.path.dirname(video_path))
            movie_name = parent_dir.split("[")[0].strip()
            logger.info(f"Processing video: {movie_name}")
            
            # Get metadata
            metadata = self.metadata_manager.fetch_metadata(movie_name)
            if metadata:
                logger.info(f"Found metadata for movie: {metadata.get('title')}")
            else:
                # Try to get English title from parent directory
                year = None
                if "[" in parent_dir and "]" in parent_dir:
                    parts = parent_dir.split("[")
                    for part in parts[1:]:
                        if part.endswith("]"):
                            year_str = part[:-1]
                            if year_str.isdigit() and len(year_str) == 4:
                                year = int(year_str)
                                break
                                
                if year:
                    logger.info(f"Trying to fetch metadata with year: {year}")
                    metadata = self.metadata_manager.fetch_metadata(movie_name, year=year)
                    if metadata:
                        logger.info(f"Found metadata for movie: {metadata.get('title')}")
                    else:
                        logger.warning(f"No metadata found for movie: {movie_name}")
                else:
                    logger.warning(f"No metadata found for movie: {movie_name}")
                    
            # Create video info
            video_info = {
                "path": video_path,
                "name": movie_name,
                "status": "processing",
                "metadata": metadata
            }
            
            # Try to extract embedded subtitles
            logger.info("Trying to extract embedded subtitles...")
            subtitle_result = self.subtitle_extractor.extract(video_path)
            
            if subtitle_result["source_type"] == "none":
                # If no embedded subtitles found, try to fetch from web
                logger.info("No embedded subtitles found, trying to fetch from web...")
                web_subtitle_result = self._fetch_subtitles_from_web(video_info)
                
                if web_subtitle_result:
                    subtitle_result = web_subtitle_result
                    
            # Update video info with subtitle information
            video_info.update({
                "subtitle_source": subtitle_result["source_type"],
                "subtitles": subtitle_result["subtitles"],
                "status": "completed"
            })
            
            # Save to database
            self.db_manager.save_video_info(video_info)
            logger.info(f"Successfully processed video: {video_path}")
            
            return video_info
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            return {
                "path": video_path,
                "status": "error",
                "error": str(e)
            }

    def batch_process_videos(self, video_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple video files.
        
        Args:
            video_paths: List of paths to video files
            
        Returns:
            List of dictionaries containing video information and processing results
        """
        results = []
        for video_path in video_paths:
            result = self.process_video(video_path)
            results.append(result)
        return results 
import os
import json
from typing import Dict, Any, Optional, List
from ..log import logger

class DatabaseManager:
    def __init__(self, db_file: str = "data/videos.json"):
        """Initialize the database manager."""
        self.db_file = db_file
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Ensure the database file exists."""
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({"videos": []}, f)
                
    def _load_db(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load the database from file."""
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {str(e)}")
            return {"videos": []}
            
    def _save_db(self, data: Dict[str, List[Dict[str, Any]]]):
        """Save the database to file."""
        try:
            with open(self.db_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")
            
    def is_video_processed(self, video_path: str) -> bool:
        """
        Check if a video has already been processed.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            True if the video has been processed, False otherwise
        """
        data = self._load_db()
        return any(video["path"] == video_path for video in data["videos"])
        
    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a processed video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing video information if found, None otherwise
        """
        data = self._load_db()
        for video in data["videos"]:
            if video["path"] == video_path:
                return video
        return None
        
    def save_video_info(self, video_info: Dict[str, Any]):
        """
        Save or update video information in the database.
        
        Args:
            video_info: Dictionary containing video information
        """
        data = self._load_db()
        
        # Update existing entry if found
        for i, video in enumerate(data["videos"]):
            if video["path"] == video_info["path"]:
                data["videos"][i] = video_info
                self._save_db(data)
                return
                
        # Add new entry if not found
        data["videos"].append(video_info)
        self._save_db(data)
        
    def delete_video(self, video_path: str) -> bool:
        """
        Delete a video from the database.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            True if the video was deleted, False otherwise
        """
        data = self._load_db()
        initial_count = len(data["videos"])
        
        data["videos"] = [
            video for video in data["videos"]
            if video["path"] != video_path
        ]
        
        if len(data["videos"]) < initial_count:
            self._save_db(data)
            return True
            
        return False
        
    def list_videos(self) -> List[Dict[str, Any]]:
        """
        Get a list of all processed videos.
        
        Returns:
            List of dictionaries containing video information
        """
        data = self._load_db()
        return data["videos"] 
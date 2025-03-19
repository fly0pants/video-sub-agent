import sqlite3
import json
from typing import Dict, Any, List, Optional
from log import logger

class DatabaseManager:
    def __init__(self, db_path: str = "videos.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Videos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    official_name TEXT NOT NULL,
                    subtitle_info TEXT,  -- JSON string
                    metadata TEXT,  -- JSON string
                    processed_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def save_video_info(self, video_info: Dict[str, Any]) -> None:
        """
        Save video information to database.
        
        Args:
            video_info: Dictionary containing video information
                - file_path: Path to video file
                - official_name: Official name of the video
                - subtitle_info: Dictionary containing subtitle information
                - metadata: Dictionary containing video metadata
                - processed_at: ISO format timestamp of when the video was processed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO videos 
                    (file_path, official_name, subtitle_info, metadata, processed_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    video_info["file_path"],
                    video_info["official_name"],
                    json.dumps(video_info["subtitle_info"]),
                    json.dumps(video_info["metadata"]),
                    video_info["processed_at"]
                ))
                
                conn.commit()
                logger.info(f"Saved video info for: {video_info['file_path']}")
                
            except Exception as e:
                logger.error(f"Error saving video info: {str(e)}")
                raise
    
    def get_video_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get video information from database.
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dictionary containing video information or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT file_path, official_name, subtitle_info, metadata, processed_at
                    FROM videos
                    WHERE file_path = ?
                """, (file_path,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                    
                return {
                    "file_path": row[0],
                    "official_name": row[1],
                    "subtitle_info": json.loads(row[2]) if row[2] else {},
                    "metadata": json.loads(row[3]) if row[3] else {},
                    "processed_at": row[4]
                }
                
            except Exception as e:
                logger.error(f"Error getting video info: {str(e)}")
                return None
    
    def list_videos(self) -> List[Dict[str, Any]]:
        """
        List all processed videos.
        
        Returns:
            List of dictionaries containing video information
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT file_path, official_name, subtitle_info, metadata, processed_at
                    FROM videos
                    ORDER BY processed_at DESC
                """)
                
                videos = []
                for row in cursor.fetchall():
                    videos.append({
                        "file_path": row[0],
                        "official_name": row[1],
                        "subtitle_info": json.loads(row[2]) if row[2] else {},
                        "metadata": json.loads(row[3]) if row[3] else {},
                        "processed_at": row[4]
                    })
                    
                return videos
                
            except Exception as e:
                logger.error(f"Error listing videos: {str(e)}")
                return []
    
    def delete_video(self, file_path: str) -> bool:
        """
        Delete video information from database.
        
        Args:
            file_path: Path to video file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    DELETE FROM videos
                    WHERE file_path = ?
                """, (file_path,))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                logger.error(f"Error deleting video: {str(e)}")
                return False 
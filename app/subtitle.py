import os
import subprocess
from typing import Dict, Any, List, Optional
from .log import logger

class SubtitleExtractor:
    def __init__(self, output_dir: str = "output/subtitles"):
        """Initialize the subtitle extractor."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if CCExtractor is available
        try:
            subprocess.run(["ccextractor", "--version"], capture_output=True)
        except FileNotFoundError:
            logger.warning("CCExtractor not found. Closed caption extraction will be disabled.")
    
    def extract(self, video_path: str) -> Dict[str, Any]:
        """
        Extract subtitles from a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing:
                - source_type: Type of subtitle source ("embedded" or "none")
                - subtitles: List of dictionaries containing:
                    - language: Language code of the subtitle
                    - content_path: Path to the extracted subtitle file
        """
        try:
            # Get subtitle streams
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-select_streams", "s",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to get subtitle streams: {result.stderr}")
                return {"source_type": "none", "subtitles": []}
            
            # Parse subtitle streams
            import json
            data = json.loads(result.stdout)
            if not data.get("streams"):
                logger.info("No subtitle streams found")
                return {"source_type": "none", "subtitles": []}
            
            # Extract each subtitle stream
            subtitles = []
            for stream in data["streams"]:
                language = stream.get("tags", {}).get("language", "unknown")
                index = stream["index"]
                
                # Generate output path
                output_path = os.path.join(
                    self.output_dir,
                    f"{os.path.splitext(os.path.basename(video_path))[0]}_{language}.srt"
                )
                
                # Extract subtitle
                cmd = [
                    "ffmpeg",
                    "-v", "quiet",
                    "-i", video_path,
                    "-map", f"0:{index}",
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    subtitles.append({
                        "language": language,
                        "content_path": output_path
                    })
                else:
                    logger.error(f"Failed to extract subtitle stream {index}: {result.stderr}")
            
            if subtitles:
                return {
                    "source_type": "embedded",
                    "subtitles": subtitles
                }
            else:
                return {"source_type": "none", "subtitles": []}
            
        except Exception as e:
            logger.error(f"Error extracting subtitles: {str(e)}")
            return {"source_type": "none", "subtitles": []} 
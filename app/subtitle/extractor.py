import os
import subprocess
import json
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SubtitleExtractor:
    """Class for extracting subtitles from video files using FFmpeg and CCExtractor"""
    
    def __init__(self, ffmpeg_path="ffmpeg", ffprobe_path="ffprobe", ccextractor_path="ccextractor"):
        """Initialize with paths to required binaries"""
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self.ccextractor_path = ccextractor_path
    
    def analyze_video(self, video_path):
        """Analyze video to detect available subtitle streams"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Extract subtitle streams
            subtitle_streams = []
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "subtitle":
                    subtitle_streams.append({
                        "index": stream.get("index"),
                        "codec": stream.get("codec_name"),
                        "language": stream.get("tags", {}).get("language", "unknown"),
                        "title": stream.get("tags", {}).get("title", "")
                    })
            
            return {
                "format": data.get("format", {}),
                "subtitle_streams": subtitle_streams
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error analyzing video: {e}")
            raise RuntimeError(f"Failed to analyze video: {e.stderr}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing ffprobe output: {e}")
            raise RuntimeError(f"Failed to parse ffprobe output: {e}")
    
    def extract_embedded_subtitle(self, video_path, output_path=None, stream_index=0, format="srt", encoding="utf-8"):
        """Extract embedded subtitle from a specific stream"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # If output_path is not specified, use video filename with format extension
        if output_path is None:
            video_name = Path(video_path).stem
            output_path = f"{video_name}.{format}"
        
        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-map", f"0:s:{stream_index}",
            "-c:s", format,
            "-f", format,
            output_path
        ]
        
        if encoding:
            cmd.insert(1, "-sub_charenc")
            cmd.insert(2, encoding)
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Read the subtitle content
            with open(output_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "path": output_path,
                "format": format,
                "content": content
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting subtitle: {e}")
            raise RuntimeError(f"Failed to extract subtitle: {e.stderr}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error with encoding {encoding}: {e}")
            raise RuntimeError(f"Failed to read subtitle with encoding {encoding}")
    
    def extract_all_embedded_subtitles(self, video_path, output_dir=None, format="srt", encoding="utf-8"):
        """Extract all embedded subtitles from the video"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Analyze video to get subtitle streams
        analysis = self.analyze_video(video_path)
        subtitle_streams = analysis.get("subtitle_streams", [])
        
        if not subtitle_streams:
            logger.info(f"No subtitle streams found in {video_path}")
            return []
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract each subtitle
        results = []
        for i, stream in enumerate(subtitle_streams):
            language = stream.get("language", "unknown")
            stream_index = i  # Use the index within subtitle streams
            
            output_path = os.path.join(
                output_dir, 
                f"{Path(video_path).stem}_{language}.{format}"
            )
            
            try:
                result = self.extract_embedded_subtitle(
                    video_path, 
                    output_path, 
                    stream_index,
                    format,
                    encoding
                )
                result["language"] = language
                results.append(result)
            except Exception as e:
                logger.error(f"Error extracting subtitle stream {stream_index}: {e}")
        
        return results
    
    def extract_with_ccextractor(self, video_path, output_dir=None, format="srt"):
        """Extract subtitles using CCExtractor (for formats not supported by FFmpeg)"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{Path(video_path).stem}.{format}")
        
        cmd = [
            self.ccextractor_path,
            video_path,
            "-o", output_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    "path": output_path,
                    "format": format,
                    "content": content,
                    "language": "unknown"  # CCExtractor doesn't provide language info
                }
            else:
                logger.warning(f"CCExtractor didn't produce output file: {output_path}")
                return None
        except subprocess.CalledProcessError as e:
            logger.error(f"Error using CCExtractor: {e}")
            raise RuntimeError(f"Failed to extract subtitles with CCExtractor: {e.stderr}")
    
    def extract_subtitles(self, video_path, output_dir=None, formats=None):
        """
        Extract subtitles from a video using multiple methods.
        
        This method tries:
        1. Extract embedded subtitles with FFmpeg
        2. If no embedded subtitles found, try CCExtractor as fallback
        """
        formats = formats or ["srt"]
        
        # First try FFmpeg for embedded subtitles
        subtitles = []
        try:
            embedded_results = self.extract_all_embedded_subtitles(
                video_path, 
                output_dir=output_dir,
                format=formats[0]
            )
            subtitles.extend(embedded_results)
        except Exception as e:
            logger.error(f"Error extracting embedded subtitles: {e}")
        
        # If no embedded subtitles found, try CCExtractor
        if not subtitles:
            try:
                cc_result = self.extract_with_ccextractor(
                    video_path, 
                    output_dir=output_dir,
                    format=formats[0]
                )
                if cc_result:
                    subtitles.append(cc_result)
            except Exception as e:
                logger.error(f"Error extracting subtitles with CCExtractor: {e}")
        
        return subtitles 
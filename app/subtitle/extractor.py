import os
import subprocess
import json
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any
import ffmpeg

logger = logging.getLogger(__name__)

class SubtitleExtractor:
    """Class for extracting subtitles from video files using FFmpeg and CCExtractor"""
    
    def __init__(self):
        self.output_dir = os.getenv('OUTPUT_DIR', 'output/subtitles')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Check for CCExtractor
        self.has_ccextractor = self._check_ccextractor()
        if not self.has_ccextractor:
            logger.warning("CCExtractor not found. Closed caption extraction will be disabled.")
    
    def _check_ccextractor(self) -> bool:
        """Check if CCExtractor is available"""
        try:
            subprocess.run(['ccextractor', '--version'], capture_output=True)
            return True
        except FileNotFoundError:
            return False
    
    def analyze_video(self, video_path):
        """Analyze video to detect available subtitle streams"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cmd = [
            "ffprobe",
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
    
    def extract_embedded(self, video_path: str) -> List[Dict[str, Any]]:
        """Extract embedded subtitles using FFmpeg"""
        try:
            # Get video info
            probe = ffmpeg.probe(video_path)
            
            results = []
            video_name = Path(video_path).stem
            
            # Find subtitle streams
            for stream in probe['streams']:
                if stream['codec_type'] == 'subtitle':
                    language = stream.get('tags', {}).get('language', 'unknown')
                    stream_index = stream['index']
                    
                    # Create output path
                    output_path = os.path.join(
                        self.output_dir,
                        f"{video_name}_{language}_{stream_index}.srt"
                    )
                    
                    # Extract subtitle
                    try:
                        (
                            ffmpeg
                            .input(video_path)
                            .output(output_path, map=f"0:{stream_index}")
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
                        
                        results.append({
                            'language': language,
                            'source_type': 'embedded',
                            'content_path': output_path
                        })
                    except ffmpeg.Error as e:
                        logger.error(f"Error extracting subtitle stream {stream_index}: {str(e)}")
                        continue
            
            return results
            
        except ffmpeg.Error as e:
            logger.error(f"Error probing video {video_path}: {str(e)}")
            return []

    def extract_external(self, video_path: str) -> List[Dict[str, Any]]:
        """Look for external subtitle files"""
        results = []
        video_dir = os.path.dirname(video_path)
        video_name = Path(video_path).stem
        
        # Common subtitle extensions
        subtitle_extensions = ['.srt', '.ass', '.ssa', '.sub', '.smi', '.vtt']
        
        for ext in subtitle_extensions:
            # Look for exact match
            sub_path = os.path.join(video_dir, video_name + ext)
            if os.path.exists(sub_path):
                results.append({
                    'language': 'unknown',  # Could try to detect language
                    'source_type': 'external',
                    'content_path': sub_path
                })
            
            # Look for language-coded subtitles (e.g. movie.en.srt)
            for sub_file in Path(video_dir).glob(f"{video_name}.??{ext}"):
                lang_code = sub_file.stem.split('.')[-1]
                results.append({
                    'language': lang_code,
                    'source_type': 'external',
                    'content_path': str(sub_file)
                })
        
        return results

    def extract_closed_captions(self, video_path: str) -> List[Dict[str, Any]]:
        """Extract closed captions using CCExtractor if available"""
        if not self.has_ccextractor:
            return []
            
        try:
            video_name = Path(video_path).stem
            output_path = os.path.join(self.output_dir, f"{video_name}_cc.srt")
            
            # Run CCExtractor
            result = subprocess.run(
                ['ccextractor', video_path, '-o', output_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                return [{
                    'language': 'unknown',  # CCExtractor doesn't provide language info
                    'source_type': 'closed_caption',
                    'content_path': output_path
                }]
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting closed captions: {str(e)}")
            return []

    def extract_all(self, video_path: str) -> List[Dict[str, Any]]:
        """Extract all available subtitles from a video file"""
        results = []
        
        # Extract embedded subtitles
        embedded_subs = self.extract_embedded(video_path)
        results.extend(embedded_subs)
        
        # Look for external subtitle files
        external_subs = self.extract_external(video_path)
        results.extend(external_subs)
        
        # Extract closed captions if available and no other subtitles found
        if not results and self.has_ccextractor:
            cc_subs = self.extract_closed_captions(video_path)
            results.extend(cc_subs)
        
        return results
    
    def extract_embedded_subtitle(self, video_path, output_path=None, stream_index=0, format="srt", encoding="utf-8"):
        """Extract embedded subtitle from a specific stream"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # If output_path is not specified, use video filename with format extension
        if output_path is None:
            video_name = Path(video_path).stem
            output_path = f"{video_name}.{format}"
        
        cmd = [
            "ffmpeg",
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
            "ccextractor",
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
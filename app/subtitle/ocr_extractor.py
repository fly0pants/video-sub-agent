import os
import cv2
import numpy as np
import subprocess
import tempfile
import logging
import pytesseract
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class OCRSubtitleExtractor:
    """Class for extracting hard-coded subtitles using OCR"""
    
    def __init__(self, ffmpeg_path="ffmpeg", tesseract_cmd=None):
        """Initialize with paths to required binaries"""
        self.ffmpeg_path = ffmpeg_path
        
        # Set Tesseract command path if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_frames(self, video_path, output_dir=None, interval=1.0):
        """
        Extract frames from a video at specified intervals
        
        Args:
            video_path: Path to the video file
            output_dir: Directory to save extracted frames
            interval: Time interval between frames in seconds
        
        Returns:
            List of paths to extracted frames
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        os.makedirs(output_dir, exist_ok=True)
        
        # Get video duration using ffprobe
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.error(f"Error getting video duration: {e}")
            raise RuntimeError(f"Failed to get video duration: {e}")
        
        # Calculate frame timestamps
        timestamps = np.arange(0, duration, interval)
        
        # Extract frames at each timestamp
        frame_paths = []
        for i, timestamp in enumerate(timestamps):
            output_path = os.path.join(output_dir, f"frame_{i:06d}.jpg")
            
            cmd = [
                self.ffmpeg_path,
                "-ss", str(timestamp),
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                output_path
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                frame_paths.append((timestamp, output_path))
            except subprocess.CalledProcessError as e:
                logger.error(f"Error extracting frame at {timestamp}s: {e}")
        
        return frame_paths
    
    def detect_subtitle_region(self, image_path):
        """
        Detect the region in the frame that likely contains subtitles
        Often at the bottom 1/4 of the frame
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (x, y, width, height) for the subtitle region
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        height, width = image.shape[:2]
        
        # Typically, subtitles appear in the bottom quarter of the screen
        # But we can make this more sophisticated with edge detection, etc.
        subtitle_region = (0, int(height * 0.75), width, int(height * 0.25))
        
        return subtitle_region
    
    def preprocess_subtitle_region(self, image_path, region=None):
        """
        Preprocess the subtitle region to enhance OCR accuracy
        
        Args:
            image_path: Path to the image
            region: Optional tuple (x, y, width, height) to crop
            
        Returns:
            Preprocessed image
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Crop to subtitle region if specified
        if region:
            x, y, w, h = region
            image = image[y:y+h, x:x+w]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply binary thresholding
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Noise removal with morphological operations
        kernel = np.ones((2, 2), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Invert back for OCR
        processed = cv2.bitwise_not(opening)
        
        return processed
    
    def extract_text_from_frame(self, image_path, lang='eng'):
        """
        Extract text from a frame using OCR
        
        Args:
            image_path: Path to the image
            lang: Language code for OCR
            
        Returns:
            Extracted text
        """
        # Detect subtitle region
        region = self.detect_subtitle_region(image_path)
        
        # Preprocess image
        processed_image = self.preprocess_subtitle_region(image_path, region)
        
        # Apply OCR
        text = pytesseract.image_to_string(processed_image, lang=lang)
        
        # Clean text (remove newlines, multiple spaces)
        text = text.strip()
        
        return text
    
    def create_srt_content(self, frame_texts):
        """
        Convert frame texts to SRT format
        
        Args:
            frame_texts: List of tuples (timestamp, text)
            
        Returns:
            SRT formatted content
        """
        srt_content = ""
        
        # Filter out empty texts
        frame_texts = [(ts, text) for ts, text in frame_texts if text.strip()]
        
        for i, (timestamp, text) in enumerate(frame_texts):
            # Calculate start and end times for this subtitle
            start_time = timestamp
            if i < len(frame_texts) - 1:
                end_time = frame_texts[i+1][0]
            else:
                end_time = start_time + 5.0  # Assume 5 seconds for the last subtitle
            
            # Format times as HH:MM:SS,mmm
            start_formatted = self._format_timestamp(start_time)
            end_formatted = self._format_timestamp(end_time)
            
            # Add subtitle entry to SRT content
            srt_content += f"{i+1}\n"
            srt_content += f"{start_formatted} --> {end_formatted}\n"
            srt_content += f"{text}\n\n"
        
        return srt_content
    
    def _format_timestamp(self, seconds):
        """Format timestamp for SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def extract_hardcoded_subtitles(self, video_path, output_path=None, interval=1.0, lang='eng'):
        """
        Extract hardcoded subtitles from a video using OCR
        
        Args:
            video_path: Path to the video file
            output_path: Path to save the SRT file
            interval: Time interval between frames in seconds
            lang: Language code for OCR
            
        Returns:
            Dictionary with path, format, content, and language
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create temporary directory for frames
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extract frames
            frame_paths = self.extract_frames(video_path, temp_dir, interval)
            
            # Extract text from each frame
            frame_texts = []
            for timestamp, frame_path in frame_paths:
                try:
                    text = self.extract_text_from_frame(frame_path, lang)
                    
                    # Only add if text is not empty and not just noise
                    if text.strip() and len(text.strip()) > 3:
                        frame_texts.append((timestamp, text))
                except Exception as e:
                    logger.error(f"Error extracting text from frame {frame_path}: {e}")
            
            # Create SRT content
            srt_content = self.create_srt_content(frame_texts)
            
            # Save to file if output_path specified
            if output_path is None:
                video_name = Path(video_path).stem
                output_path = f"{video_name}_ocr.srt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return {
                "path": output_path,
                "format": "srt",
                "content": srt_content,
                "language": lang
            }
        finally:
            # Clean up temporary files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True) 
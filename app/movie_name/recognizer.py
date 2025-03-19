import os
import re
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class MovieNameRecognizer:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        
        self.api_base = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
        self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

    def clean_filename(self, filename: str) -> str:
        # Remove common video file extensions
        filename = re.sub(r'\.(mp4|mkv|avi|mov|wmv)$', '', filename)
        
        # Remove resolution info
        filename = re.sub(r'\b(480p|720p|1080p|2160p|4K)\b', '', filename)
        
        # Remove year if in brackets
        filename = re.sub(r'\[\d{4}\]', '', filename)
        
        # Remove common tags
        filename = re.sub(r'\b(BluRay|BRRip|DVDRip|HDRip|WEBRip|x264|x265|HEVC|AAC|AC3)\b', '', filename)
        
        # Remove brackets and their contents, but preserve Chinese characters inside brackets
        def preserve_chinese(match):
            content = match.group(0)[1:-1]  # Remove brackets
            if any('\u4e00' <= c <= '\u9fff' for c in content):
                return content
            return ' '
        filename = re.sub(r'\[.*?\]', preserve_chinese, filename)
        
        # Remove parentheses and their contents, but preserve Chinese characters
        filename = re.sub(r'\(.*?\)', preserve_chinese, filename)
        
        # Clean up spaces and punctuation
        filename = re.sub(r'[._]', ' ', filename)
        filename = re.sub(r'\s+', ' ', filename)
        
        return filename.strip()

    def recognize(self, filename: str) -> Optional[str]:
        try:
            # Clean the filename first
            cleaned_name = self.clean_filename(filename)
            
            # Prepare the prompt
            messages = [
                {"role": "system", "content": """You are a movie name recognition expert. Your task is to identify the official movie name from potentially non-standard filenames.
For Chinese movies, provide both Chinese and English names if available.
Respond with ONLY the official movie name(s), nothing else.
If you're not confident, respond with just 'Unknown'."""},
                {"role": "user", "content": f"What is the official movie name for this filename: {cleaned_name}"}
            ]
            
            # Call DeepSeek API
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 100
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Get the response
            official_name = data['choices'][0]['message']['content'].strip()
            
            # Return None if the model couldn't recognize the name
            if official_name.lower() == 'unknown':
                return None
                
            return official_name
            
        except Exception as e:
            logger.error(f"Error recognizing movie name: {str(e)}")
            return None

    def recognize_movie_name(self, filename):
        """
        Recognize official movie name from filename
        
        Args:
            filename: The filename or partial movie name
            
        Returns:
            Official movie name as recognized by LLM
        """
        # Extract just the filename without extension if a path is given
        if os.path.sep in filename:
            filename = os.path.basename(filename)
        
        # Remove file extension if present
        name_without_ext = os.path.splitext(filename)[0]
        
        # Construct prompt for LLM
        prompt = f"""The filename of a video is '{name_without_ext}'. 
Please identify the official full name of this movie or TV show.
If it's a TV show, include the season and episode number if present.
Just provide the official name, no explanations or other text."""
        
        try:
            # Call the LLM API
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a movie name recognition expert. Your task is to identify the official movie name from potentially non-standard filenames."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 50
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract the official name from the response
            official_name = data['choices'][0]['message']['content'].strip()
            logger.info(f"Recognized '{name_without_ext}' as '{official_name}'")
            
            return official_name
        except Exception as e:
            logger.error(f"Error recognizing movie name: {e}")
            raise RuntimeError(f"Failed to recognize movie name: {e}")
    
    def recognize_batch(self, filenames):
        """
        Recognize official movie names for multiple files
        
        Args:
            filenames: List of filenames
            
        Returns:
            Dictionary mapping original filenames to official names
        """
        results = {}
        for filename in filenames:
            try:
                official_name = self.recognize(filename)
                results[filename] = official_name
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                results[filename] = None
        
        return results 
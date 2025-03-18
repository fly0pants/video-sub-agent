import os
import logging
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class MovieNameRecognizer:
    """Class for recognizing official movie names using LLM"""
    
    def __init__(self, api_key=None, api_base=None, model="deepseek-coder"):
        """
        Initialize with API key and configuration
        
        Args:
            api_key: API key for LLM service (Deepseek or OpenAI)
            api_base: API base URL (for Deepseek, use their API URL)
            model: Model name to use
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set DEEPSEEK_API_KEY environment variable or pass api_key.")
        
        self.api_base = api_base
        self.model = model
        
        # Initialize OpenAI client (compatible with Deepseek)
        openai.api_key = self.api_key
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        ) if self.api_base else OpenAI(api_key=self.api_key)
    
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in identifying official movie and TV show titles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Low temperature for more deterministic output
                max_tokens=100    # We need only a short response
            )
            
            # Extract the official name from the response
            official_name = response.choices[0].message.content.strip()
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
                official_name = self.recognize_movie_name(filename)
                results[filename] = official_name
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                results[filename] = None
        
        return results 
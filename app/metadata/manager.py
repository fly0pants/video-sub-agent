import os
import json
import requests
from typing import Dict, Any, Optional
from ..log import logger

class MetadataManager:
    def __init__(self):
        """Initialize the metadata manager with API keys."""
        self.tmdb_api_key = os.getenv("TMDB_API_KEY")
        self.omdb_api_key = os.getenv("OMDB_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not self.deepseek_api_key or self.deepseek_api_key == "your_deepseek_api_key":
            logger.warning(
                "DeepSeek API key not found or invalid. To use DeepSeek for metadata generation:"
                "\n1. Get an API key at https://platform.deepseek.com/"
                "\n2. Add your API key to the .env file as DEEPSEEK_API_KEY"
            )
        
        if not self.tmdb_api_key or self.tmdb_api_key == "your_tmdb_api_key":
            logger.warning(
                "TMDB API key not found. To fetch movie metadata:"
                "\n1. Get an API key at https://www.themoviedb.org/settings/api"
                "\n2. Add your API key to the .env file"
            )
        
        if not self.omdb_api_key or self.omdb_api_key == "your_omdb_api_key":
            logger.warning(
                "OMDB API key not found. To fetch additional movie metadata:"
                "\n1. Get an API key at https://www.omdbapi.com/apikey.aspx"
                "\n2. Add your API key to the .env file"
            )
    
    def _generate_metadata_with_deepseek(self, movie_name: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Generate movie metadata using DeepSeek AI.
        
        Args:
            movie_name: Name of the movie
            year: Optional release year
            
        Returns:
            Dictionary containing movie metadata if successful, None otherwise
        """
        if not self.deepseek_api_key or self.deepseek_api_key == "your_deepseek_api_key":
            return None
            
        try:
            logger.info(f"Generating metadata for '{movie_name}' using DeepSeek AI")
            
            # Construct improved prompt for DeepSeek
            prompt = f"""Please generate comprehensive and accurate metadata for the movie "{movie_name}".
"""
            if year:
                prompt += f"This movie was released in the year {year}.\n"
                
            prompt += """
I need the most accurate information possible, especially for movies from China, Japan, or other non-English speaking countries.

Return the information as a well-structured JSON object with the following fields:
- title: The official English title
- original_title: The original title in the movie's native language
- release_date: in YYYY-MM-DD format
- runtime: in minutes
- overview: A concise 2-3 sentence plot summary
- genres: Array of genres
- director: Name of the director
- actors: Array of main cast members (top 5-8 actors)
- language: Primary language of the film
- country: Country of origin
- imdb_id: The IMDb ID (e.g., "tt0111161") - this is EXTREMELY important for subtitle searches
- imdb_rating: Numerical IMDb rating if known

For accuracy:
1. If the movie is non-English, make sure to provide both the original title and English title
2. Ensure the IMDb ID is correct and in the format "tt" followed by 7-8 digits
3. If you don't know any specific field with certainty, either exclude it or mark it as null rather than guessing

If multiple movies have similar names, prioritize the most well-known or recent one, unless the year parameter indicates otherwise."""

            # Make API call to DeepSeek
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a movie database expert with comprehensive knowledge of international cinema, including Chinese, Japanese, and other foreign films. Your expertise includes accurate IMDb IDs, original language titles, and official translations. Always provide the most accurate and complete metadata possible."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
            )
            
            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.text}")
                return None
                
            # Parse response
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                logger.error("Empty response from DeepSeek API")
                return None
                
            try:
                metadata = json.loads(content)
                logger.info(f"Successfully generated metadata for '{movie_name}' using DeepSeek AI")
                return metadata
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response from DeepSeek API")
                return None
                
        except Exception as e:
            logger.error(f"Error generating metadata with DeepSeek: {str(e)}")
            return None
    
    def get_tmdb_id(self, movie_name: str, year: Optional[int] = None) -> Optional[str]:
        """
        Get TMDB ID for a movie by its name.
        
        Args:
            movie_name: Name of the movie
            year: Optional release year
            
        Returns:
            TMDB ID if found, None otherwise
        """
        if not self.tmdb_api_key:
            return None
            
        try:
            # Search for movie
            response = requests.get(
                "https://api.themoviedb.org/3/search/movie",
                params={
                    "api_key": self.tmdb_api_key,
                    "query": movie_name,
                    "language": "en-US",
                    "include_adult": "true",
                    "page": 1,
                    **({"primary_release_year": year} if year else {})
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to search movie: {response.text}")
                return None
                
            data = response.json()
            if not data.get("results"):
                logger.warning(f"No results found for movie: {movie_name}")
                return None
                
            # Return ID of first result
            return str(data["results"][0]["id"])
            
        except Exception as e:
            logger.error(f"Error getting TMDB ID: {str(e)}")
            return None
    
    def get_imdb_id(self, tmdb_id: str) -> Optional[str]:
        """
        Get IMDb ID for a movie by its TMDB ID.
        
        Args:
            tmdb_id: TMDB ID of the movie
            
        Returns:
            IMDb ID if found, None otherwise
        """
        if not self.tmdb_api_key:
            return None
            
        try:
            # Get movie details
            response = requests.get(
                f"https://api.themoviedb.org/3/movie/{tmdb_id}",
                params={
                    "api_key": self.tmdb_api_key,
                    "append_to_response": "external_ids"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get movie details: {response.text}")
                return None
                
            data = response.json()
            return data.get("imdb_id")
            
        except Exception as e:
            logger.error(f"Error getting IMDb ID: {str(e)}")
            return None
    
    def fetch_metadata(self, movie_name: str, *, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch metadata for a movie from DeepSeek AI, TMDB, and OMDB APIs.
        Priority order: DeepSeek AI > TMDB > OMDB
        
        Args:
            movie_name: Name of the movie
            year: Optional release year
            
        Returns:
            Dictionary containing movie metadata
        """
        # First try DeepSeek AI
        deepseek_metadata = self._generate_metadata_with_deepseek(movie_name, year)
        if deepseek_metadata:
            logger.info(f"Using DeepSeek AI generated metadata for movie: {movie_name}")
            return deepseek_metadata
            
        # If DeepSeek fails, fall back to TMDB and OMDB
        logger.info(f"DeepSeek failed or not configured, falling back to TMDB/OMDB for movie: {movie_name}")
        metadata = {}
        
        # Get TMDB metadata
        if self.tmdb_api_key:
            try:
                tmdb_id = self.get_tmdb_id(movie_name) if year is None else self.get_tmdb_id(movie_name, year)
                if tmdb_id:
                    # Get movie details
                    response = requests.get(
                        f"https://api.themoviedb.org/3/movie/{tmdb_id}",
                        params={
                            "api_key": self.tmdb_api_key,
                            "append_to_response": "credits,external_ids"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        metadata.update({
                            "tmdb_id": str(data["id"]),
                            "imdb_id": data.get("imdb_id"),
                            "title": data["title"],
                            "original_title": data["original_title"],
                            "release_date": data["release_date"],
                            "runtime": data["runtime"],
                            "overview": data["overview"],
                            "poster_path": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None,
                            "genres": [genre["name"] for genre in data["genres"]],
                            "actors": [
                                {
                                    "name": cast["name"],
                                    "character": cast["character"],
                                    "profile_path": f"https://image.tmdb.org/t/p/w185{cast['profile_path']}" if cast.get("profile_path") else None
                                }
                                for cast in data["credits"]["cast"][:10]  # Get top 10 actors
                            ]
                        })
            except Exception as e:
                logger.error(f"Error fetching TMDB metadata: {str(e)}")
        
        # Get OMDB metadata if IMDb ID is available
        if self.omdb_api_key and metadata.get("imdb_id"):
            try:
                response = requests.get(
                    "http://www.omdbapi.com/",
                    params={
                        "apikey": self.omdb_api_key,
                        "i": metadata["imdb_id"]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("Response") == "True":
                        metadata.update({
                            "rated": data.get("Rated"),
                            "awards": data.get("Awards"),
                            "ratings": data.get("Ratings", []),
                            "box_office": data.get("BoxOffice"),
                            "production": data.get("Production")
                        })
            except Exception as e:
                logger.error(f"Error fetching OMDB metadata: {str(e)}")
        
        return metadata 
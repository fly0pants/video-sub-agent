import os
import requests
from typing import Dict, Any, Optional
from .log import logger

class MetadataManager:
    def __init__(self):
        """Initialize the metadata manager."""
        self.tmdb_api_key = os.getenv("TMDB_API_KEY")
        self.omdb_api_key = os.getenv("OMDB_API_KEY")
        
        if not self.tmdb_api_key or self.tmdb_api_key == "your_tmdb_api_key":
            logger.warning(
                "TMDB API key not found or invalid. To fetch movie metadata:"
                "\n1. Get an API key at https://www.themoviedb.org/settings/api"
                "\n2. Add your API key to the .env file"
            )
            
        if not self.omdb_api_key or self.omdb_api_key == "your_omdb_api_key":
            logger.warning(
                "OMDB API key not found or invalid. To fetch additional movie metadata:"
                "\n1. Get an API key at https://www.omdbapi.com/apikey.aspx"
                "\n2. Add your API key to the .env file"
            )
            
    def fetch_metadata(self, movie_name: str, *, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch movie metadata from TMDB and OMDB.
        
        Args:
            movie_name: Movie name
            year: Optional release year
            
        Returns:
            Dictionary containing movie metadata if successful, None otherwise
        """
        try:
            # First try TMDB
            tmdb_data = self._search_tmdb(movie_name, year)
            if not tmdb_data:
                return None
                
            # Get IMDb ID from TMDB
            imdb_id = self._get_imdb_id(tmdb_data["id"])
            if not imdb_id:
                return tmdb_data
                
            # Then try OMDB using IMDb ID
            omdb_data = self._search_omdb(imdb_id)
            if not omdb_data:
                return tmdb_data
                
            # Merge TMDB and OMDB data
            metadata = {
                "tmdb_id": tmdb_data["id"],
                "imdb_id": imdb_id,
                "title": tmdb_data["title"],
                "original_title": tmdb_data["original_title"],
                "overview": tmdb_data["overview"],
                "release_date": tmdb_data["release_date"],
                "poster_path": f"https://image.tmdb.org/t/p/original{tmdb_data['poster_path']}" if tmdb_data.get("poster_path") else None,
                "backdrop_path": f"https://image.tmdb.org/t/p/original{tmdb_data['backdrop_path']}" if tmdb_data.get("backdrop_path") else None,
                "runtime": omdb_data.get("Runtime"),
                "genre": omdb_data.get("Genre"),
                "director": omdb_data.get("Director"),
                "actors": omdb_data.get("Actors"),
                "language": omdb_data.get("Language"),
                "country": omdb_data.get("Country"),
                "awards": omdb_data.get("Awards"),
                "imdb_rating": omdb_data.get("imdbRating"),
                "imdb_votes": omdb_data.get("imdbVotes"),
                "box_office": omdb_data.get("BoxOffice")
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error fetching metadata: {str(e)}")
            return None
            
    def _search_tmdb(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Search for a movie on TMDB.
        
        Args:
            title: Movie title
            year: Optional release year
            
        Returns:
            Dictionary containing TMDB data if successful, None otherwise
        """
        if not self.tmdb_api_key:
            return None
            
        try:
            # Prepare search parameters
            params = {
                "api_key": self.tmdb_api_key,
                "query": title,
                "language": "en-US",
                "include_adult": "true",
                "page": 1
            }
            if year:
                params["primary_release_year"] = year
                
            # Search for movie
            response = requests.get(
                "https://api.themoviedb.org/3/search/movie",
                params=params
            )
            
            if response.status_code != 200:
                logger.error(f"TMDB API error: {response.text}")
                return None
                
            data = response.json()
            if not data.get("results"):
                logger.warning(f"No results found for movie: {title}")
                return None
                
            # Return first result
            return data["results"][0]
            
        except Exception as e:
            logger.error(f"Error searching TMDB: {str(e)}")
            return None
            
    def _get_imdb_id(self, tmdb_id: int) -> Optional[str]:
        """
        Get IMDb ID from TMDB ID.
        
        Args:
            tmdb_id: TMDB movie ID
            
        Returns:
            IMDb ID if successful, None otherwise
        """
        if not self.tmdb_api_key:
            return None
            
        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids",
                params={"api_key": self.tmdb_api_key}
            )
            
            if response.status_code != 200:
                logger.error(f"TMDB API error: {response.text}")
                return None
                
            data = response.json()
            return data.get("imdb_id")
            
        except Exception as e:
            logger.error(f"Error getting IMDb ID: {str(e)}")
            return None
            
    def _search_omdb(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for a movie on OMDB using IMDb ID.
        
        Args:
            imdb_id: IMDb ID
            
        Returns:
            Dictionary containing OMDB data if successful, None otherwise
        """
        if not self.omdb_api_key:
            return None
            
        try:
            response = requests.get(
                "http://www.omdbapi.com/",
                params={
                    "apikey": self.omdb_api_key,
                    "i": imdb_id
                }
            )
            
            if response.status_code != 200:
                logger.error(f"OMDB API error: {response.text}")
                return None
                
            data = response.json()
            if data.get("Response") == "False":
                logger.warning(f"No results found for IMDb ID: {imdb_id}")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Error searching OMDB: {str(e)}")
            return None 
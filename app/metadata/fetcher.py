import os
import logging
import requests
import tmdbsimple as tmdb
import json
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class TMDBFetcher:
    """Class for fetching metadata from The Movie Database (TMDB)"""
    
    def __init__(self, api_key=None):
        """
        Initialize with TMDB API key
        
        Args:
            api_key: TMDB API key
        """
        self.api_key = api_key or os.environ.get("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError("TMDB API key is required. Set TMDB_API_KEY environment variable or pass api_key.")
        
        # Configure tmdbsimple
        tmdb.API_KEY = self.api_key
    
    def search(self, query, search_type="movie", year=None):
        """
        Search for movies, TV shows, or people
        
        Args:
            query: Search query
            search_type: Type of search (movie, tv, person)
            year: Optional year to filter results
            
        Returns:
            Search results
        """
        search = tmdb.Search()
        kwargs = {"query": query}
        
        if year:
            if search_type == "movie":
                kwargs["year"] = year
            elif search_type == "tv":
                kwargs["first_air_date_year"] = year
        
        # Execute search based on type
        if search_type == "movie":
            search.movie(**kwargs)
        elif search_type == "tv":
            search.tv(**kwargs)
        elif search_type == "person":
            search.person(**kwargs)
        else:
            raise ValueError(f"Invalid search type: {search_type}")
        
        return search.results
    
    def get_movie_details(self, movie_id):
        """
        Get detailed information about a movie
        
        Args:
            movie_id: TMDB movie ID
            
        Returns:
            Detailed movie information
        """
        movie = tmdb.Movies(movie_id)
        response = movie.info(append_to_response="credits,keywords,videos,images,alternative_titles")
        return response
    
    def get_tv_details(self, tv_id):
        """
        Get detailed information about a TV show
        
        Args:
            tv_id: TMDB TV show ID
            
        Returns:
            Detailed TV show information
        """
        tv = tmdb.TV(tv_id)
        response = tv.info(append_to_response="credits,keywords,videos,images,alternative_titles")
        return response
    
    def get_metadata(self, title, is_tv=False, year=None):
        """
        Get metadata for a movie or TV show
        
        Args:
            title: Movie or TV show title
            is_tv: Whether the title is a TV show
            year: Optional year to filter results
            
        Returns:
            Metadata for the movie or TV show, or None if not found
        """
        search_type = "tv" if is_tv else "movie"
        results = self.search(title, search_type=search_type, year=year)
        
        if not results:
            logger.warning(f"No {search_type} results found for '{title}'")
            return None
        
        # Get the top result
        top_result = results[0]
        
        # Get detailed information
        if is_tv:
            details = self.get_tv_details(top_result["id"])
        else:
            details = self.get_movie_details(top_result["id"])
        
        return details


class OMDBFetcher:
    """Class for fetching metadata from Open Movie Database (OMDb)"""
    
    def __init__(self, api_key=None):
        """
        Initialize with OMDb API key
        
        Args:
            api_key: OMDb API key
        """
        self.api_key = api_key or os.environ.get("OMDB_API_KEY")
        if not self.api_key:
            raise ValueError("OMDb API key is required. Set OMDB_API_KEY environment variable or pass api_key.")
        
        self.base_url = "http://www.omdbapi.com/"
    
    def get_by_title(self, title, year=None):
        """
        Get movie or TV show information by title
        
        Args:
            title: Movie or TV show title
            year: Optional year to filter results
            
        Returns:
            Movie or TV show information, or None if not found
        """
        params = {
            "apikey": self.api_key,
            "t": title,
            "r": "json"
        }
        
        if year:
            params["y"] = year
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") == "False":
                logger.warning(f"OMDb error: {data.get('Error', 'Unknown error')}")
                return None
            
            return data
        except requests.RequestException as e:
            logger.error(f"Error fetching from OMDb: {e}")
            return None
    
    def search(self, query, type=None, year=None):
        """
        Search for movies, TV shows, or episodes
        
        Args:
            query: Search query
            type: Type of search (movie, series, episode)
            year: Optional year to filter results
            
        Returns:
            Search results, or None if not found
        """
        params = {
            "apikey": self.api_key,
            "s": query,
            "r": "json"
        }
        
        if type:
            params["type"] = type
        
        if year:
            params["y"] = year
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") == "False":
                logger.warning(f"OMDb error: {data.get('Error', 'Unknown error')}")
                return None
            
            return data.get("Search", [])
        except requests.RequestException as e:
            logger.error(f"Error searching OMDb: {e}")
            return None
    
    def get_by_imdb_id(self, imdb_id):
        """
        Get movie or TV show information by IMDb ID
        
        Args:
            imdb_id: IMDb ID
            
        Returns:
            Movie or TV show information, or None if not found
        """
        params = {
            "apikey": self.api_key,
            "i": imdb_id,
            "r": "json"
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") == "False":
                logger.warning(f"OMDb error: {data.get('Error', 'Unknown error')}")
                return None
            
            return data
        except requests.RequestException as e:
            logger.error(f"Error fetching from OMDb: {e}")
            return None


class MetadataFetcher:
    """Main class for fetching metadata from various sources"""
    
    def __init__(self):
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        self.omdb_api_key = os.getenv('OMDB_API_KEY')
        
        if not self.tmdb_api_key:
            raise ValueError("TMDB_API_KEY environment variable is not set")
        if not self.omdb_api_key:
            raise ValueError("OMDB_API_KEY environment variable is not set")
        
        tmdb.API_KEY = self.tmdb_api_key

    def search_tmdb(self, title: str) -> Optional[Dict[str, Any]]:
        try:
            search = tmdb.Search()
            response = search.movie(query=title)
            
            if not response['results']:
                return None
            
            # Get the first (most relevant) result
            movie_id = response['results'][0]['id']
            
            # Get detailed movie info
            movie = tmdb.Movies(movie_id)
            info = movie.info()
            credits = movie.credits()
            
            # Extract relevant information
            result = {
                'title': info['title'],
                'original_title': info['original_title'],
                'release_date': info['release_date'],
                'runtime': info['runtime'],
                'overview': info['overview'],
                'poster_path': info['poster_path'],
                'tmdb_id': str(info['id']),
                'imdb_id': info.get('imdb_id'),
                'genres': [genre['name'] for genre in info['genres']],
                'actors': [
                    {
                        'name': cast['name'],
                        'profile_path': cast['profile_path']
                    }
                    for cast in credits['cast'][:10]  # Get top 10 actors
                ]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching metadata from TMDB: {str(e)}")
            return None

    def search_omdb(self, title: str) -> Optional[Dict[str, Any]]:
        try:
            # Search OMDB API
            url = f"http://www.omdbapi.com/?apikey={self.omdb_api_key}&t={title}"
            response = requests.get(url)
            data = response.json()
            
            if data.get('Response') == 'False':
                return None
            
            # Extract relevant information
            result = {
                'title': data.get('Title'),
                'release_date': data.get('Released'),
                'runtime': self._parse_runtime(data.get('Runtime', '0 min')),
                'overview': data.get('Plot'),
                'poster_path': data.get('Poster'),
                'imdb_id': data.get('imdbID'),
                'genres': [genre.strip() for genre in data.get('Genre', '').split(',') if genre.strip()],
                'actors': [
                    {'name': actor.strip(), 'profile_path': None}
                    for actor in data.get('Actors', '').split(',')
                    if actor.strip()
                ]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching metadata from OMDB: {str(e)}")
            return None

    def _parse_runtime(self, runtime_str: str) -> int:
        """Convert OMDB runtime string to minutes"""
        try:
            return int(runtime_str.split()[0])
        except (IndexError, ValueError):
            return 0

    def merge_metadata(self, tmdb_data: Optional[Dict], omdb_data: Optional[Dict]) -> Optional[Dict]:
        """Merge metadata from multiple sources, preferring TMDB data"""
        if not tmdb_data and not omdb_data:
            return None
            
        # Start with TMDB data if available
        if tmdb_data:
            result = tmdb_data.copy()
            
            # Add/update with OMDB data if available
            if omdb_data:
                # Use OMDB data only for missing fields
                for key in ['overview', 'runtime']:
                    if not result.get(key) and omdb_data.get(key):
                        result[key] = omdb_data[key]
                
                # Merge genres
                if omdb_data.get('genres'):
                    existing_genres = set(result.get('genres', []))
                    for genre in omdb_data['genres']:
                        if genre not in existing_genres:
                            result.setdefault('genres', []).append(genre)
                
                # Merge actors
                if omdb_data.get('actors'):
                    existing_actors = {actor['name'] for actor in result.get('actors', [])}
                    for actor in omdb_data['actors']:
                        if actor['name'] not in existing_actors:
                            result.setdefault('actors', []).append(actor)
            
            return result
            
        # If no TMDB data, use OMDB data
        return omdb_data

    def fetch_metadata(self, title: str) -> Optional[Dict[str, Any]]:
        """Fetch and merge metadata from all available sources"""
        tmdb_data = self.search_tmdb(title)
        omdb_data = self.search_omdb(title)
        
        return self.merge_metadata(tmdb_data, omdb_data) 
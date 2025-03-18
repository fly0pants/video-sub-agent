import os
import logging
import requests
import tmdbsimple as tmdb
import json

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
    
    def __init__(self, tmdb_api_key=None, omdb_api_key=None):
        """
        Initialize with API keys
        
        Args:
            tmdb_api_key: TMDB API key
            omdb_api_key: OMDb API key
        """
        self.fetchers = {}
        
        # Initialize TMDB fetcher if API key is provided
        if tmdb_api_key or os.environ.get("TMDB_API_KEY"):
            self.fetchers["tmdb"] = TMDBFetcher(api_key=tmdb_api_key)
        
        # Initialize OMDb fetcher if API key is provided
        if omdb_api_key or os.environ.get("OMDB_API_KEY"):
            self.fetchers["omdb"] = OMDBFetcher(api_key=omdb_api_key)
    
    def fetch_metadata(self, title, sources=None, is_tv=False, year=None):
        """
        Fetch metadata from specified sources
        
        Args:
            title: Movie or TV show title
            sources: List of sources to fetch from (e.g., ["tmdb", "omdb"])
            is_tv: Whether the title is a TV show
            year: Optional year to filter results
            
        Returns:
            Dictionary of metadata from each source
        """
        if not self.fetchers:
            raise ValueError("No metadata fetchers initialized. Provide API keys.")
        
        # If sources not specified, use all available fetchers
        sources = sources or list(self.fetchers.keys())
        
        results = {}
        
        for source in sources:
            if source not in self.fetchers:
                logger.warning(f"Metadata source '{source}' not available. Skipping.")
                continue
            
            try:
                if source == "tmdb":
                    data = self.fetchers[source].get_metadata(title, is_tv=is_tv, year=year)
                elif source == "omdb":
                    data = self.fetchers[source].get_by_title(title, year=year)
                else:
                    logger.warning(f"Unknown source '{source}'. Skipping.")
                    continue
                
                if data:
                    results[source] = data
            except Exception as e:
                logger.error(f"Error fetching metadata from {source}: {e}")
        
        return results
    
    def extract_common_metadata(self, metadata):
        """
        Extract common metadata fields from various sources
        
        Args:
            metadata: Dictionary of metadata from different sources
            
        Returns:
            Dictionary of common metadata fields
        """
        common = {
            "title": None,
            "year": None,
            "genres": [],
            "actors": [],
            "directors": [],
            "plot": None,
            "poster_url": None,
            "rating": None
        }
        
        # Extract from TMDB if available
        if "tmdb" in metadata:
            tmdb_data = metadata["tmdb"]
            
            common["title"] = tmdb_data.get("title") or tmdb_data.get("name")
            
            # Extract year from release_date or first_air_date
            release_date = tmdb_data.get("release_date") or tmdb_data.get("first_air_date")
            if release_date and len(release_date) >= 4:
                common["year"] = release_date[:4]
            
            # Extract genres
            if "genres" in tmdb_data:
                common["genres"] = [genre["name"] for genre in tmdb_data["genres"]]
            
            # Extract actors and directors from credits
            if "credits" in tmdb_data:
                # Get top actors
                cast = tmdb_data["credits"].get("cast", [])
                common["actors"] = [person["name"] for person in cast[:10]]  # Top 10 actors
                
                # Get directors (for movies)
                crew = tmdb_data["credits"].get("crew", [])
                common["directors"] = [person["name"] for person in crew if person.get("job") == "Director"]
            
            common["plot"] = tmdb_data.get("overview")
            
            # Create poster URL
            if tmdb_data.get("poster_path"):
                common["poster_url"] = f"https://image.tmdb.org/t/p/w500{tmdb_data['poster_path']}"
            
            common["rating"] = tmdb_data.get("vote_average")
        
        # Extract from OMDb if available
        if "omdb" in metadata:
            omdb_data = metadata["omdb"]
            
            # Only use OMDb data if TMDB data not available
            if not common["title"]:
                common["title"] = omdb_data.get("Title")
            
            if not common["year"]:
                year_str = omdb_data.get("Year")
                if year_str and "–" in year_str:  # TV series with range
                    common["year"] = year_str.split("–")[0]
                else:
                    common["year"] = year_str
            
            if not common["genres"]:
                genres_str = omdb_data.get("Genre")
                if genres_str:
                    common["genres"] = [g.strip() for g in genres_str.split(",")]
            
            if not common["actors"]:
                actors_str = omdb_data.get("Actors")
                if actors_str:
                    common["actors"] = [a.strip() for a in actors_str.split(",")]
            
            if not common["directors"]:
                directors_str = omdb_data.get("Director")
                if directors_str and directors_str != "N/A":
                    common["directors"] = [d.strip() for d in directors_str.split(",")]
            
            if not common["plot"]:
                common["plot"] = omdb_data.get("Plot")
            
            if not common["poster_url"]:
                poster = omdb_data.get("Poster")
                if poster and poster != "N/A":
                    common["poster_url"] = poster
            
            if not common["rating"]:
                # Try to get IMDb rating
                ratings = omdb_data.get("Ratings", [])
                for rating in ratings:
                    if rating["Source"] == "Internet Movie Database":
                        try:
                            common["rating"] = float(rating["Value"].split("/")[0])
                            break
                        except (ValueError, IndexError):
                            pass
        
        return common 
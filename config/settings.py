import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = os.getenv('OUTPUT_DIR', os.path.join(BASE_DIR, 'output', 'subtitles'))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Create necessary directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./videos.db')

# API Keys
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

# Check required environment variables
required_vars = ['DEEPSEEK_API_KEY', 'TMDB_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# API settings
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))

# Create CONFIG dictionary for app configuration
CONFIG = {
    "database_url": DATABASE_URL,
    "output_dir": OUTPUT_DIR,
    "upload_dir": UPLOAD_DIR,
    "deepseek_api_key": DEEPSEEK_API_KEY,
    "deepseek_api_base": os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1'),
    "deepseek_model": os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
    "tmdb_api_key": TMDB_API_KEY,
    "omdb_api_key": OMDB_API_KEY,
    "opensubtitles_api_key": os.getenv('OPENSUBTITLES_API_KEY'),
    "subtitle_output_dir": os.getenv('SUBTITLE_OUTPUT_DIR', 'output/subtitles'),
    "temp_dir": os.getenv('TEMP_DIR', 'temp'),
    "batch_size": int(os.getenv('BATCH_SIZE', '10')),
    "max_workers": int(os.getenv('MAX_WORKERS', '4')),
    "api_host": API_HOST,
    "api_port": API_PORT
}

# Logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__) 
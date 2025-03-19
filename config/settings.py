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

# Logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__) 
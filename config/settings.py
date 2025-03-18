import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
DB_NAME = os.environ.get("DB_NAME", "video_metadata.db")
DB_USER = os.environ.get("DB_USER", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")

# Construct database URL
if DB_TYPE == "sqlite":
    DATABASE_URL = f"sqlite:///{DB_NAME}"
elif DB_TYPE == "postgresql":
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
elif DB_TYPE == "mysql":
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    raise ValueError(f"Unsupported database type: {DB_TYPE}")

# API Keys
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.environ.get("DEEPSEEK_API_BASE")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-coder")

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")

# Paths to external tools
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = os.environ.get("FFPROBE_PATH", "ffprobe")
CCEXTRACTOR_PATH = os.environ.get("CCEXTRACTOR_PATH", "ccextractor")
TESSERACT_CMD = os.environ.get("TESSERACT_CMD")

# Subtitle extraction settings
DEFAULT_SUBTITLE_FORMAT = os.environ.get("DEFAULT_SUBTITLE_FORMAT", "srt")
EXTRACT_HARDCODED_SUBTITLES = os.environ.get("EXTRACT_HARDCODED_SUBTITLES", "false").lower() == "true"
OCR_FRAME_INTERVAL = float(os.environ.get("OCR_FRAME_INTERVAL", "1.0"))
OCR_LANGUAGE = os.environ.get("OCR_LANGUAGE", "eng")

# Output settings
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")

# Logging settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = os.environ.get("LOG_FILE", "app.log")

# API settings
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))

# Create a unified configuration dictionary
CONFIG = {
    "database_url": DATABASE_URL,
    "deepseek_api_key": DEEPSEEK_API_KEY,
    "deepseek_api_base": DEEPSEEK_API_BASE,
    "deepseek_model": DEEPSEEK_MODEL,
    "tmdb_api_key": TMDB_API_KEY,
    "omdb_api_key": OMDB_API_KEY,
    "ffmpeg_path": FFMPEG_PATH,
    "ffprobe_path": FFPROBE_PATH,
    "ccextractor_path": CCEXTRACTOR_PATH,
    "tesseract_cmd": TESSERACT_CMD,
    "default_subtitle_format": DEFAULT_SUBTITLE_FORMAT,
    "extract_hardcoded_subtitles": EXTRACT_HARDCODED_SUBTITLES,
    "ocr_frame_interval": OCR_FRAME_INTERVAL,
    "ocr_language": OCR_LANGUAGE,
    "output_dir": OUTPUT_DIR,
    "log_level": LOG_LEVEL,
    "log_file": LOG_FILE,
    "api_host": API_HOST,
    "api_port": API_PORT
}

# Configure logging
def setup_logging():
    """Set up logging configuration"""
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Set third-party loggers to a higher level to reduce noise
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__) 
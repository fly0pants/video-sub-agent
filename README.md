# Video Analysis and Metadata Management System

This system analyzes video files, extracts subtitles, identifies official movie names using LLM, and fetches metadata from external APIs.

## Features

- Extract embedded, soft, and hard-coded subtitles from video files
- Identify official movie/show names from non-standard filenames using LLM
- Fetch comprehensive metadata from TMDB, OMDb, and other APIs
- Store all information in a structured database

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Install external tools:

   - FFmpeg: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - CCExtractor: [https://www.ccextractor.org/download/](https://www.ccextractor.org/download/)
   - Tesseract OCR: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)

3. Create a `.env` file with your API keys:

   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key
   TMDB_API_KEY=your_tmdb_api_key
   OMDB_API_KEY=your_omdb_api_key
   ```

4. Run the application:
   ```
   python app/main.py
   ```

## Project Structure

- `app/`: Main application code
  - `subtitle/`: Subtitle extraction modules
  - `movie_name/`: Movie name recognition using LLM
  - `metadata/`: Metadata fetching from APIs
  - `database/`: Database models and operations
  - `api/`: FastAPI endpoints
- `config/`: Configuration files
- `tests/`: Unit and integration tests

## Usage

1. Upload a video file through the API or web interface
2. The system processes the video to extract subtitles
3. Using the filename, it identifies the official movie/show name
4. It fetches metadata from external APIs
5. All information is stored in the database and returned to the user

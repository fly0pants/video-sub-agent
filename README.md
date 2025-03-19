# Video Analysis and Metadata Management System

A comprehensive system for processing video files, extracting subtitles, recognizing movie names, and managing metadata.

## Features

- **Video Processing**

  - Extract embedded subtitles using FFmpeg
  - Extract closed captions using CCExtractor
  - Extract hardcoded subtitles using OCR (Tesseract)
  - Support for multiple video formats

- **Movie Recognition**

  - Intelligent movie name recognition using LLM
  - Handles various filename formats
  - Batch processing support

- **Metadata Management**

  - Fetch metadata from TMDB and OMDb
  - Store information in SQLite database
  - Track movie details, genres, actors, etc.

- **User Interface**

  - Modern React frontend with Material-UI
  - Clean and intuitive design
  - Real-time processing feedback
  - Error handling and notifications

- **API**
  - RESTful API built with FastAPI
  - Comprehensive endpoint documentation
  - Easy integration with other systems

## Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- FFmpeg
- CCExtractor
- Tesseract OCR

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/video-sub-agent.git
   cd video-sub-agent
   ```

2. Set up the Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   ```

4. Create a `.env` file in the project root:
   ```
   TMDB_API_KEY=your_tmdb_api_key
   OMDB_API_KEY=your_omdb_api_key
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///./videos.db
   ```

## Usage

1. Start the backend server:

   ```bash
   # In the project root directory
   uvicorn app.main:app --reload
   ```

2. Start the frontend development server:

   ```bash
   # In the frontend directory
   npm start
   ```

3. Access the web interface at `http://localhost:3000`

### Command Line Interface

The system also provides a CLI for batch processing:

```bash
# Process a single video
python cli.py process path/to/video.mp4

# Process multiple videos
python cli.py batch path/to/videos/*.mp4

# Recognize movie name
python cli.py recognize "movie filename"

# List processed videos
python cli.py list
```

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when the backend server is running.

## Project Structure

```
video-sub-agent/
├── app/
│   ├── api/            # API endpoints and models
│   ├── database/       # Database models and operations
│   ├── metadata/       # Metadata fetching modules
│   ├── movie_name/     # Movie name recognition
│   ├── subtitle/       # Subtitle extraction
│   └── main.py         # FastAPI application
├── frontend/          # React frontend
├── config/           # Configuration
├── cli.py           # Command line interface
└── requirements.txt  # Python dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FFmpeg for video processing
- CCExtractor for subtitle extraction
- Tesseract for OCR capabilities
- OpenAI for LLM support
- TMDB and OMDb for movie metadata

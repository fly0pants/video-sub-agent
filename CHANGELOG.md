# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-02-14

### Added

- Initial release of the Video Analysis and Metadata Management System
- Core functionality for video processing and subtitle extraction
- Support for embedded, soft, and hard-coded subtitle extraction
- Movie name recognition using LLM
- Metadata fetching from TMDB and OMDb APIs
- SQLite database for storing video information
- FastAPI backend with comprehensive API endpoints
- React frontend with Material-UI interface
- CLI tool for command-line operations
- Comprehensive documentation and setup instructions

### Features

- Video subtitle extraction using FFmpeg and CCExtractor
- OCR-based subtitle extraction for hardcoded subtitles
- Intelligent movie name recognition
- Metadata retrieval from multiple sources
- Clean and intuitive web interface
- Command-line interface for batch processing
- Structured database storage
- API endpoints for all operations

### Technical Details

- Python backend with FastAPI
- React frontend with Material-UI
- SQLAlchemy ORM for database operations
- Integration with external APIs (TMDB, OMDb)
- Support for multiple subtitle formats
- Configurable through environment variables
- Comprehensive error handling and logging

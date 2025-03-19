---
layout: default
title: Usage Guide
lang: en
ref: usage
---

# Usage Guide

This guide explains how to use the Video Sub Agent for video processing, subtitle extraction, and metadata management.

## Command Line Interface (CLI)

The CLI provides several commands for video processing and management:

### Process a Single Video

```bash
python -m app.cli process /path/to/video.mp4
```

Options:

- `--force`: Force reprocessing even if the video was processed before
- `--no-subs`: Skip subtitle extraction
- `--no-meta`: Skip metadata fetching

### Batch Process Multiple Videos

```bash
python -m app.cli batch /path/to/video/directory
```

Options:

- `--pattern "*.mp4"`: Process only files matching the pattern
- `--recursive`: Search for videos in subdirectories
- `--workers 4`: Number of parallel workers (default: 4)

### Recognize Movie Name

```bash
python -m app.cli recognize /path/to/video.mp4
```

This command uses AI to recognize the movie name from the video file and its content.

### List Processed Videos

```bash
python -m app.cli list
```

Options:

- `--status processed`: Filter by processing status
- `--format json`: Output in JSON format
- `--sort-by date`: Sort by processing date

### Initialize Database

```bash
python -m app.cli init
```

Creates necessary database tables and directories.

## Web API

The system provides a RESTful API for integration with other applications.

### Start the API Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

- `POST /api/videos/process`: Process a new video
- `GET /api/videos`: List all processed videos
- `GET /api/videos/{video_id}`: Get video details
- `DELETE /api/videos/{video_id}`: Delete video record
- `GET /api/health`: Check API health status

Full API documentation is available at `http://localhost:8000/docs` when the server is running.

## Web Interface

A web interface is available for easy management of videos and subtitles.

### Access the Interface

1. Start the API server as described above
2. Open `http://localhost:8000` in your browser

### Features

- Upload and process videos
- View processing status and progress
- Browse and search processed videos
- Download extracted subtitles
- View and edit video metadata
- Manage video processing queue

## Working with Subtitles

### Subtitle Features

The system extracts subtitles in multiple formats:

- SRT (SubRip)
- VTT (Web Video Text Tracks)
- TXT (Plain text)

### Multi-language Subtitle Support

The system now supports downloading subtitles in multiple languages:

- Automatically detects the movie's original language from metadata
- Downloads both English subtitles and the movie's original language subtitles
- Maps common language names to ISO 639-1 codes (e.g., "Korean" → "ko")
- Supports multiple language subtitles for the same video

### Subtitle Location

Extracted subtitles are stored in:

```
output/subtitles/
  - movie_name_en.srt  (English subtitles)
  - movie_name_ko.srt  (Korean subtitles)
  - movie_name_zh.srt  (Chinese subtitles)
  - etc.
```

### Subtitle Processing

- Automatic language detection
- OCR for hardcoded subtitles
- Timing synchronization
- Format conversion

## Metadata Management

### Available Metadata

- Movie title and year
- Genre and categories
- Director and cast
- Plot summary
- IMDb rating
- Release date
- Language

### Metadata Sources

1. Video filename analysis
2. AI-powered content recognition
3. TMDB and OMDB APIs
4. Manual user input

### Updating Metadata

```bash
# Using CLI
python -m app.cli update <video_id> --title "New Title" --year 2024

# Using API
curl -X PATCH http://localhost:8000/api/videos/{video_id} \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title", "year": 2024}'
```

## Best Practices

1. **Organize Your Videos**

   - Use consistent naming conventions
   - Keep videos in dedicated directories
   - Maintain original file names

2. **Resource Management**

   - Monitor disk space for extracted subtitles
   - Use appropriate batch sizes for large collections
   - Clean up temporary files regularly

3. **Error Handling**

   - Check logs for processing errors
   - Retry failed extractions with `--force`
   - Keep API keys and credentials up to date

4. **Performance Optimization**
   - Adjust worker count based on CPU cores
   - Process videos during off-peak hours
   - Use SSD storage for database and temp files

## Troubleshooting

### Common Issues

1. **Subtitle Extraction Fails**

   - Verify video file is not corrupted
   - Check if video has extractable subtitles
   - Try different extraction methods

2. **Movie Recognition Issues**

   - Ensure video filename is descriptive
   - Check API key validity
   - Try manual metadata input

3. **Performance Problems**
   - Reduce batch size
   - Check system resources
   - Clear temporary files

### Getting Help

- Check the [FAQ](./faq)
- Review [GitHub Issues](https://github.com/fly0pants/video-sub-agent/issues)
- Join [Discussions](https://github.com/fly0pants/video-sub-agent/discussions)

[Back to Home](./){: .btn .btn-outline }

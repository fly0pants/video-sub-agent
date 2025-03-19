---
layout: default
title: Installation Guide
lang: en
ref: installation
---

# Installation Guide

## System Requirements

- Python 3.10 or higher
- FFmpeg (for video processing)
- Git (for version control)

## Step-by-Step Installation

### 1. Install System Dependencies

#### On macOS:

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

#### On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

#### On Windows:

1. Download FFmpeg from [official website](https://www.ffmpeg.org/download.html)
2. Add FFmpeg to system PATH

### 2. Clone the Repository

```bash
git clone https://github.com/fly0pants/video-sub-agent.git
cd video-sub-agent
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key
TMDB_API_KEY=your_tmdb_api_key
OMDB_API_KEY=your_omdb_api_key

# Database Configuration
DATABASE_URL=sqlite:///./videos.db

# Output Directories
OUTPUT_DIR=output
SUBTITLE_OUTPUT_DIR=output/subtitles
TEMP_DIR=temp

# Processing Configuration
BATCH_SIZE=10
MAX_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

Replace `your_*_api_key` with your actual API keys:

- Get DeepSeek API key from [DeepSeek](https://platform.deepseek.com)
- Get TMDB API key from [TMDB](https://www.themoviedb.org/settings/api)
- Get OMDB API key from [OMDB](https://www.omdbapi.com/apikey.aspx)

### 5. Verify Installation

```bash
# Test the CLI
python -m app.cli --help

# Test the API server
python -m uvicorn app.main:app --reload
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**

   - Make sure FFmpeg is installed and available in system PATH
   - Try running `ffmpeg -version` to verify installation

2. **API Key Issues**

   - Verify all API keys are correctly set in `.env` file
   - Check API key permissions and quotas

3. **Database Issues**

   - Ensure write permissions in project directory
   - Check database URL in `.env` file

4. **Python Dependencies**
   - Try upgrading pip: `pip install --upgrade pip`
   - Install dependencies one by one if bulk install fails

## Next Steps

- Read the [Usage Guide](./usage) to learn how to use the system
- Check the [API Documentation](http://localhost:8000/docs) when running the server
- Join our [GitHub Discussions](https://github.com/fly0pants/video-sub-agent/discussions) for help

[Back to Home](./){: .btn .btn-outline }

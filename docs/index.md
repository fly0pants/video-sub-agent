---
layout: default
title: Video Sub Agent
lang: en
ref: home
---

# Video Sub Agent

A powerful video analysis and metadata management system that automatically extracts subtitles, recognizes movie names, retrieves movie metadata, and provides a convenient management interface.

[View on GitHub](https://github.com/fly0pants/video-sub-agent){: .btn .btn-primary }
[中文文档](./zh/){: .btn }

## Features

- **Subtitle Extraction**

  - Extract embedded subtitles from video files
  - Support for external subtitle files
  - Multiple subtitle formats supported
  - Intelligent subtitle language detection

- **Movie Name Recognition**

  - Intelligent movie name recognition using LLM (DeepSeek)
  - Support for multiple languages (including Chinese)
  - Handles various filename formats
  - Batch processing capability

- **Metadata Management**

  - Fetch metadata from TMDB and OMDB
  - Store movie information, genres, and actors
  - Persistent data storage
  - Easy data management

- **User Interface**
  - Command-line interface for automation
  - Web API for integration
  - Comprehensive API documentation
  - Real-time processing status

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/fly0pants/video-sub-agent.git
cd video-sub-agent
```

2. Set up Python environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

[Installation Guide](./installation){: .btn .btn-outline }
[Usage Guide](./usage){: .btn .btn-outline }

## Development Status

Current Version: 1.0.0

### Roadmap

- [ ] Add more subtitle extraction methods
- [ ] Improve movie name recognition accuracy
- [ ] Add user interface
- [ ] Support more video formats
- [ ] Add video preview feature
- [ ] Support more metadata sources
- [ ] Add subtitle translation feature

## Contributing

We welcome contributions! Please feel free to:

- Submit [Issues](https://github.com/fly0pants/video-sub-agent/issues)
- Create [Pull Requests](https://github.com/fly0pants/video-sub-agent/pulls)
- Improve documentation
- Share your ideas

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/fly0pants/video-sub-agent/blob/main/LICENSE) file for details.

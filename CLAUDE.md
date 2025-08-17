# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Video Processing Service** is a Chinese-language video processing automation service that extracts audio, generates subtitles using Whisper AI, and embeds them back into videos. The project slogan is "从此再无生番!" (No more raw/unsubtitled content!).

## Architecture

### System Design
The application follows a request-response pattern with clear separation of concerns:

- **Flask API Layer** (`app.py`): Handles HTTP requests, file uploads, and response formatting
- **Processing Engine** (`src/video_processing.py`): Core video/audio processing pipeline
- **Configuration Layer** (`config/`): Centralized path and settings management
- **Static Frontend** (`static/index.html`): Single-page web interface with glassmorphism design

### Key Processing Pipeline
```
Video Upload → Audio Extraction → Whisper Transcription → Subtitle Generation → Video Embedding → Download
```

### Core Modules

#### Application Layer
- `app.py`: Flask server with CORS-enabled REST API
  - File upload with unique naming (`get_unique_filename()`)
  - Request routing and error handling
  - Directory auto-creation via `PathConfig.ensure_dirs()`

#### Processing Layer  
- `src/video_processing.py`: Main processing logic
  - `extract_audio_from_video()`: FFmpeg-based audio extraction (44kHz WAV)
  - `generate_subtitles()`: Whisper large-v3 model for transcription
  - `embed_subtitles()`: FFmpeg subtitle burning
  - `generate_subtitles_with_translation()`: Translation support (English only)
- `src/audio_processing.py`: Standalone audio transcription utilities

#### Configuration Layer
- `config/paths.py`: `PathConfig` class managing all file paths
- `config/settings.py`: Logging configuration with file and console outputs

## Development Commands

### Environment Setup
```bash
# Create virtual environment (Python 3.9.12 recommended)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Ensure FFmpeg is installed system-wide
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### Running the Application
```bash
# Start development server
python app.py
# Server runs on http://0.0.0.0:5000
```

### API Endpoints
- `GET /` - Serve web interface
- `GET /test` - Health check endpoint
- `POST /upload` - Process video file (supports `return_option` parameter)
- `POST /burn` - Burn existing subtitles to video (JSON body with `filename`)
- `GET /download/<filename>` - Download processed files

### Testing Commands
```bash
# Health check
curl http://127.0.0.1:5000/test

# Upload and process video
curl -X POST -F "file=@video.mp4" http://127.0.0.1:5000/upload

# Return only subtitle file
curl -X POST -F "file=@video.mp4" -F "return_option=subtitle" http://127.0.0.1:5000/upload

# Burn existing subtitles
curl -X POST -H "Content-Type: application/json" -d '{"filename":"video_name"}' http://127.0.0.1:5000/burn
```

## Dependencies & Requirements

### Python Dependencies
- `Flask==3.1.0`: Web framework
- `Flask-Cors==5.0.0`: CORS support
- `openai_whisper==20240930`: Speech-to-text processing
- `jsonify==0.5`: JSON response formatting

### System Dependencies
- **FFmpeg**: Required for video/audio processing (must be in PATH)

## Configuration Details

### Path Management
All file paths are managed through `config/paths.py`:
- Automatic directory creation on startup
- Centralized path resolution methods
- Prevents path-related errors across modules

### Whisper Model Configuration
- Model: `large-v3` (hardcoded in `src/video_processing.py:28,48`)
- Language detection: Automatic
- Output format: SRT with millisecond precision

### File Handling
- **Unique Naming**: Counter-based system prevents overwrites
- **Directory Structure**: Auto-created uploads/, outputs/, audio/, subtitles/
- **File Types**: MP4 input, WAV audio extraction, SRT subtitle output

## Processing Flow Details

1. **Upload Validation**: File presence and naming conflict resolution
2. **Audio Extraction**: FFmpeg conversion to 44kHz WAV stereo
3. **Transcription**: Whisper large-v3 model processing
4. **Subtitle Formatting**: SRT file generation with timestamps
5. **Video Embedding**: FFmpeg subtitle burning with original audio preservation
6. **Response Generation**: JSON with download URLs

## Notable Implementation Details

- **Error Handling**: Try-catch blocks with user-friendly Chinese error messages
- **Logging**: Dual output to console and `app.log` file
- **Translation**: Partial implementation (Whisper's built-in English translation only)
- **Frontend**: Pure JavaScript with fetch API, glassmorphism CSS design
- **Chinese Optimization**: UI text and error messages in Chinese
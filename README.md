# Video Memories Assistant

A tool for automatic analysis of large video archives and assistance in selecting the most meaningful moments.

## Installation

```bash
poetry install
```

## Usage

### Basic Commands

```bash
# Enumerate video files and create segments
poetry run video-memories enumerate /path/to/media/directory

# Extract frames from segments
poetry run video-memories extract-frames /path/to/media/directory

# View processing status
poetry run video-memories status /path/to/media/directory

# Help
poetry run video-memories --help
```

### Usage Example

```bash
# Create test directory
mkdir -p /tmp/my_videos

# Copy video files to directory
cp *.mp4 /tmp/my_videos/

# Run analysis
poetry run video-memories enumerate /tmp/my_videos

# Extract frames
poetry run video-memories extract-frames /tmp/my_videos

# Check status
poetry run video-memories status /tmp/my_videos
```

## Data Format

### Processing Status (status.json)

```json
{
  "media_dir": "/path/to/media",
  "cache_dir": "/path/to/.cache",
  "total_files": 1,
  "segment_duration": 10,
  "files": [
    {
      "path": "/path/to/video.mp4",
      "filename": "video.mp4",
      "duration": 30.0,
      "width": 1920,
      "height": 1080,
      "fps": 30.0,
      "codec": "h264"
    }
  ],
  "segments": [
    {
      "file": "video.mp4",
      "file_path": "/path/to/video.mp4",
      "start_time": 0,
      "end_time": 10,
      "duration": 10,
      "start_timestamp": "00:00:00",
      "end_timestamp": "00:00:10",
      "segment_id": "video.mp4_000000",
      "status": "pending"
    }
  ]
}
```

## Features

- **Virtual segmentation** - files are not physically cut
- **Caching** - results saved in `.cache/` next to media files
- **Local processing** - all computations performed locally
- **Multi-project support** - each media directory has its own cache

## Testing

```bash
# Create test video
ffmpeg -f lavfi -i testsrc=duration=30:size=320x240:rate=1 -c:v libx264 -t 30 /tmp/test_media/test_video.mp4

# Test with real file
poetry run video-memories enumerate /tmp/test_media
poetry run video-memories extract-frames /tmp/test_media
poetry run video-memories status /tmp/test_media
``` 
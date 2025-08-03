from pathlib import Path
from typing import List, Dict, Any, Optional
import ffmpeg


class VideoProcessor:
    """Class for processing video files and segmentation"""
    
    # Supported video formats
    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.webm'}
    
    def __init__(self, media_dir: str, cache_dir: Optional[str] = None):
        """
        Initialize video processor
        
        Args:
            media_dir: Path to directory with media files
            cache_dir: Path to cache directory (if None, created next to media_dir)
        """
        self.media_dir = Path(media_dir)
        if cache_dir is None:
            self.cache_dir = self.media_dir.parent / '.cache'
        else:
            self.cache_dir = Path(cache_dir)
        
    def find_video_files(self) -> List[Path]:
        """
        Find all video files in media directory
        
        Returns:
            List of paths to video files
        """
        video_files = []
        
        if not self.media_dir.exists():
            raise FileNotFoundError(f"Directory {self.media_dir} not found")
        
        for file_path in self.media_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.VIDEO_EXTENSIONS:
                video_files.append(file_path)
        
        return sorted(video_files)
    
    def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """
        Get video file information
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            probe = ffmpeg.probe(str(video_path))
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            if not video_stream:
                raise ValueError(f"Video stream not found in file {video_path}")
            
            duration = float(probe['format']['duration'])
            
            return {
                'path': str(video_path),
                'filename': video_path.name,
                'duration': duration,
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'fps': eval(video_stream['r_frame_rate']),  # '30/1' -> 30.0
                'codec': video_stream['codec_name']
            }
        except Exception as e:
            raise RuntimeError(f"Error getting video information for {video_path}: {e}")
    
    def create_segments(self, video_info: Dict[str, Any], segment_duration: int = 10) -> List[Dict[str, Any]]:
        """
        Create virtual segments for video file
        
        Args:
            video_info: Video file information
            segment_duration: Segment duration in seconds
            
        Returns:
            List of segments with metadata
        """
        duration = video_info['duration']
        segments = []
        
        # Create segments by segment_duration seconds
        for start_time in range(0, int(duration), segment_duration):
            end_time = min(start_time + segment_duration, duration)
            
            segment = {
                'file': video_info['filename'],
                'file_path': video_info['path'],
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'start_timestamp': self._seconds_to_timestamp(start_time),
                'end_timestamp': self._seconds_to_timestamp(end_time),
                'segment_id': f"{video_info['filename']}_{start_time:06d}",
                'status': 'pending'  # pending, processing, completed, failed
            }
            segments.append(segment)
        
        return segments
    
    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def enumerate_and_segment(self, segment_duration: int = 10) -> Dict[str, Any]:
        """
        Main method for enumerating files and creating segments
        
        Args:
            segment_duration: Segment duration in seconds
            
        Returns:
            Dictionary with project information and segments
        """
        print(f"🔍 Searching for video files in {self.media_dir}...")
        video_files = self.find_video_files()
        
        if not video_files:
            print("❌ No video files found")
            return {}
        
        print(f"📹 Found {len(video_files)} video files")
        
        project_info = {
            'media_dir': str(self.media_dir),
            'cache_dir': str(self.cache_dir),
            'total_files': len(video_files),
            'segment_duration': segment_duration,
            'files': [],
            'segments': []
        }
        
        for video_file in video_files:
            print(f"📋 Analyzing file: {video_file.name}")
            
            try:
                video_info = self.get_video_info(video_file)
                segments = self.create_segments(video_info, segment_duration)
                
                project_info['files'].append(video_info)
                project_info['segments'].extend(segments)
                
                print(f"   ✅ Created {len(segments)} segments")
                
            except Exception as e:
                print(f"   ❌ Error processing {video_file.name}: {e}")
        
        print(f"🎯 Total segments created: {len(project_info['segments'])}")
        return project_info 
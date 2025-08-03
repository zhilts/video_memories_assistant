import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import ffmpeg


class FrameExtractor:
    """Extract representative frames from video segments"""
    
    def __init__(self, cache_dir: Path):
        """
        Initialize frame extractor
        
        Args:
            cache_dir: Path to cache directory for storing frames
        """
        self.cache_dir = cache_dir
        self.frames_dir = self.cache_dir / 'frames'
        self.frames_dir.mkdir(exist_ok=True)
    
    def extract_frames_from_segment(self, segment: Dict[str, Any], frames_per_segment: int = 2) -> List[str]:
        """
        Extract representative frames from a video segment
        
        Args:
            segment: Segment information dictionary
            frames_per_segment: Number of frames to extract per segment
            
        Returns:
            List of paths to extracted frame files
        """
        video_path = segment['file_path']
        start_time = segment['start_time']
        end_time = segment['end_time']
        segment_id = segment['segment_id']
        
        # Create segment-specific directory
        segment_frames_dir = self.frames_dir / segment_id
        segment_frames_dir.mkdir(exist_ok=True)
        
        frame_paths = []
        duration = end_time - start_time
        
        # Extract frames at different points in the segment
        if frames_per_segment == 1:
            # Extract frame at middle of segment
            frame_time = start_time + (duration / 2)
            frame_path = self._extract_single_frame(video_path, frame_time, segment_id, 0)
            frame_paths.append(frame_path)
        else:
            # Extract frames at 1/3 and 2/3 of segment
            frame_times = [
                start_time + (duration / 3),
                start_time + (2 * duration / 3)
            ]
            
            for i, frame_time in enumerate(frame_times):
                frame_path = self._extract_single_frame(video_path, frame_time, segment_id, i)
                frame_paths.append(frame_path)
        
        return frame_paths
    
    def _extract_single_frame(self, video_path: str, frame_time: float, segment_id: str, frame_index: int) -> str:
        """
        Extract a single frame at specific time
        
        Args:
            video_path: Path to video file
            frame_time: Time in seconds to extract frame
            segment_id: Segment identifier
            frame_index: Frame index within segment
            
        Returns:
            Path to extracted frame file
        """
        segment_frames_dir = self.frames_dir / segment_id
        frame_filename = f"frame_{frame_index:02d}.jpg"
        frame_path = segment_frames_dir / frame_filename
        
        try:
            # Use ffmpeg to extract frame
            stream = ffmpeg.input(video_path, ss=frame_time)
            stream = ffmpeg.output(stream, str(frame_path), vframes=1, **{'q:v': 2})
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return str(frame_path)
        except Exception as e:
            print(f"Error extracting frame at {frame_time}s from {video_path}: {e}")
            return ""
    
    def extract_frames_for_all_segments(self, segments: List[Dict[str, Any]], frames_per_segment: int = 2) -> Dict[str, List[str]]:
        """
        Extract frames for all segments
        
        Args:
            segments: List of segment dictionaries
            frames_per_segment: Number of frames per segment
            
        Returns:
            Dictionary mapping segment_id to list of frame paths
        """
        results = {}
        
        for segment in segments:
            segment_id = segment['segment_id']
            print(f"📸 Extracting frames for segment: {segment_id}")
            
            frame_paths = self.extract_frames_from_segment(segment, frames_per_segment)
            results[segment_id] = frame_paths
            
            print(f"   ✅ Extracted {len(frame_paths)} frames")
        
        return results
    
    def get_frame_info(self, frame_path: str) -> Dict[str, Any]:
        """
        Get information about extracted frame
        
        Args:
            frame_path: Path to frame file
            
        Returns:
            Dictionary with frame information
        """
        frame_path_obj = Path(frame_path)
        
        if not frame_path_obj.exists():
            return {}
        
        try:
            # Get file size
            file_size = frame_path_obj.stat().st_size
            
            return {
                'path': str(frame_path),
                'filename': frame_path_obj.name,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            }
        except Exception as e:
            print(f"Error getting frame info for {frame_path}: {e}")
            return {}
    
    def cleanup_frames(self, segment_id: str):
        """Remove frames for specific segment"""
        segment_frames_dir = self.frames_dir / segment_id
        if segment_frames_dir.exists():
            import shutil
            shutil.rmtree(segment_frames_dir)
            print(f"🧹 Cleaned up frames for segment: {segment_id}")
    
    def get_frames_summary(self) -> Dict[str, Any]:
        """Get summary of extracted frames"""
        if not self.frames_dir.exists():
            return {'total_segments': 0, 'total_frames': 0, 'total_size_mb': 0}
        
        total_segments = 0
        total_frames = 0
        total_size_bytes = 0
        
        for segment_dir in self.frames_dir.iterdir():
            if segment_dir.is_dir():
                total_segments += 1
                for frame_file in segment_dir.glob('*.jpg'):
                    total_frames += 1
                    total_size_bytes += frame_file.stat().st_size
        
        return {
            'total_segments': total_segments,
            'total_frames': total_frames,
            'total_size_mb': round(total_size_bytes / (1024 * 1024), 2)
        } 
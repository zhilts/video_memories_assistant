import json
from pathlib import Path
from typing import Dict, Any, List


class StatusManager:
    """Manages processing status and cache operations"""
    
    def __init__(self, cache_dir: Path):
        """
        Initialize status manager
        
        Args:
            cache_dir: Path to cache directory
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.status_file = self.cache_dir / 'status.json'
    
    def load_status(self) -> Dict[str, Any]:
        """Load processing status from file"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading status: {e}")
                return {}
        return {}
    
    def save_status(self, status: Dict[str, Any]):
        """Save processing status to file"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving status: {e}")
    
    def update_segment_status(self, segment_id: str, status: str):
        """Update status of specific segment"""
        current_status = self.load_status()
        segments = current_status.get('segments', [])
        
        for segment in segments:
            if segment.get('segment_id') == segment_id:
                segment['status'] = status
                break
        
        self.save_status(current_status)
    
    def update_segment_frames(self, segment_id: str, frame_paths: List[str]):
        """Update frame information for specific segment"""
        current_status = self.load_status()
        segments = current_status.get('segments', [])
        
        for segment in segments:
            if segment.get('segment_id') == segment_id:
                segment['frames'] = frame_paths
                segment['status'] = 'frames_extracted'
                break
        
        self.save_status(current_status)
    
    def get_segments_by_status(self, status: str) -> list:
        """Get all segments with specific status"""
        current_status = self.load_status()
        segments = current_status.get('segments', [])
        return [seg for seg in segments if seg.get('status') == status]
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of processing status"""
        current_status = self.load_status()
        segments = current_status.get('segments', [])
        
        status_counts = {}
        for segment in segments:
            status = segment.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_segments': len(segments),
            'status_counts': status_counts,
            'media_dir': current_status.get('media_dir'),
            'cache_dir': current_status.get('cache_dir'),
            'total_files': current_status.get('total_files', 0),
            'segment_duration': current_status.get('segment_duration', 0)
        } 
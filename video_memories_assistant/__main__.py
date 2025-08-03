#!/usr/bin/env python3
"""
Main CLI entry point for Video Memories Assistant
"""

import sys
import argparse
from .utils.video_utils import VideoProcessor
from .utils.status_manager import StatusManager

def enumerate_command(media_dir: str, segment_duration: int = 10, cache_dir: str = None):
    """Enumerate video files and create segments"""
    try:
        processor = VideoProcessor(media_dir, cache_dir)
        result = processor.enumerate_and_segment(segment_duration)
        
        if result:
            # Save status using StatusManager
            status_manager = StatusManager(processor.cache_dir)
            status_manager.save_status(result)
            
            print(f"\n✅ Processing completed!")
            print(f"📁 Media directory: {result['media_dir']}")
            print(f"💾 Cache directory: {result['cache_dir']}")
            print(f"📹 Files processed: {result['total_files']}")
            print(f"🎯 Segments created: {len(result['segments'])}")
            print(f"📄 Status saved to: {status_manager.status_file}")
        else:
            print("❌ Processing failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def status_command(media_dir: str):
    """Show current processing status"""
    try:
        processor = VideoProcessor(media_dir)
        status_manager = StatusManager(processor.cache_dir)
        status_summary = status_manager.get_status_summary()
        
        if status_summary.get('total_segments', 0) > 0:
            print(f"📊 Processing status:")
            print(f"   📁 Media directory: {status_summary.get('media_dir', 'N/A')}")
            print(f"   📹 Files: {status_summary.get('total_files', 0)}")
            print(f"   🎯 Segments: {status_summary.get('total_segments', 0)}")
            print(f"   ⏱️  Segment duration: {status_summary.get('segment_duration', 0)} sec")
            
            # Segment status statistics
            status_counts = status_summary.get('status_counts', {})
            if status_counts:
                print(f"   📈 Segment statistics:")
                for status, count in status_counts.items():
                    print(f"      {status}: {count}")
        else:
            print("📭 Status not found. Run enumerate command to start processing.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Video Memories Assistant - CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Enumerate command
    enumerate_parser = subparsers.add_parser('enumerate', help='Enumerate video files and create segments')
    enumerate_parser.add_argument('media_dir', help='Path to directory with media files')
    enumerate_parser.add_argument('--duration', '-d', type=int, default=10, 
                                help='Segment duration in seconds (default: 10)')
    enumerate_parser.add_argument('--cache', '-c', help='Path to cache directory')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current processing status')
    status_parser.add_argument('media_dir', help='Path to directory with media files')
    
    args = parser.parse_args()
    
    if args.command == 'enumerate':
        enumerate_command(args.media_dir, args.duration, args.cache)
    elif args.command == 'status':
        status_command(args.media_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Main CLI entry point for Video Memories Assistant
"""

import sys
import argparse
from .utils.video_utils import VideoProcessor
from .utils.status_manager import StatusManager
from .utils.frame_extractor import FrameExtractor
from .utils.image_analyzer import ImageAnalyzer

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

def extract_frames_command(media_dir: str, frames_per_segment: int = 2):
    """Extract frames from video segments"""
    try:
        processor = VideoProcessor(media_dir)
        status_manager = StatusManager(processor.cache_dir)
        frame_extractor = FrameExtractor(processor.cache_dir)
        
        # Get current status
        current_status = status_manager.load_status()
        segments = current_status.get('segments', [])
        
        if not segments:
            print("❌ No segments found. Run enumerate command first.")
            return
        
        print(f"📸 Starting frame extraction for {len(segments)} segments...")
        
        # Extract frames for all segments
        frame_results = frame_extractor.extract_frames_for_all_segments(segments, frames_per_segment)
        
        # Update status with frame information
        for segment_id, frame_paths in frame_results.items():
            status_manager.update_segment_frames(segment_id, frame_paths)
        
        # Get frames summary
        frames_summary = frame_extractor.get_frames_summary()
        
        print(f"\n✅ Frame extraction completed!")
        print(f"📸 Total segments processed: {frames_summary['total_segments']}")
        print(f"🖼️  Total frames extracted: {frames_summary['total_frames']}")
        print(f"💾 Total size: {frames_summary['total_size_mb']} MB")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def analyze_images_command(media_dir: str, model_name: str = "Salesforce/blip2-opt-2.7b"):
    """Analyze extracted frames using vision model"""
    try:
        processor = VideoProcessor(media_dir)
        status_manager = StatusManager(processor.cache_dir)
        image_analyzer = ImageAnalyzer(processor.cache_dir, model_name)
        
        # Get current status
        current_status = status_manager.load_status()
        segments = current_status.get('segments', [])
        
        if not segments:
            print("❌ No segments found. Run enumerate command first.")
            return
        
        # Filter segments that have frames extracted
        segments_with_frames = [seg for seg in segments if seg.get('status') == 'frames_extracted' and seg.get('frames')]
        
        if not segments_with_frames:
            print("❌ No segments with extracted frames found. Run extract-frames command first.")
            return
        
        print(f"🤖 Starting image analysis for {len(segments_with_frames)} segments...")
        
        # Analyze all segments
        analysis_results = image_analyzer.analyze_all_segments(segments_with_frames)
        
        # Update status with analysis results
        for segment_id, analysis_result in analysis_results.items():
            status_manager.update_segment_analysis(segment_id, analysis_result)
        
        # Get analysis summary
        analysis_summary = image_analyzer.get_analysis_summary()
        
        print(f"\n✅ Image analysis completed!")
        print(f"🔍 Total segments analyzed: {analysis_summary['total_segments']}")
        print(f"📸 Total frames analyzed: {analysis_summary['total_frames']}")
        
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
            
            # Frames summary if available
            frame_extractor = FrameExtractor(processor.cache_dir)
            frames_summary = frame_extractor.get_frames_summary()
            if frames_summary['total_frames'] > 0:
                print(f"   📸 Frames extracted: {frames_summary['total_frames']}")
                print(f"   💾 Frames size: {frames_summary['total_size_mb']} MB")
            
            # Analysis summary if available
            image_analyzer = ImageAnalyzer(processor.cache_dir)
            analysis_summary = image_analyzer.get_analysis_summary()
            if analysis_summary['total_frames'] > 0:
                print(f"   🔍 Frames analyzed: {analysis_summary['total_frames']}")
                print(f"   🤖 Segments analyzed: {analysis_summary['total_segments']}")
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
    
    # Extract frames command
    extract_parser = subparsers.add_parser('extract-frames', help='Extract frames from video segments')
    extract_parser.add_argument('media_dir', help='Path to directory with media files')
    extract_parser.add_argument('--frames', '-f', type=int, default=2,
                               help='Number of frames per segment (default: 2)')
    
    # Analyze images command
    analyze_parser = subparsers.add_parser('analyze-images', help='Analyze extracted frames using vision model')
    analyze_parser.add_argument('media_dir', help='Path to directory with media files')
    analyze_parser.add_argument('--model', '-m', default='Salesforce/blip2-opt-2.7b',
                               help='HuggingFace model name (default: Salesforce/blip2-opt-2.7b)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current processing status')
    status_parser.add_argument('media_dir', help='Path to directory with media files')
    
    args = parser.parse_args()
    
    if args.command == 'enumerate':
        enumerate_command(args.media_dir, args.duration, args.cache)
    elif args.command == 'extract-frames':
        extract_frames_command(args.media_dir, args.frames)
    elif args.command == 'analyze-images':
        analyze_images_command(args.media_dir, args.model)
    elif args.command == 'status':
        status_command(args.media_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
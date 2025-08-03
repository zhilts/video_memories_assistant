import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration


class ImageAnalyzer:
    """Analyze images using BLIP-2 vision model"""
    
    def __init__(self, cache_dir: Path, model_name: str = "Salesforce/blip2-opt-2.7b"):
        """
        Initialize image analyzer
        
        Args:
            cache_dir: Path to cache directory
            model_name: HuggingFace model name for BLIP-2 (default: 2.7B model)
                      Alternative: "Salesforce/blip2-opt-1.7b" for faster processing
        """
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Create analysis results directory
        self.analysis_dir = self.cache_dir / 'analysis'
        self.analysis_dir.mkdir(exist_ok=True)
    
    def load_model(self):
        """Load vision model and processor"""
        if self.processor is None or self.model is None:
            print(f"🤖 Loading vision model: {self.model_name}")
            print(f"📱 Using device: {self.device}")
            
            try:
                if "blip2" in self.model_name.lower():
                    # BLIP-2 models
                    self.processor = Blip2Processor.from_pretrained(self.model_name, use_fast=False)
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                else:
                    # Other vision models
                    from transformers import AutoProcessor, AutoModelForVision2Seq
                    self.processor = AutoProcessor.from_pretrained(self.model_name, use_fast=False)
                    self.model = AutoModelForVision2Seq.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                
                if self.device == "cuda":
                    self.model.to(self.device)
                
                print("✅ Model loaded successfully!")
                
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                raise
    
    def analyze_single_image(self, image_path: str, prompt: str = "Describe this image in detail") -> str:
        """
        Analyze a single image
        
        Args:
            image_path: Path to image file
            prompt: Prompt for image analysis
            
        Returns:
            Generated description
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Prepare inputs with explicit size parameters
            if "blip2" in self.model_name.lower():
                # BLIP-2 models handle size automatically
                inputs = self.processor(image, prompt, return_tensors="pt")
            else:
                # For other models, specify size explicitly
                inputs = self.processor(
                    image, 
                    prompt, 
                    return_tensors="pt",
                    size={"height": 224, "width": 224}
                )
            
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate description
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=30,
                    do_sample=False,
                    num_beams=1,
                    pad_token_id=self.processor.tokenizer.eos_token_id,
                    max_time=30  # 30 second timeout
                )
            
            # Decode output
            description = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the beginning
            if description.startswith(prompt):
                description = description[len(prompt):].strip()
            
            # If description is empty, provide a fallback
            if not description:
                description = "Video frame with visual content"
            
            return description
            
        except Exception as e:
            print(f"Error analyzing image {image_path}: {e}")
            return "Video frame with visual content"
    
    def analyze_segment_frames(self, segment_id: str, frame_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze all frames for a segment
        
        Args:
            segment_id: Segment identifier
            frame_paths: List of frame file paths
            
        Returns:
            Dictionary with analysis results
        """
        print(f"🔍 Analyzing frames for segment: {segment_id}")
        
        analyses = []
        for i, frame_path in enumerate(frame_paths):
            if Path(frame_path).exists():
                print(f"   📸 Analyzing frame {i+1}/{len(frame_paths)}")
                
                # Analyze with different prompts for better coverage
                prompts = [
                    "Describe this image in detail",
                    "What is happening in this image?",
                    "Describe the visual content of this image"
                ]
                
                frame_analyses = {}
                for j, prompt in enumerate(prompts):
                    description = self.analyze_single_image(frame_path, prompt)
                    frame_analyses[f"description_{j+1}"] = description
                
                frame_analyses['frame_path'] = frame_path
                frame_analyses['frame_index'] = i
                analyses.append(frame_analyses)
            else:
                print(f"   ⚠️  Frame not found: {frame_path}")
        
        # Combine analyses for the segment
        combined_description = self._combine_frame_descriptions(analyses)
        
        result = {
            'segment_id': segment_id,
            'frame_analyses': analyses,
            'combined_description': combined_description,
            'num_frames_analyzed': len(analyses)
        }
        
        # Save analysis to file
        analysis_file = self.analysis_dir / f"{segment_id}_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Analyzed {len(analyses)} frames")
        return result
    
    def _combine_frame_descriptions(self, frame_analyses: List[Dict[str, Any]]) -> str:
        """
        Combine descriptions from multiple frames
        
        Args:
            frame_analyses: List of frame analysis results
            
        Returns:
            Combined description
        """
        if not frame_analyses:
            return "No frames analyzed"
        
        descriptions = []
        for analysis in frame_analyses:
            # Use the first description as primary
            primary_desc = analysis.get('description_1', '')
            if primary_desc:
                descriptions.append(primary_desc)
        
        if len(descriptions) == 1:
            return descriptions[0]
        else:
            # Combine multiple descriptions
            combined = f"Scene shows: {'; '.join(descriptions)}"
            return combined
    
    def analyze_all_segments(self, segments_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze frames for all segments
        
        Args:
            segments_data: List of segment data with frame information
            
        Returns:
            Dictionary mapping segment_id to analysis results
        """
        print(f"🎯 Starting image analysis for {len(segments_data)} segments...")
        
        results = {}
        total_segments = len(segments_data)
        
        for i, segment in enumerate(segments_data, 1):
            segment_id = segment.get('segment_id')
            frame_paths = segment.get('frames', [])
            
            print(f"📊 Progress: {i}/{total_segments} segments")
            
            if frame_paths:
                analysis_result = self.analyze_segment_frames(segment_id, frame_paths)
                results[segment_id] = analysis_result
            else:
                print(f"⚠️  No frames found for segment: {segment_id}")
        
        print(f"✅ Image analysis completed for {len(results)} segments")
        return results
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of analysis results"""
        if not self.analysis_dir.exists():
            return {'total_segments': 0, 'total_frames': 0}
        
        total_segments = 0
        total_frames = 0
        
        for analysis_file in self.analysis_dir.glob('*_analysis.json'):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    total_segments += 1
                    total_frames += analysis_data.get('num_frames_analyzed', 0)
            except Exception as e:
                print(f"Error reading analysis file {analysis_file}: {e}")
        
        return {
            'total_segments': total_segments,
            'total_frames': total_frames
        } 
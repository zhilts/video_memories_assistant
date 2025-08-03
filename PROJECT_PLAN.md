# Video Memories Assistant

## 🧩 Project Goal
Create a local tool that helps automatically analyze a large video archive (e.g., vacation footage) and assist in selecting highlights that capture meaningful moments. The tool extracts image and audio-based descriptions from defined video segments, optionally suggests sequences for storytelling, and outputs structured data for further editing.

## 🛠️ Tools and Technologies
- Python (main logic)
- ffmpeg (for video/audio processing)
- Whisper (speech/audio analysis)
- BLIP-2 / ImageBind / etc. (image-based description)
- Node.js or Bash (optional utility scripts)
- Git for version control
- `.cache/status.json` — progress tracker for segment processing
- `.cache/` — stores intermediate results (ignored by Git)

⚠️ `.cache/` is not stored in the project folder itself. It is expected to be placed alongside the input media folder to allow switching between multiple projects with separate caches.

## 📂 Project Structure
```
video_memories_assistant/
├── main.py                  # Entry point script
├── utils/                   # Supporting modules (e.g., ffmpeg, whisper)
├── .gitignore
└── PROJECT_PLAN.md          # This file

/media/my-trip-2025/        # Input files directory (external)
├── DSC_0142.mov
├── external_audio.wav
└── .cache/                 # Cached frames, audio, status.json, etc.
    └── status.json
```

## 📌 Workflow Steps
- [x] Define project structure and purpose
- [ ] Enumerate video files and break them into virtual segments (e.g., 10 seconds)
- [ ] Extract 1–2 representative frames per segment using ffmpeg
- [ ] Run frame analysis via vision model (e.g., BLIP-2 or ImageBind)
- [ ] Extract audio and run transcription via Whisper
- [ ] Combine results into a structured JSON
- [ ] Use LLM to group and summarize segments into coherent "stories"
- [ ] Select top stories/highlights
- [ ] (Optional) Generate a rough cut using ffmpeg or export XML to video editors

## 🔄 Example JSON Fragment
```json
{
  "file": "DSC_0142.mov",
  "start": "00:01:30",
  "end": "00:01:40",
  "image_desc": "Skier rides fast, snow trail behind",
  "audio_desc": "Crunching snow, no speech",
  "tags": ["ski", "speed", "motion"]
}
```

## 📍 Notes
- Processing must work locally (target: Apple Silicon / M-series Macs)
- Maintain links to original files and timestamps
- Use virtual slicing (not actual `.mp4` cutting) via `ffmpeg -ss`
- Store `status.json` inside the `.cache/` directory located next to media inputs
- Allow manual correction at any stage (JSON or file level)

## 🎙️ Optional: External Audio Synchronization
This project may support aligning external audio recordings (e.g., from a separate device) with the original video files.

- Sync is based on matching sharp audio events (like claps)
- May be implemented via audio waveform correlation
- Can be added at any stage: either during initial processing or after some results are already present
- Each external audio file is matched to video clips and an offset (in seconds) is calculated
- Drift across long recordings is possible and needs to be addressed (either by manual cut points or dynamic resync strategies)
- For now, this feature is optional and not required for MVP

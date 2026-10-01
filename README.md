# bs_xc_ut

bs_xc_ut is an original desktop video editor project inspired by timeline-based editors, built for fast local editing, media management, and export workflows.

This project is not a copy of DaVinci Resolve, but it provides a practical starting point for a real editor UI with a timeline, media import, preview, and FFmpeg-based export.

## Features
- Add media files from your local machine
- View imported clips in a library
- Timeline list for sequence assembly
- Preview selected clip with ffplay when available
- Export combined clip sequence to MP4 using FFmpeg
- Lightweight, Python-based desktop UI using PySide6

## Requirements
- Python 3.10+
- FFmpeg installed and available on PATH
- A desktop environment (Linux/macOS/Windows)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

## Notes
- On Linux/macOS, ensure `ffmpeg` and `ffprobe` are installed.
- On Windows, install FFmpeg and add it to PATH.
- The export pipeline concatenates clips in the order they appear in the timeline.

## Project structure

```text
bs_xc_ut/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── project.py
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
└── .venv/
```

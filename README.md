# AutoYTEdit

AI-powered automatic video editor for YouTube. Drop your video, get viral-ready content with person detection, dynamic effects, and engaging text overlays.

## Features

- Person detection using YOLOv8 (GPU/CPU)
- Dynamic tracking lines and labels on detected people
- Random effects: zoom, shake, flash, glow, chromatic aberration
- Animated/glitch text with viral captions
- Cinematic color grading (cinematic/warm/cold/vintage)
- Auto vignette
- Speed ramps
- Preserves original audio
- Every edit is unique due to randomization

## Installation

```bash
git clone https://github.com/yourusername/AutoYTEdit.git
cd AutoYTEdit
pip install -r requirements.txt
```

## Usage

1. Put your videos in the `input/` folder
2. Run the editor:

```bash
python main.py
```

Or process a specific video:

```bash
python main.py path/to/video.mp4
```

3. Find edited videos in `output/`

## Requirements

- Python 3.8+
- NVIDIA GPU (optional, for faster processing)
- FFmpeg (for audio processing)

## Configuration

Edit `config.py` to customize:

- Caption texts
- Color schemes
- Effect intensities
- Detection confidence
- GPU/CPU preference

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Pull requests welcome!
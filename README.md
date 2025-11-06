# 🎬 GIF Maker v2.0 - Professional Edition

A powerful and feature-rich video to GIF converter built with Python. Transform your videos into high-quality GIFs with advanced editing capabilities, effects, and batch processing.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

### Core Functionality
- **Multi-Format Support**: Import MP4, AVI, MOV, MKV, WebM, FLV, WMV
- **Multiple Output Formats**: Export as GIF, WebP, or APNG
- **Timeline Selection**: Precisely select start and end frames with visual sliders
- **Smart Preview**: Real-time preview with all effects applied
- **Memory Optimized**: Efficient processing for large videos

### Effects & Filters
- **Image Adjustments**: 
  - Brightness control (0.0 - 2.0)
  - Contrast control (0.0 - 2.0)
  - Saturation control (0.0 - 2.0)
- **Filters**: Grayscale and Sepia tone
- **Transformations**: 
  - Rotation (90°, 180°, 270°)
  - Flip horizontal/vertical
- **Crop Tool**: Click and drag to crop any area

### Text & Overlays
- **Text Overlays**: Add custom text with:
  - Adjustable font size (10-200px)
  - 7 position presets (top, center, bottom, corners)
  - Custom color selection
  - Text outline for better visibility
- **Watermarks**: Add image watermarks (PNG, JPG, GIF)
- **Multiple Overlays**: Add and manage multiple text/watermarks

### Advanced Settings
- **Quality Control**: 
  - Adjustable color depth (32-256 colors)
  - Dithering options (None, Floyd-Steinberg)
  - File size optimization
- **Frame Sampling**: Skip frames to reduce file size
- **Reverse Playback**: Create reverse GIFs
- **Speed Control**: Adjustable FPS (frames per second)
- **Scale Options**: Resize from 0.1x to 2.0x

### Productivity Features
- **Batch Processing**: Convert multiple videos at once
- **Presets**: Quick settings for:
  - Twitter (optimized for social media)
  - Instagram (high quality, social-ready)
  - Discord (balanced size/quality)
  - High Quality (maximum quality)
  - Small File (minimum file size)
- **File Size Estimation**: Preview estimated output size
- **Activity Log**: Track all operations and progress

### User Interface
- **Dark/Light Theme**: Toggle with Ctrl+T
- **Tabbed Interface**: Organized into 4 tabs
  - Main: Video loading and export
  - Effects & Filters: Apply visual effects
  - Text & Overlays: Add text and watermarks
  - Advanced: Fine-tune settings and view logs
- **Keyboard Shortcuts**: 
  - `Ctrl+O`: Open video
  - `Ctrl+E`: Export
  - `Ctrl+T`: Toggle theme
  - `Space`: Play/Pause preview
- **Scrollable Interface**: Works on any screen size
- **Progress Tracking**: Real-time progress bar and status updates

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Required Dependencies

```bash
pip install opencv-python pillow numpy
```

Or install all dependencies at once:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. **Run the application**:
   ```bash
   python main.py
   ```

2. **Load a video**: 
   - Click "Select Video" or press `Ctrl+O`
   - Choose your video file

3. **Select frame range** (optional):
   - Use the timeline sliders to select start and end frames

4. **Apply effects** (optional):
   - Go to "Effects & Filters" tab
   - Adjust brightness, contrast, saturation
   - Apply filters or transformations

5. **Add text/watermark** (optional):
   - Go to "Text & Overlays" tab
   - Add custom text or watermark

6. **Configure export settings**:
   - Choose a preset or customize settings
   - Adjust FPS, scale, colors, and format

7. **Export**:
   - Click "Export" or press `Ctrl+E`
   - Choose save location
   - Wait for processing to complete

### Batch Processing

1. Go to **File → Batch Process**
2. Select multiple video files
3. Choose output directory
4. Wait for all files to process

### Crop Tool

1. Load a video
2. Click and drag on the preview to select crop area
3. Release to set crop
4. Click "Reset Crop" to remove

## Tips & Best Practices

### For Smaller File Sizes
- Use the "Small File" preset
- Reduce scale (0.3 - 0.5)
- Lower FPS (10-15)
- Reduce colors (64-128)
- Enable optimization
- Use frame skipping for long videos

### For Best Quality
- Use the "High Quality" preset
- Keep scale at 1.0 or higher
- Use 30 FPS
- Use 256 colors
- Disable optimization
- Use Floyd-Steinberg dithering

### For Social Media
- **Twitter**: Use Twitter preset (max 15MB)
- **Instagram**: Use Instagram preset
- **Discord**: Use Discord preset (max 8MB for free users)

### Performance Tips
- Long videos (>1 min): Use frame skipping (2-5 frames)
- Large videos (4K): Reduce scale to 0.3-0.5
- Batch processing: Use consistent settings across all files

## Technical Specifications

- **Supported Input Formats**: MP4, AVI, MOV, MKV, WebM, FLV, WMV
- **Supported Output Formats**: GIF, WebP, APNG
- **Maximum Resolution**: Limited by system memory
- **Frame Rate**: 1-60 FPS
- **Color Depth**: 32-256 colors
- **Scale Range**: 0.1x - 2.0x

## Troubleshooting

### Application won't start
- Ensure Python 3.7+ is installed
- Install all required dependencies: `pip install -r requirements.txt`
- Check Python is in system PATH

### Video won't load
- Verify video file is not corrupted
- Ensure video codec is supported
- Try converting video to MP4 format

### Export fails
- Check available disk space
- Reduce video length or scale
- Lower color count or FPS
- Enable optimization

### Out of memory errors
- Reduce video length using timeline sliders
- Lower scale setting
- Use frame skipping
- Close other applications

### Preview not showing
- Check video file integrity
- Try reloading the video
- Restart application

## Version History

### Version 2.0.0 (Current)
- Complete UI overhaul with tabbed interface
- Added effects and filters (brightness, contrast, saturation, grayscale, sepia)
- Added transformation tools (rotation, flip)
- Added crop functionality
- Added text overlays with customization
- Added watermark support
- Added batch processing
- Added multiple output formats (GIF, WebP, APNG)
- Added presets for quick settings
- Added dark/light theme toggle
- Added keyboard shortcuts
- Added file size estimation
- Added activity logging
- Memory optimization for large videos
- Timeline slider for frame selection
- Scrollable interface for any screen size
- Progress tracking with detailed status updates

### Version 1.0.0
- Basic video to GIF conversion
- Simple preview
- Basic FPS and scale controls
- MP4 input only
- GIF output only

## Requirements.txt

Create a `requirements.txt` file with:

```
opencv-python>=4.5.0
Pillow>=9.0.0
numpy>=1.19.0
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/sivaprasanth2221/GIF-Maker-in-Python.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Test thoroughly
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature`
8. Open a Pull Request

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Author

**[Siva Prasanth]**
- GitHub: [@sivaprasanth2221](https://github.com/sivaprasanth2221)
- Email: sivabhuvan20@gmail.com

## Acknowledgments

- Built with Python, OpenCV, and Pillow
- Icons: Unicode emoji
- Inspired by the need for a powerful, free GIF maker

## Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Search [existing issues](https://github.com/sivaprasanth2221/GIF-Maker-in-Python/issues)
3. Open a [new issue](https://github.com/sivaprasanth2221/GIF-Maker-in-Python/issues/new)

## Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ for the GIF community**
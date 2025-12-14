# VidFetch

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Cross-platform media downloader with a modern GUI** - Download videos, audio, and playlists from YouTube and other platforms with queue management, format conversion, and batch processing.

![VidFetch Screenshot](screenshots/main-window.png)

## ✨ Features

### 🎬 Multi-Platform Support
- **YouTube** - Videos, playlists, channels, and live streams
- **Vimeo** - High-quality video downloads
- **SoundCloud** - Audio tracks and playlists
- **Dailymotion** - Video content
- And many more supported by yt-dlp

### 📥 Flexible Downloads
- **Quality Selection** - Choose from 4K, 1080p, 720p, 480p, and more
- **Audio Extraction** - Download as MP3, M4A, FLAC, or other formats
- **Subtitles** - Download auto-generated and manual subtitles in multiple languages
- **Thumbnails** - Extract and save video thumbnails
- **Format Conversion** - Built-in FFmpeg integration for format conversion

### 🚀 Batch Processing
- **Queue Management** - Add multiple URLs and manage download queue
- **Playlist Support** - Download entire playlists or channels at once
- **Parallel Downloads** - Configure thread count for simultaneous downloads
- **Progress Tracking** - Real-time speed, ETA, and percentage for each download

### 🎨 Modern Interface
- **Clean GUI** - Built with PyQt6 for a native feel on all platforms
- **Dark/Light Theme** - Switch between themes based on preference
- **System Tray** - Minimize to tray and continue downloads in background
- **Download History** - Search and review past downloads
- **Drag & Drop** - Drop URLs directly into the app

### ⚙️ Advanced Features
- **Auto-Updates** - Automatically update yt-dlp to latest version
- **Filename Templates** - Customize output file naming patterns
- **Metadata Embedding** - Embed title, artist, and thumbnail in files
- **Scheduled Downloads** - Set downloads to start at specific times
- **Retry Logic** - Automatic retry on failed downloads
- **Settings Profiles** - Save different configurations for different use cases

## 📦 Installation

### Pre-built Binaries (Recommended)

Download the latest release for your platform:

**Windows:**
```bash
# Download VidFetch-Windows-x64.exe from Releases
# No installation required - just run the executable
```

**macOS:**
```bash
# Download VidFetch-macOS.dmg from Releases
# Drag VidFetch to Applications folder
```

**Linux:**
```bash
# Download VidFetch-Linux-x64.AppImage from Releases
chmod +x VidFetch-Linux-x64.AppImage
./VidFetch-Linux-x64.AppImage
```

### From Source

#### Prerequisites
- Python 3.9 or higher
- FFmpeg (for format conversion)

#### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/vidfetch.git
cd vidfetch
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install FFmpeg:**

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Debian/Ubuntu
sudo dnf install ffmpeg  # Fedora
```

5. **Run VidFetch:**
```bash
python src/main.py
```

## 🚀 Quick Start

### Basic Usage

1. **Launch VidFetch**
2. **Paste a URL** into the input field (or drag & drop)
3. **Select quality/format** from the dropdown
4. **Click Download** or press Enter
5. **Monitor progress** in real-time

### Downloading a Playlist

1. Paste the playlist URL
2. Click the **Playlist Options** button
3. Choose to download all or select specific videos
4. Select format and quality
5. Click **Add to Queue**
6. Start downloads

### Audio-Only Downloads

1. Paste video URL
2. Select **Audio Only** tab
3. Choose format (MP3, M4A, FLAC)
4. Select bitrate (128k, 256k, 320k)
5. Click **Download Audio**

### Batch Processing

```
# Add multiple URLs (one per line)
https://youtube.com/watch?v=VIDEO1
https://youtube.com/watch?v=VIDEO2
https://youtube.com/watch?v=VIDEO3

# Or paste entire playlist URLs
https://youtube.com/playlist?list=PLAYLIST_ID
```

## ⚙️ Configuration

### Settings Panel

Access via **Settings** (⚙️ icon) or `Ctrl+,` / `Cmd+,`

#### General
- **Download Directory** - Where files are saved
- **Filename Template** - Customize naming pattern
  - `{title}` - Video title
  - `{uploader}` - Channel name
  - `{date}` - Upload date
  - `{id}` - Video ID
  - Example: `{uploader} - {title} [{id}].{ext}`

#### Downloads
- **Parallel Downloads** - Number of simultaneous downloads (1-10)
- **Default Quality** - Preferred video quality
- **Auto-Retry** - Retry failed downloads (0-5 attempts)
- **Speed Limit** - Limit download speed (KB/s)

#### Behavior
- **Auto-Update yt-dlp** - Check for updates on startup
- **Minimize to Tray** - Hide to system tray instead of closing
- **Download Complete Notification** - Desktop notification
- **Auto-Start Downloads** - Start downloads immediately when added

#### Advanced
- **FFmpeg Path** - Custom FFmpeg location
- **Proxy Settings** - HTTP/SOCKS5 proxy configuration
- **Cookie File** - Import cookies for restricted content
- **Custom Arguments** - Pass additional yt-dlp arguments

### Filename Templates

Default: `{title}.{ext}`

Custom examples:
```
{uploader}/{title}.{ext}
{date} - {title} [{id}].{ext}
{playlist_title}/{playlist_index:03d} - {title}.{ext}
```

## 📝 Command Line Usage

VidFetch also supports command-line mode:

```bash
# Basic download
python src/main.py --url "https://youtube.com/watch?v=VIDEO_ID"

# Specify quality
python src/main.py --url "URL" --quality 1080p

# Audio only
python src/main.py --url "URL" --audio-only --format mp3

# Batch download from file
python src/main.py --batch urls.txt

# Show all options
python src/main.py --help
```

## 🔧 Building from Source

### Windows Executable

```bash
pip install pyinstaller
pyinstaller vidfetch.spec
# Output: dist/VidFetch.exe
```

### macOS App Bundle

```bash
pip install py2app
python setup.py py2app
# Output: dist/VidFetch.app
```

### Linux AppImage

```bash
pip install PyInstaller
pyinstaller --onefile src/main.py
# Use appimagetool to create AppImage
```

## 🐛 Troubleshooting

### "FFmpeg not found" error
- Ensure FFmpeg is installed and in your PATH
- Or specify FFmpeg path in Settings → Advanced

### Download fails immediately
- Update yt-dlp: Settings → About → Update yt-dlp
- Check if the video is region-restricted or private

### Slow download speeds
- Try changing DNS servers
- Disable VPN if active
- Check Settings → Downloads → Speed Limit

### "Age-restricted" video errors
- Import cookies from your browser: Settings → Advanced → Cookie File
- Use a logged-in browser session's cookies

### GUI doesn't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linter
flake8 src/

# Format code
black src/
```

### Code Style
- Follow PEP 8
- Use type hints where possible
- Write docstrings for public functions
- Add unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful video downloader backend
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [FFmpeg](https://ffmpeg.org/) - Media processing
- All contributors and users who provide feedback

## 📬 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/vidfetch/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/vidfetch/discussions)
- **Email:** your.email@example.com

## 🗺️ Roadmap

- [ ] Browser extension for one-click downloads
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Built-in video player and preview
- [ ] Subtitle editing and synchronization
- [ ] Download scheduler with calendar view
- [ ] Video conversion presets (mobile, TV, etc.)
- [ ] Multi-language interface support
- [ ] Plugin system for custom extractors

## ⭐ Star History

If you find VidFetch useful, please consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/vidfetch&type=Date)](https://star-history.com/#yourusername/vidfetch&Date)

---

**Made with ❤️ by [Your Name](https://github.com/yourusername)**

*For educational purposes only. Please respect copyright laws and terms of service of the platforms you download from.*

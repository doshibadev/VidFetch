# VidFetch

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**VidFetch** is a powerful, cross-platform media downloader built with Python and PyQt6. It provides a modern graphical interface for `yt-dlp`, enabling users to download high-quality videos, audio, and playlists from YouTube, Vimeo, SoundCloud, and hundreds of other sites.

Designed with performance in mind, VidFetch features a robust asynchronous queue system, allowing for efficient parallel downloads without freezing the interface.

![VidFetch Screenshot](screenshots/main-window.png)
*(Note: Add a screenshot here)*

## ✨ Key Features

### 🎬 Universal Compatibility
*   **Multi-Platform:** Supports YouTube, Vimeo, Dailymotion, Twitch, SoundCloud, and [1000+ others](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).
*   **Formats:** Download videos in 4K/1080p or extract audio directly to MP3.
*   **Playlists:** Batch download entire playlists or channels with a single click.

### ⚡ Powerful Download Engine
*   **Async Queue:** Robust `asyncio`-based task manager processes downloads in the background.
*   **Parallel Processing:** Configure multiple concurrent downloads to maximize bandwidth.
*   **Smart Controls:** Pause, Resume, or Cancel tasks instantly.
*   **System Tray:** Minimize the app to the tray and let it work silently in the background.

### 🛠️ Advanced Tools
*   **History Log:** Built-in SQLite database keeps track of all your downloads.
*   **Searchable History:** Quickly find past downloads by title or URL.
*   **Subtitles & Thumbnails:** Option to auto-download subtitles and video thumbnails.
*   **Format Conversion:** Integrated FFmpeg support for reliable media conversion.

## 📦 Installation

### Prerequisites
*   Python 3.10 or higher
*   [FFmpeg](https://ffmpeg.org/download.html) (Required for audio extraction and format merging)

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/doshibadev/vidfetch.git
    cd vidfetch
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python src/main.py
    ```

## 🏗️ Technical Architecture

VidFetch demonstrates a modern Python desktop application architecture:

*   **GUI Framework:** `PyQt6` for a native, responsive user interface.
*   **Core Logic:** `src/core/queue_manager.py` implements a custom `QObject` wrapper around an `asyncio` event loop, bridging the gap between Qt's signal/slot mechanism and Python's async capabilities.
*   **Backend:** Wraps `yt-dlp` for reliable media extraction.
*   **Persistence:** Uses `sqlite3` for transactional history storage and JSON for user configuration.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Disclaimer: This tool is for educational purposes only. Please respect the copyright and terms of service of the websites you download from.*

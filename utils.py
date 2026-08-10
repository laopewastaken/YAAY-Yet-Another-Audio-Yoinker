
from pathlib import Path
import winsound
import urllib.request
import tempfile
import shutil
import json
import zipfile
import tkinter as tk
from tkinter import ttk

import sys

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

DEPENDENCIES_DIR = APP_DIR / "dependencies"
DOWNLOADS_DIR = APP_DIR / "downloads"
TEMP_DOWNLOAD_DIR = DOWNLOADS_DIR / "temp_download"

YTDLP = DEPENDENCIES_DIR / "yt-dlp.exe"
FFMPEG = DEPENDENCIES_DIR / "ffmpeg.exe"
FFPROBE = DEPENDENCIES_DIR / "ffprobe.exe"

YTDLP_URL = (
    "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
)

FFMPEG_API_URL = (
    "https://api.github.com/repos/GyanD/codexffmpeg/releases/latest"
)


def ensure_directories():
    """
    Create YAAY's required runtime directories if they don't exist.
    """

    DEPENDENCIES_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

def ensure_dependencies():
    """
    Make sure all required external dependencies are installed.
    Shows a live progress window during first-time setup.
    """

    ensure_directories()

    missing_ytdlp = not YTDLP.exists()
    missing_ffmpeg = not FFMPEG.exists() or not FFPROBE.exists()

    # Everything is already installed.
    if not missing_ytdlp and not missing_ffmpeg:
        return

    import tkinter as tk
    from tkinter import ttk
    import threading
    import queue

    root = tk.Tk()
    root.title("YAAY - First-time setup")
    root.geometry("450x170")
    root.resizable(False, False)

    # Keep the setup window visible.
    root.attributes("-topmost", True)

    # Center the window.
    root.update_idletasks()

    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2

    root.geometry(f"+{x}+{y}")

    title = tk.Label(
        root,
        text="YAAY is setting things up...",
        font=("Segoe UI", 12, "bold")
    )
    title.pack(pady=(20, 8))

    status = tk.Label(
        root,
        text="Preparing...",
        font=("Segoe UI", 9)
    )
    status.pack()

    progress = ttk.Progressbar(
        root,
        length=380,
        maximum=100,
        mode="determinate"
    )
    progress.pack(pady=15)

    messages = queue.Queue()

    def send_progress(downloaded, total, percentage):
        messages.put(
            ("progress", downloaded, total, percentage)
        )

    def worker():
        try:
            if missing_ytdlp:
                messages.put(
                    ("status", "Downloading yt-dlp...")
                )

                download_ytdlp(send_progress)

            if missing_ffmpeg:
                messages.put(
                    ("status", "Downloading FFmpeg...")
                )

                install_ffmpeg(send_progress)

            messages.put(("done",))

        except Exception as error:
            messages.put(("error", str(error)))

    def update_ui():
        try:
            while True:
                message = messages.get_nowait()

                if message[0] == "status":
                    status.config(text=message[1])

                elif message[0] == "progress":
                    _, downloaded, total, percentage = message

                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total / (1024 * 1024)

                    status.config(
                        text=(
                            f"Downloading... "
                            f"{downloaded_mb:.1f} MB / "
                            f"{total_mb:.1f} MB "
                            f"({percentage:.0f}%)"
                        )
                    )

                    progress["value"] = percentage

                elif message[0] == "done":
                    status.config(text="Setup complete!")
                    progress["value"] = 100

                    root.after(700, root.destroy)
                    return

                elif message[0] == "error":
                    status.config(
                        text=f"Setup failed: {message[1]}"
                    )

                    progress["value"] = 0

                    root.after(10000, root.destroy)
                    return

        except queue.Empty:
            pass

        root.after(50, update_ui)

    # Start downloading in the background.
    threading.Thread(
        target=worker,
        daemon=True
    ).start()

    # Keep the UI responsive.
    root.after(50, update_ui)

    root.mainloop()

def download_file(url, destination, progress_callback=None):
    """
    Download a file and optionally report download progress.
    """

    def reporthook(block_count, block_size, total_size):
        if total_size > 0:
            downloaded = block_count * block_size
            downloaded = min(downloaded, total_size)

            percentage = (downloaded / total_size) * 100

            if progress_callback:
                progress_callback(
                    downloaded,
                    total_size,
                    percentage
                )

    urllib.request.urlretrieve(
        url,
        destination,
        reporthook=reporthook
    )

def download_ytdlp(progress_callback=None):
    """
    Download the latest yt-dlp executable.
    """

    ensure_directories()

    download_file(
        YTDLP_URL,
        YTDLP,
        progress_callback
    )


def get_latest_ffmpeg_url():
    """
    Get the download URL for the latest GyanD FFmpeg full build ZIP.
    """

    request = urllib.request.Request(
        FFMPEG_API_URL,
        headers={
            "User-Agent": "YAAY-FFmpeg-Downloader"
        }
    )

    with urllib.request.urlopen(request) as response:
        release = json.loads(response.read().decode("utf-8"))

    for asset in release.get("assets", []):
        name = asset.get("name", "")

        if name.endswith("-full_build.zip"):
            return asset["browser_download_url"]

    raise RuntimeError(
        "Could not find the latest FFmpeg full_build.zip release."
    )


def install_ffmpeg(progress_callback=None):
    """
    Download and install the latest GyanD FFmpeg full build.

    Uses Python's built-in ZIP support.
    No 7-Zip or other external archive program is required.
    """

    ensure_directories()

    ffmpeg_url = get_latest_ffmpeg_url()

    with tempfile.TemporaryDirectory(
        dir=TEMP_DOWNLOAD_DIR
    ) as temp_dir:

        temp_dir = Path(temp_dir)
        zip_path = temp_dir / "ffmpeg.zip"
        extract_dir = temp_dir / "extracted"

        download_file(
            ffmpeg_url,
            zip_path,
            progress_callback
        )

        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(extract_dir)

        ffmpeg_source = next(
            extract_dir.rglob("ffmpeg.exe"),
            None
        )

        ffprobe_source = next(
            extract_dir.rglob("ffprobe.exe"),
            None
        )

        if ffmpeg_source is None:
            raise RuntimeError(
                "FFmpeg was downloaded, but ffmpeg.exe could not be found."
            )

        if ffprobe_source is None:
            raise RuntimeError(
                "FFmpeg was downloaded, but ffprobe.exe could not be found."
            )

        if FFMPEG.exists():
            FFMPEG.unlink()

        if FFPROBE.exists():
            FFPROBE.unlink()

        shutil.copy2(ffmpeg_source, FFMPEG)
        shutil.copy2(ffprobe_source, FFPROBE)

    return FFMPEG, FFPROBE

def display_url(url, maximum=65):
    """
    Return a shortened visual representation of a URL.
    The original URL remains unchanged elsewhere.
    """

    if len(url) <= maximum:
        return url

    return url[:maximum] + "..."


def play_success_sound():
    """
    Play the standard Windows success/OK sound.
    """

    winsound.MessageBeep(winsound.MB_OK)


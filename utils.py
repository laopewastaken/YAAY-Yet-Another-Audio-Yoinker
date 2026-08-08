from pathlib import Path
import winsound


APP_DIR = Path(__file__).resolve().parent

DEPENDENCIES_DIR = APP_DIR / "dependencies"
DOWNLOADS_DIR = APP_DIR / "downloads"
TEMP_DOWNLOAD_DIR = DOWNLOADS_DIR / "temp_download"

YTDLP = DEPENDENCIES_DIR / "yt-dlp.exe"
FFMPEG = DEPENDENCIES_DIR / "ffmpeg.exe"


def ensure_directories():
    """
    Create YAAY's required runtime directories if they don't exist.
    """

    DEPENDENCIES_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


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

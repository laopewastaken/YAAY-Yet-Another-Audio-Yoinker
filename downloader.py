
import subprocess
from pathlib import Path

from filenames import get_filename
from utils import (
    APP_DIR,
    TEMP_DOWNLOAD_DIR,
    FFMPEG,
    YTDLP,
)


def _run(command):
    """
    Run a subprocess inside YAAY's application directory.
    """

    return subprocess.run(
        command,
        cwd=APP_DIR,
        capture_output=True,
        text=True,
    )


def _download_tiktok(current_url, metadata, output_folder):
    """
    TikTok path:
    download a usable video+audio format temporarily,
    extract the AAC stream with FFmpeg, then delete the
    temporary video.
    """

    info = metadata["info"]
    current_title = metadata["title"]
    current_channel = metadata["channel"]
    current_id = metadata["media_id"]

    formats = info.get("formats", [])

    candidates = []

    for fmt in formats:

        if fmt.get("vcodec") in (None, "none"):
            continue

        if fmt.get("acodec") in (None, "none"):
            continue

        format_id = fmt.get("format_id", "")

        if format_id == "download":
            continue

        candidates.append(fmt)

    if not candidates:
        raise RuntimeError(
            "TikTok did not provide a usable audio format."
        )

    def resolution_score(fmt):
        width = fmt.get("width") or 0
        height = fmt.get("height") or 0
        return width * height

    selected = max(
        candidates,
        key=resolution_score,
    )

    format_id = selected.get("format_id")

    if not format_id:
        raise RuntimeError(
            "Could not determine the TikTok format."
        )

    if not YTDLP.exists():
        raise FileNotFoundError(
            "yt-dlp.exe was not found in the YAAY dependencies folder."
        )

    if not FFMPEG.exists():
        raise FileNotFoundError(
            "ffmpeg.exe was not found in the YAAY dependencies folder."
        )

    TEMP_DOWNLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_template = (
        TEMP_DOWNLOAD_DIR
        / f"YAAY_temp_{current_id}.%(ext)s"
    )

    command = [
        str(YTDLP),
        "-f",
        format_id,
        "-o",
        str(temp_template),
        current_url,
    ]

    result = _run(command)

    if result.returncode != 0:
        error = result.stderr.strip()

        raise RuntimeError(
            error[-3000:]
            if error
            else "TikTok download failed."
        )

    temp_files = list(
        TEMP_DOWNLOAD_DIR.glob(
            f"YAAY_temp_{current_id}.*"
        )
    )

    if not temp_files:
        raise RuntimeError(
            "TikTok downloaded successfully, but the temporary "
            "file could not be found."
        )

    temp_file = temp_files[0]

    final_name = get_filename(
        current_title,
        current_channel,
        current_id,
        "m4a",
    )

    final_file = output_folder / final_name

    ffmpeg_command = [
        str(FFMPEG),
        "-y",
        "-i",
        str(temp_file),
        "-vn",
        "-c:a",
        "copy",
        str(final_file),
    ]

    ffmpeg_result = _run(ffmpeg_command)

    if ffmpeg_result.returncode != 0:
        error = ffmpeg_result.stderr.strip()

        raise RuntimeError(
            error[-3000:]
            if error
            else "FFmpeg failed to extract the audio."
        )

    try:
        temp_file.unlink()
    except Exception:
        pass

    return final_file


def _download_standard(
    current_url,
    metadata,
    output_folder,
):
    """
    YouTube / Instagram / other standard path.
    """

    if not YTDLP.exists():
        raise FileNotFoundError(
            "yt-dlp.exe was not found in the YAAY dependencies folder."
        )

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        str(YTDLP),
        "-f",
        "bestaudio/best",
        "-o",
        str(
            output_folder
            / "%(title)s - %(uploader)s - %(id)s.%(ext)s"
        ),
        current_url,
    ]

    result = _run(command)

    if result.returncode != 0:
        error = result.stderr.strip()

        raise RuntimeError(
            error[-3000:]
            if error
            else "Download failed."
        )

    return None


def download_audio(
    current_url,
    metadata,
    output_folder,
):
    """
    Download audio using the platform-specific path.

    Returns the final file path when YAAY creates it directly
    (currently TikTok), otherwise None for yt-dlp-managed output.
    """

    output_folder = Path(output_folder)

    extractor = metadata["extractor"]

    if "tiktok" in extractor:
        return _download_tiktok(
            current_url,
            metadata,
            output_folder,
        )

    return _download_standard(
        current_url,
        metadata,
        output_folder,
    )

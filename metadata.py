import json
import subprocess

from filenames import get_filename, limit_title
from utils import APP_DIR, YTDLP


def get_metadata(url):
    """
    Ask yt-dlp for metadata without downloading media.

    Returns:
        {
            "info": raw yt-dlp metadata,
            "extractor": normalized extractor name,
            "title": YAAY display title,
            "channel": uploader/profile name,
            "media_id": unique media ID,
            "filename": preview filename
        }

    Raises:
        FileNotFoundError if yt-dlp.exe is missing.
        RuntimeError for yt-dlp extraction failures.
        ValueError if yt-dlp returns invalid JSON.
    """

    if not YTDLP.exists():
        raise FileNotFoundError(
            "yt-dlp.exe was not found in the YAAY dependencies folder."
        )

    command = [
        str(YTDLP),
        "--skip-download",
        "--dump-single-json",
        url,
    ]

    # TikTok extraction can intermittently fail even when the exact
    # same URL and command work on the next attempt. Retry only the
    # two known transient webpage/extraction errors.
    max_attempts = 3 if "tiktok.com" in url.lower() else 1
    last_error = ""

    for attempt in range(1, max_attempts + 1):
        result = subprocess.run(
            command,
            cwd=APP_DIR,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            break

        last_error = result.stderr.strip() or "Unknown yt-dlp error."

        retryable = (
            "Unable to extract universal data for rehydration" in last_error
            or "Unexpected response from webpage request" in last_error
        )

        if not retryable or attempt >= max_attempts:
            raise RuntimeError(last_error[-3000:])

    else:
        raise RuntimeError(last_error[-3000:])

    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(
            "yt-dlp returned information that YAAY couldn't understand."
        ) from error

    extractor = (
        info.get("extractor_key")
        or info.get("extractor")
        or ""
    ).lower()

    if "instagram" in extractor:
        title = (
            info.get("description")
            or info.get("title")
            or "Unknown"
        )
    else:
        title = info.get("title") or "Unknown"

    title = limit_title(title)

    channel = (
        info.get("uploader")
        or info.get("channel")
        or info.get("creator")
        or "Unknown"
    )

    media_id = info.get("id") or "Unknown"

    formats = info.get("formats") or []

    audio_formats = [
        fmt
        for fmt in formats
        if fmt.get("vcodec") == "none"
        and fmt.get("ext")
    ]

    if audio_formats:
        extension = audio_formats[-1].get("ext")
    else:
        extension = info.get("ext") or "audio"

    filename = get_filename(
        title,
        channel,
        media_id,
        extension,
    )

    return {
        "info": info,
        "extractor": extractor,
        "title": title,
        "channel": channel,
        "media_id": media_id,
        "filename": filename,
    }

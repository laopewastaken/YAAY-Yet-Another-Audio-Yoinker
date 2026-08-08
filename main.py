import json
import re
import subprocess
import tkinter as tk
import winsound
from tkinter import messagebox
from pathlib import Path


# AAY! folder
APP_DIR = Path(__file__).resolve().parent

YTDLP = APP_DIR / "yt-dlp.exe"


# Information about the currently checked URL
current_url = None
current_title = None
current_channel = None
current_id = None
current_info = None


def sanitize_filename(text):
    """
    Remove characters that Windows does not allow
    in filenames.
    """

    if not text:
        return "Unknown"

    # Windows-invalid filename characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)

    # Remove control characters
    text = re.sub(r'[\x00-\x1f]', '', text)

    # Remove trailing spaces and periods
    text = text.strip().rstrip('.')

    return text or "Unknown"


def limit_title(text, maximum=30):
    """
    Limit the title to a maximum number of characters.
    """

    if len(text) <= maximum:
        return text

    return text[:maximum].rstrip()


def get_filename(title, channel, media_id, extension):
    """
    Build the final AAY filename.

    Format:
    Title - Channel - ID.extension
    """

    title = sanitize_filename(title)
    channel = sanitize_filename(channel)
    media_id = sanitize_filename(media_id)

    title = limit_title(title)

    return f"{title} - {channel} - {media_id}.{extension}"


def display_url(url, maximum=65):
    """
    Create a shortened visual representation of the URL.
    The actual URL is kept separately in current_url.
    """

    if len(url) <= maximum:
        return url

    return url[:maximum] + "..."


def reset_url_entry():
    """
    Clear the URL box and make it editable again.
    """

    url_entry.config(state="normal")
    url_entry.delete(0, tk.END)


def check_url():
    global current_url
    global current_title
    global current_channel
    global current_id
    global current_info

    url = url_entry.get().strip()

    if not url:
        messagebox.showwarning(
            "AAY!",
            "Paste a URL first."
        )
        return

    if not YTDLP.exists():
        messagebox.showerror(
            "AAY!",
            "yt-dlp.exe was not found in the AAY folder."
        )
        return

    status_label.config(text="Checking...")
    check_button.config(state="disabled")
    download_button.config(state="disabled")

    title_value.config(text="—")
    channel_value.config(text="—")
    filename_value.config(text="—")

    root.update()

    command = [
        str(YTDLP),

        # Don't download anything.
        "--skip-download",

        # Return metadata as JSON.
        "--dump-single-json",

        url,
    ]

    try:
        result = subprocess.run(
            command,
            cwd=APP_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            status_label.config(
                text="Could not retrieve information."
            )

            error = result.stderr.strip()

            messagebox.showerror(
                "AAY!",
                error[-3000:] if error else "Unknown error."
            )

            return

        info = json.loads(result.stdout)
        current_info = info

        # -------------------------------------------------
        # Determine platform
        # -------------------------------------------------

        extractor = (
            info.get("extractor_key")
            or info.get("extractor")
            or ""
        ).lower()

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        if "instagram" in extractor:
            # Instagram's description is the actual caption.
            title = (
                info.get("description")
                or info.get("title")
                or "Unknown"
            )
        else:
            title = info.get("title") or "Unknown"

        # Limit title to 30 characters.
        title = limit_title(title)

        # -------------------------------------------------
        # Channel / profile
        # -------------------------------------------------

        channel = (
            info.get("uploader")
            or info.get("channel")
            or info.get("creator")
            or "Unknown"
        )

        # -------------------------------------------------
        # Unique media ID
        # -------------------------------------------------

        media_id = info.get("id") or "Unknown"

        # -------------------------------------------------
        # Display information
        # -------------------------------------------------

        title_value.config(text=title)
        channel_value.config(text=channel)

        # We don't know the final extension until the
        # actual audio format is selected/downloaded.
        #
        # For now, show the filename using the extension
        # yt-dlp reports for the selected best audio format.
        formats = info.get("formats") or []

        audio_formats = [
            fmt for fmt in formats
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
            extension
        )

        filename_value.config(text=filename)

        current_url = url
        current_title = title
        current_channel = channel
        current_id = media_id

        # Show a shortened URL to the user while keeping
        # the complete original URL internally.
        url_entry.config(state="normal")
        url_entry.delete(0, tk.END)
        url_entry.insert(0, display_url(url))
        url_entry.config(state="disabled")

        status_label.config(
            text="✓ Ready to download"
        )

        download_button.config(
            state="normal"
        )

    except json.JSONDecodeError:
        url_entry.config(state="normal")
        status_label.config(
            text="Invalid response from yt-dlp."
        )

        messagebox.showerror(
            "AAY!",
            "yt-dlp returned information that AAY! couldn't understand."
        )

    except Exception as error:
        url_entry.config(state="normal")
        status_label.config(
            text="Something went wrong."
        )

        messagebox.showerror(
            "AAY!",
            str(error)
        )

    finally:
        check_button.config(state="normal")


def download_audio():

    global current_info

    if not current_url or not current_info:
        messagebox.showwarning(
            "AAY!",
            "Check a URL first."
        )
        return

    if not YTDLP.exists():
        messagebox.showerror(
            "AAY!",
            "yt-dlp.exe was not found in the AAY folder."
        )
        return

    status_label.config(
        text="Downloading..."
    )

    check_button.config(
        state="disabled"
    )

    download_button.config(
        state="disabled"
    )

    root.update()

    extractor = (
        current_info.get("extractor_key")
        or current_info.get("extractor")
        or ""
    ).lower()

    # =====================================================
    # TIKTOK
    # =====================================================

    if "tiktok" in extractor:

        formats = current_info.get("formats", [])

        # Find usable video+audio formats.
        candidates = []

        for fmt in formats:

            if fmt.get("vcodec") in (None, "none"):
                continue

            if fmt.get("acodec") in (None, "none"):
                continue

            format_id = fmt.get("format_id", "")

            # Avoid TikTok's special watermarked
            # "download" format.
            if format_id == "download":
                continue

            candidates.append(fmt)

        if not candidates:
            messagebox.showerror(
                "AAY!",
                "TikTok did not provide a usable audio format."
            )

            check_button.config(state="normal")
            download_button.config(state="normal")

            return

        # Prefer the highest resolution.
        def resolution_score(fmt):
            width = fmt.get("width") or 0
            height = fmt.get("height") or 0
            return width * height

        selected = max(
            candidates,
            key=resolution_score
        )

        format_id = selected.get("format_id")

        if not format_id:
            messagebox.showerror(
                "AAY!",
                "Could not determine the TikTok format."
            )

            check_button.config(state="normal")
            download_button.config(state="normal")

            return

        # Temporary video filename.
        temp_template = (
            f"AAY_temp_{current_id}.%(ext)s"
        )

        command = [
            str(YTDLP),

            "-f",
            format_id,

            "-o",
            temp_template,

            current_url,
        ]

        try:

            result = subprocess.run(
                command,
                cwd=APP_DIR,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                url_entry.config(state="normal")

                error = result.stderr.strip()

                raise Exception(
                    error[-3000:]
                    if error
                    else "TikTok download failed."
                )

            # Find the temporary downloaded file.
            temp_files = list(
                APP_DIR.glob(
                    f"AAY_temp_{current_id}.*"
                )
            )

            if not temp_files:

                raise Exception(
                    "TikTok downloaded successfully, "
                    "but the temporary file could not be found."
                )

            temp_file = temp_files[0]

            # Final filename.
            final_name = get_filename(
                current_title,
                current_channel,
                current_id,
                "m4a"
            )

            final_file = APP_DIR / final_name

            # FFmpeg executable bundled with AAY.
            ffmpeg = APP_DIR / "ffmpeg.exe"

            if not ffmpeg.exists():

                raise Exception(
                    "ffmpeg.exe was not found in the AAY folder."
                )

            status_label.config(
                text="Extracting audio..."
            )

            root.update()

            ffmpeg_command = [
                str(ffmpeg),

                "-y",

                "-i",
                str(temp_file),

                "-vn",

                "-c:a",
                "copy",

                str(final_file)
            ]

            ffmpeg_result = subprocess.run(
                ffmpeg_command,
                cwd=APP_DIR,
                capture_output=True,
                text=True
            )

            if ffmpeg_result.returncode != 0:

                error = ffmpeg_result.stderr.strip()

                raise Exception(
                    error[-3000:]
                    if error
                    else "FFmpeg failed to extract the audio."
                )

            # Delete temporary TikTok video.
            try:
                temp_file.unlink()
            except Exception:
                pass

            status_label.config(
                text="✓ Download complete!"
            )

            winsound.MessageBeep(
                winsound.MB_OK
            )

            reset_url_entry()

        except Exception as error:
            url_entry.config(state="normal")
            status_label.config(
                text="Download failed."
            )

            messagebox.showerror(
                "AAY!",
                str(error)
            )

    # =====================================================
    # YOUTUBE / INSTAGRAM / EVERYTHING ELSE
    # =====================================================

    else:

        command = [
            str(YTDLP),

            "-f",
            "bestaudio/best",

            "-o",
            "%(title)s - %(uploader)s - %(id)s.%(ext)s",

            current_url,
        ]

        try:

            result = subprocess.run(
                command,
                cwd=APP_DIR,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                status_label.config(
                    text="✓ Download complete!"
                )

                winsound.MessageBeep(
                    winsound.MB_OK
                )

                reset_url_entry()

            else:

                error = result.stderr.strip()

                messagebox.showerror(
                    "AAY!",
                    error[-3000:]
                    if error
                    else "Download failed."
                )

                status_label.config(
                    text="Download failed."
                )

        except Exception as error:
            url_entry.config(state="normal")
            status_label.config(
                text="Something went wrong."
            )

            messagebox.showerror(
                "AAY!",
                str(error)
            )

    check_button.config(
        state="normal"
    )

    download_button.config(
        state="normal"
    )


# =========================================================
# GUI
# =========================================================

root = tk.Tk()

root.title(
    "AAY! — Another Audio Yoinker"
)

root.geometry(
    "650x400"
)

root.resizable(
    False,
    False
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

title_label = tk.Label(
    root,
    text="AAY!",
    font=("Segoe UI", 26, "bold")
)

title_label.pack(
    pady=(20, 0)
)


subtitle_label = tk.Label(
    root,
    text="Another Audio Yoinker",
    font=("Segoe UI", 10)
)

subtitle_label.pack()


# ---------------------------------------------------------
# URL
# ---------------------------------------------------------

url_label = tk.Label(
    root,
    text="URL",
    font=("Segoe UI", 10, "bold")
)

url_label.pack(
    pady=(20, 3)
)


url_entry = tk.Entry(
    root,
    width=75
)

url_entry.pack()


# ---------------------------------------------------------
# Check
# ---------------------------------------------------------

check_button = tk.Button(
    root,
    text="CHECK",
    command=check_url,
    width=15
)

check_button.pack(
    pady=10
)


# ---------------------------------------------------------
# Information
# ---------------------------------------------------------

info_frame = tk.Frame(root)

info_frame.pack(
    pady=5
)


# Title
tk.Label(
    info_frame,
    text="Title:",
    font=("Segoe UI", 9, "bold"),
    anchor="e",
    width=12
).grid(
    row=0,
    column=0,
    padx=5,
    pady=3
)


title_value = tk.Label(
    info_frame,
    text="—",
    font=("Segoe UI", 9),
    anchor="w",
    width=65
)

title_value.grid(
    row=0,
    column=1,
    padx=5,
    pady=3
)


# Channel
tk.Label(
    info_frame,
    text="Channel:",
    font=("Segoe UI", 9, "bold"),
    anchor="e",
    width=12
).grid(
    row=1,
    column=0,
    padx=5,
    pady=3
)


channel_value = tk.Label(
    info_frame,
    text="—",
    font=("Segoe UI", 9),
    anchor="w",
    width=65
)

channel_value.grid(
    row=1,
    column=1,
    padx=5,
    pady=3
)


# Filename
tk.Label(
    info_frame,
    text="Filename:",
    font=("Segoe UI", 9, "bold"),
    anchor="e",
    width=12
).grid(
    row=2,
    column=0,
    padx=5,
    pady=3
)


filename_value = tk.Label(
    info_frame,
    text="—",
    font=("Segoe UI", 9),
    anchor="w",
    width=65
)

filename_value.grid(
    row=2,
    column=1,
    padx=5,
    pady=3
)


# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

download_button = tk.Button(
    root,
    text="🎵 DOWNLOAD AUDIO",
    command=download_audio,
    width=25,
    height=2,
    state="disabled"
)

download_button.pack(
    pady=15
)


# ---------------------------------------------------------
# Status
# ---------------------------------------------------------

status_label = tk.Label(
    root,
    text="Ready.",
    font=("Segoe UI", 9)
)

status_label.pack()


root.mainloop()
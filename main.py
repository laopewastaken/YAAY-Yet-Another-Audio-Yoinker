import json
import re
import subprocess
import tkinter as tk
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


def check_url():
    global current_url
    global current_title
    global current_channel
    global current_id

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

        # Remember information for download.
        current_url = url
        current_title = title
        current_channel = channel
        current_id = media_id

        status_label.config(
            text="✓ Ready to download"
        )

        download_button.config(
            state="normal"
        )

    except json.JSONDecodeError:
        status_label.config(
            text="Invalid response from yt-dlp."
        )

        messagebox.showerror(
            "AAY!",
            "yt-dlp returned information that AAY! couldn't understand."
        )

    except Exception as error:
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

    if not current_url:
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

    command = [
        str(YTDLP),

        # Prefer audio-only.
        # Fall back to the best format containing audio.
        "-f",
        "bestaudio/best",

        # Extract audio from combined formats.
        "-x",

        # Keep AAC audio in an M4A container.
        "--audio-format",
        "m4a",

        # Don't re-encode the audio if possible.
        "--postprocessor-args",
        "ExtractAudio:-c:a copy",

        # Temporary filename.
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

            messagebox.showinfo(
                "AAY!",
                f"Downloaded:\n{current_title}"
            )

        else:

            status_label.config(
                text="Download failed."
            )

            error = result.stderr.strip()

            messagebox.showerror(
                "AAY!",
                error[-3000:] if error else "Unknown error."
            )

    except Exception as error:

        status_label.config(
            text="Something went wrong."
        )

        messagebox.showerror(
            "AAY!",
            str(error)
        )

    finally:

        check_button.config(
            state="normal"
        )

        if current_url:
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
import json
import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path


# AAY! folder
APP_DIR = Path(__file__).resolve().parent

YTDLP = APP_DIR / "yt-dlp.exe"


# Store information about the currently checked URL.
current_url = None
current_title = None


def check_url():
    global current_url, current_title

    url = url_entry.get().strip()

    if not url:
        messagebox.showwarning("AAY!", "Paste a URL first.")
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
    root.update()

    command = [
        str(YTDLP),

        # Don't download anything.
        "--skip-download",

        # Give us machine-readable information.
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
            status_label.config(text="Could not retrieve information.")

            error = result.stderr.strip()

            messagebox.showerror(
                "AAY!",
                error[-3000:] if error else "Unknown error."
            )

            return

        # Convert yt-dlp's JSON output into a Python dictionary.
        info = json.loads(result.stdout)

        title = info.get("title") or "Unknown title"

        # "uploader" generally contains the channel/profile name.
        uploader = (
            info.get("uploader")
            or info.get("channel")
            or info.get("creator")
            or "Unknown"
        )

        # Display the information.
        title_value.config(text=title)
        channel_value.config(text=uploader)

        # Remember the URL that was successfully checked.
        current_url = url
        current_title = title

        status_label.config(text="✓ Ready to download")
        download_button.config(state="normal")

    except json.JSONDecodeError:
        status_label.config(text="Invalid response from yt-dlp.")

        messagebox.showerror(
            "AAY!",
            "yt-dlp returned information that AAY! couldn't understand."
        )

    except Exception as error:
        status_label.config(text="Something went wrong.")

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

    status_label.config(text="Downloading...")
    check_button.config(state="disabled")
    download_button.config(state="disabled")
    root.update()

    command = [
        str(YTDLP),

        # Best available audio-only stream.
        "-f", "bestaudio",

        # Use the media title as the filename.
        "-o", "%(title)s.%(ext)s",

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
            status_label.config(text="✓ Download complete!")

            messagebox.showinfo(
                "AAY!",
                f"Downloaded:\n{current_title}"
            )

        else:
            status_label.config(text="Download failed.")

            error = result.stderr.strip()

            messagebox.showerror(
                "AAY!",
                error[-3000:] if error else "Unknown error."
            )

    except Exception as error:
        status_label.config(text="Something went wrong.")

        messagebox.showerror(
            "AAY!",
            str(error)
        )

    finally:
        check_button.config(state="normal")

        if current_url:
            download_button.config(state="normal")


# -------------------------
# GUI
# -------------------------

root = tk.Tk()

root.title("AAY! — Another Audio Yoinker")
root.geometry("600x360")
root.resizable(False, False)


# Title
title_label = tk.Label(
    root,
    text="AAY!",
    font=("Segoe UI", 26, "bold")
)
title_label.pack(pady=(20, 0))


# Subtitle
subtitle_label = tk.Label(
    root,
    text="Another Audio Yoinker",
    font=("Segoe UI", 10)
)
subtitle_label.pack()


# URL label
url_label = tk.Label(
    root,
    text="URL",
    font=("Segoe UI", 10, "bold")
)
url_label.pack(pady=(20, 3))


# URL entry
url_entry = tk.Entry(
    root,
    width=70
)
url_entry.pack()


# Check button
check_button = tk.Button(
    root,
    text="CHECK",
    command=check_url,
    width=15
)
check_button.pack(pady=10)


# Metadata frame
info_frame = tk.Frame(root)
info_frame.pack(pady=5)


# Title
title_name_label = tk.Label(
    info_frame,
    text="Title:",
    font=("Segoe UI", 9, "bold"),
    anchor="e",
    width=10
)
title_name_label.grid(row=0, column=0, padx=5, pady=3)


title_value = tk.Label(
    info_frame,
    text="—",
    font=("Segoe UI", 9),
    anchor="w",
    width=55
)
title_value.grid(row=0, column=1, padx=5, pady=3)


# Channel
channel_name_label = tk.Label(
    info_frame,
    text="Channel:",
    font=("Segoe UI", 9, "bold"),
    anchor="e",
    width=10
)
channel_name_label.grid(row=1, column=0, padx=5, pady=3)


channel_value = tk.Label(
    info_frame,
    text="—",
    font=("Segoe UI", 9),
    anchor="w",
    width=55
)
channel_value.grid(row=1, column=1, padx=5, pady=3)


# Download button
download_button = tk.Button(
    root,
    text="🎵 DOWNLOAD AUDIO",
    command=download_audio,
    width=25,
    height=2,
    state="disabled"
)
download_button.pack(pady=15)


# Status
status_label = tk.Label(
    root,
    text="Ready.",
    font=("Segoe UI", 9)
)
status_label.pack()


root.mainloop()
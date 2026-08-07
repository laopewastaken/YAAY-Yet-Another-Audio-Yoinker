import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path


# AAY! folder
APP_DIR = Path(__file__).resolve().parent

YTDLP = APP_DIR / "yt-dlp.exe"


def download_audio():
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

    status_label.config(text="Downloading...")
    download_button.config(state="disabled")
    root.update()

    command = [
        str(YTDLP),

        # Select the best available audio-only stream.
        "-f", "bestaudio",

        # Save using the media title.
        "-o", "%(title)s.%(ext)s",

        url,
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
                "Audio downloaded successfully!"
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
        download_button.config(state="normal")


# -------------------------
# GUI
# -------------------------

root = tk.Tk()

root.title("AAY! — Another Audio Yoinker")
root.geometry("500x220")
root.resizable(False, False)


title_label = tk.Label(
    root,
    text="AAY!",
    font=("Segoe UI", 24, "bold")
)
title_label.pack(pady=(20, 0))


subtitle_label = tk.Label(
    root,
    text="Another Audio Yoinker",
    font=("Segoe UI", 10)
)
subtitle_label.pack()


url_entry = tk.Entry(
    root,
    width=60
)
url_entry.pack(pady=20)


download_button = tk.Button(
    root,
    text="🎵 DOWNLOAD AUDIO",
    command=download_audio,
    width=25,
    height=2
)
download_button.pack()


status_label = tk.Label(
    root,
    text="Ready.",
    font=("Segoe UI", 9)
)
status_label.pack(pady=10)


root.mainloop()
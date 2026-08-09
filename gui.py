import tkinter as tk
from tkinter import messagebox, filedialog

from downloader import download_audio
from metadata import get_metadata
from utils import ensure_directories, play_success_sound
from pathlib import Path


class YAAYApp:
    def __init__(self, root):
        self.root = root

        self.current_url = None
        self.current_metadata = None

        self._build_window()
        self._build_header()
        self._build_url_section()
        self._build_information_section()
        self._build_save_section()
        self._build_download_section()
        self._build_status_bar()

    # ---------------------------------------------------------
    # Window
    # ---------------------------------------------------------

    def _build_window(self):
        self.root.title(
            "YAAY! — Yet Another Audio Yoinker"
        )

        self.root.geometry("700x470")
        self.root.resizable(False, False)

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    def _build_header(self):
        title_label = tk.Label(
            self.root,
            text="YAAY!",
            font=("Segoe UI", 26, "bold"),
        )

        title_label.pack(pady=(20, 0))

        subtitle_label = tk.Label(
            self.root,
            text="Yet Another Audio Yoinker",
            font=("Segoe UI", 10),
        )

        subtitle_label.pack()

    # ---------------------------------------------------------
    # URL
    # ---------------------------------------------------------

    def _build_url_section(self):
        url_label = tk.Label(
            self.root,
            text="URL",
            font=("Segoe UI", 10, "bold"),
        )

        url_label.pack(pady=(20, 3))

        self.url_entry = tk.Entry(
            self.root,
            width=80,
        )

        self.url_entry.pack()

        self.url_entry.bind(
            "<KeyRelease>",
            self._url_changed,
        )

        self.check_button = tk.Button(
            self.root,
            text="CHECK",
            command=self.check_url,
            width=15,
        )

        self.check_button.pack(pady=10)

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def _build_information_section(self):
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)

        tk.Label(
            info_frame,
            text="Title:",
            font=("Segoe UI", 9, "bold"),
            anchor="e",
            width=12,
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=3,
        )

        self.title_value = tk.Label(
            info_frame,
            text="—",
            font=("Segoe UI", 9),
            anchor="w",
            width=65,
        )

        self.title_value.grid(
            row=0,
            column=1,
            padx=5,
            pady=3,
        )

        tk.Label(
            info_frame,
            text="Channel:",
            font=("Segoe UI", 9, "bold"),
            anchor="e",
            width=12,
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=3,
        )

        self.channel_value = tk.Label(
            info_frame,
            text="—",
            font=("Segoe UI", 9),
            anchor="w",
            width=65,
        )

        self.channel_value.grid(
            row=1,
            column=1,
            padx=5,
            pady=3,
        )

        tk.Label(
            info_frame,
            text="Filename:",
            font=("Segoe UI", 9, "bold"),
            anchor="e",
            width=12,
        ).grid(
            row=2,
            column=0,
            padx=5,
            pady=3,
        )

        self.filename_value = tk.Label(
            info_frame,
            text="—",
            font=("Segoe UI", 9),
            anchor="w",
            width=65,
        )

        self.filename_value.grid(
            row=2,
            column=1,
            padx=5,
            pady=3,
        )

    # ---------------------------------------------------------
    # Save To
    # ---------------------------------------------------------

    def _build_save_section(self):
        save_frame = tk.Frame(self.root)
        save_frame.pack(
            pady=(12, 5),
        )

        tk.Label(
            save_frame,
            text="Save to:",
            font=("Segoe UI", 9, "bold"),
            anchor="e",
            width=12,
        ).grid(
            row=0,
            column=0,
            padx=5,
        )

        self.save_path_entry = tk.Entry(
            save_frame,
            width=55,
        )

        self.save_path_entry.grid(
            row=0,
            column=1,
            padx=5,
        )

        ensure_directories()

        default_download_folder = (
            Path(__file__).resolve().parent
            / "downloads"
        )

        self.save_path_entry.insert(
            0,
            str(default_download_folder),
        )

        self.browse_button = tk.Button(
            save_frame,
            text="Browse...",
            command=self.browse_save_folder,
            width=10,
        )

        self.browse_button.grid(
            row=0,
            column=2,
            padx=5,
        )

    def browse_save_folder(self):
        selected_folder = filedialog.askdirectory(
            title="Select download folder",
        )

        if selected_folder:
            self.save_path_entry.delete(
                0,
                tk.END,
            )

            self.save_path_entry.insert(
                0,
                selected_folder,
            )

    # ---------------------------------------------------------
    # Download
    # ---------------------------------------------------------

    def _build_download_section(self):
        self.download_button = tk.Button(
            self.root,
            text="🎵 DOWNLOAD AUDIO",
            command=self.download,
            width=25,
            height=2,
            state="disabled",
        )

        self.download_button.pack(
            pady=15,
        )

    # ---------------------------------------------------------
    # Status Bar
    # ---------------------------------------------------------

    def _build_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            anchor="w",
            relief="sunken",
            bd=1,
            padx=8,
        )

        self.status_bar.pack(
            side="bottom",
            fill="x",
        )

    def _set_status(self, text):
        self.status_bar.config(
            text=text,
        )

    # ---------------------------------------------------------
    # URL Changes
    # ---------------------------------------------------------

    def _url_changed(self, event=None):
        current_text = self.url_entry.get().strip()

        if (
            self.current_url is not None
            and current_text != self.current_url
        ):
            self.current_url = None
            self.current_metadata = None

            self.title_value.config(text="—")
            self.channel_value.config(text="—")
            self.filename_value.config(text="—")

            self.download_button.config(
                state="disabled",
            )

            self._set_status(
                "URL changed — click CHECK"
            )

    # ---------------------------------------------------------
    # Check
    # ---------------------------------------------------------

    def check_url(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning(
                "YAAY!",
                "Paste a URL first.",
            )
            return

        self._set_status(
            "Checking..."
        )

        self.check_button.config(
            state="disabled",
        )

        self.download_button.config(
            state="disabled",
        )

        self.title_value.config(text="—")
        self.channel_value.config(text="—")
        self.filename_value.config(text="—")

        self.current_url = None
        self.current_metadata = None

        self.root.update()

        try:
            metadata = get_metadata(url)

            self.current_url = url
            self.current_metadata = metadata

            self.title_value.config(
                text=metadata["title"]
            )

            self.channel_value.config(
                text=metadata["channel"]
            )

            self.filename_value.config(
                text=metadata["filename"]
            )

            self._set_status(
                "✓ Ready to download"
            )

            self.download_button.config(
                state="normal",
            )

        except Exception as error:
            self.current_url = None
            self.current_metadata = None

            self._set_status(
                "Could not retrieve information."
            )

            messagebox.showerror(
                "YAAY!",
                str(error),
            )

        finally:
            self.check_button.config(
                state="normal",
            )

    # ---------------------------------------------------------
    # Download
    # ---------------------------------------------------------

    def download(self):
        if (
            not self.current_url
            or not self.current_metadata
        ):
            messagebox.showwarning(
                "YAAY!",
                "Check a URL first.",
            )
            return

        save_path = self.save_path_entry.get().strip()

        if not save_path:
            messagebox.showwarning(
                "YAAY!",
                "Select a download folder first.",
            )
            return

        self._set_status(
            "Downloading..."
        )

        self.check_button.config(
            state="disabled",
        )

        self.download_button.config(
            state="disabled",
        )

        self.root.update()

        try:
            download_audio(
                self.current_url,
                self.current_metadata,
            )

            self._set_status(
                "✓ Download complete!"
            )

            play_success_sound()

            self.url_entry.delete(
                0,
                tk.END,
            )

            self.current_url = None
            self.current_metadata = None

            self.title_value.config(text="—")
            self.channel_value.config(text="—")
            self.filename_value.config(text="—")

        except Exception as error:
            self._set_status(
                "Download failed."
            )

            messagebox.showerror(
                "YAAY!",
                str(error),
            )

        finally:
            self.check_button.config(
                state="normal",
            )

            self.download_button.config(
                state=(
                    "normal"
                    if self.current_url
                    else "disabled"
                )
            )


def start_app():
    ensure_directories()

    root = tk.Tk()

    YAAYApp(root)

    root.mainloop()

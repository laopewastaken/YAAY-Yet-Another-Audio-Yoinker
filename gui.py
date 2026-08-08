import tkinter as tk
from tkinter import messagebox

from downloader import download_audio
from metadata import get_metadata
from utils import ensure_directories, play_success_sound


class YAAYApp:
    def __init__(self, root):
        self.root = root

        self.current_url = None
        self.current_metadata = None

        self._build_window()
        self._build_header()
        self._build_url_section()
        self._build_information_section()
        self._build_download_section()

    # ---------------------------------------------------------
    # Window
    # ---------------------------------------------------------

    def _build_window(self):
        self.root.title(
            "YAAY! — Yet Another Audio Yoinker"
        )

        self.root.geometry("650x400")
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
            width=75,
        )

        self.url_entry.pack()

        # Changing the URL invalidates the metadata from the previous CHECK.
        self.url_entry.bind("<KeyRelease>", self._url_changed)
        self.url_entry.bind("<<Paste>>", self._url_changed)

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
        ).grid(row=0, column=0, padx=5, pady=3)

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
        ).grid(row=1, column=0, padx=5, pady=3)

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
        ).grid(row=2, column=0, padx=5, pady=3)

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

        self.download_button.pack(pady=15)

        self.status_label = tk.Label(
            self.root,
            text="Ready.",
            font=("Segoe UI", 9),
        )

        self.status_label.pack()

    # ---------------------------------------------------------
    # URL state
    # ---------------------------------------------------------

    def _url_changed(self, event=None):
        """Invalidate checked metadata when the user changes the URL."""

        if not self.current_url:
            return

        entered_url = self.url_entry.get().strip()

        if entered_url != self.current_url:
            self.current_url = None
            self.current_metadata = None

            self.title_value.config(text="—")
            self.channel_value.config(text="—")
            self.filename_value.config(text="—")

            self.download_button.config(state="disabled")
            self.status_label.config(
                text="URL changed — click CHECK"
            )

    def _clear_url_entry(self):
        self.url_entry.delete(0, tk.END)

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

        # A new CHECK always replaces any previous checked URL.
        self.current_url = None
        self.current_metadata = None

        self.status_label.config(text="Checking...")
        self.check_button.config(state="disabled")
        self.download_button.config(state="disabled")

        self.title_value.config(text="—")
        self.channel_value.config(text="—")
        self.filename_value.config(text="—")

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

            self.status_label.config(
                text="✓ Ready to download"
            )

            self.download_button.config(
                state="normal"
            )

        except Exception as error:
            self.url_entry.config(state="normal")

            self.status_label.config(
                text="Could not retrieve information."
            )

            messagebox.showerror(
                "YAAY!",
                str(error),
            )

        finally:
            self.check_button.config(state="normal")

    # ---------------------------------------------------------
    # Download
    # ---------------------------------------------------------

    def download(self):
        if not self.current_url or not self.current_metadata:
            messagebox.showwarning(
                "YAAY!",
                "Check a URL first.",
            )
            return

        self.status_label.config(
            text="Downloading..."
        )

        self.check_button.config(
            state="disabled"
        )

        self.download_button.config(
            state="disabled"
        )

        self.root.update()

        try:
            extractor = self.current_metadata["extractor"]

            if "tiktok" in extractor:
                self.status_label.config(
                    text="Downloading..."
                )
                self.root.update()

            final_file = download_audio(
                self.current_url,
                self.current_metadata,
            )

            # TikTok has an explicit extraction stage.
            if "tiktok" in extractor:
                self.status_label.config(
                    text="✓ Download complete!"
                )
            else:
                self.status_label.config(
                    text="✓ Download complete!"
                )

            play_success_sound()

            self._clear_url_entry()

            self.current_url = None
            self.current_metadata = None

        except Exception as error:
            self.status_label.config(
                text="Download failed."
            )

            messagebox.showerror(
                "YAAY!",
                str(error),
            )

        finally:
            self.check_button.config(
                state="normal"
            )

            self.download_button.config(
                state="disabled"
                if not self.current_url
                else "normal"
            )


def start_app():
    ensure_directories()

    root = tk.Tk()
    YAAYApp(root)
    root.mainloop()

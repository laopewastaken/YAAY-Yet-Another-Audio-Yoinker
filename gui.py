
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path

from downloader import download_audio
from metadata import get_metadata
from utils import ensure_directories, play_success_sound


# =========================================================
# YAAY TERMINAL THEME
# =========================================================

BG = "#050505"
PANEL = "#0a0a0a"
AMBER = "#ff9d00"
AMBER_DIM = "#a76500"
AMBER_DARK = "#3d2600"
BORDER = "#8f5900"
DISABLED = "#543600"

FONT = ("Consolas", 10)
FONT_BOLD = ("Consolas", 10, "bold")
FONT_TITLE = ("Consolas", 18, "bold")
FONT_SMALL = ("Consolas", 9)


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

    # =====================================================
    # Window
    # =====================================================

    def _build_window(self):
        self.root.title(
            "YAAY! // Yet Another Audio Yoinker"
        )

        self.root.geometry("760x560")
        self.root.resizable(False, False)

        self.root.configure(
            bg=BG
        )

 # =====================================================
    # Header (The Main Banner)
    # =====================================================
    def _build_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(15, 10))

        # Use a more distinct 'terminal box' look
        tk.Label(
            header,
            text="╔════════════════════════════════════════════════════════════════════╗",
            font=FONT_SMALL,
            fg=AMBER_DIM,
            bg=BG,
        ).pack()
        tk.Label(
            header,
            text="║  YAAY! // YET ANOTHER AUDIO YOINKER                                ║",
            font=FONT_BOLD,
            fg=AMBER,
            bg=BG,
        ).pack()
        tk.Label(
            header,
            text="║  AUDIO EXTRACTION TERMINAL                                         ║",
            font=FONT_SMALL,
            fg=AMBER_DIM,
            bg=BG,
        ).pack()
        tk.Label(
            header,
            text="╚════════════════════════════════════════════════════════════════════╝",
            font=FONT_SMALL,
            fg=AMBER_DIM,
            bg=BG,
        ).pack()

    # =====================================================
    # URL Section
    # =====================================================
    def _build_url_section(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="x", padx=28, pady=(15, 10))

        tk.Label(
            frame,
            text="[ SOURCE URL ]",
            font=FONT_BOLD,
            fg=AMBER,
            bg=BG,
        ).pack(anchor="w")

        self.url_entry = tk.Entry(
            frame,
            font=FONT,
            fg=AMBER,
            bg=PANEL,
            insertbackground=AMBER,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.url_entry.pack(fill="x", pady=(5, 8), ipady=7)

        self.url_entry.bind("<KeyRelease>", self._url_changed)

        self.check_button = tk.Button(
            frame,
            text="[ CHECK SOURCE ]",
            command=self.check_url,
            font=FONT_BOLD,
            fg=AMBER,
            bg=BG,
            activebackground=BORDER,
            relief="flat",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.check_button.pack(anchor="e")

    # =====================================================
    # Information Section
    # =====================================================
    def _build_information_section(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="x", padx=28, pady=(15, 10))

        tk.Label(
            outer,
            text="┌─ SOURCE INFORMATION ────────────────────────────────-------------------┐",
            font=FONT_SMALL,
            fg=AMBER_DIM,
            bg=BG,
        ).pack(fill="x")

        info_frame = tk.Frame(outer, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        info_frame.pack(fill="x")

        self._create_info_row(info_frame, "TITLE", 0)
        self._create_info_row(info_frame, "CHANNEL", 1)
        self._create_info_row(info_frame, "OUTPUT", 2)

        tk.Label(
            outer,
            text="└────────────────────────────────────────────────────────────────-----------┘",
            font=FONT_SMALL,
            fg=AMBER_DIM,
            bg=BG,
        ).pack(fill="x")

    def _create_info_row(self, parent, label, row):
        tk.Label(
            parent,
            text=f" {label:<8}:",
            font=FONT_BOLD,
            fg=AMBER_DIM,
            bg=PANEL,
            anchor="w",
            width=12,
        ).grid(row=row, column=0, sticky="w", padx=(5, 0), pady=5)

        value = tk.Label(
            parent,
            text="---",
            font=FONT,
            fg=AMBER,
            bg=PANEL,
            anchor="w"
        )
        value.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        parent.grid_columnconfigure(1, weight=1)

        if label == "TITLE":
            self.title_value = value
        elif label == "CHANNEL":
            self.channel_value = value
        elif label == "OUTPUT":
            self.filename_value = value
# =====================================================
    # Save To
    # =====================================================
    def _build_save_section(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="x", padx=28, pady=(15, 0))

        tk.Label(
            frame,
            text="[ SAVE TO ]",
            font=FONT_BOLD,
            fg=AMBER,
            bg=BG,
        ).pack(anchor="w")

        path_frame = tk.Frame(frame, bg=BG)
        path_frame.pack(fill="x", pady=(5, 0))

        self.save_path_entry = tk.Entry(
            path_frame,
            font=FONT_SMALL,
            fg=AMBER,
            bg=PANEL,
            insertbackground=AMBER,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.save_path_entry.pack(side="left", fill="x", expand=True, ipady=6)

        ensure_directories()
        default_folder = str(Path(__file__).resolve().parent / "downloads")
        self.save_path_entry.insert(0, default_folder)

        self.browse_button = tk.Button(
            path_frame,
            text="[ BROWSE ]",
            command=self.browse_save_folder,
            font=FONT_BOLD,
            fg=AMBER,
            bg=BG,
            activebackground=BORDER,
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.browse_button.pack(side="left", padx=(8, 0))

    def browse_save_folder(self):
        selected = filedialog.askdirectory(title="Select YAAY download folder")
        if selected:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, selected)

    # =====================================================
    # Download Button & Action Area
    # =====================================================
    def _build_download_section(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(pady=(20, 15))

        # The primary interactable button is larger to stand out as the 'main quest' of the terminal.
        self.download_button = tk.Button(
            frame,
            text="[ >>> YOINK AUDIO <<< ]",
            command=self.download,
            font=("Consol", 14, "bold"), # Keep standard console font but high weight
            fg=AMBER,
            bg=BG,
            activeforeground="#0a0a00",
            activebackground=BORDER,
            disabledforeground=DISABLED,
            relief="flat",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            state="disabled"
        )
        self.download_button.pack()

    # =====================================================
    # Status Bar (The "Terminal Heartbeat")
    # =====================================================
    def _build_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="● READY",
            font=FONT_BOLD,
            fg=AMBER,
            bg=BG,
            anchor="w",
            padx=10,
            pady=5,
        )
        self.status_bar.pack(side="bottom", fill="x", padx=20, pady=(0, 8))

        # A consistent bottom border to 'enclose' the terminal window
        tk.Frame(
            self.root,
            bg=BORDER,
            height=1
        ).pack(side="bottom", fill="x", padx=20, pady=(0, 5))

    # =====================================================
    # URL Changes
    # =====================================================

    def _url_changed(self, event=None):

        current_text = (
            self.url_entry.get().strip()
        )

        if (
            self.current_url is not None
            and current_text != self.current_url
        ):

            self.current_url = None
            self.current_metadata = None

            self.title_value.config(
                text="—"
            )

            self.channel_value.config(
                text="—"
            )

            self.filename_value.config(
                text="—"
            )

            self.download_button.config(
                state="disabled",
            )

            self._set_status(
                "URL changed — click CHECK"
            )

    # =====================================================
    # Check
    # =====================================================

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

        self.title_value.config(
            text="—"
        )

        self.channel_value.config(
            text="—"
        )

        self.filename_value.config(
            text="—"
        )

        self.current_url = None
        self.current_metadata = None

        self.root.update()

        try:

            metadata = get_metadata(
                url
            )

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
                "✓ READY TO DOWNLOAD"
            )

            self.download_button.config(
                state="normal",
            )

        except Exception as error:

            self.current_url = None
            self.current_metadata = None

            self._set_status(
                "ERROR — COULD NOT RETRIEVE INFORMATION"
            )

            messagebox.showerror(
                "YAAY!",
                str(error),
            )

        finally:

            self.check_button.config(
                state="normal",
            )

    # =====================================================
    # Download
    # =====================================================

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

        save_path = (
            self.save_path_entry.get().strip()
        )

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
                Path(
                    self.save_path_entry
                    .get()
                    .strip()
                ),
            )

            self._set_status(
                "✓ DOWNLOAD COMPLETE"
            )

            play_success_sound()

            self.url_entry.delete(
                0,
                tk.END,
            )

            self.current_url = None
            self.current_metadata = None

            self.title_value.config(
                text="—"
            )

            self.channel_value.config(
                text="—"
            )

            self.filename_value.config(
                text="—"
            )

        except Exception as error:

            self._set_status(
                "ERROR — DOWNLOAD FAILED"
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


# =========================================================
# START
# =========================================================

def start_app():

    ensure_directories()

    root = tk.Tk()

    YAAYApp(root)

    root.mainloop()

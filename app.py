import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import sys

def resource_path(filename):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)

BG = "#0f0f0f"
CARD = "#1a1a1a"
ACCENT = "#00e5ff"
TEXT = "#f0f0f0"
MUTED = "#888888"
SUCCESS = "#00e676"
ERROR = "#ff5252"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YT Downloader")
        self.geometry("640x520")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.output_dir = os.path.expanduser("~/Downloads")
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(28, 0))
        tk.Label(hdr, text="YT", font=("Courier New", 28, "bold"), fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(hdr, text="Downloader", font=("Courier New", 28, "bold"), fg=TEXT, bg=BG).pack(side="left", padx=(4,0))
        tk.Label(hdr, text="video & playlist → mp3 / mp4 / wav", font=("Courier New", 10), fg=MUTED, bg=BG).pack(side="left", padx=(16,0), pady=(8,0))

        sep = tk.Frame(self, bg=ACCENT, height=1)
        sep.pack(fill="x", padx=30, pady=(14, 20))

        # URL input
        self._label("Paste YouTube URL or Playlist URL")
        self.url_var = tk.StringVar()
        url_frame = tk.Frame(self, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        url_frame.pack(fill="x", padx=30)
        tk.Entry(url_frame, textvariable=self.url_var, font=("Courier New", 11),
                 bg=CARD, fg=TEXT, insertbackground=ACCENT, relief="flat",
                 bd=10).pack(fill="x")

        # Format
        self._label("Output Format", pady=(18,6))
        fmt_frame = tk.Frame(self, bg=BG)
        fmt_frame.pack(fill="x", padx=30)
        self.fmt_var = tk.StringVar(value="mp3")
        for fmt, desc in [("mp3","Audio MP3"), ("wav","Audio WAV"), ("mp4","Video MP4"), ("webm","Video WebM")]:
            self._radio(fmt_frame, fmt, desc)

        # Output folder
        self._label("Output Folder", pady=(18,6))
        dir_frame = tk.Frame(self, bg=CARD, highlightbackground="#333", highlightthickness=1)
        dir_frame.pack(fill="x", padx=30)
        inner = tk.Frame(dir_frame, bg=CARD)
        inner.pack(fill="x", padx=10, pady=6)
        self.dir_label = tk.Label(inner, text=self.output_dir, font=("Courier New", 10),
                                   fg=MUTED, bg=CARD, anchor="w")
        self.dir_label.pack(side="left", fill="x", expand=True)
        tk.Button(inner, text="Browse", font=("Courier New", 9), bg="#222", fg=ACCENT,
                  relief="flat", cursor="hand2", bd=0, padx=8,
                  command=self._browse).pack(side="right")

        # Download button
        self.dl_btn = tk.Button(self, text="⬇  DOWNLOAD", font=("Courier New", 13, "bold"),
                                 bg=ACCENT, fg="#000", relief="flat", cursor="hand2",
                                 bd=0, pady=12, command=self._start)
        self.dl_btn.pack(fill="x", padx=30, pady=(24, 0))

        # Log box
        log_frame = tk.Frame(self, bg=CARD, highlightbackground="#222", highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=30, pady=(14, 24))
        self.log = tk.Text(log_frame, font=("Courier New", 9), bg=CARD, fg=MUTED,
                           relief="flat", bd=8, state="disabled", wrap="word", height=7)
        self.log.pack(fill="both", expand=True)

    def _label(self, text, pady=(0,6)):
        tk.Label(self, text=text, font=("Courier New", 10), fg=MUTED, bg=BG)\
          .pack(anchor="w", padx=30, pady=pady)

    def _radio(self, parent, value, label):
        f = tk.Frame(parent, bg=BG)
        f.pack(side="left", padx=(0, 20))
        rb = tk.Radiobutton(f, variable=self.fmt_var, value=value,
                             bg=BG, fg=TEXT, selectcolor=BG,
                             activebackground=BG, activeforeground=ACCENT,
                             font=("Courier New", 11, "bold"),
                             relief="flat", cursor="hand2",
                             indicatoron=False,
                             text=f" {value.upper()} ",
                             bd=1)
        rb.pack(side="left")
        tk.Label(f, text=label, font=("Courier New", 9), fg=MUTED, bg=BG).pack(side="left", padx=(4,0))

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.output_dir)
        if d:
            self.output_dir = d
            self.dir_label.config(text=d)

    def _log(self, msg, color=None):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _start(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please paste a URL first.")
            return
        self.dl_btn.config(state="disabled", text="Downloading...")
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url):
        fmt = self.fmt_var.get()
        yt_dlp = resource_path("yt-dlp.exe")
        ffmpeg_dir = resource_path(".")

        if fmt in ("mp3", "wav"):
            cmd = [yt_dlp, "-x", "--audio-format", fmt,
                   "--ffmpeg-location", ffmpeg_dir,
                   "-o", os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                   url]
        else:
            cmd = [yt_dlp, "-f", "bestvideo+bestaudio",
                   "--merge-output-format", fmt,
                   "--ffmpeg-location", ffmpeg_dir,
                   "-o", os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                   url]

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1)
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    self.after(0, self._log, line)
            proc.wait()
            if proc.returncode == 0:
                self.after(0, self._log, "\n✅ Done! Files saved to: " + self.output_dir)
            else:
                self.after(0, self._log, "\n❌ Something went wrong. Check the log above.")
        except FileNotFoundError:
            self.after(0, self._log, "❌ yt-dlp.exe not found next to this app!")
        finally:
            self.after(0, lambda: self.dl_btn.config(state="normal", text="⬇  DOWNLOAD"))

if __name__ == "__main__":
    app = App()
    app.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys


def resource_path(filename):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


# YouTube Dark theme
BG      = "#0F0F0F"
CARD    = "#212121"
ACCENT  = "#FF0000"   # YouTube red
TEXT    = "#FFFFFF"
MUTED   = "#AAAAAA"
SUCCESS = "#00e676"
ERROR   = "#CC0000"   # darker red for Stop button
FONT    = "Arial"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("660x540")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.output_dir = os.path.expanduser("~/Downloads")
        self.dl_proc = None
        self._stopped_by_user = False
        try:
            self.iconbitmap(resource_path('icon.ico'))
        except Exception:
            pass
        self._build_ui()

    def _build_ui(self):
        # ── Header: YouTube logo canvas + wordmark ──────────────────────────
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(28, 0))

        # Logo from assets/logo.png (falls back to drawn canvas if missing)
        try:
            raw = tk.PhotoImage(file=resource_path(os.path.join('assets', 'logo.png')))
            factor = max(1, raw.width() // 56)
            self._logo_photo = raw.subsample(factor, factor)
            tk.Label(hdr, image=self._logo_photo, bg=BG).pack(side="left")
        except Exception:
            logo = tk.Canvas(hdr, width=42, height=30, bg=BG, highlightthickness=0)
            logo.pack(side="left")
            logo.create_rectangle(2, 2, 40, 28, fill=ACCENT, outline="")
            logo.create_polygon(16, 8, 16, 22, 32, 15, fill="white", outline="")

        tk.Label(hdr, text="YouTube",    font=(FONT, 22, "bold"), fg=TEXT,  bg=BG).pack(side="left", padx=(8, 0))
        tk.Label(hdr, text="Downloader", font=(FONT, 22),          fg=TEXT,  bg=BG).pack(side="left", padx=(4, 0))

        tk.Label(self, text="video & playlist  ·  mp3 / mp4 / wav / webm",
                 font=(FONT, 9), fg=MUTED, bg=BG).pack(anchor="w", padx=30, pady=(4, 0))

        sep = tk.Frame(self, bg=ACCENT, height=2)
        sep.pack(fill="x", padx=30, pady=(12, 20))

        # ── URL input ───────────────────────────────────────────────────────
        self._label("Paste YouTube URL or Playlist URL")
        self.url_var = tk.StringVar()
        url_frame = tk.Frame(self, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        url_frame.pack(fill="x", padx=30)
        tk.Entry(url_frame, textvariable=self.url_var, font=(FONT, 11),
                 bg=CARD, fg=TEXT, insertbackground=ACCENT, relief="flat",
                 bd=10).pack(fill="x")

        # ── Single / Playlist toggle ────────────────────────────────────────
        self._label("Download", pady=(18, 6))
        mode_frame = tk.Frame(self, bg=BG)
        mode_frame.pack(fill="x", padx=30)
        self.playlist_var = tk.BooleanVar(value=False)
        for val, lbl in [(False, "Single video"), (True, "Playlist")]:
            tk.Radiobutton(mode_frame, variable=self.playlist_var, value=val,
                           text=lbl, bg=BG, fg=TEXT, selectcolor=ACCENT,
                           activebackground=BG, activeforeground=ACCENT,
                           font=(FONT, 10), relief="flat", cursor="hand2",
                           indicatoron=False).pack(side="left", padx=(0, 12))

        # ── Format ──────────────────────────────────────────────────────────
        self._label("Output Format", pady=(18, 6))
        fmt_frame = tk.Frame(self, bg=BG)
        fmt_frame.pack(fill="x", padx=30)
        self.fmt_var = tk.StringVar(value="mp3")
        for fmt, desc in [("mp3", "Audio MP3"), ("wav", "Audio WAV"),
                           ("mp4", "Video MP4"), ("webm", "Video WebM")]:
            self._radio(fmt_frame, fmt, desc)

        # ── Output folder ───────────────────────────────────────────────────
        self._label("Output Folder", pady=(18, 6))
        dir_frame = tk.Frame(self, bg=CARD, highlightbackground="#333", highlightthickness=1)
        dir_frame.pack(fill="x", padx=30)
        inner = tk.Frame(dir_frame, bg=CARD)
        inner.pack(fill="x", padx=10, pady=6)
        self.dir_label = tk.Label(inner, text=self.output_dir, font=(FONT, 10),
                                   fg=MUTED, bg=CARD, anchor="w")
        self.dir_label.pack(side="left", fill="x", expand=True)
        tk.Button(inner, text="Browse", font=(FONT, 9, "bold"), bg=CARD, fg=ACCENT,
                  relief="flat", cursor="hand2", bd=0, padx=8,
                  command=self._browse).pack(side="right")

        # ── Download / Stop buttons ─────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill="x", padx=30, pady=(24, 0))
        self.dl_btn = tk.Button(btn_frame, text="▶  DOWNLOAD", font=(FONT, 13, "bold"),
                                 bg=ACCENT, fg=TEXT, relief="flat", cursor="hand2",
                                 bd=0, pady=12, command=self._start)
        self.dl_btn.pack(side="left", fill="x", expand=True)
        self.stop_btn = tk.Button(btn_frame, text="■  STOP", font=(FONT, 13, "bold"),
                                   bg="#272727", fg=TEXT, relief="flat", cursor="hand2",
                                   bd=0, pady=12, padx=20, command=self._stop,
                                   state="disabled")
        self.stop_btn.pack(side="right")

        # ── Log box ─────────────────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=CARD, highlightbackground="#333", highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=30, pady=(14, 24))
        self.log = tk.Text(log_frame, font=(FONT, 9), bg=CARD, fg=MUTED,
                           relief="flat", bd=8, state="disabled", wrap="word", height=7)
        self.log.pack(fill="both", expand=True)

    def _label(self, text, pady=(0, 6)):
        tk.Label(self, text=text, font=(FONT, 10), fg=MUTED, bg=BG)\
          .pack(anchor="w", padx=30, pady=pady)

    def _radio(self, parent, value, label):
        f = tk.Frame(parent, bg=BG)
        f.pack(side="left", padx=(0, 20))
        tk.Radiobutton(f, variable=self.fmt_var, value=value,
                       bg=BG, fg=TEXT, selectcolor=ACCENT,
                       activebackground=BG, activeforeground=ACCENT,
                       font=(FONT, 11, "bold"), relief="flat", cursor="hand2",
                       indicatoron=False, text=f" {value.upper()} ",
                       bd=1).pack(side="left")
        tk.Label(f, text=label, font=(FONT, 9), fg=MUTED, bg=BG).pack(side="left", padx=(4, 0))

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
        self._stopped_by_user = False
        self.dl_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _stop(self):
        if self.dl_proc and self.dl_proc.poll() is None:
            self._stopped_by_user = True
            subprocess.call(
                ['taskkill', '/F', '/T', '/PID', str(self.dl_proc.pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            self.after(0, self._log, "\n⏹ Stopped by user.")

    def _download(self, url):
        fmt = self.fmt_var.get()
        yt_dlp = resource_path("yt-dlp.exe")
        ffmpeg_dir = resource_path(".")

        base_opts = ["--ffmpeg-location", ffmpeg_dir,
                     "-o", os.path.join(self.output_dir, "%(title)s.%(ext)s")]
        if not self.playlist_var.get():
            base_opts.insert(0, "--no-playlist")
        if fmt in ("mp3", "wav"):
            cmd = [yt_dlp, "-x", "--audio-format", fmt] + base_opts + [url]
        else:
            cmd = [yt_dlp, "-f", "bestvideo+bestaudio",
                   "--merge-output-format", fmt] + base_opts + [url]

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1)
            self.dl_proc = proc
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    self.after(0, self._log, line)
            proc.wait()
            if self._stopped_by_user:
                pass
            elif proc.returncode == 0:
                self.after(0, self._log, "\n✅ Done! Files saved to: " + self.output_dir)
            else:
                self.after(0, self._log, "\n❌ Something went wrong. Check the log above.")
        except FileNotFoundError:
            self.after(0, self._log, "❌ yt-dlp.exe not found next to this app!")
        finally:
            self.dl_proc = None
            self._stopped_by_user = False
            self.after(0, lambda: (self.dl_btn.config(state="normal"),
                                   self.stop_btn.config(state="disabled")))


if __name__ == "__main__":
    app = App()
    app.mainloop()

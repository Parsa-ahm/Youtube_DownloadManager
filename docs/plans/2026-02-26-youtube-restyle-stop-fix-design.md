# YouTube Restyle + Stop Fix — Design

**Date:** 2026-02-26

---

## Problem

1. **Stop button doesn't fully stop downloads.** `proc.terminate()` only kills `yt-dlp.exe` directly. yt-dlp spawns `ffmpeg.exe` as a child process; that child keeps running after terminate, holding file locks and consuming resources.

2. **App looks like a generic dark tool, not a YouTube product.** Current theme uses cyan (`#00e5ff`) and Courier New — no visual connection to YouTube's brand.

---

## Design

### Fix 1 — Stop button: kill full process tree

Replace `proc.terminate()` with `taskkill /F /T /PID`:

```python
def _stop(self):
    if self.dl_proc and self.dl_proc.poll() is None:
        self._stopped_by_user = True
        subprocess.call(
            ['taskkill', '/F', '/T', '/PID', str(self.dl_proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        self.after(0, self._log, "\n⏹ Stopped by user.")
```

`taskkill` is built into every Windows install. `/T` kills all child processes (including ffmpeg). No new dependencies.

---

### Fix 2 — YouTube Dark restyle

#### Color palette

| Token   | Old        | New        | Meaning                     |
|---------|------------|------------|-----------------------------|
| `BG`    | `#0f0f0f`  | `#0F0F0F`  | YouTube dark bg (unchanged) |
| `CARD`  | `#1a1a1a`  | `#212121`  | YouTube secondary bg        |
| `ACCENT`| `#00e5ff`  | `#FF0000`  | YouTube red                 |
| `TEXT`  | `#f0f0f0`  | `#FFFFFF`  | Pure white                  |
| `MUTED` | `#888888`  | `#AAAAAA`  | YouTube muted text          |
| `SUCCESS`| `#00e676` | `#00e676`  | Unchanged                   |
| `ERROR` | `#ff5252`  | `#CC0000`  | Darker red (Stop button)    |

#### Font

`"Courier New"` (monospace) → `"Arial"` everywhere. YouTube uses Roboto; Arial is the closest available system font on Windows.

#### Header

Replace the `"YT" + "Downloader"` text combo with a YouTube-style header:
- A red rounded rectangle (`Canvas`) containing a white `▶` play triangle — mimics the YouTube logo icon
- Next to it: `"YouTube"` in white Arial bold + `"Downloader"` in white Arial regular
- Subtitle line: `"video & playlist  ·  mp3 / mp4 / wav / webm"` in muted gray

#### Buttons

- **Download**: `#FF0000` bg, white text, Arial bold
- **Stop**: `#272727` bg, white text (distinct from download, not competing red)
- **Browse**: red text (`#FF0000`) on dark card bg
- **Format/mode radiobuttons**: red fill + white text when selected; dark outline + gray text when unselected

#### URL input

Border highlight color: `#FF0000` (red) instead of cyan. Cursor color: `#FF0000`.

#### Window

- Title: `"YouTube Downloader"`
- Size: `660×540` (slightly wider for header breathing room)

---

## Files Changed

| File    | Change                                      |
|---------|---------------------------------------------|
| `app.py`| Color constants, font, header, `_stop()`, window size/title |

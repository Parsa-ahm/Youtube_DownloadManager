# Production-Ready Release Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the repo shippable — fix `.gitignore`, harden the GitHub Action's DLL handling, add an app icon, and polish the README so users can download the exe from the Releases page on first tag push.

**Architecture:** Pure repo/CI configuration work. No new application logic. The GitHub Action downloads yt-dlp + FFmpeg at build time, discovers DLLs dynamically, bundles everything with PyInstaller, and publishes to GitHub Releases. A prebuilt `icon.ico` is generated once locally via a throwaway Python script and committed.

**Tech Stack:** Python 3.12, PyInstaller 6+, PowerShell (GitHub Actions windows-latest), yt-dlp, FFmpeg 8.x (BtbN GPL-shared build), softprops/action-gh-release@v2

---

### Task 1: Fix `.gitignore`

**Files:**
- Modify: `.gitignore`

**Step 1: Remove `*.spec` from `.gitignore`**

Open `.gitignore`. Find and delete this line:
```
*.spec
```
`YTDownloader.spec` is already tracked — this line was only causing confusion.

**Step 2: Add local build artifacts to `.gitignore`**

In the `# Binaries` section, add these two lines:
```
ffmpeg.zip
ffmpeg_extracted/
```

**Step 3: Verify**

Run:
```bash
git status
```
Expected: `ffmpeg.zip` and `ffmpeg_extracted/` no longer appear as untracked. `YTDownloader.spec` is NOT listed (it's tracked, unmodified).

**Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: fix gitignore — track spec, ignore ffmpeg build artifacts"
```

---

### Task 2: Generate and commit `icon.ico`

**Files:**
- Create: `generate_icon.py` (temporary — deleted after use)
- Create: `icon.ico` (committed to repo)

**Step 1: Install Pillow temporarily**

```bash
pip install Pillow
```

**Step 2: Create `generate_icon.py`**

Create this file at the repo root:

```python
from PIL import Image, ImageDraw

BG      = (15,  15,  15,  255)   # #0f0f0f
CYAN    = (0,  229, 255,  255)   # #00e5ff

def frame(size):
    img  = Image.new("RGBA", (size, size), BG)
    draw = ImageDraw.Draw(img)

    # Rounded-ish border rectangle
    b = max(1, size // 20)
    pad = max(2, size // 16)
    draw.rectangle([pad, pad, size - pad - 1, size - pad - 1],
                   outline=CYAN, width=b)

    # Draw a simple down-arrow inside
    cx   = size // 2
    top  = size // 4
    bot  = size * 3 // 4
    stem = max(1, size // 8)

    # Vertical stem
    draw.rectangle([cx - stem // 2, top, cx + stem // 2, bot - stem * 2],
                   fill=CYAN)
    # Arrow head (triangle via polygon)
    hw = size // 4
    draw.polygon([
        (cx - hw, bot - stem * 2),
        (cx + hw, bot - stem * 2),
        (cx,      bot),
    ], fill=CYAN)

    # Horizontal base line
    lw = max(1, size // 16)
    draw.rectangle([cx - hw, bot + lw, cx + hw, bot + lw * 3], fill=CYAN)

    return img

sizes  = [256, 128, 64, 48, 32, 16]
frames = [frame(s) for s in sizes]
frames[0].save(
    "icon.ico",
    format="ICO",
    append_images=frames[1:],
    sizes=[(s, s) for s in sizes],
)
print("icon.ico written")
```

**Step 3: Run it**

```bash
python generate_icon.py
```
Expected output: `icon.ico written`

**Step 4: Verify**

```bash
python -c "import os; s=os.path.getsize('icon.ico'); print(f'{s} bytes'); assert s > 5000, 'too small'"
```
Expected: a byte count above 5 000 (it will be ~100 KB).

**Step 5: Delete the generator script**

```bash
rm generate_icon.py
```

**Step 6: Commit**

```bash
git add icon.ico
git commit -m "feat: add app icon (cyan download arrow on dark background)"
```

---

### Task 3: Update `BUILD.bat`

**Files:**
- Modify: `BUILD.bat`

**Step 1: Add `--icon` flag**

Find the pyinstaller block in `BUILD.bat`. It currently ends with:
```bat
    app.py
```

Add `--icon icon.ico ^` on the line before `app.py`:
```bat
    --icon icon.ico ^
    app.py
```

Full pyinstaller block should now read:
```bat
pyinstaller --onefile --windowed --name "YTDownloader" ^
    --add-binary "yt-dlp.exe;." ^
    --add-binary "ffmpeg.exe;." ^
    --add-binary "ffprobe.exe;." ^
    --add-binary "avcodec-62.dll;." ^
    --add-binary "avdevice-62.dll;." ^
    --add-binary "avfilter-11.dll;." ^
    --add-binary "avformat-62.dll;." ^
    --add-binary "avutil-60.dll;." ^
    --add-binary "swresample-6.dll;." ^
    --add-binary "swscale-9.dll;." ^
    --icon icon.ico ^
    app.py
```

**Step 2: Verify syntax**

```bash
cmd /c "BUILD.bat" 2>&1 | head -5
```
Expected: prints the banner without a syntax error (it will fail later when binaries aren't present — that's fine).

**Step 3: Commit**

```bash
git add BUILD.bat
git commit -m "chore: add --icon flag to local build script"
```

---

### Task 4: Update `YTDownloader.spec`

**Files:**
- Modify: `YTDownloader.spec`

**Step 1: Add icon to the EXE() call**

Find the `EXE(` block. It currently has:
```python
    console=False,
```

Change the `icon` parameter (it currently doesn't exist — add it). The full `EXE()` call should read:

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='YTDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
```

**Step 2: Verify it parses**

```bash
python -c "exec(open('YTDownloader.spec').read())" 2>&1 | head -5
```
Expected: no Python syntax errors (it will complain about PyInstaller symbols not being defined — that's fine; we're only checking parse).

**Step 3: Commit**

```bash
git add YTDownloader.spec
git commit -m "chore: add icon to PyInstaller spec"
```

---

### Task 5: Rewrite `.github/workflows/release.yml`

**Files:**
- Modify: `.github/workflows/release.yml`

**Step 1: Replace the file entirely**

Write the following content to `.github/workflows/release.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Download yt-dlp
        run: |
          Invoke-WebRequest `
            -Uri "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" `
            -OutFile "yt-dlp.exe" -UseBasicParsing

      - name: Download and extract FFmpeg
        run: |
          Invoke-WebRequest `
            -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n8.0-latest-win64-gpl-shared-8.0.zip" `
            -OutFile "ffmpeg.zip" -UseBasicParsing
          Expand-Archive -Path ffmpeg.zip -DestinationPath ffmpeg_extracted
          $binPath = (Get-ChildItem -Path ffmpeg_extracted -Recurse -Filter "ffmpeg.exe" |
                      Select-Object -First 1).DirectoryName
          Copy-Item "$binPath\ffmpeg.exe", "$binPath\ffprobe.exe" -Destination .
          Copy-Item "$binPath\*.dll" -Destination .

      - name: Build EXE
        run: |
          # Discover every .dll copied into the workspace and build --add-binary flags
          $dllFlags = Get-ChildItem -Path . -Filter "*.dll" |
                      ForEach-Object { "--add-binary"; "$($_.Name);." }

          $pyArgs = @(
            "--onefile", "--windowed",
            "--name",    "YTDownloader",
            "--icon",    "icon.ico",
            "--add-binary", "yt-dlp.exe;.",
            "--add-binary", "ffmpeg.exe;.",
            "--add-binary", "ffprobe.exe;."
          ) + $dllFlags + @("app.py")

          Write-Host "pyinstaller $pyArgs"
          & pyinstaller @pyArgs

      - name: Verify EXE was produced
        run: |
          if (-not (Test-Path "dist\YTDownloader.exe")) {
            Write-Error "dist\YTDownloader.exe not found — build failed"
            exit 1
          }
          $size = (Get-Item "dist\YTDownloader.exe").Length
          Write-Host "EXE size: $size bytes"
          if ($size -lt 1MB) {
            Write-Error "EXE is suspiciously small ($size bytes)"
            exit 1
          }

      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/YTDownloader.exe
          generate_release_notes: true
          body: |
            Standalone Windows app — download YouTube videos and playlists as MP3, WAV, MP4, or WebM.

            **No install needed.** Download `YTDownloader.exe`, run it, done.

            **Bundled:**
            - [yt-dlp](https://github.com/yt-dlp/yt-dlp) — video/audio extraction
            - [FFmpeg](https://ffmpeg.org) — audio/video conversion
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Step 2: Validate YAML syntax**

```bash
python -c "import yaml, sys; yaml.safe_load(open('.github/workflows/release.yml')); print('YAML OK')"
```
Expected: `YAML OK`

**Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: dynamic DLL discovery, verify step, icon, use requirements.txt"
```

---

### Task 6: Update `README.md`

**Files:**
- Modify: `README.md`

**Step 1: Add release badge**

The README currently starts with:
```markdown
# YT Downloader

A standalone Windows app...

![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
```

Change it to:
```markdown
# YT Downloader

A standalone Windows app to download YouTube videos and playlists as **MP3**, **WAV**, **MP4**, or **WebM**. Paste a URL, pick a format, click Download.

[![Latest Release](https://img.shields.io/github/v/release/Parsa-ahm/Youtube_DownloadManager?style=flat-square&color=00e5ff)](https://github.com/Parsa-ahm/Youtube_DownloadManager/releases/latest)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add release badge to README"
```

---

### Task 7: Push and trigger the first release

**Step 1: Push all commits**

```bash
git push origin main
```

**Step 2: Create and push a version tag**

```bash
git tag -a v1.0.0 -m "Initial public release"
git push origin v1.0.0
```

**Step 3: Verify the Action triggered**

Go to: `https://github.com/Parsa-ahm/Youtube_DownloadManager/actions`

Expected: a workflow run named `Build and Release` appears within ~30 seconds with status "in progress".

**Step 4: Verify the release was created**

Once the Action completes (~3-5 minutes):

Go to: `https://github.com/Parsa-ahm/Youtube_DownloadManager/releases`

Expected:
- Release `v1.0.0` exists
- `YTDownloader.exe` is attached as a release asset
- Asset size is > 1 MB

---

## Done

After Task 7, anyone can:
1. Go to `https://github.com/Parsa-ahm/Youtube_DownloadManager/releases/latest`
2. Download `YTDownloader.exe`
3. Run it — no install needed

Future releases: `git tag -a vX.Y.Z -m "..." && git push origin vX.Y.Z`

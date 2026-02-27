# Production-Ready Release Pipeline — Design

**Date:** 2026-02-26
**Scope:** Make the repo shippable: fix `.gitignore`, harden the GitHub Action, add an app icon, polish README.

---

## Problem

The GitHub Action (`release.yml`) exists but has never been triggered. Key fragility:

1. `ffmpeg.zip` and `ffmpeg_extracted/` are not gitignored — pollute `git status`.
2. `.gitignore` lists `*.spec` but `YTDownloader.spec` is already tracked — confusing.
3. PyInstaller step hardcodes DLL filenames (`avcodec-62.dll`, etc.) — breaks silently if FFmpeg bumps major version.
4. No app icon — exe looks unprofessional.
5. No release badge in README.

---

## Design (Approach B)

### 1. `.gitignore`

- Add `ffmpeg.zip` and `ffmpeg_extracted/` entries.
- Remove `*.spec` line (spec file is intentionally tracked for local builds).

### 2. `release.yml` — dynamic DLL discovery

Replace 9 hardcoded `--add-binary` flags with a PowerShell snippet that discovers all `.dll` files in the working directory at build time:

```powershell
$dlls = Get-ChildItem -Path . -Filter "*.dll" |
        ForEach-Object { "--add-binary `"$($_.Name);.`"" }
$pyArgs = @("--onefile","--windowed","--name","YTDownloader",
            "--icon","icon.ico",
            "--add-binary","yt-dlp.exe;.",
            "--add-binary","ffmpeg.exe;.",
            "--add-binary","ffprobe.exe;.") + $dlls + @("app.py")
& pyinstaller @pyArgs
```

Also switch `pip install pyinstaller` → `pip install -r requirements.txt`.

### 3. `icon.ico`

A prebuilt 256×256 `.ico` file committed to the repo root. Matches the app's cyan-on-black (`#00e5ff` / `#0f0f0f`) aesthetic. Referenced in:
- `release.yml` PyInstaller step (`--icon icon.ico`)
- `YTDownloader.spec` (`icon='icon.ico'`)
- `BUILD.bat` (`--icon icon.ico`)

### 4. `README.md`

Add a release badge directly below the title:

```markdown
[![Latest Release](https://img.shields.io/github/v/release/Parsa-ahm/Youtube_DownloadManager)](https://github.com/Parsa-ahm/Youtube_DownloadManager/releases/latest)
```

---

## Files Changed

| File | Action |
|------|--------|
| `.gitignore` | Add `ffmpeg.zip`, `ffmpeg_extracted/`; remove `*.spec` |
| `.github/workflows/release.yml` | Dynamic DLL flags, `requirements.txt`, `--icon` |
| `YTDownloader.spec` | Add `icon='icon.ico'` |
| `BUILD.bat` | Add `--icon icon.ico` |
| `icon.ico` | New prebuilt file |
| `README.md` | Add release badge |

---

## Release Flow (post-implementation)

```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

GitHub Action triggers → builds `YTDownloader.exe` → publishes release with EXE attached.

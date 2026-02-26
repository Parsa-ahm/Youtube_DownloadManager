# Developer / Build Instructions

For you — build from source, create releases, etc.

## Prerequisites

- **Python 3.10+** — [python.org](https://python.org) (tick "Add to PATH")
- **yt-dlp.exe** — [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases)
- **FFmpeg 8.x** — [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases) (use the "full" / "gpl-shared" variant)

## Files Needed Before Building

Copy into project root:

| File | Source |
|------|--------|
| `yt-dlp.exe` | yt-dlp releases |
| `ffmpeg.exe`, `ffprobe.exe` | FFmpeg build |
| `avcodec-62.dll`, `avdevice-62.dll`, `avfilter-11.dll`, `avformat-62.dll`, `avutil-60.dll`, `swresample-6.dll`, `swscale-9.dll` | FFmpeg 8.x build |

> FFmpeg 7.x uses different DLL numbers (e.g. `avcodec-61.dll`). Update `BUILD.bat` if needed.

## Build

1. Put all `.exe` and `.dll` files in this folder
2. Double-click `BUILD.bat`
3. EXE is in `dist\YTDownloader.exe`

## Creating a Release

### Automated (recommended)

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

The workflow downloads yt-dlp + FFmpeg, builds, and publishes the release with the EXE attached.

### Manual

1. Build locally
2. Create tag and push
3. On GitHub: Releases → Draft new release → attach `dist\YTDownloader.exe`

## Release Checklist

- [ ] Test on clean Windows
- [ ] Push tag
- [ ] Add changelog in release notes

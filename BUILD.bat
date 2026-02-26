@echo off
echo ================================
echo  YT Downloader - Build Script
echo ================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Download from https://python.org
    pause
    exit /b 1
)

:: Install pyinstaller
echo Installing PyInstaller...
pip install pyinstaller -q

:: Build the exe
echo.
echo Building YTDownloader.exe ...
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
    app.py

echo.
if exist "dist\YTDownloader.exe" (
    echo ================================
    echo  SUCCESS! 
    echo  Your exe is in the dist\ folder
    echo ================================
) else (
    echo BUILD FAILED - check errors above
)
pause

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('yt-dlp.exe', '.'), ('ffmpeg.exe', '.'), ('ffprobe.exe', '.'), ('avcodec-62.dll', '.'), ('avdevice-62.dll', '.'), ('avfilter-11.dll', '.'), ('avformat-62.dll', '.'), ('avutil-60.dll', '.'), ('swresample-6.dll', '.'), ('swscale-9.dll', '.')],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    icon=['icon.ico'],
)

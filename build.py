"""Exe derlemesi ve paketleme.

    .venv/Scripts/python build.py            # ikon → PyInstaller → gereksiz Qt dosyalarını buda → zip (+ .sha256)
    .venv/Scripts/python build.py --release  # yukarıdakiler + gh ile v<sürüm> release'i (sürüm: fatura_okuyucu/version.py)

Çıktı: build/dist/FaturaOkuyucu/FaturaOkuyucu.exe ve build/FaturaOkuyucu-windows.zip
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
NAME = "FaturaOkuyucu"
DIST = BUILD / "dist" / NAME
ZIP = BUILD / f"{NAME}-windows.zip"
ICON = ROOT / "assets" / "app.ico"

# Arayüz yalnızca QtCore/QtGui/QtWidgets kullanıyor
EXCLUDE_MODULES = [
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets", "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtMultimedia",
    "PySide6.Qt3DCore", "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtOpenGL",
    "PySide6.QtSql", "PySide6.QtTest", "PySide6.QtBluetooth", "PySide6.QtPositioning",
    "tkinter", "unittest", "pydoc",
]
# Derlemeden sonra silinecek Qt DLL / klasörleri (glob, _internal/PySide6 altında)
PRUNE = [
    "Qt6WebEngine*", "Qt6Quick*", "Qt6Qml*", "Qt6Pdf*", "Qt6Network*", "Qt6Multimedia*",
    "Qt63D*", "Qt6Charts*", "Qt6OpenGL*", "Qt6Positioning*", "Qt6Sql*", "Qt6VirtualKeyboard*",
    "opengl32sw.dll", "qml", "resources", "translations/qtwebengine*",
]


def make_icon() -> None:
    if ICON.exists():
        return
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter

    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841
    img = QImage(256, 256, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#1F4E78"))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(QRectF(16, 16, 224, 224), 40, 40)
    p.setBrush(QColor("#FFFFFF"))
    p.drawRoundedRect(QRectF(64, 44, 128, 168), 12, 12)
    p.setBrush(QColor("#2E75B6"))
    for i in range(4):
        p.drawRect(QRectF(84, 74 + i * 26, 88 - (i % 2) * 30, 10))
    p.setPen(QColor("#1F7A3D"))
    p.setFont(QFont("Segoe UI", 46, QFont.Bold))
    p.drawText(QRectF(110, 150, 120, 80), Qt.AlignCenter, "₺")
    p.end()
    ICON.parent.mkdir(exist_ok=True)
    img.save(str(ICON))
    img.save(str(ICON.with_suffix(".png")))


def build() -> None:
    make_icon()
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed",
           "--name", NAME, "--icon", str(ICON),
           "--add-data", f"{ICON.with_suffix('.png')};assets",
           "--distpath", str(BUILD / "dist"), "--workpath", str(BUILD / "work"),
           "--specpath", str(BUILD),
           "--collect-submodules", "winrt"]
    for m in EXCLUDE_MODULES:
        cmd += ["--exclude-module", m]
    subprocess.run(cmd + [str(ROOT / "main.py")], check=True)

    qt = DIST / "_internal" / "PySide6"
    for pat in PRUNE:
        for p in qt.glob(pat):
            shutil.rmtree(p) if p.is_dir() else p.unlink()


def package() -> None:
    ZIP.unlink(missing_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in DIST.rglob("*"):
            z.write(p, Path(NAME) / p.relative_to(DIST))
    # Güncelleyici yalnızca bu iki ada bakar; değiştirmeyin
    digest = hashlib.sha256(ZIP.read_bytes()).hexdigest()
    ZIP.with_name(ZIP.name + ".sha256").write_text(f"{digest}  {ZIP.name}\n", encoding="ascii")
    print(f"{ZIP} ({ZIP.stat().st_size / 1e6:.1f} MB)")


def release() -> None:
    sys.path.insert(0, str(ROOT))
    from fatura_okuyucu.version import REPO, __version__
    notes = ROOT / "build" / "notes.md"
    cmd = ["gh", "release", "create", f"v{__version__}", str(ZIP), str(ZIP) + ".sha256",
           "--repo", REPO, "--title", f"GİB Fatura Okuyucu {__version__}"]
    cmd += ["--notes-file", str(notes)] if notes.exists() else ["--generate-notes"]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build()
    package()
    if "--release" in sys.argv:
        release()

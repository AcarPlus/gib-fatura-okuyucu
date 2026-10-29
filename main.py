"""GİB Fatura Okuyucu - başlatıcı. Komut satırı yolları açılışta işlenir ("Birlikte aç")."""
import argparse
import sys
from pathlib import Path

from fatura_okuyucu import updater

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from fatura_okuyucu.ui import MainWindow


def main() -> int:
    # Güncelleyici modu Qt başlamadan çalışır (yeni exe eski kurulumun üzerine yazar)
    if "--apply-update" in sys.argv:
        ap = argparse.ArgumentParser()
        ap.add_argument("--apply-update", required=True)
        ap.add_argument("--wait-pid", type=int, required=True)
        ap.add_argument("--no-restart", action="store_true")
        a = ap.parse_args()
        return updater.apply_update(Path(a.apply_update), a.wait_pid, not a.no_restart)

    # Pencere açmadan: FaturaOkuyucu.exe --excel cikti.xlsx girdi.rar [klasör ...]
    if "--excel" in sys.argv:
        from fatura_okuyucu import core
        ap = argparse.ArgumentParser()
        ap.add_argument("--excel", required=True)
        ap.add_argument("girdiler", nargs="+")
        a = ap.parse_args()
        belgeler = core.isle([Path(g) for g in a.girdiler])
        core.excel_yaz(belgeler, Path(a.excel))
        return 0

    app = QApplication(sys.argv)
    app.setApplicationName("GİB Fatura Okuyucu")
    app.setStyle("Fusion")
    pencere = MainWindow()
    pencere.show()
    yollar = [Path(a) for a in sys.argv[1:]]
    if yollar:
        QTimer.singleShot(0, lambda: pencere.girdileri_ekle(yollar))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

"""GİB Fatura Okuyucu - PySide6 masaüstü arayüzü."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import (QAbstractTableModel, QModelIndex, QSortFilterProxyModel,
                            QStandardPaths, Qt, QThread, QTimer, QUrl, Signal)
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import (QAbstractItemView, QFileDialog, QFrame, QHBoxLayout, QHeaderView,
                               QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar,
                               QPushButton, QTableView, QVBoxLayout, QWidget)

from . import core, updater
from .parsers import Belge
from .version import __version__

SARI = QColor("#FFF2CC")
SIRALA_ROLU = Qt.ItemDataRole.UserRole
GIRDI_FILTRESI = "Desteklenen dosyalar (*.rar *.zip *.7z *.pdf);;Tüm dosyalar (*.*)"

STIL = """
QMainWindow, QWidget#merkez { background: #F5F6F8; }
QLabel { color: #1F2933; }
QFrame#birakAlani {
    background: #FFFFFF; border: 2px dashed #9AA5B1; border-radius: 10px;
}
QFrame#birakAlani[surukle="true"] { background: #E8F1FB; border-color: #2E75B6; }
QLabel#birakBaslik { font-size: 16px; font-weight: 600; color: #364152; }
QLabel#birakAlt { color: #7B8794; }
QPushButton {
    background: #FFFFFF; border: 1px solid #C5CCD4; border-radius: 5px; padding: 6px 14px;
}
QPushButton:hover { background: #EEF2F6; }
QPushButton:disabled { color: #A0A8B0; background: #F0F2F4; }
QPushButton#birincil {
    background: #1F4E78; color: #FFFFFF; border: 1px solid #1F4E78; font-weight: 600;
    padding: 8px 20px;
}
QPushButton#birincil:hover { background: #2E75B6; }
QPushButton#birincil:disabled { background: #A9BBCB; border-color: #A9BBCB; color: #F5F6F8; }
QLineEdit { background: #FFFFFF; border: 1px solid #C5CCD4; border-radius: 5px; padding: 5px 8px; }
QTableView {
    background: #FFFFFF; alternate-background-color: #FAFBFC; gridline-color: #E4E7EB;
    border: 1px solid #D5DAE0; selection-background-color: #BBD7F0; selection-color: #000000;
}
QHeaderView::section {
    background: #1F4E78; color: #FFFFFF; padding: 6px 8px; border: none;
    border-right: 1px solid #2E75B6; font-weight: 600;
}
QProgressBar { border: 1px solid #C5CCD4; border-radius: 4px; background: #FFFFFF;
               text-align: center; height: 16px; }
QProgressBar::chunk { background: #2E75B6; border-radius: 3px; }
QStatusBar { color: #52606D; }
"""


def para_bicim(v: float | None) -> str:
    if v is None:
        return ""
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tarih_bicim(v: date | None) -> str:
    return v.strftime("%d.%m.%Y") if v else ""


class Okuyucu(QThread):
    """Girdileri arka planda işler."""
    ilerledi = Signal(int, int, str)
    bitti = Signal(list)
    hata = Signal(str)

    def __init__(self, girdiler: list[Path], parent=None):
        super().__init__(parent)
        self._girdiler = girdiler
        self._iptal = False

    def iptal_et(self) -> None:
        self._iptal = True

    def run(self) -> None:
        try:
            sonuc = core.isle(self._girdiler,
                              ilerleme=lambda i, n, ad: self.ilerledi.emit(i, n, ad),
                              iptal=lambda: self._iptal)
        except Exception as e:  # noqa: BLE001 - kullanıcıya gösterilecek
            self.hata.emit(str(e))
            return
        self.bitti.emit(sonuc)


class Guncelleyici(QThread):
    """Yeni sürümü denetler; varsa indirip doğrular (yalnız exe sürümünde)."""
    hazir = Signal(str, object)    # sürüm, açılmış yeni exe yolu
    elle = Signal(str)             # sürüm; klasör yazılamıyor → sayfadan indirilmeli

    def run(self) -> None:
        try:
            info = updater.check()
            if not info:
                return
            if not updater.can_self_update():
                self.elle.emit(info["version"])
                return
            self.hazir.emit(info["version"], updater.download(info))
        except Exception as e:  # noqa: BLE001 - internet yoksa sessizce geç
            updater.log(f"güncelleme denetimi başarısız: {e}")


class BelgeModeli(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._belgeler: list[Belge] = []

    @property
    def belgeler(self) -> list[Belge]:
        return self._belgeler

    def ekle(self, yeni: list[Belge]) -> None:
        if not yeni:
            return
        ilk = len(self._belgeler)
        self.beginInsertRows(QModelIndex(), ilk, ilk + len(yeni) - 1)
        self._belgeler.extend(yeni)
        self.endInsertRows()

    def temizle(self) -> None:
        self.beginResetModel()
        self._belgeler = []
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._belgeler)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(core.SUTUNLAR)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return core.SUTUNLAR[section][0]
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return int(Qt.AlignmentFlag.AlignCenter)
        elif role == Qt.ItemDataRole.DisplayRole:
            return section + 1
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        b = self._belgeler[index.row()]
        _, alan, tur, _ = core.SUTUNLAR[index.column()]
        deger = getattr(b, alan)
        if role == Qt.ItemDataRole.DisplayRole:
            if tur == "para":
                return para_bicim(deger)
            if tur == "tarih":
                return tarih_bicim(deger)
            return deger or ""
        if role == SIRALA_ROLU:
            if tur == "para":
                return float("-inf") if deger is None else float(deger)
            if tur == "tarih":
                return deger.toordinal() if deger else 0
            return (deger or "").casefold()
        if role == Qt.ItemDataRole.BackgroundRole:
            if alan in b.eksik or (alan == "kontrol" and deger):
                return SARI
            return None
        if role == Qt.ItemDataRole.ForegroundRole:
            return QColor("#000000") if (alan in b.eksik or (alan == "kontrol" and deger)) else None
        if role == Qt.ItemDataRole.ToolTipRole:
            return b.kontrol or None
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if tur == "para":
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if tur == "tarih":
                return int(Qt.AlignmentFlag.AlignCenter)
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None


class FiltreModeli(QSortFilterProxyModel):
    """Tüm sütunlarda metin araması; sıralama gerçek değerlere göre."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortRole(SIRALA_ROLU)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._aranan = ""

    def ara(self, metin: str) -> None:
        self._aranan = metin.casefold().strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, satir: int, ust: QModelIndex) -> bool:
        if not self._aranan:
            return True
        m = self.sourceModel()
        for c in range(m.columnCount()):
            v = m.index(satir, c, ust).data(Qt.ItemDataRole.DisplayRole)
            if v and self._aranan in str(v).casefold():
                return True
        return False


class BirakAlani(QFrame):
    """Sürükle-bırak alanı + dosya/klasör seçme düğmeleri."""
    girdilerAlindi = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("birakAlani")
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)

        baslik = QLabel("RAR, ZIP, klasör veya PDF'leri buraya sürükleyin")
        baslik.setObjectName("birakBaslik")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt = QLabel("ya da aşağıdaki düğmelerle seçin")
        alt.setObjectName("birakAlt")
        alt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dosya_btn = QPushButton("Dosya Seç…")
        self.klasor_btn = QPushButton("Klasör Seç…")
        self.dosya_btn.clicked.connect(self._dosya_sec)
        self.klasor_btn.clicked.connect(self._klasor_sec)
        dugmeler = QHBoxLayout()
        dugmeler.addStretch()
        dugmeler.addWidget(self.dosya_btn)
        dugmeler.addWidget(self.klasor_btn)
        dugmeler.addStretch()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)
        lay.addStretch()
        lay.addWidget(baslik)
        lay.addWidget(alt)
        lay.addLayout(dugmeler)
        lay.addStretch()

    def _isaretle(self, acik: bool) -> None:
        self.setProperty("surukle", acik)
        self.style().unpolish(self)
        self.style().polish(self)

    def _dosya_sec(self) -> None:
        yollar, _ = QFileDialog.getOpenFileNames(self, "Dosya Seç", "", GIRDI_FILTRESI)
        if yollar:
            self.girdilerAlindi.emit([Path(y) for y in yollar])

    def _klasor_sec(self) -> None:
        yol = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if yol:
            self.girdilerAlindi.emit([Path(yol)])

    def dragEnterEvent(self, e) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._isaretle(True)

    def dragLeaveEvent(self, e) -> None:
        self._isaretle(False)

    def dropEvent(self, e) -> None:
        self._isaretle(False)
        yollar = [Path(u.toLocalFile()) for u in e.mimeData().urls() if u.isLocalFile()]
        if yollar:
            e.acceptProposedAction()
            self.girdilerAlindi.emit(yollar)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"GİB Fatura Okuyucu {__version__}")
        self.resize(1300, 750)
        self.setStyleSheet(STIL)

        self._okuyucu: Okuyucu | None = None
        self._kuyruk: list[list[Path]] = []

        merkez = QWidget()
        merkez.setObjectName("merkez")
        self.setCentralWidget(merkez)
        ana = QVBoxLayout(merkez)
        ana.setContentsMargins(14, 14, 14, 10)
        ana.setSpacing(10)

        # --- bırakma alanı
        self.birak = BirakAlani()
        self.birak.girdilerAlindi.connect(self.girdileri_ekle)
        ana.addWidget(self.birak)

        # --- ilerleme satırı
        self.ilerleme_satiri = QWidget()
        il = QHBoxLayout(self.ilerleme_satiri)
        il.setContentsMargins(0, 0, 0, 0)
        self.durum_etiketi = QLabel("")
        self.ilerleme = QProgressBar()
        self.ilerleme.setTextVisible(False)
        self.iptal_btn = QPushButton("İptal")
        self.iptal_btn.clicked.connect(self.iptal_et)
        il.addWidget(self.durum_etiketi, 3)
        il.addWidget(self.ilerleme, 2)
        il.addWidget(self.iptal_btn)
        self.ilerleme_satiri.setVisible(False)
        ana.addWidget(self.ilerleme_satiri)

        # --- arama + temizle
        ust = QHBoxLayout()
        self.arama = QLineEdit()
        self.arama.setPlaceholderText("Ara… (tüm sütunlarda)")
        self.arama.setClearButtonEnabled(True)
        self.temizle_btn = QPushButton("Temizle")
        self.temizle_btn.clicked.connect(self.temizle)
        ust.addWidget(self.arama, 1)
        ust.addWidget(self.temizle_btn)
        ana.addLayout(ust)

        # --- tablo
        self.model = BelgeModeli(self)
        self.proxy = FiltreModeli(self)
        self.proxy.setSourceModel(self.model)
        self.arama.textChanged.connect(self.proxy.ara)
        self.tablo = QTableView()
        self.tablo.setModel(self.proxy)
        self.tablo.setSortingEnabled(True)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setWordWrap(False)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tablo.verticalHeader().setDefaultSectionSize(26)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tablo.horizontalHeader().setHighlightSections(False)
        for c, (_, _, _, gen) in enumerate(core.SUTUNLAR):
            self.tablo.setColumnWidth(c, int(gen * 8.5) + 16)
        self.tablo.doubleClicked.connect(self._satir_ac)
        ana.addWidget(self.tablo, 1)

        # --- alt çubuk
        alt = QHBoxLayout()
        self.ozet = QLabel("")
        self.ozet.setStyleSheet("font-weight: 600;")
        self.excel_btn = QPushButton("Excel'e Aktar…")
        self.excel_btn.setObjectName("birincil")
        self.excel_btn.clicked.connect(self.excel_aktar)
        alt.addWidget(self.ozet, 1)
        alt.addWidget(self.excel_btn)
        ana.addLayout(alt)

        self.statusBar().showMessage("Hazır. Çift tıklayarak bir belgenin PDF'ini açabilirsiniz.")
        self.model.rowsInserted.connect(self._ozet_guncelle)
        self.model.modelReset.connect(self._ozet_guncelle)
        self._ozet_guncelle()

        # --- otomatik güncelleme: indirilen sürüm kapanışta kurulur
        self._yeni_exe: Path | None = None
        self.guncelle_btn = QPushButton()
        self.guncelle_btn.setObjectName("birincil")
        self.guncelle_btn.hide()
        self.guncelle_btn.clicked.connect(self._yeniden_baslat)
        self.statusBar().addPermanentWidget(self.guncelle_btn)
        self._guncelleyici = Guncelleyici(self)
        self._guncelleyici.hazir.connect(self._guncelleme_hazir)
        self._guncelleyici.elle.connect(self._guncelleme_elle)
        if updater.is_frozen():
            updater.cleanup()
            QTimer.singleShot(2000, self._guncelleyici.start)

    # ------------------------------------------------------------ güncelleme
    def _guncelleme_hazir(self, surum: str, exe) -> None:
        self._yeni_exe = Path(exe)
        self.guncelle_btn.setText(f"Sürüm {surum} hazır · Yeniden başlat")
        self.guncelle_btn.setToolTip("Program kapanınca da kendiliğinden kurulur")
        self.guncelle_btn.show()

    def _guncelleme_elle(self, surum: str) -> None:
        self.guncelle_btn.setText(f"Sürüm {surum} çıktı · İndir")
        self.guncelle_btn.setToolTip("Kurulum klasörüne yazılamıyor; yeni sürümü sayfadan indirin")
        self.guncelle_btn.show()

    def _yeniden_baslat(self) -> None:
        if self._yeni_exe is None:
            QDesktopServices.openUrl(QUrl(updater.RELEASES_PAGE))
            return
        if self._okuyucu is not None:
            self.statusBar().showMessage("Okuma bitince yeniden başlatabilirsiniz.", 5000)
            return
        updater.launch_apply(self._yeni_exe, restart=True)
        self._yeni_exe = None
        self.close()

    # ------------------------------------------------------------ işleme
    def girdileri_ekle(self, yollar: list) -> None:
        """Sürükle-bırak, düğmeler ve komut satırı için ortak giriş noktası."""
        yollar = [Path(y) for y in yollar if Path(y).exists()]
        if not yollar:
            self.statusBar().showMessage("Geçerli bir dosya veya klasör bulunamadı.", 5000)
            return
        if self._okuyucu is not None:
            self._kuyruk.append(yollar)
            self.statusBar().showMessage("İşlem sürüyor; yeni girdiler sıraya alındı.", 5000)
            return
        self._baslat(yollar)

    def _baslat(self, yollar: list[Path]) -> None:
        self._okuyucu = Okuyucu(yollar, self)
        self._okuyucu.ilerledi.connect(self._ilerledi)
        self._okuyucu.bitti.connect(self._bitti)
        self._okuyucu.hata.connect(self._hata)
        self._okuyucu.finished.connect(self._is_parcacigi_bitti)
        self.ilerleme.setRange(0, 0)  # belirsiz: arşivler açılıyor
        self.durum_etiketi.setText("Dosyalar hazırlanıyor…")
        self.iptal_btn.setEnabled(True)
        self.ilerleme_satiri.setVisible(True)
        self._dugmeleri_ayarla(False)
        self._okuyucu.start()

    def _dugmeleri_ayarla(self, bosta: bool) -> None:
        for w in (self.birak.dosya_btn, self.birak.klasor_btn, self.temizle_btn, self.excel_btn):
            w.setEnabled(bosta)

    def _ilerledi(self, i: int, toplam: int, ad: str) -> None:
        if toplam <= 0:
            return
        self.ilerleme.setRange(0, toplam)
        self.ilerleme.setValue(i)
        self.durum_etiketi.setText(f"{i} / {toplam} · {ad}" if ad else f"{i} / {toplam}")

    def _bitti(self, belgeler: list) -> None:
        self.model.ekle(belgeler)
        iptal = self._okuyucu is not None and self._okuyucu._iptal
        self.statusBar().showMessage(
            f"{len(belgeler)} belge eklendi." + (" (İptal edildi)" if iptal else ""), 8000)
        if iptal:
            self._kuyruk.clear()

    def _hata(self, mesaj: str) -> None:
        self._kuyruk.clear()
        QMessageBox.critical(self, "Hata", f"Dosyalar işlenirken bir hata oluştu:\n\n{mesaj}")

    def _is_parcacigi_bitti(self) -> None:
        okuyucu, self._okuyucu = self._okuyucu, None
        if okuyucu is not None:
            okuyucu.deleteLater()
        if self._kuyruk:
            self._baslat(self._kuyruk.pop(0))
            return
        self.ilerleme_satiri.setVisible(False)
        self._dugmeleri_ayarla(True)

    def iptal_et(self) -> None:
        if self._okuyucu is not None:
            self._okuyucu.iptal_et()
            self.iptal_btn.setEnabled(False)
            self.durum_etiketi.setText("İptal ediliyor…")

    def bekle(self, ms: int = -1) -> bool:
        """Çalışan işlem bitene kadar bekler (test/kapanış için)."""
        o = self._okuyucu
        return o.wait(ms) if o is not None else True

    def temizle(self) -> None:
        if self.model.rowCount() == 0:
            return
        self.model.temizle()
        self.statusBar().showMessage("Liste temizlendi.", 5000)

    # ------------------------------------------------------------ tablo
    def _satir_ac(self, index: QModelIndex) -> None:
        b = self.model.belgeler[self.proxy.mapToSource(index).row()]
        if b.yol:
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(b.yol)):
                self.statusBar().showMessage("PDF açılamadı.", 6000)
        else:
            self.statusBar().showMessage(
                "Bu belge bir arşivden okundu; özgün PDF dosyası bulunmuyor.", 6000)

    def _ozet_guncelle(self, *_) -> None:
        bel = self.model.belgeler
        kontrol = sum(1 for b in bel if b.eksik or b.kontrol)
        toplam = sum(b.odenecek or 0.0 for b in bel)
        self.ozet.setText(f"{len(bel)} belge · {kontrol} kontrol gerekli · "
                          f"Ödenecek toplamı: {para_bicim(round(toplam, 2))} TL")

    # ------------------------------------------------------------ Excel
    def excel_yaz(self, hedef: Path) -> Path:
        """Diyalogsuz dışa aktarma (test edilebilir)."""
        return core.excel_yaz(self.model.belgeler, Path(hedef))

    def excel_aktar(self) -> None:
        if not self.model.belgeler:
            QMessageBox.information(self, "Excel'e Aktar", "Aktarılacak belge yok.")
            return
        belgelerim = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        varsayilan = str(Path(belgelerim) / f"faturalar_{date.today().isoformat()}.xlsx")
        yol, _ = QFileDialog.getSaveFileName(self, "Excel'e Aktar", varsayilan,
                                             "Excel çalışma kitabı (*.xlsx)")
        if not yol:
            return
        if not yol.lower().endswith(".xlsx"):
            yol += ".xlsx"
        try:
            hedef = self.excel_yaz(Path(yol))
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Hata",
                                 f"Excel dosyası yazılamadı (başka bir programda açık olabilir):\n\n{e}")
            return
        kutu = QMessageBox(QMessageBox.Icon.Information, "Excel'e Aktar",
                           f"{len(self.model.belgeler)} belge aktarıldı:\n{hedef}", parent=self)
        ac = kutu.addButton("Dosyayı Aç", QMessageBox.ButtonRole.AcceptRole)
        kutu.addButton("Kapat", QMessageBox.ButtonRole.RejectRole)
        kutu.exec()
        if kutu.clickedButton() is ac:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(hedef)))

    def closeEvent(self, e) -> None:
        self._kuyruk.clear()
        if self._okuyucu is not None:
            self._okuyucu.iptal_et()
            self._okuyucu.wait(15000)
        self._guncelleyici.wait(3000)
        if self._yeni_exe is not None:
            updater.launch_apply(self._yeni_exe, restart=False)
        super().closeEvent(e)

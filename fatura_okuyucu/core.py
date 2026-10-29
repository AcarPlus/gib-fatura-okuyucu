"""Girdileri (RAR/ZIP/7z, klasör, PDF) toplar, PDF'leri okur, Excel'e yazar."""
import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import date
from pathlib import Path
from typing import Callable, Iterable

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import kodlar, ubl
from .parsers import Belge, oku

ARSIV = {".rar", ".zip", ".7z"}
BELGE = {".pdf", ".xml"}


def _tar() -> str:
    sistem = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "tar.exe"
    return str(sistem) if sistem.exists() else "tar"


def arsiv_ac(path: Path, hedef: Path) -> None:
    hedef.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                # Windows Gezgini ile yapılmış zip'lerde Türkçe adlar cp857 kodlu
                if not info.flag_bits & 0x800:
                    try:
                        info.filename = info.filename.encode("cp437").decode("cp857")
                    except UnicodeError:
                        pass
                z.extract(info, hedef)
        return
    # RAR / 7z: Windows'un kendi tar.exe'si (libarchive) açabiliyor
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    res = subprocess.run([_tar(), "-xf", str(path), "-C", str(hedef)],
                         capture_output=True, text=True, creationflags=flags)
    if res.returncode != 0:
        raise RuntimeError(f"{path.name} açılamadı: {res.stderr.strip() or res.returncode}")


def pdfleri_topla(girdiler: Iterable[Path], calisma: Path) -> list[Path]:
    """Girdilerdeki tüm PDF ve XML'leri (iç içe arşivler dahil) bulur."""
    pdfler: list[Path] = []

    def tara(kok: Path, derinlik: int) -> None:
        for p in sorted(kok.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() in BELGE:
                pdfler.append(p)
            elif p.suffix.lower() in ARSIV and derinlik < 3:
                ic = calisma / f"{len(list(calisma.iterdir()))}_{p.stem}"
                arsiv_ac(p, ic)
                tara(ic, derinlik + 1)

    for g in map(Path, girdiler):
        if g.is_dir():
            tara(g, 0)
        elif g.suffix.lower() in BELGE:
            pdfler.append(g)
        elif g.suffix.lower() in ARSIV:
            ic = calisma / f"{len(list(calisma.iterdir()))}_{g.stem}"
            arsiv_ac(g, ic)
            tara(ic, 1)
    return pdfler


def isle(girdiler: Iterable[Path], ilerleme: Callable[[int, int, str], None] | None = None,
         iptal: Callable[[], bool] | None = None) -> list[Belge]:
    """Girdileri okuyup Belge listesi döndürür. ilerleme(i, toplam, dosya_adı)."""
    calisma = Path(tempfile.mkdtemp(prefix="fatura_okuyucu_"))
    try:
        pdfler = pdfleri_topla(girdiler, calisma)
        sonuc = []
        for i, p in enumerate(pdfler):
            if iptal and iptal():
                break
            if ilerleme:
                ilerleme(i, len(pdfler), p.name)
            okunan = ubl.oku(p) if p.suffix.lower() == ".xml" else [oku(p)]
            for b in okunan:
                b.yol = "" if calisma in p.parents else str(p)  # geçici dosya yolu saklanmaz
            sonuc += okunan
        if ilerleme:
            ilerleme(len(pdfler), len(pdfler), "")
        return tekillestir(sonuc)
    finally:
        shutil.rmtree(calisma, ignore_errors=True)


def tekillestir(belgeler: list[Belge]) -> list[Belge]:
    """Aynı ETTN'li XML'leri eler; XML'i olan faturanın PDF'ini de (XML daha ayrıntılı) çıkarır."""
    gorulen, out = set(), []
    for b in belgeler:
        if b.kaynak == "XML" and b.ettn:
            if b.ettn in gorulen:
                continue
            gorulen.add(b.ettn)
        out.append(b)
    xml_nolar = {b.fatura_no for b in out if b.kaynak == "XML" and b.fatura_no}
    for b in out:
        if b.kaynak == "XML" and b.fatura_no in {p.fatura_no for p in out if p.kaynak == "PDF"}:
            b.uyarilar.append("Bu faturanın PDF'i de vardı; XML'deki bilgiler kullanıldı")
    return [b for b in out if not (b.kaynak == "PDF" and b.fatura_no in xml_nolar)]


# ---------------------------------------------------------------- Excel

# (başlık, Belge alanı, tür, genişlik)
SUTUNLAR = [
    ("DOSYA NO", "dosya", "metin", 38),
    ("FATURA NO", "fatura_no", "metin", 22),
    ("ALICI VERGİ DAİRESİ", "alici_vd", "metin", 28),
    ("ALICI VKN/TCKN", "alici_vkn", "metin", 15),
    ("SATICI VKN/TCKN", "satici_vkn", "metin", 15),
    ("TARİH", "tarih", "tarih", 12),
    ("TUTAR", "tutar", "para", 15),
    ("KDV", "kdv", "para", 13),
    ("ÖDENECEK TUTAR", "odenecek", "para", 16),
    # ek istek: tevkifat ve toplam alanları
    ("TOPLAM İSKONTO", "iskonto", "para", 13),
    ("KDV TEVKİFAT", "tevkifat", "para", 13),
    ("TEVKİFATA TABİ İŞLEM TUTARI", "tevkifata_tabi_tutar", "para", 16),
    ("TEVKİFATA TABİ İŞLEM ÜZ. HES. KDV", "tevkifata_tabi_kdv", "para", 16),
    ("VERGİLER DAHİL TOPLAM", "vergiler_dahil", "para", 16),
    ("DİĞER VERGİLER", "diger_vergi", "para", 13),
    ("G.V. STOPAJ", "stopaj", "para", 13),
    ("SATICI UNVANI", "satici_unvan", "metin", 32),
    ("ALICI UNVANI", "alici_unvan", "metin", 32),
    ("BELGE TÜRÜ", "tur", "metin", 22),
    ("KONTROL NOTU", "kontrol", "metin", 60),
]
# e-Fatura XML'lerinden gelen ayrıntılar (yalnız XML varsa eklenir)
XML_SUTUNLAR = [
    ("ETTN", "ettn", "metin", 38),
    ("SENARYO", "senaryo", "metin", 16),
    ("FATURA TİPİ", "fatura_tipi", "metin", 14),
    ("PARA BİRİMİ", "para_birimi", "metin", 8),
    ("KUR", "kur", "kur", 10),
    ("SATICI VERGİ DAİRESİ", "satici_vd", "metin", 24),
    ("SATICI ADRESİ", "satici_adres", "metin", 40),
    ("ALICI ADRESİ", "alici_adres", "metin", 40),
    ("TEVKİFAT KODU", "tevkifat_kodu", "metin", 14),
    ("İSTİSNA / MUAFİYET", "istisna", "metin", 40),
    ("İRSALİYE NO", "irsaliye_no", "metin", 20),
    ("SİPARİŞ NO", "siparis_no", "metin", 16),
    ("VADE", "vade", "tarih", 12),
    ("ÖDEME", "odeme", "metin", 34),
    ("KALEM SAYISI", "kalem_sayisi", "sayi", 8),
    ("NOTLAR", "notlar", "metin", 50),
]
KALEM_SUTUNLAR = [
    ("FATURA NO", "fatura_no", "metin", 20), ("TARİH", "tarih", "tarih", 12),
    ("SATICI VKN/TCKN", "satici_vkn", "metin", 15), ("SATICI UNVANI", "satici_unvan", "metin", 30),
    ("ALICI VKN/TCKN", "alici_vkn", "metin", 15), ("SIRA", "sira", "metin", 6),
    ("MAL / HİZMET", "ad", "metin", 36), ("AÇIKLAMA", "aciklama", "metin", 24),
    ("SATICI ÜRÜN KODU", "satici_kodu", "metin", 16), ("ALICI ÜRÜN KODU", "alici_kodu", "metin", 16),
    ("MARKA", "marka", "metin", 12), ("MODEL", "model", "metin", 12), ("GTİP", "gtip", "metin", 14),
    ("MİKTAR", "miktar", "miktar", 10), ("BİRİM", "birim", "metin", 14), ("BİRİM KODU", "birim_kodu", "metin", 8),
    ("BİRİM FİYAT", "fiyat", "fiyat", 14), ("İSKONTO %", "iskonto_oran", "sayi", 9),
    ("İSKONTO", "iskonto", "para", 12), ("ARTTIRIM", "arttirim", "para", 12),
    ("MAL HİZMET TUTARI", "tutar", "para", 15), ("KDV %", "kdv_oran", "sayi", 7), ("KDV", "kdv", "para", 13),
    ("TEVKİFAT KODU", "tevkifat_kodu", "metin", 10), ("TEVKİFAT %", "tevkifat_oran", "sayi", 9),
    ("TEVKİFAT", "tevkifat", "para", 12), ("İSTİSNA", "istisna", "metin", 34),
    ("DİĞER VERGİLER", "diger_vergiler", "metin", 30), ("PARA BİRİMİ", "para", "metin", 8),
    ("NOT", "not", "metin", 30), ("DOSYA", "dosya", "metin", 30),
]
VERGI_SUTUNLAR = [
    ("FATURA NO", "fatura_no", "metin", 20), ("TARİH", "tarih", "tarih", 12),
    ("SATICI VKN/TCKN", "satici_vkn", "metin", 15), ("SATICI UNVANI", "satici_unvan", "metin", 30),
    ("VERGİ KODU", "kod", "metin", 9), ("VERGİ", "ad", "metin", 34), ("TÜR", "tur", "metin", 10),
    ("ORAN %", "oran", "sayi", 8), ("MATRAH", "matrah", "para", 15), ("VERGİ TUTARI", "tutar", "para", 15),
    ("İSTİSNA KODU", "istisna_kodu", "metin", 10), ("İSTİSNA SEBEBİ", "istisna", "metin", 44),
    ("PARA BİRİMİ", "para", "metin", 8),
]
BICIM = {"para": "#,##0.00", "tarih": "DD.MM.YYYY", "kur": "#,##0.0000", "sayi": "0.##",
         "miktar": "#,##0.###", "fiyat": "#,##0.00####", "metin": "@"}

_BASLIK = PatternFill("solid", fgColor="1F4E78")
_EK_BASLIK = PatternFill("solid", fgColor="2E75B6")
_BILGI_BASLIK = PatternFill("solid", fgColor="7F7F7F")
_SARI = PatternFill("solid", fgColor="FFF2CC")
_TOPLAM = PatternFill("solid", fgColor="DDEBF7")
_INCE = Side(style="thin", color="BFBFBF")


_XML_BASLIK = PatternFill("solid", fgColor="548235")


def _sayfa(ws, sutunlar, satirlar, renk=lambda c: _BASLIK, sari=lambda r, alan, v: False) -> None:
    """Başlık + satırlar + filtreyle çalışan toplam satırı. satirlar: (kaynak, alan -> değer) listesi."""
    for c, (baslik, _, _, gen) in enumerate(sutunlar, 1):
        h = ws.cell(1, c, baslik)
        h.font = Font(bold=True, color="FFFFFF")
        h.fill = renk(c)
        h.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(c)].width = gen
    ws.row_dimensions[1].height = 32
    for r, (kaynak, al) in enumerate(satirlar, 2):
        for c, (_, alan, tur, _) in enumerate(sutunlar, 1):
            v = al(alan)
            cell = ws.cell(r, c, None if v in ("", None) else v)
            cell.border = Border(bottom=_INCE)
            cell.number_format = BICIM[tur]  # metin "@": VKN'lerin baştaki sıfırı kaybolmasın
            if tur == "tarih":
                cell.alignment = Alignment(horizontal="center")
            if sari(kaynak, alan, v):
                cell.fill = _SARI
    son = len(satirlar) + 1
    ws.cell(son + 1, 1, "TOPLAM").font = Font(bold=True)
    for c, (_, _, tur, _) in enumerate(sutunlar, 1):
        cell = ws.cell(son + 1, c)
        cell.fill = _TOPLAM
        if tur == "para" and son >= 2:
            col = get_column_letter(c)
            cell.value = f"=SUBTOTAL(9,{col}2:{col}{son})"  # filtreyle birlikte çalışır
            cell.number_format = BICIM["para"]
            cell.font = Font(bold=True)
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(sutunlar))}{max(son, 2)}"
    ws.sheet_view.zoomScale = 90


def excel_yaz(belgeler: list[Belge], hedef: Path) -> Path:
    xml = [b for b in belgeler if b.kaynak == "XML"]
    sutunlar = SUTUNLAR + (XML_SUTUNLAR if xml else [])
    wb = Workbook()
    ws = wb.active
    ws.title = "Faturalar"
    n1, n2 = 9, 16
    _sayfa(ws, sutunlar, [(b, lambda a, b=b: getattr(b, a)) for b in belgeler],
           renk=lambda c: _BASLIK if c <= n1 else _EK_BASLIK if c <= n2 else
           _BILGI_BASLIK if c <= len(SUTUNLAR) else _XML_BASLIK,
           sari=lambda b, a, v: a in b.eksik or (a == "kontrol" and bool(v)))

    if xml:
        ust = lambda b, k: lambda a: k[a] if a in k else getattr(b, a, None)  # noqa: E731
        _sayfa(wb.create_sheet("Kalemler"), KALEM_SUTUNLAR,
               [(b, ust(b, k)) for b in xml for k in b.kalemler])
        vergiler = []
        for b in xml:
            for v in b.vergiler:
                v = {**v, "tur": "Tevkifat" if v["tevkifat"] else "Vergi", "para": b.para_birimi}
                vergiler.append((b, ust(b, v)))
        _sayfa(wb.create_sheet("Vergiler"), VERGI_SUTUNLAR, vergiler)

    a = wb.create_sheet("Açıklama")
    for satir in [
        ("GİB Fatura Okuyucu çıktısı", date.today().strftime("%d.%m.%Y")),
        ("Belge sayısı", len(belgeler)),
        ("  e-Fatura XML", len(xml)),
        ("Kontrol gereken belge", sum(1 for b in belgeler if b.eksik or b.kontrol)),
        (),
        ("Sarı hücre", "Bulunamadı ya da OCR ile okundu; PDF'le karşılaştırın"),
        ("TUTAR", "KDV hariç tutar (mal/hizmet toplamı, bilette toplam − KDV, makbuzda brüt ücret)"),
        ("ÖDENECEK TUTAR", "Tevkifat düşülmüş, ödenecek / tahsil edilen tutar"),
        ("Döviz faturaları", "Faturalar sayfasında TL karşılığı (belgedeki kurla); Kalemler/Vergiler belge parasında"),
        ("Başlık renkleri", "Koyu mavi: istenen sütunlar · açık mavi: tevkifat/toplam · gri: bilgi · yeşil: XML ayrıntısı"),
        ("Kod adları", f"GİB UBL-TR Kod Listeleri V{kodlar.SURUM} (ebelge.gib.gov.tr)"),
        ("Aynı fatura", "XML'i ve PDF'i birlikte verilen faturada XML kullanılır; aynı ETTN'li XML bir kez yazılır"),
    ]:
        a.append(satir)
    a["A1"].font = Font(bold=True, size=13)
    a.column_dimensions["A"].width = 24
    a.column_dimensions["B"].width = 90

    hedef = Path(hedef)
    wb.save(hedef)
    return hedef

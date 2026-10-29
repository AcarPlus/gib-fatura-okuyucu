"""PDF'ten fatura / bilet / makbuz bilgilerini çıkarır.

Her belge türü için ayrı bir ayrıştırıcı var; hiçbiri tanımazsa `genel` en azından
tarih ve tutarı bulmaya çalışır. Bulunamayan alanlar `eksik` kümesine yazılır, Excel'de
sarı boyanır.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from pypdf import PdfReader

from . import ocr

# 26.500,00 · 1.064.470,33 · 404.17 · 1512.00 (TCDD/Pegasus noktalı ondalık kullanıyor)
_AMT = r"(?<![\d.,])(?:\d{1,3}(?:\.\d{3})+,\d{2}|\d+,\d{2}|\d+\.\d{2})(?![\d])"
_CUR = r"\s*(TL|TRY|USD|EUR|GBP)?"
_DATE = re.compile(r"(?<!\d)(\d{2})[-./](\d{2})[-./](\d{4})(?!\d)|(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_ID = re.compile(r"\b(VKN|TCKN)\s*:?\s*(\d{10,11})\b")

# Excel'de "istenen" sütunlar; bunlar boşsa sarı + uyarı
ZORUNLU = ("fatura_no", "tarih", "satici_vkn", "tutar", "kdv", "odenecek")


@dataclass
class Belge:
    dosya: str
    tur: str = "Tanınmadı"
    fatura_no: str | None = None
    tarih: date | None = None
    satici_unvan: str | None = None
    satici_vkn: str | None = None
    alici_unvan: str | None = None
    alici_vd: str | None = None
    alici_vkn: str | None = None
    tutar: float | None = None            # KDV hariç (mal hizmet toplamı / matrah)
    iskonto: float | None = None
    kdv: float | None = None
    tevkifat: float | None = None
    tevkifata_tabi_tutar: float | None = None
    tevkifata_tabi_kdv: float | None = None
    diger_vergi: float | None = None      # konaklama vergisi, BSMV vb.
    stopaj: float | None = None
    vergiler_dahil: float | None = None
    odenecek: float | None = None
    para_birimi: str = "TL"
    ocr: bool = False
    yol: str = ""
    uyarilar: list[str] = field(default_factory=list)
    eksik: set[str] = field(default_factory=set)

    @property
    def kontrol(self) -> str:
        notlar = list(self.uyarilar)
        if self.ocr:
            notlar.insert(0, "Taranmış belge, OCR ile okundu; değerleri kontrol edin")
        return " · ".join(notlar)


# ---------------------------------------------------------------- yardımcılar

def para(s: str | None) -> float | None:
    if not s:
        return None
    s = s.replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def tarih(s: str | None) -> date | None:
    m = _DATE.search(s or "")
    if not m:
        return None
    try:
        if m.group(1):
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        return date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
    except ValueError:
        return None


def ara(pattern: str, text: str, group: int = 1, flags=re.I) -> str | None:
    m = re.search(pattern, text, flags)
    return m.group(group).strip() if m and m.group(group) else None


def tutar_ara(label: str, text: str) -> float | None:
    """`label` ardından gelen (araya parantez/iki nokta girebilir) ilk tutar."""
    return para(ara(label + r"(?:\s*\([^)]*\))*\s*:?\s*(" + _AMT + ")", text))


def satirlar(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", ln).strip() for ln in text.replace("\t", " ").splitlines() if ln.strip()]


def dosya_on_ek(dosya: str) -> str | None:
    """'GIB2026...-SATICI ADI' → 'GIB2026...' (dosya adının başındaki belge no)."""
    return dosya.split("-")[0].strip() or None


def dosya_unvan(dosya: str) -> str | None:
    parca = dosya.split("-", 1)
    return parca[1].strip(" -") if len(parca) == 2 and parca[1].strip(" -") else None


# ---------------------------------------------------------------- GİB e-Arşiv / e-Fatura

_TOPLAM_ETIKET = {
    "tutar": r"Mal\s*Hizmet\s*Toplam\s*Tutar[ıiIl]",
    "iskonto": r"Toplam\s*[İI]skonto",
    "tevkifat": r"Hesaplanan\s*KDV\s*Tevkifat",
    "kdv": r"Hesaplanan\s*KDV(?!\s*Tevkifat)",
    "tevkifata_tabi_tutar": r"Tevkifata\s*Tabi\s*[İI]şlem\s*Tutar[ıi]",
    "tevkifata_tabi_kdv": r"Tevkifata\s*Tabi\s*[İI]şlem\s*Üzerinden[^\d]*?KDV",
    "vergiler_dahil": r"Vergiler\s*Dahil\s*Toplam\s*Tutar[ıi]?",
    "odenecek": r"Ödenecek\s*Tutar[ıi]?",
}


def _toplamlar_metin(b: Belge, text: str) -> bool:
    flat = re.sub(r"\s+", " ", text)
    bulundu = False
    for alan, etiket in _TOPLAM_ETIKET.items():
        pat = etiket + r"(?:\s*\([^)]*\))*\s*:?\s*(" + _AMT + ")" + _CUR
        hits = [(para(m.group(1)), (m.group(2) or "TL").upper().replace("TRY", "TL"))
                for m in re.finditer(pat, flat, re.I)]
        if not hits:
            continue
        # Döviz faturasında aynı satırın bir de "(TL)" karşılığı var; TL olanı al
        tl = [v for v, c in hits if c == "TL"]
        if not tl:
            b.para_birimi = hits[0][1]
        vals = tl or [v for v, _ in hits]
        # Birden çok KDV oranı varsa (%1 + %20) toplanır
        setattr(b, alan, round(sum(vals), 2) if alan == "kdv" else vals[0])
        bulundu = True
    doviz = [m for m in re.finditer(r"Ödenecek\s*Tutar[ıi]?\s*(" + _AMT + r")\s*(USD|EUR|GBP)", flat, re.I)]
    if doviz:
        b.uyarilar.append(f"Döviz faturası: {doviz[0].group(1)} {doviz[0].group(2)} (TL karşılığı alındı)")
    for m in re.finditer(r"Hesaplanan\s+(?!KDV)([A-ZÇĞİÖŞÜ ]{4,}?VERG[İI]S[İI])\s*(?:\([^)]*\))?\s*:?\s*(" + _AMT + ")", flat):
        b.diger_vergi = round((b.diger_vergi or 0) + para(m.group(2)), 2)
        b.uyarilar.append(f"{m.group(1).strip()}: {m.group(2)}")
    return bulundu and b.odenecek is not None


def _toplamlar_ocr(b: Belge, lines: list[str]) -> None:
    """OCR'da etiketler bir sütunda, tutarlar sonra başka sütunda geliyor: sırayla eşle."""
    alanlar, son = [], None
    for i, ln in enumerate(lines):
        for alan, etiket in _TOPLAM_ETIKET.items():
            if re.match(etiket, ln, re.I) or (alan == "kdv" and re.fullmatch(r"Hesaplanan", ln, re.I)):
                alanlar.append(alan)
                son = i
                break
    if son is None:
        return
    tutarlar = [para(m.group(0)) for ln in lines[son + 1:]
                if re.fullmatch(r"(" + _AMT + r")\s*(TL)?", ln)
                for m in [re.search(_AMT, ln)]]
    if len(tutarlar) < len(alanlar):
        b.uyarilar.append("Toplamlar OCR'da eksik okundu")
        return
    for alan, v in zip(alanlar, tutarlar[-len(alanlar):]):
        setattr(b, alan, v)


def gib_fatura(b: Belge, text: str) -> None:
    b.tur = "e-Arşiv Fatura" if re.search(r"e-?Ar[sş]iv", text, re.I) else "e-Fatura"
    lines = satirlar(text)

    b.fatura_no = ara(r"Fatura\s*No\s*:\s*([A-Z0-9]{16})\b", text)
    if not b.fatura_no:  # OCR: 'GlB2026000000001' (I yerine l)
        m = re.search(r"\b([A-Za-z0-9]{3})(20\d{2}\d{9})\b", text)
        if m:
            b.fatura_no = m.group(1).replace("l", "I").upper() + m.group(2)
    tt = re.search(r"Fatura\s*Tarihi\s*:?", text, re.I) or re.search(r"\bTarih\s*:", text, re.I)
    b.tarih = tarih(text[tt.end():] if tt else text)

    # SAYIN'dan sonraki ilk VKN/TCKN alıcı, kalan ilk numara satıcı
    sayin = next((i for i, ln in enumerate(lines) if re.fullmatch(r"SAYIN", ln, re.I)), 0)
    kimlikler = [(i, m.group(2)) for i, ln in enumerate(lines) for m in [_ID.search(ln)] if m]
    alici = next(((i, n) for i, n in kimlikler if i > sayin), None)
    satici = next(((i, n) for i, n in kimlikler if alici is None or n != alici[1]), None)

    def vd(idx):
        for ln in lines[max(0, idx - 3):idx][::-1]:
            m = re.match(r"Vergi\s*Dairesi\s*:\s*(.*)", ln, re.I)
            if m:
                return m.group(1).strip() or None
        return None

    if alici:
        b.alici_vkn, b.alici_vd = alici[1], vd(alici[0])
        b.alici_unvan = lines[sayin + 1] if sayin + 1 < len(lines) else None
    if satici:
        b.satici_vkn = satici[1]
        # Satıcı bloğu önce geliyorsa ilk satır unvandır (OCR'da başta tarih/saat olabilir)
        if satici[0] < sayin:
            ilk = next((ln for ln in lines[:satici[0]] if not re.search(r"\d", ln)), None)
            if ilk and ilk.upper() != "SAYIN" and not any(re.match(e, ilk, re.I) for e in _TOPLAM_ETIKET.values()):
                b.satici_unvan = ilk

    if not _toplamlar_metin(b, text):
        _toplamlar_ocr(b, lines)


# ---------------------------------------------------------------- e-Serbest Meslek Makbuzu

def smm(b: Belge, text: str) -> None:
    b.tur = "e-Serbest Meslek Makbuzu"
    lines = satirlar(text)
    b.fatura_no = ara(r"Belge\s*Numaras[ıi]\s*:\s*(\S+)", text)
    b.tarih = tarih(ara(r"Düzenleme\s*Tarihi\s*:\s*(\S+)", text))
    i_duz = next((i for i, ln in enumerate(lines) if ln.upper() == "DÜZENLEYEN"), None)
    i_ali = next((i for i, ln in enumerate(lines) if "ALICI BİLGİLERİ" in ln.upper()), len(lines))
    if i_duz is not None:
        b.satici_unvan = lines[i_duz + 1]
    sat = _ID.search("\n".join(lines[:i_ali]))
    ali_text = "\n".join(lines[i_ali:])
    ali = _ID.search(ali_text)
    b.satici_vkn = sat.group(2) if sat else None
    b.alici_vkn = ali.group(2) if ali else None
    b.alici_vd = ara(r"Vergi\s*Dairesi\s*:\s*([^\n]+)", ali_text)
    b.alici_unvan = lines[i_ali + 1] if i_ali + 1 < len(lines) else None
    b.tutar = tutar_ara(r"Brüt\s*Ücret\s*Tutar[ıi]", text)
    b.kdv = tutar_ara(r"(?<!Tahsil Edilen )KDV\s*Tutar[ıi]", text)
    b.stopaj = tutar_ara(r"G\.?\s*V\.?\s*Stopaj\s*Tutar[ıi]", text)
    b.tevkifat = tutar_ara(r"KDV\s*Tevkifat[ıi]\s*Tutar[ıi]", text)
    b.odenecek = tutar_ara(r"Net\s*Tutar", text)
    if b.tutar is not None and b.kdv is not None:
        b.vergiler_dahil = round(b.tutar + b.kdv, 2)


# ---------------------------------------------------------------- biletler

def thy_ajet(b: Belge, text: str) -> None:
    b.tur = "Elektronik Uçak Bileti"
    ajet = re.search(r"AJet", text, re.I)
    b.satici_unvan = "AJet Hava Taşımacılığı A.Ş." if ajet else "Türk Hava Yolları A.O."
    b.satici_vkn = ara(r"Vergi\s*Dairesi\s*:\s*(\d{10})", text)
    if not b.satici_vkn:
        b.uyarilar.append("Satıcı VKN belgede yazmıyor")
    b.fatura_no = ara(r"\b(\d{13})\b", text)
    m = re.search(r"^(.*?)\(\s*(VKN|TCKN)\s*:\s*(\d+)\s*\)", text, re.M)
    if m and m.group(3).strip("0"):
        b.alici_unvan, b.alici_vkn = m.group(1).strip() or None, m.group(3)
        if m.group(2) == "TCKN":
            b.uyarilar.append("Bilet şahıs adına kesilmiş")
    b.tarih = tarih(text[text.find(b.fatura_no or "") + 13:] if b.fatura_no else text)
    tutarlar = [para(x) for x in re.findall("(" + _AMT + r")\s*TRY", text)]
    if len(tutarlar) >= 2:
        b.kdv, b.odenecek = tutarlar[0], tutarlar[1]
        b.vergiler_dahil = b.odenecek
        b.tutar = round(b.odenecek - b.kdv, 2)


def pegasus(b: Belge, text: str) -> None:
    b.tur = "Elektronik Uçak Bileti"
    b.satici_unvan = "Pegasus Hava Taşımacılığı A.Ş."
    vkn = ara(r"Mükellefler\s*V\.?\s*D\.?\s*:\s*([\d ]{10,14})", text)
    b.satici_vkn = vkn.replace(" ", "") if vkn else None
    b.fatura_no = ara(r"B[ıi]let\s*No\s*:\s*(\d+)", text)
    b.tarih = tarih(ara(r"\bTarih\s*:\s*(\S+)", text))
    b.odenecek = b.vergiler_dahil = tutar_ara(r"(?<!Ara )\bToplam", text)
    b.kdv = tutar_ara(r"KDV\s*Tutar[ıi]", text)
    if b.kdv is None and re.search(r"KDV'den\s*istisna", text, re.I):
        b.kdv = 0.0
        b.uyarilar.append("KDV'den istisna")
    b.alici_vd = ara(r"Vergi\s*Dairesi\s*:[ \t]*([^\n]+)", text)
    if b.odenecek is not None and b.kdv is not None:
        b.tutar = round(b.odenecek - b.kdv, 2)
    alici = ara(r"Vergi\s*Kimlik\s*Numaras[ıi]\s*:\s*(\d{10,11})", text)
    b.alici_vkn = alici
    if not alici:
        b.uyarilar.append("Bilette alıcı (mükellef) bilgisi yok")


def tcdd(b: Belge, text: str) -> None:
    b.tur = "Elektronik Tren Bileti"
    b.satici_unvan = "TCDD Taşımacılık A.Ş."
    b.satici_vkn = ara(r"VKN\s*:\s*(\d{10})", text)
    b.fatura_no = ara(r"Bilet\s*No\s*/\s*Ticket\s*No\s*:\s*(\S+)", text)
    b.alici_unvan = ara(r"Mükellef\s*/\s*Tax\s*Payer\s*:\s*([^\n]+)", text)
    b.alici_vkn = ara(r"TCKN/VKN\s*NO\s*:\s*(\d+)", text)
    b.tarih = tarih(ara(r"Düzenlenme\s*Tarihi\s*/\s*Issue\s*Date\s*:\s*(\S+)", text))
    b.tutar = tutar_ara(r"KDV'siz\s*Tutar\s*/\s*Subtotal", text)
    b.kdv = tutar_ara(r"KDV\s*/\s*VAT", text)
    b.odenecek = b.vergiler_dahil = tutar_ara(r"Toplam\s*Tutar\s*/\s*Total\s*Amount", text)


# ---------------------------------------------------------------- vergi / banka belgeleri

def vergi_alindisi(b: Belge, text: str) -> None:
    b.tur = "Vergi Ödeme Alındısı"
    b.fatura_no = ara(r"\b(\d{6}-[A-Za-z0-9]{12})\b", text)
    b.tarih = tarih(text)
    b.satici_unvan = ara(r"Vergi\s*Dairesi\s*\(Tax\s*Office\)\s*:\s*\d*\s*-?\s*([^\n]+)", text)
    b.satici_vkn = None
    b.alici_vkn = ara(r"Tax\s*Id\)\s*(\d{10,11})", text)
    b.odenecek = b.vergiler_dahil = b.tutar = para(ara(r"#\s*(" + _AMT + r")\s*#", text))
    b.kdv = 0.0
    tur = ara(r"\d{12,}-(\S[^\n]*?)\s+[\d.]+,", text)
    if tur:
        b.uyarilar.append(f"Vergi türü: {tur}")
    b.eksik.discard("satici_vkn")


def tahakkuk(b: Belge, text: str) -> None:
    b.tur = "Vergi Tahakkuk Fişi"
    b.fatura_no = ara(r"\b(\d{10}[A-Z0-9]{10})\b", text)
    b.tarih = tarih(text)
    b.alici_vkn = ara(r"VERG[İI]\s*K[İI]ML[İI]K\s*NUMARASI\s*(\d{10,11})", text)
    b.alici_unvan = ara(r"SOYADI\s*\(UNVANI\)\s*([^\n]+)", text)
    b.satici_unvan = ara(r"([^\n]*Vergi\s*Dairesi\s*Müdürlüğü)", text) or "Vergi Dairesi"
    b.odenecek = b.vergiler_dahil = tutar_ara(r"\bTOPLAM", text)
    vergi = ara(r"\n\d{4}\s+(" + _AMT + r")\s+" + "(" + _AMT + ")", text, group=2)
    matrah = ara(r"\n\d{4}\s+(" + _AMT + r")\s+", text)
    if matrah:
        b.uyarilar.append(f"Matrah {matrah}, ÖTV {vergi}" if vergi else f"Matrah {matrah}")
    b.tutar = b.odenecek  # ödenen vergi; KDV yok
    b.kdv = 0.0
    b.eksik.discard("satici_vkn")


def dekont(b: Belge, text: str) -> None:
    b.tur = "Banka Dekontu"
    b.satici_unvan = ara(r"Kurum\s*Ad[ıi]\s*\n?\s*([^\n]+?)\s+Saat", text) or ara(r"^([A-ZÇĞİÖŞÜ ]+BANK)", text, flags=re.M)
    b.fatura_no = ara(r"Fatura\s*No\s*:\s*(\d+)", text) or ara(r"İŞLEM\s*NO\s*(\d+)", text)
    b.tarih = tarih(ara(r"\bTarih\s*(\S+)", text))
    b.odenecek = b.vergiler_dahil = b.tutar = tutar_ara(r"Tutar(?![ıi])", text)
    b.uyarilar.append("Banka dekontu; KDV ve satıcı VKN belgede yok")
    b.eksik.discard("satici_vkn")


def police(b: Belge, text: str) -> None:
    b.tur = "Sigorta Poliçesi"
    m = re.search(r"^([A-ZÇĞİÖŞÜ ]+SİGORTA (?:A\.Ş\.|ANONİM ŞİRKETİ))", text, re.M)
    b.satici_unvan = m.group(1).strip() if m else None
    vkn = ara(r"Mükellefler\s*V\.?\s*D\.?\s*([\d\s]{10,20})", text)
    vkn = re.sub(r"\D", "", vkn or "")
    b.satici_vkn = vkn[:10] if len(vkn) >= 10 else None
    b.alici_vkn = ara(r"(?:Vergi\s*No|Vergi\s*No\s*:)\s*:?\s*\n?\s*(\d{10})", text)
    b.alici_unvan = ara(r"Sigortal[ıi]n[ıi]n\s*Adresi\s*\n\s*([^\n]+)", text)
    tanzim = re.search(r"Tanzim\s*Tarihi", text)
    b.tarih = tarih(text[tanzim.end():] if tanzim else text)
    b.tutar = tutar_ara(r"Net\s*Prim", text) or para(ara("(" + _AMT + r")\s*Net\s*Prim", text))
    bsmv = tutar_ara(r"Bsmv", text) or para(ara("(" + _AMT + r")\s*BSMV", text, flags=re.I))
    b.odenecek = (tutar_ara(r"Ödenecek\s*Prim", text) or tutar_ara(r"Toplam\s*Brüt\s*Prim", text)
                  or para(ara("(" + _AMT + r")\s*(?:Ödenecek|Toplam)\s*Prim", text)))
    if bsmv is not None:
        b.diger_vergi = bsmv
        b.uyarilar.append(f"BSMV {bsmv:.2f} (sigortada KDV yok)")
    if b.odenecek is None and b.tutar is not None and bsmv is not None:
        b.odenecek = round(b.tutar + bsmv, 2)
    b.vergiler_dahil = b.odenecek
    b.kdv = 0.0


# ---------------------------------------------------------------- tanınmayanlar

def genel(b: Belge, text: str) -> None:
    b.uyarilar.append("Belge türü tanınmadı, elle kontrol edin")
    b.tarih = tarih(text)
    no = ara(r"\bN[oOeº°]\.?\s*:?\s*(\d{5,})", text)
    b.fatura_no = no
    vergi = re.search(r"V\.?\s*D\.?\s*:?\s*(\d{10})", text)
    if vergi:
        b.satici_vkn = vergi.group(1)
    # Yalnız virgüllü tutarlar: telefon numarası parçaları tutar sanılmasın
    tutarlar = [para(x) for x in re.findall(r"(?<![\d.,])(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2}(?!\d)", text)]
    if tutarlar:
        b.odenecek = max(tutarlar)


TURLER = [
    (lambda t: re.search(r"Serbest\s*Meslek\s*Makbuzu", t, re.I), smm),
    (lambda t: "ÖDEME ALINDISI" in t.upper(), vergi_alindisi),
    (lambda t: "TAHAKKUK FİŞİ" in t, tahakkuk),
    (lambda t: re.search(r"PEGASUS", t), pegasus),
    (lambda t: "Bilet No / Ticket No" in t and "DEMİRYOLLARI" in t, tcdd),
    (lambda t: "Elektronik Bilet" in t and re.search(r"Belge No / Bilet No", t), thy_ajet),
    (lambda t: re.search(r"POL[İI]ÇE", t) and re.search(r"Prim", t, re.I), police),
    (lambda t: re.search(r"Fatura\s*No\s*:?", t) and re.search(r"Ödenecek|Mal\s*Hizmet", t), gib_fatura),
    (lambda t: re.search(r"DEKONT|HESAPTAN|KURUM\s*TAHS", t, re.I), dekont),
]


def metin(path: Path) -> tuple[str, bool]:
    """PDF metni; metin katmanı yoksa OCR. (metin, ocr_mu)"""
    try:
        text = "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    except Exception:
        text = ""
    if len(text.strip()) >= 40:
        return text, False
    try:
        return ocr.pdf_text(path), True
    except Exception:
        return "", True


def oku(path: Path, ad: str | None = None) -> Belge:
    path = Path(path)
    b = Belge(dosya=unicodedata.normalize("NFC", ad or path.stem), yol=str(path))
    text, b.ocr = metin(path)
    text = unicodedata.normalize("NFC", text)
    if not text.strip():
        b.uyarilar.append("PDF okunamadı (metin yok, OCR sonuç vermedi)")
        b.eksik.update(ZORUNLU)
        return b
    b.eksik.update(ZORUNLU)  # ayrıştırıcı muaf tutabilir (discard)
    for test, fn in TURLER:
        if test(text):
            fn(b, text)
            break
    else:
        genel(b, text)
    muaf = set(ZORUNLU) - b.eksik
    _tamamla(b)
    b.eksik = {a for a in ZORUNLU if getattr(b, a) is None and a not in muaf}
    if b.ocr:  # OCR'dan gelen her değer şüpheli: tüm sütunlar kontrol edilsin
        b.eksik |= {a for a in ZORUNLU if a not in muaf}
    return b


def _tamamla(b: Belge) -> None:
    """Eksikleri dosya adından doldur, tutarlılığı denetle."""
    on_ek = dosya_on_ek(b.dosya)
    if not b.fatura_no and on_ek and re.search(r"\d", on_ek):
        b.fatura_no = on_ek
        b.uyarilar.append("Belge no dosya adından alındı")
    if not b.satici_unvan:
        b.satici_unvan = dosya_unvan(b.dosya)
    if b.odenecek is None and b.vergiler_dahil is not None:
        b.odenecek = round(b.vergiler_dahil - (b.tevkifat or 0), 2)
    if b.vergiler_dahil is None and b.tutar is not None and b.kdv is not None:
        b.vergiler_dahil = round(b.tutar - (b.iskonto or 0) + b.kdv + (b.diger_vergi or 0), 2)
    if b.tur.startswith("e-") and b.tur != "e-Serbest Meslek Makbuzu":
        if None not in (b.tutar, b.kdv, b.vergiler_dahil):
            beklenen = b.tutar - (b.iskonto or 0) + b.kdv + (b.diger_vergi or 0)
            if abs(beklenen - b.vergiler_dahil) > 0.05:
                b.uyarilar.append(f"Tutar + KDV ({beklenen:,.2f}) ≠ vergiler dahil ({b.vergiler_dahil:,.2f})")
        if None not in (b.vergiler_dahil, b.odenecek):
            if abs(b.vergiler_dahil - (b.tevkifat or 0) - b.odenecek) > 0.05:
                b.uyarilar.append("Ödenecek tutar, vergiler dahil − tevkifat ile tutmuyor")

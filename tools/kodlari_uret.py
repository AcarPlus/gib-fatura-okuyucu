"""GİB "UBL-TR Kod Listeleri" PDF'inden fatura_okuyucu/kodlar.py üretir.

    .venv/Scripts/python tools/kodlari_uret.py "UBL-TR Kod Listeleri - V 1.43.pdf"

Kaynak: https://ebelge.gib.gov.tr/dosyalar/kilavuzlar/UBLTR_1.2.1_Kilavuzlar.zip (KOD LİSTELERİ klasörü).
GİB listeyi güncellediğinde yeni PDF ile tekrar çalıştırın.
"""
import pprint
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]

# (değişken adı, bölümün başladığı satır, bittiği satır)
BOLUMLER = [
    ("BIRIMLER", "ÖLÇÜ BİRİM KODLARI LİSTESİ", "1.6 PaymentMeansCode"),
    ("KISMI_ISTISNA", "KISMİ İSTİSNA KODLARI LİSTESİ", "TAM İSTİSNA KODLARI LİSTESİ"),
    ("TAM_ISTISNA", "TAM İSTİSNA KODLARI LİSTESİ", "DİĞER İŞLEM TÜRÜ KODLARI LİSTESİ"),
    ("DIGER_ISLEM", "DİĞER İŞLEM TÜRÜ KODLARI LİSTESİ", "ÖTV İSTİSNA KODLARI LİSTESİ"),
    ("OTV_ISTISNA", "ÖTV İSTİSNA KODLARI LİSTESİ", "KONAKLAMA VERGİSİ İSTİSNA KODLARI LİSTESİ"),
    ("KONAKLAMA_ISTISNA", "KONAKLAMA VERGİSİ İSTİSNA KODLARI LİSTESİ", "Diğer yandan eğer fatura"),
    ("OZEL_MATRAH", "ÖZEL MATRAH KODLARI LİSTESİ", "İHRAÇ KAYITLI SATIŞLAR İLE"),
    ("IHRAC_KAYITLI", "KABUL REJİMİ KAPSAMINDAKİ SATIŞ\nKODLARI LİSTESİ", "1.9 TaxTypeCode"),
    ("VERGILER", "VERGİ ADI KISALTMA", "Diğer yandan bu eleman"),
    ("TEVKIFATLAR", "KODU ADI ORANI", "1.10 Taşıma"),
]
GURULTU = re.compile(r"^(UBL-TR Kod Listeleri .*|Versiyon: .*|KODU ADI.*|\d+\s+https?://.*|https?://.*|B1\.xlsx|\d|\*.*|"
                     r"kullanılacaktır\.|.*doldurulmasına ilişkin.*|dışındaki, istisna.*|gereken durumlarda.*|"
                     r"Faaliyet ve sicil.*|\(yansıtma.*)$")


def bolum(metin: str, bas: str, son: str) -> list[str]:
    i = metin.index(bas) + len(bas)
    j = metin.index(son, i)
    return [ln.strip() for ln in metin[i:j].splitlines() if ln.strip() and not GURULTU.match(ln.strip())]


def kodlu(satirlar: list[str], desen=r"(\d{3,4})\*{0,2}") -> dict:
    out, son = {}, None
    for ln in satirlar:
        m = re.match(desen + r"(?:\s+(.*))?$", ln)
        if m:
            son = m.group(1)
            out[son] = (m.group(2) or "").strip()
        elif son:
            out[son] = (out[son] + " " + ln).strip()
    return {k: re.sub(r"\s+", " ", v) for k, v in out.items()}


def main(pdf: str) -> None:
    metin = "\n".join(p.extract_text() or "" for p in PdfReader(pdf).pages)
    metin = "\n".join(re.sub(r"\s+", " ", ln).strip() for ln in metin.splitlines())
    surum = re.search(r"Versiyon:\s*([\d.]+)", metin).group(1)
    tarih = re.search(r"UBL-TR Kod Listeleri (\w+ \d{4})", metin).group(1)
    sonuc = {}
    for ad, bas, son in BOLUMLER:
        sat = bolum(metin, bas, son)
        if ad == "BIRIMLER":
            sonuc[ad] = kodlu(sat, r"([A-Z0-9]{1,3})")
        elif ad == "VERGILER":
            sonuc[ad] = kodlu(sat, r"(\d{4})")
        elif ad == "TEVKIFATLAR":
            ham = kodlu(sat, r"(\d{3})")
            sonuc[ad] = {k: (re.sub(r"\s*\d+/10$", "", v).strip(), (re.search(r"(\d+/10)$", v) or [None, ""])[1])
                         for k, v in ham.items()}
        else:
            sonuc[ad] = kodlu(sat)
    satirlar = [f'"""GİB UBL-TR Kod Listeleri V{surum} ({tarih}) — tools/kodlari_uret.py ile üretildi, elle düzenlemeyin."""',
                f'SURUM = "{surum}"', ""]
    for ad, d in sonuc.items():
        satirlar.append(f"{ad} = " + pprint.pformat(d, width=120, sort_dicts=False))
        satirlar.append("")
        print(ad, len(d))
    (ROOT / "fatura_okuyucu" / "kodlar.py").write_text("\n".join(satirlar), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])

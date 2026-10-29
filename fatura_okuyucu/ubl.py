"""e-Fatura / e-Arşiv Fatura XML'lerini (UBL-TR 1.2.1) ayrıntılı okur.

Alan yolları GİB "UBL-TR Fatura" ve "UBL-TR Ortak Elemanlar" kılavuzlarına, kod adları
"UBL-TR Kod Listeleri"ne (kodlar.py) göre. GİB zarfı (StandardBusinessDocument) içindeki
birden çok fatura da okunur.
"""
from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from . import kodlar
from .parsers import Belge

INV = "{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice"
CAC = "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}"
CBC = "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}"
KOK = re.compile(rb"<(?:[A-Za-z_][\w.-]*:)?(Invoice|StandardBusinessDocument)\b")

SENARYOLAR = {"TEMELFATURA": "Temel Fatura", "TICARIFATURA": "Ticari Fatura", "EARSIVFATURA": "e-Arşiv Fatura",
              "IHRACAT": "İhracat", "YOLCUBERABERFATURA": "Yolcu Beraber", "OZELFATURA": "Özel Fatura",
              "KAMU": "Kamu", "HKS": "Hal Kayıt Sistemi", "STDKODFATURA": "Standart Kod", "ENERJI": "Enerji",
              "ILAC_TIBBICIHAZ": "İlaç ve Tıbbi Cihaz", "YATIRIMTESVIK": "Yatırım Teşvik", "IDIS": "İDİS"}
KDV = "0015"
STOPAJ = {"0003", "0011"}  # gelir / kurumlar vergisi stopajı


def _t(el, yol: str) -> str:
    if el is None:
        return ""
    v = el.find(yol)
    return (v.text or "").strip() if v is not None and v.text else ""


def _f(el, yol: str) -> float | None:
    s = _t(el, yol)
    try:
        return round(float(s), 2) if s else None
    except ValueError:
        return None


def _tarih(s: str) -> date | None:
    try:
        return date.fromisoformat(s[:10]) if s else None
    except ValueError:
        return None


def _taraf(p) -> dict:
    if p is None:
        return {}
    no = ""
    for pid in p.findall(f"{CAC}PartyIdentification/{CBC}ID"):
        if (pid.get("schemeID") or "").upper() in ("VKN", "TCKN"):
            no = (pid.text or "").strip()
            break
    ad = _t(p, f"{CAC}PartyName/{CBC}Name") or " ".join(
        x for x in (_t(p, f"{CAC}Person/{CBC}FirstName"), _t(p, f"{CAC}Person/{CBC}FamilyName")) if x)
    a = p.find(CAC + "PostalAddress")
    adres = ", ".join(x for x in (
        " ".join(y for y in (_t(a, CBC + "StreetName"), _t(a, CBC + "BuildingNumber")) if y),
        _t(a, CBC + "CitySubdivisionName"), _t(a, CBC + "CityName"), _t(a, f"{CAC}Country/{CBC}Name")) if x)
    return {"no": no or None, "ad": ad or None, "vd": _t(p, f"{CAC}PartyTaxScheme/{CAC}TaxScheme/{CBC}Name") or None,
            "adres": adres or None}


def vergi_adi(kod: str, xml_adi: str = "") -> str:
    if kod in kodlar.TEVKIFATLAR:
        return f"KDV Tevkifatı ({kodlar.TEVKIFATLAR[kod][1]})"
    return xml_adi or kodlar.VERGILER.get(kod, "") or f"Vergi {kod}"


def istisna_adi(kod: str) -> str:
    for liste in (kodlar.TAM_ISTISNA, kodlar.KISMI_ISTISNA, kodlar.IHRAC_KAYITLI, kodlar.OZEL_MATRAH,
                  kodlar.DIGER_ISLEM, kodlar.OTV_ISTISNA, kodlar.KONAKLAMA_ISTISNA):
        if kod in liste:
            return liste[kod]
    return ""


def _alt_vergiler(kap, tevkifat: bool) -> list[dict]:
    out = []
    for st in kap.findall(CAC + "TaxSubtotal"):
        kod = _t(st, f"{CAC}TaxCategory/{CAC}TaxScheme/{CBC}TaxTypeCode")
        ist_kod = _t(st, f"{CAC}TaxCategory/{CBC}TaxExemptionReasonCode")
        out.append({
            "kod": kod, "ad": vergi_adi(kod, "" if tevkifat else _t(st, f"{CAC}TaxCategory/{CAC}TaxScheme/{CBC}Name")),
            "tevkifat": tevkifat, "oran": _f(st, CBC + "Percent"),
            "matrah": _f(st, CBC + "TaxableAmount"), "tutar": _f(st, CBC + "TaxAmount"),
            "istisna_kodu": ist_kod or None,
            "istisna": _t(st, f"{CAC}TaxCategory/{CBC}TaxExemptionReason") or istisna_adi(ist_kod) or None,
        })
    return out


def _kalem(ln, para: str) -> dict:
    q = ln.find(CBC + "InvoicedQuantity")
    birim = q.get("unitCode", "") if q is not None else ""
    iskonto = arttirim = 0.0
    iskonto_oran = None
    for ac in ln.findall(CAC + "AllowanceCharge"):
        tutar = _f(ac, CBC + "Amount") or 0.0
        if _t(ac, CBC + "ChargeIndicator").lower() == "true":
            arttirim += tutar
        else:
            iskonto += tutar
            oran = _f(ac, CBC + "MultiplierFactorNumeric")
            iskonto_oran = round(oran * 100, 2) if oran is not None and oran <= 1 else oran
    vergiler = []
    for tt in ln.findall(CAC + "TaxTotal"):
        vergiler += _alt_vergiler(tt, False)
    for wt in ln.findall(CAC + "WithholdingTaxTotal"):
        vergiler += _alt_vergiler(wt, True)
    kdv = [v for v in vergiler if v["kod"] == KDV]
    tev = [v for v in vergiler if v["tevkifat"]]
    diger = [v for v in vergiler if v["kod"] != KDV and not v["tevkifat"]]
    item = ln.find(CAC + "Item")
    return {
        "sira": _t(ln, CBC + "ID"),
        "ad": _t(item, CBC + "Name"),
        "aciklama": _t(item, CBC + "Description") or None,
        "satici_kodu": _t(item, f"{CAC}SellersItemIdentification/{CBC}ID") or None,
        "alici_kodu": _t(item, f"{CAC}BuyersItemIdentification/{CBC}ID") or None,
        "marka": _t(item, CBC + "BrandName") or None,
        "model": _t(item, CBC + "ModelName") or None,
        "gtip": _t(ln, f"{CAC}Delivery/{CAC}Shipment/{CAC}GoodsItem/{CBC}RequiredCustomsID") or None,
        "miktar": _f(ln, CBC + "InvoicedQuantity"),
        "birim_kodu": birim,
        "birim": kodlar.BIRIMLER.get(birim, birim),
        "fiyat": _f(ln, f"{CAC}Price/{CBC}PriceAmount"),
        "iskonto_oran": iskonto_oran,
        "iskonto": round(iskonto, 2) or None,
        "arttirim": round(arttirim, 2) or None,
        "tutar": _f(ln, CBC + "LineExtensionAmount"),
        "kdv_oran": kdv[0]["oran"] if kdv else None,
        "kdv": round(sum(v["tutar"] or 0 for v in kdv), 2) if kdv else None,
        "istisna": "; ".join(f"{v['istisna_kodu']} {v['istisna'] or ''}".strip() for v in kdv if v["istisna_kodu"]) or None,
        "tevkifat_kodu": ", ".join(v["kod"] for v in tev) or None,
        "tevkifat_oran": tev[0]["oran"] if tev else None,
        "tevkifat": round(sum(v["tutar"] or 0 for v in tev), 2) if tev else None,
        "diger_vergiler": "; ".join(f"{v['ad']} {v['tutar']:.2f}" for v in diger if v["tutar"] is not None) or None,
        "not": "; ".join(n.text.strip() for n in ln.findall(CBC + "Note") if n.text and n.text.strip()) or None,
        "para": para,
    }


def fatura(el, dosya: str, yol: str) -> Belge:
    b = Belge(dosya=dosya, yol=yol, kaynak="XML")
    b.fatura_no = _t(el, CBC + "ID") or None
    b.ettn = _t(el, CBC + "UUID") or None
    b.tarih = _tarih(_t(el, CBC + "IssueDate"))
    profil = _t(el, CBC + "ProfileID")
    b.senaryo = SENARYOLAR.get(profil, profil) or None
    b.fatura_tipi = _t(el, CBC + "InvoiceTypeCode") or None
    b.tur = "e-Arşiv Fatura (XML)" if profil == "EARSIVFATURA" else "e-Fatura (XML)"
    para = _t(el, CBC + "DocumentCurrencyCode") or "TRY"
    b.para_birimi = "TL" if para in ("TRY", "TL") else para
    kur = _f(el, f"{CAC}PricingExchangeRate/{CBC}CalculationRate")
    b.kur = kur if b.para_birimi != "TL" else None

    sat = _taraf(el.find(f"{CAC}AccountingSupplierParty/{CAC}Party"))
    ali = _taraf(el.find(f"{CAC}AccountingCustomerParty/{CAC}Party"))
    b.satici_vkn, b.satici_unvan, b.satici_vd, b.satici_adres = sat.get("no"), sat.get("ad"), sat.get("vd"), sat.get("adres")
    b.alici_vkn, b.alici_unvan, b.alici_vd, b.alici_adres = ali.get("no"), ali.get("ad"), ali.get("vd"), ali.get("adres")

    lm = el.find(CAC + "LegalMonetaryTotal")
    tutar = _f(lm, CBC + "LineExtensionAmount")
    iskonto = _f(lm, CBC + "AllowanceTotalAmount")
    dahil = _f(lm, CBC + "TaxInclusiveAmount")
    odenecek = _f(lm, CBC + "PayableAmount")

    for tt in el.findall(CAC + "TaxTotal"):
        b.vergiler += _alt_vergiler(tt, False)
    for wt in el.findall(CAC + "WithholdingTaxTotal"):
        b.vergiler += _alt_vergiler(wt, True)
    kdv = [v for v in b.vergiler if v["kod"] == KDV]
    tev = [v for v in b.vergiler if v["tevkifat"]]
    stopaj = [v for v in b.vergiler if v["kod"] in STOPAJ]
    diger = [v for v in b.vergiler if v["kod"] not in STOPAJ | {KDV} and not v["tevkifat"]]
    toplam = lambda lst, alan="tutar": round(sum(v[alan] or 0 for v in lst), 2) if lst else None  # noqa: E731

    b.kalemler = [_kalem(ln, b.para_birimi) for ln in el.findall(CAC + "InvoiceLine")]
    b.kalem_sayisi = len(b.kalemler)

    # İstenen sütunlar TL; döviz faturasında kurla çevrilir (kalem ve vergi sayfaları belge parasında kalır)
    c = (lambda v: round(v * b.kur, 2) if v is not None else None) if b.kur else (lambda v: v)
    b.tutar, b.iskonto, b.vergiler_dahil, b.odenecek = c(tutar), c(iskonto), c(dahil), c(odenecek)
    b.kdv = c(toplam(kdv)) if kdv else 0.0
    b.tevkifat = c(toplam(tev))
    b.tevkifata_tabi_kdv = c(toplam(tev, "matrah"))
    tevkifatli = [k["tutar"] or 0 for k in b.kalemler if k["tevkifat_kodu"]]
    b.tevkifata_tabi_tutar = c(round(sum(tevkifatli), 2)) if tevkifatli else (c(tutar) if tev else None)
    b.stopaj = c(toplam(stopaj))
    b.diger_vergi = c(toplam(diger))
    b.tevkifat_kodu = ", ".join(dict.fromkeys(
        f"{v['kod']} {kodlar.TEVKIFATLAR.get(v['kod'], ('', ''))[1]}".strip() for v in tev)) or None
    b.istisna = "; ".join(dict.fromkeys(
        f"{v['istisna_kodu']} {v['istisna'] or ''}".strip() for v in b.vergiler if v["istisna_kodu"])) or None

    b.irsaliye_no = ", ".join(_t(r, CBC + "ID") for r in el.findall(CAC + "DespatchDocumentReference")) or None
    b.siparis_no = _t(el, f"{CAC}OrderReference/{CBC}ID") or None
    pm = el.find(CAC + "PaymentMeans")
    b.vade = _tarih(_t(pm, CBC + "PaymentDueDate"))
    iban = _t(pm, f"{CAC}PayeeFinancialAccount/{CBC}ID")
    b.odeme = " · ".join(x for x in (_t(pm, CBC + "PaymentMeansCode") and f"Ödeme kodu {_t(pm, CBC + 'PaymentMeansCode')}",
                                     iban and f"IBAN {iban}") if x) or None
    iade = [_t(r, f"{CAC}InvoiceDocumentReference/{CBC}ID") for r in el.findall(CAC + "BillingReference")]
    notlar = [n.text.strip() for n in el.findall(CBC + "Note") if n.text and n.text.strip()]
    if any(iade):
        notlar.insert(0, "İade edilen fatura: " + ", ".join(x for x in iade if x))
    b.notlar = " | ".join(notlar) or None

    if b.kur:
        b.uyarilar.append(f"Döviz faturası: {odenecek:,.2f} {b.para_birimi}, kur {b.kur} (TL karşılığı alındı)")
    haric = _f(lm, CBC + "TaxExclusiveAmount")
    if None not in (haric, dahil):
        beklenen = haric + sum(v["tutar"] or 0 for v in b.vergiler if not v["tevkifat"])
        if abs(beklenen - dahil) > 0.05 and not stopaj:
            b.uyarilar.append(f"Vergiler dahil toplam ({dahil:,.2f}) kalem/vergi toplamıyla ({beklenen:,.2f}) tutmuyor")
    b.eksik = {a for a in ("fatura_no", "tarih", "satici_vkn", "tutar", "odenecek") if getattr(b, a) is None}
    return b


def oku(path: Path, ad: str | None = None) -> list[Belge]:
    """XML dosyasındaki faturalar (UBL Invoice değilse boş liste)."""
    path = Path(path)
    try:
        with open(path, "rb") as f:
            if not KOK.search(f.read(4096)):
                return []
        kok = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return []
    faturalar = [kok] if kok.tag == INV else [e for e in kok.iter() if e.tag == INV]
    ad = unicodedata.normalize("NFC", ad or path.stem)
    return [fatura(el, ad if len(faturalar) == 1 else f"{ad} #{i + 1}", str(path))
            for i, el in enumerate(faturalar)]

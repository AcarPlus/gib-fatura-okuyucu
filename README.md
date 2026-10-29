# GİB Fatura Okuyucu

GİB e-Arşiv / e-Fatura PDF'lerini (ve yanlarındaki bilet, makbuz, poliçe gibi belgeleri) okuyup tek bir Excel tablosuna döken Windows masaüstü uygulaması.

RAR, ZIP, 7z arşivini, klasörü ya da PDF'leri pencereye sürükleyin; belgeler okunur, tabloda görünür, **Excel'e Aktar** ile kaydedilir. Belgeler bilgisayardan dışarı çıkmaz; internete yalnızca güncelleme denetimi için bağlanılır.

## Excel sütunları

| Sütun | Açıklama |
|---|---|
| DOSYA NO | PDF dosyasının adı |
| FATURA NO | Fatura / bilet / makbuz numarası |
| ALICI VERGİ DAİRESİ, ALICI VKN/TCKN | Faturanın kesildiği taraf |
| SATICI VKN/TCKN | Faturayı kesen |
| TARİH | Belge tarihi |
| TUTAR | KDV hariç tutar |
| KDV | Hesaplanan KDV (birden çok oran varsa toplamı) |
| ÖDENECEK TUTAR | Tevkifat düşülmüş ödenecek tutar |
| Ek sütunlar | Toplam iskonto, KDV tevkifat, tevkifata tabi işlem tutarı ve KDV'si, vergiler dahil toplam, diğer vergiler (konaklama, BSMV), G.V. stopajı |
| Bilgi sütunları | Satıcı ve alıcı unvanı, belge türü, kontrol notu |

Bulunamayan ya da OCR ile okunan hücreler **sarı** boyanır; *Kontrol Notu* nedenini yazar (döviz faturası, tutar tutarsızlığı, KDV istisnası vb.). En alttaki toplam satırı filtreyle birlikte çalışır.

## Tanınan belgeler

- GİB e-Arşiv / e-Fatura (tevkifatlı ve döviz faturaları dahil)
- e-Serbest Meslek Makbuzu
- THY, AJet, Pegasus elektronik uçak biletleri; TCDD tren bileti
- İnternet vergi dairesi ödeme alındısı, vergi tahakkuk fişi, banka dekontu
- Sigorta poliçesi (net prim, BSMV, ödenecek prim)
- Taranmış (metinsiz) PDF'ler Windows'un kendi OCR'ı ile okunur (Türkçe dil paketi gerekir; Windows 10/11'de genelde kuruludur)

Tanınmayan belgelerde tarih ve tutar bulunmaya çalışılır, satır sarı işaretlenir.

## Kurulum

[Son sürümü](../../releases/latest) indirin (`FaturaOkuyucu-windows.zip`), bir klasöre açın ve `FaturaOkuyucu.exe`'yi çalıştırın. Klasör yazılabilir bir yerde olmalı (ör. `%LOCALAPPDATA%\Programs\FaturaOkuyucu`); yeni sürümler arka planda indirilir ve program kapanınca kurulur.

Exe imzalı olmadığından Windows SmartScreen ilk açılışta uyarı verebilir: *Ek bilgi → Yine de çalıştır*.

Pencere açmadan da kullanılabilir:

```
FaturaOkuyucu.exe --excel cikti.xlsx faturalar.rar [klasör ...]
```

## Geliştirme

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt pyinstaller==6.22.3
.venv\Scripts\python main.py
.venv\Scripts\python build.py            # exe + zip + .sha256
.venv\Scripts\python build.py --release  # + GitHub release (sürüm: fatura_okuyucu/version.py)
```

Güncelleyici release'teki `FaturaOkuyucu-windows.zip` ve `FaturaOkuyucu-windows.zip.sha256` adlarına bakar; bu adlar değişmemeli.

"""GİB UBL-TR Kod Listeleri V1.43 (Temmuz 2026) — tools/kodlari_uret.py ile üretildi, elle düzenlemeyin."""
SURUM = "1.43"

BIRIMLER = {'B32': 'KG-METRE KARE',
 'C62': 'ADET(UNIT)',
 'CCT': 'TON BAŞINA TAŞIMA KAPASİTESİ',
 'PR': 'ÇİFT',
 'D30': 'BRÜT KALORİ DEĞERİ',
 'D40': 'BİN LİTRE',
 'GFI': 'FISSILE İZOTOP GRAMI',
 'GRM': 'GRAM',
 'GT': 'GROSS TON',
 'CEN': 'YÜZ ADET',
 'KPO': 'KİLOGRAM POTASYUM OKSİT',
 'MND': 'KURUTULMUŞ NET AĞIRLIKLI KİLOGRAMI',
 '3I': 'KİLOGRAM-ADET',
 'KFO': 'DİFOSFOR PENTAOKSİT KİLOGRAMI',
 'KGM': 'KİLOGRAM',
 'KHY': 'HİDROJEN PEROKSİT KİLOGRAMI',
 'KMA': 'METİL AMİNLERİN KİLOGRAMI',
 'KNI': 'AZOTUN KİLOGRAMI',
 'KPH': 'KİLOGRAM POTASYUM HİDROKSİT',
 'KSD': '%90 KURU ÜRÜN KİLOGRAMI',
 'KSH': 'SODYUM HİDROKSİT KİLOGRAMI',
 'KUR': 'URANYUM KİLOGRAMI',
 'D32': 'TERAWATT SAAT',
 'GWH': 'GİGAWATT SAAT',
 'MWH': 'MEGAWATT SAAT (1000 kW.h)',
 'KWH': 'KİLOWATT SAAT',
 'KWT': 'KİLOWATT',
 'LPA': 'SAF ALKOL LİTRESİ',
 'LTR': 'LİTRE',
 'MTK': 'METRE KARE',
 'DMK': 'DESİMETRE KARE',
 'MTQ': 'METRE KÜP',
 'MTR': 'METRE',
 'NCL': 'HÜCRE ADEDİ',
 'CTM': 'KARAT',
 'SM3': 'STANDART METREKÜP',
 'R9': 'BİN METRE KÜP',
 'SET': 'SET',
 'T3': 'BİN ADET'}

KISMI_ISTISNA = {'201': '17/1 Kültür ve Eğitim Amacı Taşıyan İşlemler',
 '202': '17/2-a Sağlık, Çevre Ve Sosyal Yardım Amaçlı İşlemler',
 '204': '17/2-c Yabancı Diplomatik Organ Ve Hayır Kurumlarının Yapacakları Bağışlarla İlgili Mal Ve Hizmet Alışları',
 '205': '17/2-d Taşınmaz Kültür Varlıklarına İlişkin Teslimler ve Mimarlık Hizmetleri',
 '206': '17/2-e Mesleki Kuruluşların İşlemleri',
 '207': '17/3 Askeri Fabrika, Tersane ve Atölyelerin İşlemleri',
 '208': '17/4-c Birleşme, Devir, Dönüşüm ve Bölünme İşlemleri',
 '209': '17/4-e Banka ve Sigorta Muameleleri Vergisi Kapsamına Giren İşlemler',
 '211': '17/4-h Zirai Amaçlı Su Teslimleri İle Köy Tüzel Kişiliklerince Yapılan İçme Suyu teslimleri',
 '212': '17/4-ı Serbest Bölgelerde Verilen Hizmetler',
 '213': '17/4-j Boru Hattı İle Yapılan Petrol Ve Gaz Taşımacılığı',
 '214': '17/4-k Organize Sanayi Bölgelerindeki Arsa ve İşyeri Teslimleri İle Konut Yapı Kooperatiflerinin Üyelerine '
        'Konut Teslimleri',
 '215': '17/4-l Varlık Yönetim Şirketlerinin İşlemleri',
 '216': '17/4-m Tasarruf Mevduatı Sigorta Fonunun İşlemleri',
 '217': '17/4-n Basın-Yayın ve Enformasyon Genel Müdürlüğüne Verilen Haber Hizmetleri',
 '218': 'KDV 17/4 -o md. Gümrük Antrepoları, Geçici Depolama Yerleri ile Gümrüklü Sahalarda Vergisiz Satış Yapılan '
        'İşyeri, Depo ve Ardiye Gibi Bağımsız Birimlerin Kiralanması',
 '219': 'Hazine , Toplu Konut İdaresi Başkanlığı, Belediyeler, il özel idareleri ve yatırım izleme ve koordinasyon '
        'başkanlıklarının İşlemleri',
 '220': '17/4-r İki Tam Yıl Süreyle Sahip Olunan Taşınmaz ve İştirak Hisseleri ile 15/7/2023 tarihinden önce '
        'kurumların aktifinde kayıtlı Taşınmaz satışı',
 '221': 'Geçici 15 Konut Yapı Kooperatifleri, Belediyeler ve Sosyal Güvenlik Kuruluşlarına Verilen İnşaat Taahhüt '
        'Hizmeti',
 '223': 'Geçici 20/1 Teknoloji Geliştirme Bölgelerinde Yapılan İşlemler',
 '225': 'Geçici 23 Milli Eğitim Bakanlığına Yapılan Bilgisayar Bağışları İle İlgili Teslimler',
 '226': '17/2-b Özel Okulları, Üniversite ve Yüksekokullar Tarafından Verilen Bedelsiz Eğitim Ve Öğretim Hizmetleri',
 '227': '17/2-b Kanunların Gösterdiği Gerek Üzerine Bedelsiz Olarak Yapılan Teslim ve Hizmetler',
 '228': '17/2-b Kanunun (17/1) Maddesinde Sayılan Kurum ve Kuruluşlara Bedelsiz Olarak Yapılan Teslimler',
 '229': 'Gıda Bankacılığı Faaliyetinde Bulunan Darülacezeye, Dernek ve Vakıflara Bağışlanan, Gıda, Temizlik, Giyecek '
        've Yakacak Maddeleri',
 '230': '17/4-g Külçe Altın, Külçe Gümüş Ve Kiymetli Taşlarin Teslimi',
 '231': '17/4-g Metal Plastik, Lastik, Kauçuk, Kağit, Cam Hurda Ve Atıkların Teslimi',
 '232': '17/4-g Döviz, Para, Damga Pulu, Değerli Kağıtlar, Hisse Senedi ve Tahvil Teslimleri',
 '233': '2942 Sayılı Kamulaştırma Kanunu Kaps amında Taşınmazların Kamulaştırmayı Yapan Devlet ve Kamu Tüzel '
        'Kişilerine Devri',
 '234': '17/4-ş Konut Finansmanı Amacıyla Teminat Gösterilen ve İpotek Konulan Konutların Teslimi',
 '235': '16/1-c Transit ve Gümrük Antrepo Rejimleri İle Geçici Depolama ve Serbest Böl ge Hükümlerinin Uygulandığiı '
        'Malların Teslimi',
 '236': '19/2 Usulüne Göre Yürürlüğe Girmiş Uluslararası Anlaşmalar Kapsamındaki İstisnalar (İade Hakkı Tanınmayan)',
 '237': '17/4-t 5300 Sayılı Kanuna Göre Düzenlenen Ürün Senetlerinin İhtisas/Ticaret Borsaları Aracılığıyla İlk '
        'Teslimlerinden Sonraki Teslim',
 '238': '17/4-u Varlıkların Varlık Kiralama Şirketlerine Devri İle Bu Varlıkların Varlık Kiralama Şirketlerince '
        'Kiralanması ve Devralınan Kuruma Devri',
 '239': '17/4-y Taşınmazların Finansal Kiralama Şirketlerine Devri, Finan sal Kiralama Şirketi Tarafından Devredene '
        'Kiralanması ve Devri',
 '240': '17/4-z Patentli Veya Faydalı Model Belgeli Buluşa İlişkin Gayri Maddi Hakların Kiralanması, Devri ve Satışı',
 '241': 'TürkAkım Gaz Boru Hattı Projesine İlişkin Anlaşmanın (9/b) Maddesinde Yer A lan Hizmetler',
 '242': 'KDV 17/4 -ö md. Gümrük Antrepoları, Geçici Depolama Yerleri ile Gümrüklü Sahalarda, İthalat ve İhracat '
        'İşlemlerine konu mallar ile transit rejim kapsamında işlem gören mallar için verilen ardiye, depolama ve '
        'terminal hizmetleri',
 '250': 'Diğerleri'}

TAM_ISTISNA = {'301': '11/1-a Mal İhracatı',
 '302': '11/1-a Hizmet İhracatı',
 '303': '11/1-a Roaming Hizmetleri',
 '304': '13/a Deniz Hava ve Demiryolu Taşıma Araçlarının Teslimi İle İnşa, Tadil, Bakım ve Onarımları',
 '305': '13/b Deniz ve Hava Taş ıma Araçları İçin Liman Ve Hava Meydanlarında Yapılan Hizmetler',
 '306': '13/c Petrol Aramaları ve Petrol Boru Hatlarının İnşa ve Modernizasyonuna İlişkin Yapılan Teslim ve Hizmetler',
 '307': '13/c Maden Arama, Altın, Gümüş ve Platin Madenleri İçin İşletme, Zenginle ştirme Ve Rafinaj Faaliyetlerine '
        'İlişkin Teslim Ve Hizmetler[KDVGUT-(II/8-4)]',
 '308': '13/d Teşvikli Yatırım Mallarının Teslimi',
 '309': '13/e Liman Ve Hava Meydanlarının İnşası, Yenilenmesi Ve Genişletilmesi',
 '310': '13/f Ulusal Güvenlik Amaçlı Teslim ve Hizmetler',
 '311': '14/1 Uluslararası Taşımacılık',
 '312': '15/a Diplomatik Organ Ve Misyonlara Yapılan Teslim ve Hizmetler',
 '313': '15/b Uluslararası Kuruluşlara Yapılan Teslim ve Hizmetler',
 '314': '19/2 Usulüne Göre Yürürlüğe Girmiş Uluslar Arası Anlaşmalar Kapsamındaki İstisnalar',
 '315': '14/3 İhraç Konusu Eşyayı Taşıyan Kamyon, Çekici ve Yarı Romorklara Yapılan Motorin Teslimleri',
 '316': '11/1-a Serbest Bölgelerdeki Müşteriler İçin Yapılan Fason Hizmetler',
 '317': '17/4-s Engellilerin Eğitimleri, Meslekleri ve Günlük Yaşamlarına İlişkin Araç -Gereç ve Bilgisayar '
        'Programları',
 '318': 'Geçici 29 3996 Sayılı Kanuna Göre Yap -İşlet-Devret Modeli Çerçevesinde Gerçekleştirilecek Projeler, 3359 '
        'Sayılı Kanuna Göre Kiralama Karşılığı Yaptırılan Sağlık Tesislerine İlişkin Projeler ve 652 Sayılı Kanun '
        'Hükmünde Kara rnameye Göre Kiralama Karşılığı Yaptırılan Eğitim Öğretim Tesislerine İlişkin Projelere İlişkin '
        'Teslim ve Hizmetler',
 '319': '13/g Başbakanlık Merkez Teşkilatına Yapılan Araç Teslimleri',
 '320': "Geçici 16 (6111 sayılı K.) İSMEP Kapsamında İstanbul İl Özel İdaresi'n e Bağlı Olarak Faaliyet Gösteren "
        '"İstanbul Proje Koordinasyon Birimi"ne Yapılacak Teslim ve Hizmetler',
 '321': 'Geçici 26 Birleşmiş Milletler (BM) ile Kuzey Atlantik Antlaşması Teşkilatı (NATO) Temsilcilikleri ve Bu '
        'Teşkilatlara Bağlı Program, Fon ve Özel İhtis as Kuruluşları ile İktisadi İşbirliği ve Kalkınma Teşkilatına '
        '(OECD) Resmi Kullanımları İçin Yapılacak Mal Teslimi ve Hizmet İfaları, Bunların Sosyal ve Ekonomik Yardım '
        'Amacıyla Bedelsiz Olarak Yapacakları Mal Teslimi ve Hizmet İfaları İle İlgili Bunlara Y apılan Mal Teslimi ve '
        'Hizmet İfaları',
 '322': "11/1-a Türkiye'de İkamet Etmeyenlere Özel Fatura ile Yapılan Teslimler (Bavul Ticareti)",
 '323': '13/ğ 5300 Sayılı Kanuna Göre Düzenlenen Ürün Senetlerinin İhtisas/Ticaret Borsaları Aracılığıyla İlk Teslimi',
 '324': '13/h Tü rkiye Kızılay Derneğine Yapılan Teslim ve Hizmetler ile Türkiye Kızılay Derneğinin Teslim ve '
        'Hizmetleri',
 '325': '13/ı Yem Teslimleri',
 '326': '13/ı Gıda, Tarım ve Hayvancılık Bakanlığı Tarafından Tescil Edilmiş Gübrelerin Teslimi',
 '327': '13/ı Gıda, Tarım ve Hayvancılı k Bakanlığı Tarafından Tescil Edilmiş Gübrelerin İçeriğinde Bulunan '
        'Hammaddelerin Gübre Üreticilerine Teslimi',
 '328': '13/i Konut veya İşyeri Teslimleri',
 '329': 'Eğitimde Fırsatları Artırma ve T eknolojiyi İyileştirme Hareketi (FATİH) projesi Kapsamında Milli Eğitim '
        'Bakanlığına Yapılacak Mal Teslimi ve Hizmet İfası',
 '330': 'KDV 13/j md. Organize Sanayi Bölgeleri ile Küçük Sanayi Sitelerinin İnşasına İlişkin Teslim ve Hizmetler',
 '331': 'KDV 13/m md. Ar -Ge, Yenilik ve Tasarım Faaliyetlerinde Ku llanılmak Üzere Yapılan Yeni Makina ve Teçhizat '
        'Teslimlerinde İstisna',
 '332': 'KDV Geçici 39. Md. İmalat Sanayiinde Kullanılmak Üzere Yapılan Yeni Makina ve Teçhizat Teslimlerinde İstisna',
 '333': 'KDV 13/k md. Kapsamında Genel ve Özel Bütçeli Kamu İdarelerine, İ l Özel İdarelerine, Belediyelere ve Köylere '
        'bağışlanan Tesislerin İnşasına İlişkin İstisna',
 '334': 'KDV 13/l md. Kapsamında Yabancılara Verilen Sağlık Hizmetlerinde İstisna',
 '335': 'KDV 13/n Basılı Kitap ve Süreli Yayınların Teslimleri',
 '336': 'Geçici 46 UEFA Müsabakaları Kapsamında Yapılacak Teslim ve Hizmetler',
 '337': 'Türk Akım Gaz Boru Hattı Projesine İlişkin Anlaşmanın (9/h) Maddesi Kapsamındaki Gaz Taşıma Hizmetleri',
 '338': 'İmalatçıların Mal İhracatları',
 '339': 'İmalat Sanayii ile Turizme Yönelik Yatırım Teşvik Belgesi K apsamındaki İnşaat İşlerine İlişkin Teslim ve '
        'Hizmetler',
 '340': 'Elektrik Motorlu Taşıt Araçlarının Geliştirilmesine Yönelik Mühendislik Hizmetleri',
 '341': 'Afetzedelere Bağışlanacak Konutların İnşasına İlişkin İstisna',
 '342': 'Genel Bütçeli Kamu İdarelerine Bağışlanacak Taşınmazların İnşasına İlişkin İstisna',
 '343': 'Genel Bütçeli Kamu İdarelerine Bağışlanacak Konutların Yabancı Devlet Kurum ve Kuruluşlarına Teslimine '
        'İlişkin İstisna',
 '344': '13/o Milli Savunma ve İç Güvenlik İhtiyaçlarında Kullanılmak Üzere Taşıt Teslimi',
 '350': 'Diğerleri',
 '351': 'KDV - İstisna Olmayan Diğer'}

DIGER_ISLEM = {'555': 'KDV Oran Kontrolüne Tabi Olmayan Satışlar'}

OTV_ISTISNA = {'101': 'İhracat İstisnası',
 '102': 'Diplomatik İstisna',
 '103': 'Askeri Amaçlı İstisna',
 '104': 'Petrol Arama Faaliyetlerinde Bulunanlara Yapılan Teslimler',
 '105': 'Uluslararası Anlaşmadan Doğan İstisna',
 '106': 'Diğer İstisnalar',
 '107': '7/a Maddesi Kapsamında Yapılan Teslimler',
 '108': 'Geçici 5. Madde Kapsamında Yapılan Teslimler',
 '151': 'ÖTV - İstisna Olmayan Diğer'}

KONAKLAMA_ISTISNA = {'001': 'Diplomatik İstisna'}

OZEL_MATRAH = {'801': 'Milli Piyango, Spor Toto vb. Oyunlar',
 '802': 'At Yarışları ve Diğer Müşterek Bahis ve Talih Oyunları',
 '803': 'Profesyonel Sanatçıların Yer Aldığı Gösteriler, Konserler, Profesyonel Sporcuların Katıldığı Sportif '
        'Faaliyetler, Maçlar, Yarışlar ve Yarışmalar',
 '804': 'Gümrük Depolarında ve Müzayede Mahallerinde Yapılan Satışlar',
 '805': 'Altından Mamül veya Altın İçeren Ziynet Eşyaları İle Sikke Altınların Teslimi',
 '806': 'Tütün Mamülleri',
 '807': 'Muzır Neşriyat Kapsamındaki Gazete, Dergi vb. Periyodik Yayınlar',
 '808': 'Gümüşten Mamul veya Gümüş İçeren Ziynet Eşyaları ile Sikke Gümüşlerin Teslimi',
 '809': 'Belediyeler Tarafından Yapılan Şehir İçi Yolcu Taşımacılığında Kullanılan Biletlerin ve Kartların Bayiler '
        'Tarafından Satışı',
 '810': 'Ön Ödemeli Elektronik Haberleşme Hizmetleri',
 '811': 'TŞOF Tarafından Araç Plakaları ile Sürücü Kurslarında Kullanılan Bir Kısım Evrakın Teslimi',
 '812': 'KDV Uygulanmadan Alınan İkinci El Motorlu Kara Taşıtı veya Taşınmaz Teslimi'}

IHRAC_KAYITLI = {'701': '3065 s. KDV Kanununun 11/1-c md. Kapsamındaki İhraç Kayıtlı Satış',
 '702': 'DİİB ve Geçici Kabul Rejimi Kapsamındaki Satışlar',
 '703': '4760 s. ÖTV Kanununun 8/2 Md. Kapsamındaki İhraç Kayıtlı Satış',
 '704': '3065 sayılı KDV Kanununun (11/1-c) maddesi ve 4760 s. Ötv Kanununun 8/2. Md. Kapsamındaki İhraç Kayıtlı Satış'}

VERGILER = {'0003': 'Gelir Vergisi Stopajı GV STOPAJI',
 '0011': 'Kurumlar Vergisi Stopajı KV STOPAJI',
 '0015': 'Gerçek Usulde Katma Değer Vergisi KDV GERCEK',
 '0021': 'Banka Muameleleri Vergisi BMV',
 '0022': 'Sigorta Muameleleri Vergisi SMV',
 '0061': 'Kaynak Kullanımı Destekleme Fonu Kesintisi KKDF KESİNTİ',
 '0071': 'Petrol Ve Doğalgaz Ürünlerine İlişkin Özel Tüketim Vergisi ÖTV 1.LİSTE',
 '0073': 'Kolalı Gazoz, Alkollü İçeçekler Ve Tütün Mamüllerine İlişkin Özel Tüketim Vergisi ÖTV 3.LİSTE',
 '0074': 'Dayanıklı Tüketim Ve Diğer Mallara İlişkin Özel Tüketim Vergisi ÖTV 4.LİSTE',
 '0075': 'Alkollü İçeçeklere İlişkin Özel Tüketim Vergisi ÖTV 3A LİSTE',
 '0076': 'Tütün Mamüllerine İlişkin Özel Tüketim Vergisi ÖTV 3B LİSTE',
 '0077': 'Kolalı Gazozlara İlişkin Özel Tüketim Vergisi ÖTV 3C LİSTE',
 '1047': 'Damga Vergisi DAMGA V',
 '1048': '5035 Sayılı Kanuna Göre Damga Vergisi 5035SKDAMGAV',
 '4071': 'Elektrik Ve Havagazi Tüketim Vergisi ELK.HAVAGAZ.TÜK.VER.',
 '4080': 'Özel İletişim Vergisi Ö.İLETİŞİM V',
 '4081': '5035 Sayılı Kanuna Göre Özel İletişim Vergisi 5035ÖZİLETV.',
 '4171': 'Petrol Ve Doğalgaz Ürünlerine İlişkin Ötv Tevkifatı PTR-DGZ ÖTV TEVKİFAT',
 '8001': 'Borsa Tescil Ücreti BORSA TES.ÜC.',
 '8002': 'Enerji Fonu ENERJİ FONU',
 '8004': 'Trt Payı TRT PAYI',
 '8005': 'Elektrik Tüketim Vergisi ELK.TÜK.VER.',
 '8006': 'Telsiz Kullanım Ücreti TK KULLANIM',
 '8007': 'Telsiz Ruhsat Ücreti TK RUHSAT',
 '8008': 'Çevre Temizlik Vergisi ÇEV. TEM .VER.',
 '9021': '4961 Banka Sigorta Muameleleri Vergisi 4961BANKASMV',
 '9040': 'Mera Fonu MERA FONU',
 '9077': 'Motorlu Taşıt Araçlarına İlişkin Özel Tüketim Vergisi (Tescile Tabi Olanlar) ÖTV 2.LİSTE',
 '9944': 'Belediyelere Ödenen Hal Rüsumu BEL.ÖD.HAL RÜSUM'}

TEVKIFATLAR = {'601': ('Yapim İşleri İle Bu İşlerle Birlikte İfa Edilen Mühendislik-Mimarlik Ve Etüt-Proje Hizmetleri', '4/10'),
 '602': ('Etüt, Plan-Proje, Danişmanlik, Denetim Ve Benzeri Hizmetler', '9/10'),
 '603': ('Makine, Teçhizat, Demirbaş Ve Taşitlara Ait Tadil, Bakim Ve Onarim Hizmetleri', '7/10'),
 '604': ('Yemek Servis Hizmeti', '5/10'),
 '605': ('Organizasyon Hizmeti', '5/10'),
 '606': ('İşgücü Temin Hizmetleri', '9/10'),
 '607': ('Özel Güvenlik Hizmeti', '9/10'),
 '608': ('Yapi Denetim Hizmetleri', '9/10'),
 '609': ('Fason Olarak Yaptirilan Tekstil Ve Konfeksiyon İşleri, Çanta Ve Ayakkabi Dikim İşleri Ve Bu İşlere Aracilik '
         'Hizmetleri',
         '7/10'),
 '610': ('Turistik Mağazalara Verilen Müşteri Bulma / Götürme Hizmetleri', '9/10'),
 '611': ('Spor Kulüplerinin Yayin, Reklâm Ve İsim Hakki Gelirlerine Konu İşlemleri', '9/10'),
 '612': ('Temizlik Hizmeti', '9/10'),
 '613': ('Çevre Ve Bahçe Bakim Hizmetleri', '9/10'),
 '614': ('Servis Taşimaciliği Hizmeti', '5/10'),
 '615': ('Her Türlü Baski Ve Basim Hizmetleri', '7/10'),
 '616': ('Diğer Hizmetler [Kdvgut-(I/C-2.1.3.2.13)]', '5/10'),
 '617': ('Hurda Metalden Elde Edilen Külçe Teslimleri', '7/10'),
 '618': ('Hurda Metalden Elde Edilenler Dişindaki Bakir, Çinko Demir ; Çelik Alüminyum Ve Kurşun Külçe Teslimleri '
         '[Kdvgut-(I/C- 2.1.3.3.1)]',
         '7/10'),
 '619': ('Bakir, Çinko Ve Alüminyum Ürünlerinin Teslimi', '7/10'),
 '620': ('İstisnadan Vazgeçenlerin Hurda Ve Atik Teslimi', '7/10'),
 '621': ('Metal, Plastik, Lastik, Kauçuk, Kâğit Ve Cam Hurda Ve Atiklardan Elde Edilen Hammadde Teslimi', '9/10'),
 '622': ('Pamuk, Tiftik, Yün Ve Yapaği İle Ham Post Ve Deri Teslimleri', '9/10'),
 '623': ('Ağaç Ve Orman Ürünleri Teslimi', '5/10'),
 '624': ('Yük Taşimaciliği Hizmeti [Kdvgut-(I/C-2.1.3.2.11)]', '2/10'),
 '625': ('Ticari Reklam Hizmetleri [Kdvgut-(I/C-2.1.3.2.15)]', '3/10'),
 '626': ('Diğer Teslimler [Kdvgut-(I/C-2.1.3.3.7.)]', '2/10'),
 '627': ('Demir-Çelik Ürünlerinin Teslimi [Kdvgut-(I/C-2.1.3.3.8)]', '5/10'),
 '801': ('Yapım İşleri ile Bu İşlerle Birlikte İfa Edilen Mühendislik-Mimarlık ve Etüt-Proje '
         'Hizmetleri[KDVGUT-(I/C-2.1.3.2.1)]',
         '10/10'),
 '802': ('Etüt, Plan-Proje, Danışmanlık, Denetim ve Benzeri Hizmetler[KDVGUT-(I/C-2.1.3.2.2)]', '10/10'),
 '803': ('Makine, Teçhizat, Demirbaş ve Taşıtlara Ait Tadil, Bakım ve Onarım Hizmetleri[KDVGUT- (I/C-2.1.3.2.3)]',
         '10/10'),
 '804': ('Yemek Servis Hizmeti[KDVGUT-(I/C-2.1.3.2.4)]', '10/10'),
 '805': ('Organizasyon Hizmeti[KDVGUT-(I/C-2.1.3.2.4)]', '10/10'),
 '806': ('İşgücü Temin Hizmetleri[KDVGUT-(I/C-2.1.3.2.5)]', '10/10'),
 '807': ('Özel Güvenlik Hizmeti[KDVGUT-(I/C-2.1.3.2.5)]', '10/10'),
 '808': ('Yapı Denetim Hizmetleri[KDVGUT-(I/C-2.1.3.2.6)]', '10/10'),
 '809': ('Fason Olarak Yaptırılan Tekstil ve Konfeksiyon İşleri, Çanta ve Ayakkabı Dikim İşleri ve Bu İşlere Aracılık '
         'Hizmetleri[KDVGUT- (I/C-2.1.3.2.7)]',
         '10/10'),
 '810': ('Turistik Mağazalara Verilen Müşteri Bulma/ Götürme Hizmetleri[KDVGUT-(I/C-2.1.3.2.8)]', '10/10'),
 '811': ('Spor Kulüplerinin Yayın, Reklâm ve İsim Hakkı Gelirlerine Konu İşlemleri[KDVGUT-(I/C-2.1.3.2.9)]', '10/10'),
 '812': ('Temizlik Hizmeti[KDVGUT-(I/C-2.1.3.2.10)]', '10/10'),
 '813': ('Çevre ve Bahçe Bakım Hizmetleri[KDVGUT-(I/C-2.1.3.2.10)]', '10/10'),
 '814': ('Servis Taşımacılığı Hizmeti[KDVGUT-(I/C-2.1.3.2.11)]', '10/10'),
 '815': ('Her Türlü Baskı ve Basım Hizmetleri[KDVGUT-(I/C-2.1.3.2.12)]', '10/10'),
 '816': ('Hurda Metalden Elde Edilen Külçe Teslimleri[KDVGUT-(I/C-2.1.3.3.1)]', '10/10'),
 '817': ('Hurda Metalden Elde Edilenler Dışındaki Bakır, Çinko, Demir Çelik, Alüminyum ve Kurşun Külçe Teslimi '
         '[KDVGUT-(I/C- 2.1.3.3.1)]',
         '10/10'),
 '818': ('Bakır, Çinko, Alüminyum ve Kurşun Ürünlerinin Teslimi[KDVGUT-(I/C-2.1.3.3.2)]', '10/10'),
 '819': ('İstisnadan Vazgeçenlerin Hurda ve Atık Teslimi[KDVGUT-(I/C-2.1.3.3.3)]', '10/10'),
 '820': ('Metal, Plastik, Lastik, Kauçuk, Kâğıt ve Cam Hurda ve Atıklardan Elde Edilen Hammadde '
         'Teslimi[KDVGUT-(I/C-2.1.3.3.4)]',
         '10/10'),
 '821': ('Pamuk, Tiftik, Yün ve Yapağı İle Ham Post ve Deri Teslimleri[KDVGUT-(I/C-2.1.3.3.5)]', '10/10'),
 '822': ('Ağaç ve Orman Ürünleri Teslimi[KDVGUT-(I/C-2.1.3.3.6)]', '10/10'),
 '823': ('Yük Taşımacılığı Hizmeti [KDVGUT-(I/C-2.1.3.2.11)]', '10/10'),
 '824': ('Ticari Reklam Hizmetleri [KDVGUT-(I/C-2.1.3.2.15)]', '10/10'),
 '825': ('Demir-Çelik Ürünlerinin Teslimi [KDVGUT-(I/C-2.1.3.3.8)]', '10/10')}

# ⚡ Veri Kaydedici v2

Seri porttan (UART / USB sanal COM) gelen verileri **kayıpsız** toplayan, canlı grafiğini çizen ve **Excel / CSV / TXT** olarak kaydeden masaüstü uygulaması.

**Çalıştığı kartlar:** STM32 (ST-Link sanal COM ya da USB), Arduino (Uno, Nano, Mega…), ESP32, ESP8266, Raspberry Pi Pico ve CH340 / CP2102 / FTDI USB-seri dönüştürücülü her kart. Kısacası seri porttan satır satır yazı gönderen her cihaz.

> Eski adı: *STM32 Veri Kaydedici*

![Deney aktarımı](docs/ekran_deney.png)

---

## ✨ v2'de neler değişti?

| | v1.2 | v2.0 |
|---|---|---|
| Hızlı veride kayıp (ör. 1450 → 1780 atlaması) | Var | **Yok**: okuma ayrı bir thread'de, veri asla beklemiyor |
| Kayıp tespiti | Yok | **Sıra no + START/END ile otomatik**, grafikte kırmızı bölge |
| Çıktı biçimi | Sadece .txt | **Excel (.xlsx)**, CSV, TXT + ham yedek |
| Grafik | Kayıttan sonra, yavaş | **Canlı**, 1 milyon nokta ~1 sn'de, zoom/pan, PNG |
| DMA ile toplu gönderim | Desteklenmiyor | **"Deney aktarımı" modu**: bitişi algılar, otomatik kaydeder |
| Zaman damgası | Saniye | **Milisaniye** + örnekleme frekansından gerçek zaman |
| Açılış | Yavaş (onefile + matplotlib) | Hızlı (onedir, gereksiz kütüphane yok) |
| Dil | Türkçe | **Türkçe / English** |
| Kart olmadan deneme | Yok | **DEMO portu** |
| Desteklenen kartlar | STM32 | **STM32, Arduino, ESP32/8266, Pico…** (port listesinde ★ ile tanınır) |

### Eski sürümde veri neden kayboluyordu?
Okuma thread'i her satırda (1) kayıt dosyasını açıp kapatıyor, (2) ekrana yazıyordu. Dosya OneDrive'daki Masaüstü'nde olduğunda, antivirüs ve senkronizasyon yüzünden dosyayı açmak bazen yüzlerce ms sürebiliyor. Bu sırada Windows'un seri port tamponu (varsayılan birkaç KB) dolup taşıyor ve **aradaki satırlar kayboluyordu**. Ekrandaki metin kutusu da hiç temizlenmediği için zamanla yavaşlıyordu; kaymanın "bir süre sonra" başlaması bununla uyumlu. Kart, DMA'daki veriyi deney sonunda tam hızda gönderdiği için sorun en çok o anda görülüyordu.

v2'de veri üç katmandan geçiyor:

```
[Okuyucu thread]  sadece ser.read() → kuyruk     (tampon asla taşmaz, sürücü tamponu 1 MB)
[İşlemci thread]  ham yedek + satırlara böl + çözümle + aktarım sonu tespiti
[Arayüz]          50 ms'de bir toplu güncelleme  (yavaşlarsa veri bellekte bekler, kaybolmaz)
```

Test: 300.000 satırlık tek parça aktarım ≈ 125.000 satır/sn hızında, sıfır kayıpla işleniyor (921600 baud'un ~20 katı).

![Kayıp tespiti](docs/ekran_kayip.png)

---

## ⬇️ İndirme

**Actions** sekmesi → en son başarılı build → **Artifacts**:

| Platform | Dosya | Çalıştırma |
|---|---|---|
| 🖥️ Windows | `Veri_Kaydedici_Windows.zip` | Zip'i bir klasöre çıkar → `Veri_Kaydedici.exe` |
| 🍎 macOS | `Veri_Kaydedici_macOS.dmg` | Aç → Applications'a sürükle |

> `v2.0.0` gibi bir etiket (tag) push'layınca bu dosyalar **Releases** sayfasına da otomatik eklenir.
>
> macOS'ta "bilinmeyen geliştirici" uyarısı çıkarsa: **Sistem Ayarları → Gizlilik ve Güvenlik → Yine de Aç**.

---

## 🚀 Kullanım

### Deney aktarımı modu (DMA ile toplu gönderim)
1. Portu seç (tanınan kartlar — STM32, Arduino, ESP32… — ★ ile işaretli ve otomatik seçilir), baud'u kart koduyla aynı yap.
2. **Deney aktarımı** modunu seç → **Bağlan**.
3. Kartta deneyi başlat. Deney bitip veri gelince uygulama:
   - ilerleme çubuğunu gösterir (kart `START,N` gönderiyorsa),
   - aktarım bitince (`END` gelince ya da 1 sn veri gelmeyince) **otomatik kaydeder**,
   - eksik veri varsa kırmızı uyarı verir ve grafikte yerini gösterir,
   - bağlantıyı koparmadan **sonraki deneyi bekler**.

### Canlı izleme modu
Kart sürekli veri gönderiyorsa: veriler anlık grafikte akar, **Bağlantıyı kes** deyince kaydedilir. Grafikte son 10 sn / 30 sn / 1 dk / 5 dk ya da tümü gösterilebilir.

### Kart olmadan denemek
Port listesinin en altındaki **DEMO** seçeneğiyle bağlan. Deney aktarımı modunda 4000 örneklik sahte bir deney gönderir. Komut kutusuna `GONDER` yazarsan tekrar gönderir.

### Kaydedilen dosyalar
Varsayılan klasör: `Belgeler\Veri Kaydedici` (değiştirilebilir).

- `deney_2026-10-11_14-30-05.xlsx`: **Özet** (port, süre, bütünlük, kanal istatistikleri), **Veriler**, **Grafik** sayfaları
- `ham\ham_....txt`: Karttan gelen her bayt, hiç değiştirilmeden (her ihtimale karşı)

**Kayıtlı dosyayı aç…** ile eski kayıtlar (v1'in `.txt` dosyaları dahil) yeniden grafikte açılabilir.

---

## 📡 Kart tarafı: veri biçimi

Uygulama şu satırların hepsini anlar:

```
1450                      tek kanal
12,345,678                çok kanal (virgül, noktalı virgül, boşluk ya da tab)
Sicaklik:25.3 Nem:60      isimli kanallar
zaman,ivme,sicaklik       başlık satırı (veriden önce gelirse kanal adı olur)
START,4000 / END,4000     aktarımın başı / sonu (BASLA / BITTI da olur)
```

**Kayıpları yakalamak için önerilen biçim**: ilk sütunda 0'dan artan sıra numarası, başta `START,N`, sonda `END,N`:

```
START,4000
0,2048
1,2051
...
3999,2040
END,4000
```

Hazır örnekler:
- **STM32 (HAL):** [`firmware_ornek/veri_gonder.c`](firmware_ornek/veri_gonder.c) (Timer tetiklemeli ADC + DMA + UART gönderimi)
- **Arduino / ESP32 / ESP8266:** [`firmware_ornek/arduino_ornek/arduino_ornek.ino`](firmware_ornek/arduino_ornek/arduino_ornek.ino) (canlı mod ya da `GONDER` komutuyla deney aktarımı)

> ⚠️ DMA'yı **Circular** modda kullanıp gönderim sırasında örneklemeye devam ederseniz tampon başa dönüp eski verinin üstüne yazar. Bu durumda da veriler "kayar". Deney kaydı için DMA **Normal** modda olmalı ve gönderimden önce `HAL_ADC_Stop_DMA` çağrılmalı.

---

## 🛠️ Geliştirici: kaynak koddan çalıştırma

Windows'ta en kolayı: **`baslat.bat`** dosyasına çift tıkla. İlk seferde gerekenleri kurar.

Elle:
```bash
pip install -r requirements.txt
python main.py
```

Testler:
```bash
pip install pytest
python -m pytest tests
```

### Proje yapısı
```
main.py                     giriş noktası
stm32logger/
  engine.py                 kayıpsız okuma motoru + DEMO port
  parser.py                 satır çözümleyici
  session.py                oturum verisi, sıra no / kayıp tespiti
  exporter.py               Excel / CSV / TXT çıktısı
  importer.py               kayıtlı dosyaları açma
  i18n.py                   Türkçe / English metinler
  ui/                       PySide6 arayüzü (pyqtgraph grafik)
firmware_ornek/             STM32 (HAL) ve Arduino/ESP32 örnek kodları
tests/                      testler (300 bin satırlık yük testi dahil)
```

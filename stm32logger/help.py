"""Uygulama içi kullanım kılavuzu (Türkçe / English).

Her konu: başlık + HTML gövde. Gövdedeki {img:ad} etiketi assets/help/<dil>/<ad>.png
görseliyle değiştirilir. Görsellerdeki numaralar (①②③…) metindeki numaralarla aynıdır.
Görselleri yeniden üretmek için:  python packaging/make_help_images.py
"""
from __future__ import annotations

TOPICS = ["quickstart", "connect", "modes", "format", "saving", "chart", "trouble", "security"]

GUIDE: dict[str, dict[str, tuple[str, str]]] = {
    # ------------------------------------------------------------------ TÜRKÇE
    "tr": {
        "quickstart": ("Hızlı başlangıç", """
<h2>Hızlı başlangıç</h2>
<p>Kart takılı olmasa da uygulamayı 30 saniyede deneyebilirsiniz:</p>
{img:quickstart}
<ol>
<li><b>①&nbsp;Port</b> listesinden <b>DEMO — kart olmadan dene</b>'yi seçin.</li>
<li><b>②&nbsp;Çalışma modu</b> olarak <b>Deney aktarımı</b>'nı seçin.</li>
<li><b>③&nbsp;Bağlan</b>'a basın. Sahte bir kart 4000 örneklik bir deneyi gönderir.</li>
<li><b>④</b> Üstteki kutucuklarda satır sayısı, hız ve <b>eksik veri</b> görünür.</li>
<li><b>⑤</b> Aktarım bitince yeşil bant çıkar ve dosya otomatik kaydedilir. <i>Dosyayı aç</i> ile Excel'de açabilirsiniz.</li>
<li><b>⑥</b> Grafikte fare tekerleğiyle yakınlaştırın, sürükleyerek kaydırın.</li>
</ol>
<p class="tip">💡 Komut kutusuna <code>GONDER</code> yazıp <b>Gönder</b>'e basarsanız DEMO yeni bir deney gönderir.</p>
"""),
        "connect": ("Kart bağlama", """
<h2>Kart bağlama</h2>
{img:connect}
<ol>
<li><b>①&nbsp;Port:</b> Kartınızın portunu seçin. Tanınan kartlar (STM32, Arduino, ESP32, CH340, CP2102, FTDI, Pico) <b>★</b> ile işaretlenir ve listenin başına gelir.</li>
<li><b>②&nbsp;Yenile:</b> Kartı sonradan taktıysanız basın. Liste zaten 2 saniyede bir kendini yeniler.</li>
<li><b>③&nbsp;Baud hızı:</b> Kart kodundaki değerle <b>aynı</b> olmalı (ör. 115200, 921600). Listede yoksa elle yazabilirsiniz.</li>
<li><b>④&nbsp;Çalışma modu:</b> Canlı izleme ya da Deney aktarımı (sonraki konuya bakın).</li>
<li><b>⑤&nbsp;USB koparsa yeniden bağlan:</b> Kablo çıkarsa ya da kart yeniden başlarsa o ana kadarki veriler dosyaya kaydedilir; port geri gelince uygulama kendiliğinden bağlanır.</li>
<li><b>⑥&nbsp;Bağlan</b> / <b>Bağlantıyı kes</b> (kısayol: <b>F5</b>).</li>
</ol>
<h3>Veri ayarları</h3>
<ul>
<li><b>⑦&nbsp;Örnekleme frekansı:</b> Kartınız sabit hızda örnekliyorsa (ör. 1000 Hz) yazın. Excel'de her örneğin zamanı (s) hesaplanır. Bilmiyorsanız boş bırakın.</li>
<li><b>⑧&nbsp;Sıra numarası:</b> <i>Otomatik algıla</i> çoğu zaman doğrudur. İlk sütun 0, 1, 2… diye artıyorsa kayıp satırlar yakalanır.</li>
<li><b>⑨&nbsp;Aktarım bitiş süresi:</b> Deney aktarımında bu kadar süre veri gelmezse aktarım bitti sayılır. <b>1 s</b> iyi bir değerdir. Kart <code>END</code> gönderiyorsa beklenmez.</li>
</ul>
<p class="tip">⚠️ <b>Port görünmüyorsa:</b> Arduino klonları ve ESP kartları için <b>CH340</b> ya da <b>CP2102</b> sürücüsünü kurun. Kablonun sadece şarj kablosu olmadığından emin olun. Port başka bir programda (Arduino IDE seri monitörü, STM32CubeIDE) açıksa önce oradan kapatın.</p>
"""),
        "modes": ("Canlı izleme ve deney aktarımı", """
<h2>Canlı izleme ve deney aktarımı</h2>
<table>
<tr><th></th><th>Canlı izleme</th><th>Deney aktarımı</th></tr>
<tr><td><b>Ne zaman?</b></td><td>Kart veriyi ölçtükçe sürekli gönderiyorsa</td><td>Kart deneyi belleğe (ör. DMA) kaydedip <b>sonunda topluca</b> gönderiyorsa</td></tr>
<tr><td><b>Grafik</b></td><td>Akan grafik; son 10 s / 30 s / 1 dk / 5 dk ya da tümü</td><td>Aktarım boyunca dolar, bitince tamamı gösterilir</td></tr>
<tr><td><b>Kayıt</b></td><td><i>Bağlantıyı kes</i> deyince</td><td>Her aktarım bitince otomatik; uygulama sonraki deneyi bekler</td></tr>
</table>
{img:modes}
<ul>
<li><b>①</b> Kart <code>START,N</code> gönderirse <b>beklenen</b> satır sayısı görünür.</li>
<li><b>②</b> Aktarım sırasında ilerleme çubuğu dolar.</li>
<li><b>③&nbsp;Durum:</b> <i>Veri bekleniyor</i> → <i>Alınıyor…</i> → <i>Tamamlandı</i>.</li>
</ul>
<p class="tip">💡 Hızlı toplu gönderimde terminal ekranı bazı satırları <b>göstermeyebilir</b>. Bu sadece ekranla ilgilidir; dosyaya <b>her satır</b> kaydedilir.</p>
"""),
        "format": ("Kart tarafı: veri biçimi", """
<h2>Kart tarafı: veri biçimi</h2>
<p>Kartınız her ölçümü <b>bir satır</b> olarak göndermelidir (satır sonu <code>\\r\\n</code> ya da <code>\\n</code>). Uygulama şunların hepsini anlar:</p>
<pre>1450                    tek değer
12,345,678              çok kanal (virgül ; boşluk ya da tab)
Sicaklik:25.3 Nem:60    isimli kanallar
zaman,adc1,adc2         başlık (veriden önce) → kanal adları</pre>
<h3>Kayıpları yakalamak için önerilen biçim</h3>
<pre>START,4000      ← kaç satır geleceği
0,2048          ← sıra no, değer(ler)
1,2051
...
3999,2040
END,4000        ← aktarım bitti</pre>
<p>İlk sütundaki sıra numarası sayesinde tek bir satır bile kaybolsa hangi aralıkta kaybolduğu gösterilir.</p>
<h3>Arduino / ESP32 örneği</h3>
<pre>Serial.print("START,"); Serial.println(N);
for (int i = 0; i &lt; N; i++) {
  Serial.print(i); Serial.print(','); Serial.println(buf[i]);
}
Serial.print("END,"); Serial.println(N);</pre>
<h3>STM32 (HAL) örneği</h3>
<pre>n = snprintf(s, sizeof s, "%lu,%u\\r\\n", (unsigned long)i, adc_buf[i]);
HAL_UART_Transmit(&amp;huart2, (uint8_t*)s, n, HAL_MAX_DELAY);</pre>
<p>Hazır örnek kodların tamamı GitHub sayfasındaki <code>firmware_ornek</code> klasöründedir.</p>
<p class="tip">💡 Ondalıklı sayı için <code>printf</code> float desteği gerekir. Daha kolayı: değeri 100 ile çarpıp tamsayı gönderin (25,31 °C → 2531).</p>
"""),
        "saving": ("Kayıt ve dosyalar", """
<h2>Kayıt ve dosyalar</h2>
{img:saving}
<ol>
<li><b>①&nbsp;Dosya biçimi:</b>
  <ul><li><b>Excel:</b> <i>Özet</i> (bütünlük, min/max/ortalama), <i>Veriler</i> ve <i>Grafik</i> sayfaları. Raporlar için en iyisi.</li>
  <li><b>CSV:</b> Python, MATLAB ve benzeri programlar için.</li>
  <li><b>TXT:</b> Sekmeyle ayrılmış sade metin, başında açıklama satırları.</li></ul></li>
<li><b>②&nbsp;Kayıt klasörü:</b> Varsayılan <code>Belgeler\\Data Logger</code>.</li>
<li><b>③&nbsp;Dosya adı:</b> Dosyalar <code>ad_2026-10-17_14-30-05.xlsx</code> biçiminde adlandırılır.</li>
<li><b>④&nbsp;Bitince otomatik kaydet:</b> Açıkken her aktarım ya da kayıt kendiliğinden kaydedilir.</li>
<li><b>⑤&nbsp;Ham yedek:</b> Karttan gelen her bayt hiç değiştirilmeden <code>ham</code> klasörüne de yazılır. Her ihtimale karşı açık tutun.</li>
<li><b>⑥&nbsp;Farklı kaydet:</b> Ekrandaki veriyi istediğiniz ad ve biçimde kaydeder.</li>
<li><b>⑦&nbsp;Klasörü aç</b> · <b>⑧&nbsp;Kayıtlı dosyayı aç:</b> Eski kayıtları (eski sürümün .txt dosyaları dahil) yeniden grafikte açar.</li>
</ol>
<p class="tip">🛟 Veri kaybına karşı: Kaydedilmemiş bir kayıt varken pencereyi kapatırsanız, yeni bağlantı açarsanız ya da dosya açarsanız uygulama sorar. Dosyalar önce geçici adla yazılır, bitince asıl adını alır; yazma yarıda kalsa bile yarım dosya oluşmaz. Canlı izlemede kayıt 1 milyon satıra ulaşınca bellek dolmasın diye dosya otomatik bölünür.</p>
<p class="tip">⌨️ <b>Ctrl+S</b> farklı kaydet · <b>Ctrl+O</b> kayıtlı dosyayı aç</p>
"""),
        "chart": ("Grafik ve terminal", """
<h2>Grafik ve terminal</h2>
{img:chart}
<ol>
<li><b>①&nbsp;X ekseni:</b> <i>Otomatik</i>, örnek no, zaman (s) ya da PC süresi.</li>
<li><b>②&nbsp;Pencere:</b> Canlı izlemede son kaç saniyenin gösterileceği.</li>
<li><b>③&nbsp;Sığdır:</b> Yakınlaştırdıktan sonra tüm veriyi tekrar gösterir.</li>
<li><b>④&nbsp;PNG kaydet:</b> Grafiği rapor için resim olarak kaydeder.</li>
<li><b>⑤</b> Gösterge kutusunda bir kanalın adına tıklayınca o kanal gizlenir ya da gösterilir.</li>
<li><b>⑥&nbsp;HEX / Duraklat / Temizle:</b> <b>HEX</b> gelen baytları onaltılık gösterir (baud hızı yanlışsa ya da kart ikili veri gönderiyorsa işe yarar). Duraklat terminali dondurur, Temizle (<b>Ctrl+L</b>) siler. Kayıt etkilenmez.</li>
<li><b>⑦&nbsp;Komut gönder:</b> Karta yazı gönderir (ör. <code>GONDER</code>). Yanındaki kutudan satır sonu seçilir. <b>HEX</b> işaretliyse <code>01 A0 FF</code> gibi bayt gönderir. Klavyedeki <b>↑ / ↓</b> ile önceki komutlar geri gelir.</li>
</ol>
<p class="tip">🖱️ Tekerlek: yakınlaştır · Sol tık sürükle: kaydır · Sağ tık: eksen seçenekleri</p>
"""),
        "trouble": ("Sorun giderme", """
<h2>Sorun giderme</h2>
{img:trouble}
<p><b>①</b> Kırmızı bant ve <b>②</b> kırmızı <b>Eksik veri</b> sayısı, bazı satırların gelmediğini gösterir. <b>③</b> Kayıp aralık grafikte kırmızı ile işaretlenir; araya sahte değer konmaz.</p>
<table>
<tr><th>Belirti</th><th>Muhtemel neden ve çözüm</th></tr>
<tr><td>Anlamsız karakterler, hiç sayı yok</td><td><b>Baud hızı</b> kart koduyla aynı değil.</td></tr>
<tr><td>Veriler belli bir yerden sonra "kayıyor", eski değerler tekrar ediyor</td><td>STM32'de ADC DMA'sı <b>Circular</b> modda. <b>Normal</b> moda alın ve göndermeden önce <code>HAL_ADC_Stop_DMA</code> çağırın.</td></tr>
<tr><td>Eksik veri sayılıyor ama "kontrol edilemedi" yazıyor</td><td>Kart sıra numarası ya da <code>START,N</code> göndermiyor. <i>Kart tarafı: veri biçimi</i> konusuna bakın.</td></tr>
<tr><td>Aktarım ortada iki dosyaya bölünüyor</td><td><b>Aktarım bitiş süresi</b> çok kısa. 1–2 s yapın.</td></tr>
<tr><td>Port açılamadı hatası</td><td>Port başka bir programda açık (seri monitör, CubeIDE) ya da kart çıkarıldı.</td></tr>
<tr><td>Port listede yok</td><td>Sürücü (CH340 / CP2102) eksik ya da kablo sadece şarj kablosu.</td></tr>
<tr><td>"Bağlantı koptu, yeniden bağlanıyor…"</td><td>USB kablosu gevşek ya da kart yeniden başladı. O ana kadarki veri kaydedildi; kart geri gelince devam edilir. Sürekli oluyorsa başka kablo / USB girişi deneyin.</td></tr>
<tr><td>Uygulama tuhaf davranıyor, pencere ekran dışında</td><td><b>? → Ayarları sıfırla</b>. (Açılmıyorsa: <code>Data_Logger.exe --reset-settings</code>)</td></tr>
</table>
<p>Çözemediğiniz bir sorun olursa <b>? → Hata bildir / öneri</b> ile bize yazın.</p>
"""),
        "security": ("Güvenlik ve Windows uyarısı", """
<h2>Güvenlik</h2>
<p>Data Logger yönetici izni istemez, sistem ayarlarına ve başka programlara dokunmaz, arka planda çalışan bir servis kurmaz. Sadece seçtiğiniz seri portu ve kayıt klasörünü kullanır.</p>
<h3>Dosyaların sağlam olduğunu kontrol etmek</h3>
<ul>
<li>Uygulama yalnızca GitHub'daki herkese açık derleme sisteminde, bu repodaki koddan üretilir. Her sürümde derleme kanıtı (<i>build provenance</i>) bulunur.</li>
<li>Derlenirken klasördeki <b>her dosyanın parmak izi</b> (SHA-256) uygulamanın içine yazılır. <b>? → Hakkında → Dosyaları doğrula</b> ile değişmiş, bozulmuş, eksik ya da klasöre <b>sonradan eklenmiş</b> dosya olup olmadığını görürsünüz.</li>
<li><b>En güçlü kontrol:</b> İndirdiğiniz zip'in parmak izi sürüm sayfasındaki <code>SHA256SUMS.txt</code> ile aynı olmalı. PowerShell: <code>Get-FileHash Data_Logger_Windows.zip</code>. (Klasördeki liste de aynı klasörde durduğu için, bilgisayara zaten sızmış bir saldırgan onu da değiştirebilir; bu yüzden asıl güvence indirme anındaki bu kontroldür.)</li>
<li>Uygulamayı sadece <b>GitHub sayfasından</b> indirin; başka sitelerdeki kopyalar değiştirilmiş olabilir.</li>
</ul>
<p class="tip">ℹ️ İmzasız yeni programlar bazen antivirüs tarafından yanlışlıkla şüpheli bulunur (yanlış alarm). Böyle olursa önce <b>Dosyaları doğrula</b>'yı çalıştırın, sonra <b>? → Hata bildir</b> ile bize haber verin.</p>
<h2>"Bu dosyayı çalıştırmak istiyor musunuz?" uyarısı</h2>
<p>Windows, internetten indirilen ve <b>dijital imzası olmayan</b> programlarda bu uyarıyı gösterir. Data Logger açık kaynaklıdır ve kodu GitHub'da herkese açıktır; uyarı sadece henüz imza sertifikası olmamasından kaynaklanır.</p>
<h3>Uyarının bir daha çıkmaması için</h3>
<ul>
<li><b>Bu bilgisayarda:</b> Uygulama ilk açılışta size sorar ve izin verirseniz Windows'un "internetten indirildi" etiketini kaldırır. Bu, dosyanın <i>Özellikler → Engellemeyi kaldır</i> seçeneğiyle aynı işlemdir. Etiket <b>sadece parmak izi derlemeyle birebir aynı olan</b> kendi dosyalarından kaldırılır; tanınmayan ya da değiştirilmiş dosyalar için Windows uyarmaya devam eder. Bu soruyu kaçırdıysanız <b>? → Hakkında</b> penceresinden tekrar yapabilirsiniz.</li>
<li><b>Başka birine gönderirken:</b> Zip'i açmadan önce sağ tıklayın → <b>Özellikler</b> → alttaki <b>Engellemeyi kaldır</b> kutusunu işaretleyin → <b>Tamam</b>. Sonra zip'i açın.</li>
<li><b>Mavi "Windows kişisel bilgisayarınızı korudu" ekranı</b> çıkarsa: <b>Ek bilgi</b> → <b>Yine de çalıştır</b>.</li>
</ul>
<h3>macOS</h3>
<p>"Geliştirici doğrulanamadı" uyarısında <b>Sistem Ayarları → Gizlilik ve Güvenlik</b> sayfasının altındaki <b>Yine de Aç</b>'a basın (eski macOS sürümlerinde uygulamaya sağ tık → <b>Aç</b> da olur). Bu sadece ilk açılışta gerekir. macOS sürümü Apple Silicon (M1 ve sonrası) içindir.</p>
<h3>Gizlilik</h3>
<p>Data Logger hiçbir veriyi internete göndermez. Sadece seçtiğiniz seri portla haberleşir ve seçtiğiniz klasöre dosya yazar. Tek istisna, siz <b>Güncellemeleri kontrol et</b>'e bastığınızda GitHub'dan son sürüm numarasının okunmasıdır.</p>
"""),
    },
    # ------------------------------------------------------------------ ENGLISH
    "en": {
        "quickstart": ("Quick start", """
<h2>Quick start</h2>
<p>You can try the app in 30 seconds, even without a board:</p>
{img:quickstart}
<ol>
<li>In <b>①&nbsp;Port</b>, choose <b>DEMO — try without a board</b>.</li>
<li>As <b>②&nbsp;Mode</b>, choose <b>Experiment dump</b>.</li>
<li>Click <b>③&nbsp;Connect</b>. A simulated board sends a 4000-sample experiment.</li>
<li><b>④</b> The tiles show rows, rate and <b>missing data</b>.</li>
<li><b>⑤</b> When the transfer ends, a green banner appears and the file is saved automatically. Use <i>Open file</i> to open it in Excel.</li>
<li><b>⑥</b> Zoom the chart with the mouse wheel, drag to pan.</li>
</ol>
<p class="tip">💡 Type <code>SEND</code> in the command box and click <b>Send</b> to make the DEMO send a new experiment.</p>
"""),
        "connect": ("Connecting a board", """
<h2>Connecting a board</h2>
{img:connect}
<ol>
<li><b>①&nbsp;Port:</b> Choose your board's port. Known boards (STM32, Arduino, ESP32, CH340, CP2102, FTDI, Pico) are marked <b>★</b> and listed first.</li>
<li><b>②&nbsp;Refresh:</b> Use it if you plugged the board in later. The list also refreshes itself every 2 seconds.</li>
<li><b>③&nbsp;Baud rate:</b> Must be the <b>same</b> as in your firmware (e.g. 115200, 921600). You can type a custom value.</li>
<li><b>④&nbsp;Mode:</b> Live monitor or Experiment dump (see the next topic).</li>
<li><b>⑤&nbsp;Reconnect if USB drops:</b> If the cable is unplugged or the board restarts, the data received so far is saved and the app reconnects by itself when the port comes back.</li>
<li><b>⑥&nbsp;Connect</b> / <b>Disconnect</b> (shortcut: <b>F5</b>).</li>
</ol>
<h3>Data settings</h3>
<ul>
<li><b>⑦&nbsp;Sample rate:</b> If your board samples at a fixed rate (e.g. 1000 Hz), enter it. Excel then gets a time (s) column for every sample. Leave it empty if you don't know it.</li>
<li><b>⑧&nbsp;Sequence number:</b> <i>Auto-detect</i> is usually right. If the first column counts 0, 1, 2…, lost lines are detected.</li>
<li><b>⑨&nbsp;Transfer end timeout:</b> In experiment dump mode, the transfer counts as finished after this much silence. <b>1 s</b> is a good value. Not needed if the board sends <code>END</code>.</li>
</ul>
<p class="tip">⚠️ <b>Port not listed?</b> Install the <b>CH340</b> or <b>CP2102</b> driver for Arduino clones and ESP boards. Make sure the USB cable is not a charge-only cable. If the port is open in another program (Arduino IDE serial monitor, STM32CubeIDE), close it there first.</p>
"""),
        "modes": ("Live vs. experiment mode", """
<h2>Live monitor vs. experiment dump</h2>
<table>
<tr><th></th><th>Live monitor</th><th>Experiment dump</th></tr>
<tr><td><b>When?</b></td><td>The board sends data continuously while measuring</td><td>The board stores the experiment in memory (e.g. DMA) and sends it <b>all at the end</b></td></tr>
<tr><td><b>Chart</b></td><td>Scrolling chart; last 10 s / 30 s / 1 min / 5 min or all</td><td>Fills during the transfer, then shows everything</td></tr>
<tr><td><b>Saving</b></td><td>When you click <i>Disconnect</i></td><td>Automatically after each transfer; then waits for the next one</td></tr>
</table>
{img:modes}
<ul>
<li><b>①</b> If the board sends <code>START,N</code>, the <b>expected</b> row count is shown.</li>
<li><b>②</b> A progress bar fills during the transfer.</li>
<li><b>③&nbsp;Status:</b> <i>Waiting for data</i> → <i>Receiving…</i> → <i>Complete</i>.</li>
</ul>
<p class="tip">💡 During very fast transfers the terminal may <b>skip displaying</b> some lines. This only affects the screen; <b>every line</b> is saved to the file.</p>
"""),
        "format": ("Board side: data format", """
<h2>Board side: data format</h2>
<p>Your board should send each measurement as <b>one line</b> (ending with <code>\\r\\n</code> or <code>\\n</code>). The app understands all of these:</p>
<pre>1450                    single value
12,345,678              multiple channels (comma ; space or tab)
Temp:25.3 Hum:60        named channels
time,adc1,adc2          header (before data) → channel names</pre>
<h3>Recommended format for loss detection</h3>
<pre>START,4000      ← how many lines will follow
0,2048          ← sequence number, value(s)
1,2051
...
3999,2040
END,4000        ← transfer finished</pre>
<p>With a sequence number in the first column, even a single lost line is detected and its position is shown.</p>
<h3>Arduino / ESP32 example</h3>
<pre>Serial.print("START,"); Serial.println(N);
for (int i = 0; i &lt; N; i++) {
  Serial.print(i); Serial.print(','); Serial.println(buf[i]);
}
Serial.print("END,"); Serial.println(N);</pre>
<h3>STM32 (HAL) example</h3>
<pre>n = snprintf(s, sizeof s, "%lu,%u\\r\\n", (unsigned long)i, adc_buf[i]);
HAL_UART_Transmit(&amp;huart2, (uint8_t*)s, n, HAL_MAX_DELAY);</pre>
<p>Complete examples are in the <code>firmware_ornek</code> folder on the GitHub page.</p>
<p class="tip">💡 Decimal numbers need float support in <code>printf</code>. Easier: multiply by 100 and send an integer (25.31 °C → 2531).</p>
"""),
        "saving": ("Saving and files", """
<h2>Saving and files</h2>
{img:saving}
<ol>
<li><b>①&nbsp;File format:</b>
  <ul><li><b>Excel:</b> <i>Summary</i> (integrity, min/max/mean), <i>Data</i> and <i>Chart</i> sheets. Best for reports.</li>
  <li><b>CSV:</b> for Python, MATLAB and similar tools.</li>
  <li><b>TXT:</b> plain tab-separated text with comment lines at the top.</li></ul></li>
<li><b>②&nbsp;Output folder:</b> <code>Documents\\Data Logger</code> by default.</li>
<li><b>③&nbsp;File name:</b> Files are named like <code>name_2026-10-17_14-30-05.xlsx</code>.</li>
<li><b>④&nbsp;Save automatically when done:</b> Every transfer or recording is saved on its own.</li>
<li><b>⑤&nbsp;Raw backup:</b> Every byte received from the board is also written, untouched, to the <code>ham</code> (raw) folder. Keep it on, just in case.</li>
<li><b>⑥&nbsp;Save as:</b> Saves the data on screen with any name and format.</li>
<li><b>⑦&nbsp;Open folder</b> · <b>⑧&nbsp;Open saved file:</b> Reopens earlier recordings (including .txt files from the old version) in the chart.</li>
</ol>
<p class="tip">🛟 Protection against data loss: if a recording is not saved yet, the app asks before you close the window, connect again or open a file. Files are first written under a temporary name and renamed when complete, so an interrupted save never leaves a half-written file. In live monitor mode the recording is split into a new file every 1 million rows so memory never fills up.</p>
<p class="tip">⌨️ <b>Ctrl+S</b> save as · <b>Ctrl+O</b> open saved file</p>
"""),
        "chart": ("Chart and terminal", """
<h2>Chart and terminal</h2>
{img:chart}
<ol>
<li><b>①&nbsp;X axis:</b> <i>Auto</i>, sample number, time (s) or PC time.</li>
<li><b>②&nbsp;Window:</b> How many recent seconds to show in live monitor mode.</li>
<li><b>③&nbsp;Fit:</b> Shows all data again after zooming.</li>
<li><b>④&nbsp;Save PNG:</b> Saves the chart as an image for reports.</li>
<li><b>⑤</b> Click a channel name in the legend to hide or show that channel.</li>
<li><b>⑥&nbsp;HEX / Pause / Clear:</b> <b>HEX</b> shows the received bytes in hexadecimal (useful when the baud rate is wrong or the board sends binary data). Pause freezes the terminal, Clear (<b>Ctrl+L</b>) empties it. Recording is not affected.</li>
<li><b>⑦&nbsp;Send command:</b> Sends text to the board (e.g. <code>SEND</code>). Choose the line ending in the box next to it. With <b>HEX</b> ticked it sends bytes such as <code>01 A0 FF</code>. Press <b>↑ / ↓</b> to recall previous commands.</li>
</ol>
<p class="tip">🖱️ Wheel: zoom · Left-drag: pan · Right-click: axis options</p>
"""),
        "trouble": ("Troubleshooting", """
<h2>Troubleshooting</h2>
{img:trouble}
<p>The <b>①</b> red banner and the <b>②</b> red <b>Missing</b> count mean some lines never arrived. <b>③</b> The lost range is marked red on the chart; no fake values are drawn in between.</p>
<table>
<tr><th>Symptom</th><th>Likely cause and fix</th></tr>
<tr><td>Garbage characters, no numbers</td><td>The <b>baud rate</b> does not match your firmware.</td></tr>
<tr><td>Data "jumps" after some point, old values repeat</td><td>On STM32 the ADC DMA is in <b>Circular</b> mode. Use <b>Normal</b> mode and call <code>HAL_ADC_Stop_DMA</code> before sending.</td></tr>
<tr><td>Missing data says "not checked"</td><td>The board sends no sequence number or <code>START,N</code>. See <i>Board side: data format</i>.</td></tr>
<tr><td>One transfer is split into two files</td><td><b>Transfer end timeout</b> is too short. Set it to 1–2 s.</td></tr>
<tr><td>"Could not open port"</td><td>The port is open in another program (serial monitor, CubeIDE), or the board was unplugged.</td></tr>
<tr><td>Port not listed</td><td>Missing driver (CH340 / CP2102) or a charge-only USB cable.</td></tr>
<tr><td>"Connection lost, reconnecting…"</td><td>Loose USB cable or the board restarted. The data so far was saved; recording continues when the board is back. If it keeps happening, try another cable / USB port.</td></tr>
<tr><td>The app behaves oddly, window is off-screen</td><td><b>? → Reset settings</b>. (If it does not open: <code>Data_Logger.exe --reset-settings</code>)</td></tr>
</table>
<p>Still stuck? Use <b>? → Report a problem / suggestion</b>.</p>
"""),
        "security": ("Security & Windows warning", """
<h2>Security</h2>
<p>Data Logger never asks for administrator rights, does not touch system settings or other programs and installs no background service. It only uses the serial port and the output folder you choose.</p>
<h3>Checking that the files are intact</h3>
<ul>
<li>The app is built only by the public GitHub build system, from the code in this repository. Every release includes build provenance.</li>
<li>During the build, the <b>fingerprint of every file</b> (SHA-256) is stored inside the app. <b>? → About → Verify files</b> shows whether any file was modified, corrupted, is missing, or was <b>added to the folder later</b>.</li>
<li><b>Strongest check:</b> the fingerprint of the zip you downloaded should match <code>SHA256SUMS.txt</code> on the release page. PowerShell: <code>Get-FileHash Data_Logger_Windows.zip</code>. (The list inside the folder lives in that same folder, so an attacker who already controls the computer could change it too; the check at download time is the real guarantee.)</li>
<li>Only download the app from its <b>GitHub page</b>; copies on other sites may have been modified.</li>
</ul>
<p class="tip">ℹ️ New unsigned programs are sometimes flagged by antivirus software by mistake (a false positive). If that happens, run <b>Verify files</b> first, then let us know via <b>? → Report a problem</b>.</p>
<h2>"Do you want to run this file?" warning</h2>
<p>Windows shows this warning for programs downloaded from the internet that are <b>not digitally signed</b>. Data Logger is open source and its code is public on GitHub; the warning only appears because it does not have a signing certificate yet.</p>
<h3>To stop the warning</h3>
<ul>
<li><b>On this computer:</b> On first launch the app asks you, and with your permission removes Windows' "downloaded from the internet" mark. This is the same as <i>Properties → Unblock</i> on the file. The mark is removed <b>only from its own files whose fingerprint exactly matches the build</b>; Windows keeps warning about unknown or modified files. If you skipped the question, you can do it again from <b>? → About</b>.</li>
<li><b>When sharing with others:</b> Before extracting, right-click the zip → <b>Properties</b> → tick <b>Unblock</b> at the bottom → <b>OK</b>. Then extract it.</li>
<li><b>If a blue "Windows protected your PC" screen appears:</b> click <b>More info</b> → <b>Run anyway</b>.</li>
</ul>
<h3>macOS</h3>
<p>For "developer cannot be verified", open <b>System Settings → Privacy &amp; Security</b> and click <b>Open Anyway</b> at the bottom (on older macOS versions, right-click the app → <b>Open</b> also works). This is only needed on first launch. The macOS build is for Apple Silicon (M1 and later).</p>
<h3>Privacy</h3>
<p>Data Logger never sends your data anywhere. It only talks to the serial port you choose and writes files to the folder you choose. The only exception: when you click <b>Check for updates</b>, it reads the latest version number from GitHub.</p>
"""),
    },
}

HELP_CSS = """
body { color: #e6edf3; font-size: 10pt; }
h2 { color: #ffffff; font-size: 15pt; margin: 0 0 8px 0; }
h3 { color: #58a6ff; font-size: 11pt; margin: 14px 0 4px 0; }
p, li { line-height: 140%; }
code { color: #a5d6ff; background-color: #161b22; }
pre { color: #a5d6ff; background-color: #010409; padding: 8px; font-size: 9pt; }
table { border-collapse: collapse; margin: 6px 0; }
th { background-color: #1c2333; color: #e6edf3; padding: 6px; text-align: left; }
td { border-top: 1px solid #30363d; padding: 6px; vertical-align: top; }
.tip { background-color: #121d2f; padding: 8px; }
a { color: #58a6ff; }
"""


def topics(lang: str) -> list[tuple[str, str]]:
    """[(anahtar, başlık)]"""
    table = GUIDE.get(lang, GUIDE["tr"])
    return [(k, table[k][0]) for k in TOPICS]


def body_html(lang: str, key: str, img_width, img_exists=lambda name: True) -> str:
    """img_width: sayı ya da ad -> genişlik veren fonksiyon (küçük görseller büyütülmesin diye)."""
    table = GUIDE.get(lang, GUIDE["tr"])
    html = table[key][1]
    import re

    def repl(m):
        name = m.group(1)
        if not img_exists(name):
            return ""
        w = img_width(name) if callable(img_width) else img_width
        hint = "🔍 Büyütmek için görsele tıklayın" if lang == "tr" else "🔍 Click the image to enlarge"
        return (f'<p><a href="img:{name}"><img src="{lang}/{name}.png" width="{w}"></a><br>'
                f'<span style="color:#6e7681; font-size:8.5pt">{hint}</span></p>')

    return re.sub(r"\{img:(\w+)\}", repl, html)


def image_names() -> set[str]:
    import re

    out = set()
    for lang in GUIDE.values():
        for _, body in lang.values():
            out |= set(re.findall(r"\{img:(\w+)\}", body))
    return out

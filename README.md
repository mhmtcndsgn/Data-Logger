<p align="center">
  <img src="assets/icon.png" width="96" alt="Data Logger icon">
</p>

<h1 align="center">Data Logger</h1>

<p align="center">
  <b>🇬🇧 English</b> · <a href="README.tr.md">🇹🇷 Türkçe</a>
</p>

<p align="center">
  Lossless serial data logger for <b>STM32, Arduino, ESP32</b> and any board that prints lines over a serial port.<br>
  Live chart, gap detection, and one-click export to <b>Excel / CSV / TXT</b>.
</p>

<p align="center">
  <a href="https://github.com/mhmtcndsgn/Data-Logger/releases/latest/download/Data_Logger_Windows.zip"><img src="https://img.shields.io/badge/Download-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Download for Windows"></a>
  <a href="https://github.com/mhmtcndsgn/Data-Logger/releases/latest/download/Data_Logger_macOS.dmg"><img src="https://img.shields.io/badge/Download-macOS-000000?style=for-the-badge&logo=apple&logoColor=white" alt="Download for macOS"></a>
  <br>
  <a href="https://github.com/mhmtcndsgn/Data-Logger/releases/latest"><img src="https://img.shields.io/github/v/release/mhmtcndsgn/Data-Logger?label=latest&style=flat-square" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT license">
</p>

![Data Logger](docs/screenshot.png)

---

## ✨ Features

- **Zero data loss.** Reading runs in its own thread and never waits on the disk or the screen, so high-speed bursts (e.g. a DMA buffer dumped at 921600 baud) arrive complete. Tested with a 300,000-line burst at ~125,000 lines/s.
- **Gap detection.** If the board sends a sequence number and `START,N` / `END,N` markers, every lost line is counted and highlighted in red on the chart.
- **Two modes**
  - **Live monitor:** data streams onto the chart as it arrives.
  - **Experiment dump:** the board records into memory and sends everything at the end; the app detects the end of the transfer, saves it automatically and waits for the next one.
- **Excel, CSV or TXT.** Excel files include a summary sheet (integrity, min/max/mean), the data and a chart. A raw backup of every received byte is kept as well.
- **Fast live chart** with zoom/pan and PNG export; 1 million points render in about a second.
- **Board detection:** STM32 (ST-Link), Arduino, ESP32, CH340, CP2102, FTDI and Raspberry Pi Pico ports are marked with ★.
- **Send commands** to the board (e.g. `SEND` to request a new dump).
- **English / Turkish** interface, settings are remembered.
- **DEMO port** to try everything without a board.

![Gap detection](docs/screenshot_gap.png)

---

## ⬇️ Install

### Windows 10 / 11
1. Download **[Data_Logger_Windows.zip](https://github.com/mhmtcndsgn/Data-Logger/releases/latest/download/Data_Logger_Windows.zip)**.
2. **Before extracting:** right-click the zip → **Properties** → tick **Unblock** at the bottom → **OK**.
   *This prevents the "Do you want to run this file?" / SmartScreen warning. The app is not code-signed yet (see [Code signing](#-code-signing-policy)).*
3. Extract and run **`Data_Logger.exe`**. Keep it next to its `_internal` folder.

### macOS
1. Download **[Data_Logger_macOS.dmg](https://github.com/mhmtcndsgn/Data-Logger/releases/latest/download/Data_Logger_macOS.dmg)** and drag the app to **Applications**.
2. First launch: right-click the app → **Open** (or **System Settings → Privacy & Security → Open Anyway**).

---

## 🚀 Usage

1. Select the port (known boards are marked ★) and the same baud rate as your firmware.
2. Choose **Live monitor** or **Experiment dump** and click **Connect**.
3. Files are saved to `Documents\Data Logger` by default. **Open saved file…** reopens any earlier recording, including files from v1.

---

## 📡 Data format (board side)

The app understands all of these, one per line:

```
1450                      single value
12,345,678                multiple channels (comma, semicolon, space or tab)
Temp:25.3 Hum:60          named channels
time,adc1,adc2            header line (before data) → channel names
START,4000 / END,4000     start / end of a dump
```

**Recommended for loss detection:** a sequence number in the first column, plus `START,N` and `END,N`:

```
START,4000
0,2048
1,2051
...
3999,2040
END,4000
```

Ready-made examples:
- **STM32 (HAL):** [`firmware_ornek/veri_gonder.c`](firmware_ornek/veri_gonder.c): timer-triggered ADC + DMA + UART dump
- **Arduino / ESP32 / ESP8266:** [`firmware_ornek/arduino_ornek/arduino_ornek.ino`](firmware_ornek/arduino_ornek/arduino_ornek.ino): live mode, or a dump on the `GONDER` command

> ⚠️ **STM32 users:** if the ADC DMA runs in **Circular** mode while you transmit, the buffer wraps and overwrites old samples, which looks like "jumping" data. Use **Normal** mode and call `HAL_ADC_Stop_DMA` before sending.

---

## 🛠️ Run from source

```bash
pip install -r requirements.txt
python main.py
```
On Windows you can also double-click **`baslat.bat`**: it sets everything up on first run.

Tests: `pip install pytest && python -m pytest tests`

### Releasing a new version
**Actions → Build Data Logger → Run workflow**, type a version such as `v2.0.1`, then click **Run**. Windows and macOS builds are tested automatically, published under **Releases**, and the download buttons above always point to the latest one.

### Project layout
```
main.py                     entry point
stm32logger/                application package
  engine.py                 lossless serial reader + DEMO port
  parser.py / session.py    line parsing, sequence / gap detection
  exporter.py / importer.py Excel / CSV / TXT
  ui/                       PySide6 + pyqtgraph interface
firmware_ornek/             STM32 and Arduino/ESP32 examples
packaging/                  Windows version info for the .exe
tests/                      tests (incl. a 300k-line stress test)
```

---

## 🔏 Code signing policy

Windows builds are produced only by the public GitHub Actions workflow in this repository, from the source code in this repository. Free code signing through [SignPath Foundation](https://signpath.org) has been applied for. Until it is approved, releases are unsigned.

- **Committers and reviewers:** [mhmtcndsgn](https://github.com/mhmtcndsgn)
- **Approvers:** [mhmtcndsgn](https://github.com/mhmtcndsgn)

### Privacy policy
This program does not transfer any information to other networked systems. It only communicates with the serial device you select and writes files to the folder you choose.

---

## 📄 License

[MIT](LICENSE) © 2026 Mehmet Can

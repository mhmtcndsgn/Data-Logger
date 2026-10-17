"""Kılavuz görsellerini (assets/help/<dil>/*.png) uygulamanın kendisinden üretir.

Arayüz değiştiğinde çalıştırın:
    python packaging/make_help_images.py
Ekran olmadan da çalışır (QT_QPA_PLATFORM=offscreen). Numaralı işaretler (1, 2, 3…)
kılavuz metnindeki ①②③ ile aynı sıradadır (bkz. stm32logger/help.py).
"""
import math
import os
import sys
import tempfile
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.argv.append("--no-first-run")

from PySide6.QtCore import QPoint, QRect, QRectF, QSettings, Qt  # noqa: E402
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from stm32logger import ORG_NAME  # noqa: E402
from stm32logger.engine import DEMO_PORT  # noqa: E402
from stm32logger.parser import parse_line  # noqa: E402
from stm32logger.session import Session  # noqa: E402

ACCENT = QColor("#e3b341")
OUT = os.path.join(ROOT, "assets", "help")


def pump(app, sec):
    t = time.time()
    while time.time() - t < sec:
        app.processEvents()
        time.sleep(0.01)


def wrect(win, widget) -> QRect:
    return QRect(widget.mapTo(win, QPoint(0, 0)), widget.size())


def union(*rects) -> QRect:
    r = QRect(rects[0])
    for x in rects[1:]:
        r = r.united(x)
    return r


def scene_rect(win, plot, item) -> QRect:
    poly = plot.mapFromScene(item.sceneBoundingRect())
    r = poly.boundingRect().intersected(plot.viewport().rect())
    return QRect(plot.viewport().mapTo(win, r.topLeft()), r.size())


def annotate(pix, marks, crop: QRect, path):
    """marks: [(rect_in_window, numara)]"""
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    f = QFont()
    f.setBold(True)
    f.setPixelSize(13)
    p.setFont(f)
    for rect, num in marks:
        r = QRectF(rect).adjusted(-3, -3, 3, 3)
        p.setPen(QPen(ACCENT, 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(r, 7, 7)
        d = 22
        cx = max(crop.left() + d / 2 + 1, r.left())
        cy = max(crop.top() + d / 2 + 1, r.top())
        badge = QRectF(cx - d / 2, cy - d / 2, d, d)
        p.setPen(QPen(QColor("#0d1117"), 2))
        p.setBrush(QBrush(ACCENT))
        p.drawEllipse(badge)
        p.setPen(QColor("#0d1117"))
        p.drawText(badge, Qt.AlignCenter, str(num))
    p.end()
    img = pix.copy(crop)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", 85)
    print("  ", os.path.relpath(path, ROOT), img.width(), "x", img.height())


WIN_FOLDER = r"C:\Users\user\Documents\Data Logger"


def tidy(w):
    """Görsellerde Linux geçici yolları görünmesin: Windows'taki gibi göster."""
    name = os.path.basename(w.last_saved or "deney.xlsx")
    w.folder_edit.setText(WIN_FOLDER)
    w.term.clear()
    w.term.appendPlainText("3997,2031,2129\n3998,2043,2123\n3999,2036,2119\nEND,4000")
    w._log(w.t("msg_saved", path=WIN_FOLDER + "\\" + name), "ok")


def numbered(rects):
    return [(r, i) for i, r in enumerate(rects, start=1)]


def make(lang: str, app) -> None:
    from stm32logger.ui.main_window import MainWindow

    QSettings(ORG_NAME, "DataLogger").clear()
    w = MainWindow()
    w._ask = lambda *a: "alt"          # kapanışta "kaydedilmemiş veri" sorusu çıkmasın
    w.lang_cb.setCurrentIndex(0 if lang == "tr" else 1)
    w.folder_edit.setText(tempfile.mkdtemp(prefix="help_"))
    w.prefix_edit.setText("deney" if lang == "tr" else "experiment")
    w.fs_spin.setValue(1000)
    w.baud_cb.setCurrentText("115200")
    w.seg_mode.set_value("dma")
    w._on_mode_changed("dma")
    w.port_cb.setCurrentIndex(w.port_cb.findData(DEMO_PORT))
    w.resize(1360, 860)
    w.show()
    pump(app, 0.5)
    d = os.path.join(OUT, lang)

    # --- modes: aktarım sürerken üst kutucuklar + ilerleme çubuğu
    w._connect()
    t0 = time.time()
    while time.time() - t0 < 8 and not (w.progress.isVisible() and w.progress.value() > 350):
        pump(app, 0.05)
    pump(app, 0.1)
    pix = w.grab()
    crop = union(wrect(w, w.tile_rows), wrect(w, w.tile_status), wrect(w, w.progress)).adjusted(-14, -14, 14, 14)
    annotate(pix, numbered([wrect(w, w.tile_rows), wrect(w, w.progress), wrect(w, w.tile_status)]),
             crop, os.path.join(d, "modes.png"))

    # --- quickstart: aktarım bitti, bant görünüyor
    t0 = time.time()
    while time.time() - t0 < 15 and not w.last_saved:
        pump(app, 0.05)
    w._disconnect()
    pump(app, 0.6)
    tidy(w)
    pump(app, 0.2)
    pix = w.grab()
    marks = [wrect(w, w.port_cb), wrect(w, w.seg_mode), wrect(w, w.btn_connect),
             union(wrect(w, w.tile_rows), wrect(w, w.tile_status)), wrect(w, w.banner), wrect(w, w.plot)]
    annotate(pix, numbered(marks), w.rect(), os.path.join(d, "quickstart.png"))

    # --- chart: grafik + terminal
    w.term.appendPlainText("SEND" if lang == "en" else "GONDER")
    pix = w.grab()
    plot_panel = w.plot.parentWidget()
    term_panel = w.term.parentWidget()
    crop = union(wrect(w, plot_panel), wrect(w, term_panel)).adjusted(-8, -8, 8, 8)
    marks = [wrect(w, w.x_cb), wrect(w, w.win_cb), wrect(w, w.btn_fit), wrect(w, w.btn_png),
             scene_rect(w, w.plot, w.legend), union(wrect(w, w.chk_hex), wrect(w, w.btn_clear)),
             union(wrect(w, w.send_edit), wrect(w, w.btn_send))]
    annotate(pix, numbered(marks), crop, os.path.join(d, "chart.png"))

    # --- connect + saving: yan panel tamamı görünsün diye pencereyi uzat
    w.resize(1360, 1260)
    pump(app, 0.5)
    pix = w.grab()
    crop = union(wrect(w, w.card_conn), wrect(w, w.card_data)).adjusted(-10, -10, 10, 10)
    marks = [wrect(w, w.port_cb), wrect(w, w.btn_refresh), wrect(w, w.baud_cb), wrect(w, w.seg_mode),
             wrect(w, w.chk_reconnect), wrect(w, w.btn_connect), wrect(w, w.fs_spin), wrect(w, w.seq_cb),
             wrect(w, w.idle_spin)]
    annotate(pix, numbered(marks), crop, os.path.join(d, "connect.png"))

    pix = w.grab()
    crop = wrect(w, w.card_save).adjusted(-10, -10, 10, 10)
    marks = [wrect(w, w.seg_fmt), union(wrect(w, w.folder_edit), wrect(w, w.btn_browse)), wrect(w, w.prefix_edit),
             wrect(w, w.chk_auto), wrect(w, w.chk_raw), wrect(w, w.btn_save_as), wrect(w, w.btn_open_folder),
             wrect(w, w.btn_open_saved)]
    annotate(pix, numbered(marks), crop, os.path.join(d, "saving.png"))

    # --- trouble: kayıplı bir aktarım
    w.resize(1360, 860)
    w.chk_auto.setChecked(False)
    pump(app, 0.3)
    s = Session(mode="dma", sample_rate=1000, port="COM5", baud=921600, channel_prefix=w.t("channel_prefix"))
    s.add(0, parse_line("START,3000"))
    for i in range(3000):
        if 1450 < i < 1780:
            continue
        a = 2048 + 1200 * math.sin(i / 90) * math.exp(-i / 1500)
        b = 2048 + 500 * math.cos(i / 160) * math.exp(-i / 2500)
        s.add(0, parse_line(f"{i},{a:.0f},{b:.0f}"))
    s.add(0, parse_line("END,3000"))
    s.finish("end")
    w._on_session_done(s)
    pump(app, 1.0)
    pix = w.grab()
    crop = union(wrect(w, w.tile_rows), wrect(w, w.plot)).adjusted(-12, -12, 12, 12)
    marks = [wrect(w, w.banner), wrect(w, w.tile_missing), scene_rect(w, w.plot, w._gap_items[0])]
    annotate(pix, numbered(marks), crop, os.path.join(d, "trouble.png"))

    w.close()
    w.deleteLater()
    pump(app, 0.2)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    f = QFont()
    f.setFamilies(["Segoe UI", "Inter", "DejaVu Sans"])
    f.setPointSizeF(9.5)
    app.setFont(f)
    from stm32logger.ui import theme
    from stm32logger.ui.main_window import ASSETS

    app.setStyleSheet(theme.build_qss(ASSETS))
    for lang in ("tr", "en"):
        print(lang)
        make(lang, app)
    QSettings(ORG_NAME, "DataLogger").clear()


if __name__ == "__main__":
    main()

"""Veri Kaydedici — giriş noktası.

Kaynak koddan çalıştırma:
    pip install -r requirements.txt
    python main.py
"""
import datetime
import os
import sys
import traceback
from pathlib import Path


def _crash_log_path() -> str:
    base = Path.home() / "Documents"
    if not base.exists():
        base = Path.home()
    return str(base / "veri_kaydedici_hata.txt")


def _excepthook(exc_type, exc, tb):
    err = "".join(traceback.format_exception(exc_type, exc, tb))
    path = _crash_log_path()
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n===== {datetime.datetime.now():%Y-%m-%d %H:%M:%S} =====\n{err}")
    except OSError:
        pass
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        if QApplication.instance():
            from stm32logger.i18n import T

            QMessageBox.critical(None, "Veri Kaydedici", T("tr")("crash", path=path) + "\n\n" + err[-1500:])
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc, tb)


def main() -> int:
    sys.excepthook = _excepthook
    if sys.platform == "win32":
        # Görev çubuğunda Python yerine uygulamanın kendi ikonu görünsün
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mhmtcndsgn.verikaydedici")
        except Exception:
            pass

    from PySide6.QtGui import QFont, QIcon
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("Veri Kaydedici")
    app.setOrganizationName("mhmtcndsgn")
    app.setStyle("Fusion")

    font = QFont()
    font.setFamilies(["Segoe UI", "Inter", "SF Pro Text", "Helvetica Neue", "Arial"])
    font.setPointSizeF(9.5)
    app.setFont(font)

    from stm32logger.ui import theme
    from stm32logger.ui.main_window import ASSETS, MainWindow

    app.setStyleSheet(theme.build_qss(ASSETS))
    icon = ASSETS / "icon.png"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))

    win = MainWindow()
    win.show()
    if "--selftest" in sys.argv:
        _selftest(app, win)
    return app.exec()


def _selftest(app, win) -> None:
    """Paketlenmiş uygulamanın uçtan uca çalıştığını doğrular (CI'da kullanılır).

    Veri_Kaydedici --selftest sonuc.txt
    DEMO portuna bağlanır, bir deney aktarımı alır, Excel + PNG kaydeder, çıkar.
    """
    import tempfile
    import time

    from PySide6.QtCore import QTimer

    from stm32logger.engine import DEMO_PORT

    i = sys.argv.index("--selftest")
    out = sys.argv[i + 1] if len(sys.argv) > i + 1 else "selftest.txt"
    d = tempfile.mkdtemp(prefix="verikaydedici_")
    win.folder_edit.setText(d)
    win.seg_mode.set_value("dma")
    win._on_mode_changed("dma")
    win.seg_fmt.set_value("xlsx")
    win.chk_auto.setChecked(True)
    win.baud_cb.setCurrentText("921600")
    win.port_cb.setCurrentIndex(win.port_cb.findData(DEMO_PORT))
    win._connect()
    deadline = time.time() + 40

    def finish(ok: bool, msg: str) -> None:
        with open(out, "w", encoding="utf-8") as f:
            f.write(("OK " if ok else "FAIL ") + msg + "\n")
        win._disconnect()
        app.exit(0 if ok else 1)

    def poll() -> None:
        try:
            if win.last_saved and os.path.exists(win.last_saved):
                from pyqtgraph.exporters import ImageExporter

                png = os.path.join(d, "grafik.png")
                ImageExporter(win.plot.getPlotItem()).export(png)
                v = win.view
                ok = v is not None and v.n == 4000 and v.missing == 0 and os.path.getsize(png) > 1000
                finish(ok, f"rows={v.n if v else 0} missing={v.missing if v else '?'} xlsx={win.last_saved}")
                return
            if time.time() > deadline:
                finish(False, "timeout")
                return
        except Exception as e:  # noqa: BLE001
            finish(False, repr(e))
            return
        QTimer.singleShot(200, poll)

    QTimer.singleShot(200, poll)


if __name__ == "__main__":
    sys.exit(main())

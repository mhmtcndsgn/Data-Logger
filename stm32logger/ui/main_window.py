"""Ana pencere."""
from __future__ import annotations

import collections
import datetime as _dt
import html
import os
import queue
import threading
import time
from bisect import bisect_left
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QSettings, QStandardPaths, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QFontDatabase, QIcon, QIntValidator, QPixmap, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFrame,
                               QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit,
                               QProgressBar, QPushButton, QScrollArea, QSplitter, QVBoxLayout, QWidget)

from .. import APP_NAME, ORG_NAME, __version__
from ..engine import DEMO_PORT, Engine, list_ports, open_port
from ..exporter import FORMATS, default_filename, export_session
from ..i18n import T
from ..session import Session
from . import theme as th
from .widgets import Card, PanelHeader, Segmented, Tile, guard_wheel, hint_label, hrow

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"
BAUDS = ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600", "1000000", "2000000"]
WINDOWS = [10, 30, 60, 300, 0]  # sn, 0 = tümü
TERM_MAX_PER_TICK = 400


def _fmt_dur(sec: float) -> str:
    sec = max(0, int(sec))
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(ORG_NAME, "STM32VeriKaydedici")
        self.lang = str(self.settings.value("lang", "tr"))
        self.t = T(self.lang)

        self.engine: Engine | None = None
        self.view: Session | None = None          # ekranda gösterilen oturum
        self.banner_session: Session | None = None
        self.last_saved: str | None = None
        self._export_q: queue.SimpleQueue = queue.SimpleQueue()
        self._export_threads: list[threading.Thread] = []
        self._reserved: set[str] = set()   # yazılmakta olan dosyalar (aynı ada iki kayıt olmasın)
        self._rate = collections.deque()
        self._conn_t0 = 0.0
        self._conn_info = ("", 0, "live")
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._gap_items: list = []
        self._plot_t = 0.0
        self._plot_dur = 0.0
        self._curve_owner = None
        self._plot_sig = None
        self._port_sig = None

        self.setWindowTitle(APP_NAME)
        icon = ASSETS / "icon.png"
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))
        self.resize(1360, 860)
        self.setMinimumSize(1080, 700)

        self._build()
        guard_wheel(self.port_cb, self.baud_cb, self.fs_spin, self.seq_cb, self.idle_spin,
                    self.x_cb, self.win_cb, self.eol_cb, self.lang_cb)
        self._load_settings()
        self.retranslate()
        self._refresh_ports(initial=True)
        self._set_controls_enabled(True)
        self._on_mode_changed(self.seg_mode.value())
        self._update_stats()

        self.ui_timer = QTimer(self, interval=50, timeout=self._tick)
        self.ui_timer.start()
        self.plot_timer = QTimer(self, interval=200, timeout=self._update_plot)
        self.plot_timer.start()
        self.port_timer = QTimer(self, interval=2000, timeout=lambda: self._refresh_ports(silent=True))
        self.port_timer.start()

    # ================================================================ ARAYÜZ
    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(16, 14, 16, 12)
        body.setSpacing(14)
        v.addLayout(body, 1)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_main(), 1)
        self._build_statusbar()

    def _build_header(self) -> QWidget:
        hdr = QFrame()
        hdr.setObjectName("Header")
        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(20, 10, 20, 10)
        lay.setSpacing(10)
        logo = QLabel()
        pm = QPixmap(str(ASSETS / "icon.png"))
        if not pm.isNull():
            logo.setPixmap(pm.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setStyleSheet("background: transparent;")
        lay.addWidget(logo)
        a = QLabel("STM32")
        a.setObjectName("TitleBlue")
        self.lbl_title = QLabel()
        self.lbl_title.setObjectName("TitleMain")
        lay.addWidget(a)
        lay.addWidget(self.lbl_title)
        lay.addStretch(1)
        self.lbl_lang = QLabel()
        self.lbl_lang.setObjectName("Version")
        self.lang_cb = QComboBox()
        self.lang_cb.addItem("Türkçe", "tr")
        self.lang_cb.addItem("English", "en")
        self.lang_cb.setCurrentIndex(0 if self.lang == "tr" else 1)
        self.lang_cb.setFixedWidth(110)
        self.lang_cb.currentIndexChanged.connect(lambda _: self._set_lang(self.lang_cb.currentData()))
        ver = QLabel(f"v{__version__}")
        ver.setObjectName("Version")
        lay.addWidget(self.lbl_lang)
        lay.addWidget(self.lang_cb)
        lay.addSpacing(10)
        lay.addWidget(ver)
        return hdr

    def _build_sidebar(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setObjectName("Sidebar")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedWidth(332)
        inner = QWidget()
        inner.setObjectName("SidebarInner")
        col = QVBoxLayout(inner)
        col.setContentsMargins(0, 0, 8, 0)
        col.setSpacing(12)

        # --- Bağlantı ---
        c = self.card_conn = Card()
        self.lbl_port = c.label()
        self.port_cb = QComboBox()
        self.port_cb.setMinimumContentsLength(10)
        self.port_cb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.setObjectName("Icon")
        self.btn_refresh.clicked.connect(lambda: self._refresh_ports(manual=True))
        c.add(hrow(self.port_cb, self.btn_refresh))
        self.lbl_baud = c.label()
        self.baud_cb = QComboBox()
        self.baud_cb.setEditable(True)
        self.baud_cb.addItems(BAUDS)
        self.baud_cb.lineEdit().setValidator(QIntValidator(300, 20_000_000, self))
        c.add(self.baud_cb)
        self.lbl_mode = c.label()
        self.seg_mode = Segmented(["live", "dma"])
        self.seg_mode.changed.connect(self._on_mode_changed)
        c.add(self.seg_mode)
        self.lbl_mode_hint = hint_label()
        c.add(self.lbl_mode_hint)
        c.lay.addSpacing(6)
        self.btn_connect = QPushButton()
        self.btn_connect.setObjectName("Primary")
        self.btn_connect.setCursor(Qt.PointingHandCursor)
        self.btn_connect.clicked.connect(self._toggle_connect)
        c.add(self.btn_connect)
        col.addWidget(c)

        # --- Veri ayarları ---
        c = self.card_data = Card()
        self.lbl_fs = c.label()
        self.fs_spin = QDoubleSpinBox()
        self.fs_spin.setRange(0, 10_000_000)
        self.fs_spin.setDecimals(2)
        self.fs_spin.setSuffix(" Hz")
        self.fs_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        c.add(self.fs_spin)
        self.lbl_seq = c.label()
        self.seq_cb = QComboBox()
        for k in ("auto", "on", "off"):
            self.seq_cb.addItem(k, k)
        c.add(self.seq_cb)
        self.lbl_idle = c.label()
        self.idle_spin = QDoubleSpinBox()
        self.idle_spin.setRange(0.2, 60)
        self.idle_spin.setDecimals(1)
        self.idle_spin.setSingleStep(0.5)
        self.idle_spin.setSuffix(" s")
        self.idle_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        c.add(self.idle_spin)
        col.addWidget(c)

        # --- Kayıt ---
        c = self.card_save = Card()
        self.lbl_fmt = c.label()
        self.seg_fmt = Segmented(["xlsx", "csv", "txt"])
        self.seg_fmt.set_texts({"xlsx": "Excel", "csv": "CSV", "txt": "TXT"})
        c.add(self.seg_fmt)
        self.lbl_folder = c.label()
        self.folder_edit = QLineEdit()
        self.btn_browse = QPushButton()
        self.btn_browse.clicked.connect(self._browse_folder)
        c.add(hrow(self.folder_edit, self.btn_browse))
        self.lbl_prefix = c.label()
        self.prefix_edit = QLineEdit()
        c.add(self.prefix_edit)
        c.lay.addSpacing(4)
        self.chk_auto = QCheckBox()
        self.chk_raw = QCheckBox()
        c.add(self.chk_auto)
        c.add(self.chk_raw)
        c.lay.addSpacing(4)
        self.btn_save_as = QPushButton()
        self.btn_save_as.clicked.connect(self._save_as)
        self.btn_open_folder = QPushButton()
        self.btn_open_folder.clicked.connect(self._open_folder)
        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(self.btn_save_as, 1)
        row.addWidget(self.btn_open_folder, 1)
        c.add(row)
        self.btn_open_saved = QPushButton()
        self.btn_open_saved.clicked.connect(self._open_saved_file)
        c.add(self.btn_open_saved)
        col.addWidget(c)
        col.addStretch(1)

        scroll.setWidget(inner)
        return scroll

    def _build_main(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        tiles = QHBoxLayout()
        tiles.setSpacing(10)
        self.tile_rows, self.tile_rate, self.tile_missing, self.tile_dur, self.tile_status = (Tile() for _ in range(5))
        for tl in (self.tile_rows, self.tile_rate, self.tile_missing, self.tile_dur, self.tile_status):
            tiles.addWidget(tl, 1)
        v.addLayout(tiles)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setTextVisible(True)
        self.progress.setFixedHeight(14)
        self.progress.hide()
        v.addWidget(self.progress)

        # --- Sonuç bandı ---
        self.banner = QFrame()
        self.banner.setObjectName("Banner")
        bl = QHBoxLayout(self.banner)
        bl.setContentsMargins(14, 8, 8, 8)
        self.banner_lbl = QLabel()
        self.banner_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.banner_open = QPushButton()
        self.banner_open.setObjectName("Link")
        self.banner_open.clicked.connect(lambda: self._open_path(self.last_saved))
        self.banner_folder = QPushButton()
        self.banner_folder.setObjectName("Link")
        self.banner_folder.clicked.connect(self._open_folder)
        self.banner_close = QPushButton("✕")
        self.banner_close.setObjectName("Link")
        self.banner_close.clicked.connect(self.banner.hide)
        bl.addWidget(self.banner_lbl, 1)
        bl.addWidget(self.banner_open)
        bl.addWidget(self.banner_folder)
        bl.addWidget(self.banner_close)
        self.banner.hide()
        v.addWidget(self.banner)

        split = self.splitter = QSplitter(Qt.Vertical)
        split.setChildrenCollapsible(False)
        split.addWidget(self._build_plot_panel())
        split.addWidget(self._build_terminal_panel())
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        split.setSizes([480, 260])
        v.addWidget(split, 1)
        return w

    def _build_plot_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        v = QVBoxLayout(panel)
        v.setContentsMargins(12, 10, 12, 12)
        v.setSpacing(4)
        h = self.plot_hdr = PanelHeader()
        self.lbl_x = h.add(QLabel())
        self.lbl_x.setObjectName("FieldLabel")
        self.x_cb = h.add(QComboBox())
        for k in ("auto", "sample", "time", "host"):
            self.x_cb.addItem(k, k)
        self.x_cb.currentIndexChanged.connect(self._invalidate_plot)
        self.lbl_win = h.add(QLabel())
        self.lbl_win.setObjectName("FieldLabel")
        self.win_cb = h.add(QComboBox())
        for s in WINDOWS:
            self.win_cb.addItem(str(s), s)
        self.win_cb.currentIndexChanged.connect(self._invalidate_plot)
        self.btn_fit = h.add(QPushButton())
        self.btn_fit.clicked.connect(self._fit_plot)
        self.btn_png = h.add(QPushButton())
        self.btn_png.clicked.connect(self._save_png)
        v.addWidget(h)

        pg.setConfigOptions(antialias=True, background=th.BG_PLOT, foreground=th.MUTED)
        self.plot = pg.PlotWidget()
        pi = self.plot.getPlotItem()
        pi.showGrid(x=True, y=True, alpha=0.12)
        pi.setClipToView(True)
        pi.setDownsampling(auto=True, mode="peak")
        for ax in ("left", "bottom"):
            a = pi.getAxis(ax)
            a.setPen(pg.mkPen(th.BORDER))
            a.setTextPen(pg.mkPen(th.MUTED))
        self.legend = pi.addLegend(offset=(12, 8), labelTextColor=th.TEXT,
                                   brush=pg.mkBrush(22, 27, 34, 220), pen=pg.mkPen(th.BORDER))
        self.legend.setVisible(False)
        v.addWidget(self.plot, 1)
        return panel

    def _build_terminal_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        v = QVBoxLayout(panel)
        v.setContentsMargins(12, 10, 12, 12)
        v.setSpacing(6)
        h = self.term_hdr = PanelHeader()
        self.chk_pause = h.add(QCheckBox())
        self.btn_clear = h.add(QPushButton())
        self.btn_clear.clicked.connect(lambda: self.term.clear())
        v.addWidget(h)

        self.term = QPlainTextEdit()
        self.term.setReadOnly(True)
        self.term.setMaximumBlockCount(3000)
        self.term.setLineWrapMode(QPlainTextEdit.NoWrap)
        mono = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        for fam in ("Cascadia Mono", "Consolas", "JetBrains Mono", "SF Mono", "Menlo", "DejaVu Sans Mono"):
            if fam in QFontDatabase.families():
                mono = QFont(fam)
                break
        mono.setPointSizeF(9.5)
        self.term.setFont(mono)
        v.addWidget(self.term, 1)

        self.send_edit = QLineEdit()
        self.send_edit.returnPressed.connect(self._send)
        self.eol_cb = QComboBox()
        self.eol_cb.addItem("\\r\\n", "\r\n")
        self.eol_cb.addItem("\\n", "\n")
        self.eol_cb.addItem("-", "")
        self.btn_send = QPushButton()
        self.btn_send.setObjectName("Accent")
        self.btn_send.clicked.connect(self._send)
        v.addLayout(hrow(self.send_edit, self.eol_cb, self.btn_send))
        return panel

    def _build_statusbar(self) -> None:
        sb = self.statusBar()
        sb.setSizeGripEnabled(False)
        self.status_dot = QLabel("●")
        self.status_lbl = QLabel()
        sb.addWidget(self.status_dot)
        sb.addWidget(self.status_lbl, 1)
        self.saved_btn = QPushButton()
        self.saved_btn.setObjectName("Link")
        self.saved_btn.clicked.connect(lambda: self._open_path(self.last_saved))
        self.saved_btn.hide()
        sb.addPermanentWidget(self.saved_btn)
        self._set_status_dot(False)

    # ================================================================ METİNLER
    def retranslate(self) -> None:
        t = self.t
        self.lbl_title.setText(t("app_title"))
        self.lbl_lang.setText(t("language"))
        self.card_conn.title.setText(t("card_conn"))
        self.lbl_port.setText(t("port"))
        self.btn_refresh.setToolTip(t("refresh"))
        self.lbl_baud.setText(t("baud"))
        self.lbl_mode.setText(t("mode"))
        self.seg_mode.set_texts({"live": t("mode_live"), "dma": t("mode_dma")})
        self.lbl_mode_hint.setText(t("mode_" + self.seg_mode.value() + "_hint"))
        self._style_connect_button()

        self.card_data.title.setText(t("card_data"))
        self.lbl_fs.setText(t("fs"))
        self.fs_spin.setSpecialValueText(t("fs_unknown"))
        self.fs_spin.setToolTip(t("fs_tip"))
        self.lbl_fs.setToolTip(t("fs_tip"))
        self.lbl_seq.setText(t("seq"))
        for i, k in enumerate(("seq_auto", "seq_on", "seq_off")):
            self.seq_cb.setItemText(i, t(k))
        self.seq_cb.setToolTip(t("seq_tip"))
        self.lbl_idle.setText(t("idle"))
        self.idle_spin.setToolTip(t("idle_tip"))

        self.card_save.title.setText(t("card_save"))
        self.lbl_fmt.setText(t("format"))
        self.seg_fmt.setToolTip(t("format_tip"))
        self.lbl_folder.setText(t("folder"))
        self.btn_browse.setText(t("browse"))
        self.lbl_prefix.setText(t("prefix"))
        self.chk_auto.setText(t("autosave"))
        self.chk_raw.setText(t("rawbackup"))
        self.chk_raw.setToolTip(t("rawbackup_tip"))
        self.btn_save_as.setText(t("save_now"))
        self.btn_open_folder.setText(t("open_folder"))
        self.btn_open_saved.setText(t("open_saved"))

        self.tile_rows.label.setText(t("st_rows").upper())
        self.tile_rate.label.setText(t("st_rate").upper())
        self.tile_missing.label.setText(t("st_missing").upper())
        self.tile_dur.label.setText(t("st_duration").upper())
        self.tile_status.label.setText(t("st_status").upper())

        self.plot_hdr.title.setText(t("plot_title"))
        self.lbl_x.setText(t("x_axis"))
        for i, k in enumerate(("x_auto", "x_sample", "x_time", "x_host")):
            self.x_cb.setItemText(i, t(k))
        self.lbl_win.setText(t("window"))
        for i, s in enumerate(WINDOWS):
            self.win_cb.setItemText(i, t("win_all") if s == 0 else (f"{s} s" if s < 60 else f"{s // 60} dk" if self.lang == "tr" else f"{s // 60} min"))
        self.btn_fit.setText(t("fit"))
        self.btn_png.setText(t("save_png"))
        self.plot.getPlotItem().setLabel("left", t("value"))

        self.term_hdr.title.setText(t("terminal"))
        self.chk_pause.setText(t("pause"))
        self.btn_clear.setText(t("clear"))
        self.send_edit.setPlaceholderText(t("send_placeholder"))
        self.btn_send.setText(t("send"))
        self.eol_cb.setItemText(2, t("eol_none"))
        self.banner_open.setText(t("open_file"))
        self.banner_folder.setText(t("open_folder"))

        idx = self.port_cb.findData(DEMO_PORT)
        if idx >= 0:
            self.port_cb.setItemText(idx, t("demo_port"))
        self._plot_sig = None
        self._update_status_text()

    def _set_lang(self, lang: str) -> None:
        if lang == self.lang:
            return
        self.lang = lang
        self.t = T(lang)
        self.settings.setValue("lang", lang)
        self.retranslate()
        self._update_stats(force=True)

    # ================================================================ AYARLAR
    def _default_folder(self) -> str:
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        return os.path.join(docs, "STM32 Kayitlari")

    def _load_settings(self) -> None:
        s = self.settings
        self.baud_cb.setCurrentText(str(s.value("baud", "115200")))
        self.seg_mode.set_value(str(s.value("mode", "dma")))
        self.fs_spin.setValue(float(s.value("fs", 0) or 0))
        i = self.seq_cb.findData(str(s.value("seq", "auto")))
        self.seq_cb.setCurrentIndex(max(0, i))
        self.idle_spin.setValue(float(s.value("idle", 1.0) or 1.0))
        self.seg_fmt.set_value(str(s.value("fmt", "xlsx")))
        self.folder_edit.setText(str(s.value("folder", "") or self._default_folder()))
        self.prefix_edit.setText(str(s.value("prefix", "deney")))
        self.chk_auto.setChecked(str(s.value("autosave", "true")).lower() == "true")
        self.chk_raw.setChecked(str(s.value("raw", "true")).lower() == "true")
        i = self.x_cb.findData(str(s.value("xaxis", "auto")))
        self.x_cb.setCurrentIndex(max(0, i))
        i = self.win_cb.findData(int(s.value("window", 30) or 0))
        self.win_cb.setCurrentIndex(i if i >= 0 else 1)
        i = self.eol_cb.findData(str(s.value("eol", "\r\n")))
        self.eol_cb.setCurrentIndex(max(0, i))
        geo = s.value("geometry")
        if geo is not None:
            self.restoreGeometry(geo)
        sp = s.value("splitter")
        if sp is not None:
            self.splitter.restoreState(sp)

    def _save_settings(self) -> None:
        s = self.settings
        s.setValue("port", self.port_cb.currentData() or "")
        s.setValue("baud", self.baud_cb.currentText())
        s.setValue("mode", self.seg_mode.value())
        s.setValue("fs", self.fs_spin.value())
        s.setValue("seq", self.seq_cb.currentData())
        s.setValue("idle", self.idle_spin.value())
        s.setValue("fmt", self.seg_fmt.value())
        s.setValue("folder", self.folder_edit.text())
        s.setValue("prefix", self.prefix_edit.text())
        s.setValue("autosave", "true" if self.chk_auto.isChecked() else "false")
        s.setValue("raw", "true" if self.chk_raw.isChecked() else "false")
        s.setValue("xaxis", self.x_cb.currentData())
        s.setValue("window", self.win_cb.currentData())
        s.setValue("eol", self.eol_cb.currentData())
        s.setValue("geometry", self.saveGeometry())
        s.setValue("splitter", self.splitter.saveState())
        s.setValue("lang", self.lang)

    # ================================================================ PORTLAR
    def _refresh_ports(self, initial=False, silent=False, manual=False) -> None:
        if self.engine is not None and not manual:
            return
        try:
            ports = list_ports()
        except Exception:
            ports = []
        sig = tuple((p, d) for p, d, _ in ports)
        if sig == self._port_sig and not initial:
            if manual:
                self._log(self.t("msg_ports", n=len(ports)), "info")
            return
        self._port_sig = sig
        cur = self.port_cb.currentData()
        if initial:
            cur = str(self.settings.value("port", "") or "")
        self.port_cb.blockSignals(True)
        self.port_cb.clear()
        for dev, desc, is_stm in ports:
            label = dev if desc == dev or desc in ("n/a", "") else f"{dev} — {desc}"
            self.port_cb.addItem(("★ " if is_stm else "") + label, dev)
            self.port_cb.setItemData(self.port_cb.count() - 1, desc, Qt.ToolTipRole)
        self.port_cb.addItem(self.t("demo_port"), DEMO_PORT)
        i = self.port_cb.findData(cur) if cur else -1
        if i < 0:
            stm = next((k for k, (_, _, s) in enumerate(ports) if s), None)
            i = stm if stm is not None else 0
            if initial and not ports:
                i = self.port_cb.findData(DEMO_PORT)
        self.port_cb.setCurrentIndex(i)
        self.port_cb.blockSignals(False)
        if not silent or manual:
            self._log(self.t("msg_ports", n=len(ports)) if ports else self.t("no_port"),
                      "info" if ports else "warn")
        elif ports and len(ports) > 0 and not initial:
            self._log(self.t("msg_ports", n=len(ports)), "info")

    # ================================================================ BAĞLANTI
    def _on_mode_changed(self, mode: str) -> None:
        self.lbl_mode_hint.setText(self.t("mode_" + mode + "_hint"))
        self.idle_spin.setEnabled(mode == "dma" and self.engine is None)
        self.lbl_idle.setEnabled(mode == "dma")
        self.win_cb.setEnabled(mode == "live")
        self._plot_sig = None

    def _style_connect_button(self) -> None:
        on = self.engine is not None
        self.btn_connect.setText(("■  " + self.t("disconnect")) if on else ("▶  " + self.t("connect")))
        self.btn_connect.setObjectName("Danger" if on else "Primary")
        self.btn_connect.style().unpolish(self.btn_connect)
        self.btn_connect.style().polish(self.btn_connect)

    def _toggle_connect(self) -> None:
        if self.engine is None:
            self._connect()
        else:
            self._disconnect()

    def _connect(self) -> None:
        t = self.t
        port = self.port_cb.currentData()
        if not port:
            QMessageBox.warning(self, t("err_title"), t("no_port"))
            return
        try:
            baud = int(self.baud_cb.currentText() or 115200)
        except ValueError:
            baud = 115200
        mode = self.seg_mode.value()
        try:
            ser = open_port(port, baud, mode)
        except Exception as e:
            self._log(t("msg_open_err", err=e), "error")
            QMessageBox.critical(self, t("err_title"), t("msg_open_err", err=e))
            return

        raw_path = None
        folder = self.folder_edit.text().strip() or self._default_folder()
        if self.chk_raw.isChecked():
            stamp = _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            safe_port = "".join(ch for ch in os.path.basename(port) if ch.isalnum()) or "port"
            raw_path = os.path.join(folder, "ham", f"ham_{stamp}_{safe_port}.txt")

        seq_mode = self.seq_cb.currentData()
        prefix = t("channel_prefix")
        fs = self.fs_spin.value()
        port_name = "DEMO" if port == DEMO_PORT else port

        def factory():
            return Session(mode=mode, seq_mode=seq_mode, channel_prefix=prefix,
                           port=port_name, baud=baud, sample_rate=fs)

        self.engine = Engine(ser, mode=mode, session_factory=factory, raw_path=raw_path,
                             idle_timeout=self.idle_spin.value())
        self.engine.start()
        self._conn_t0 = time.time()
        self._conn_info = (port_name, baud, mode)
        self._rate.clear()
        self.view = self.engine.current
        self.banner.hide()
        self._plot_sig = None
        self._set_controls_enabled(False)
        self._style_connect_button()
        self._set_status_dot(True)
        self._update_status_text()
        self._log(t("msg_connected", port=port_name, baud=baud, mode=t("mode_" + mode)), "ok")
        if raw_path:
            self._log(t("msg_raw", path=raw_path), "muted")

    def _disconnect(self, lost: str | None = None) -> None:
        eng = self.engine
        if eng is None:
            return
        self.engine = None
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            eng.stop()
        finally:
            QApplication.restoreOverrideCursor()
        self._drain_terminal(eng)
        self._drain_done(eng)
        self._set_controls_enabled(True)
        self._style_connect_button()
        self._set_status_dot(False)
        self.progress.hide()
        self._update_status_text()
        if lost:
            self._log(self.t("msg_lost", err=lost), "error")
        else:
            self._log(self.t("msg_disconnected"), "warn")
        self._plot_sig = None
        self._update_stats(force=True)

    def _set_controls_enabled(self, on: bool) -> None:
        for w in (self.port_cb, self.btn_refresh, self.baud_cb, self.seg_mode, self.fs_spin,
                  self.seq_cb, self.btn_open_saved, self.chk_raw):
            w.setEnabled(on)
        self.idle_spin.setEnabled(on and self.seg_mode.value() == "dma")
        self.send_edit.setEnabled(not on)
        self.btn_send.setEnabled(not on)
        self.eol_cb.setEnabled(not on)

    # ================================================================ DÖNGÜ
    def _tick(self) -> None:
        self._drain_exports()
        eng = self.engine
        if eng is not None:
            try:
                while True:
                    kind, msg = eng.events_q.get_nowait()
                    if kind == "disconnected":
                        self._disconnect(lost=msg or "?")
                        return
                    if kind == "error" and msg.startswith("raw:"):
                        self._log(self.t("msg_raw_err", err=msg[4:]), "error")
            except queue.Empty:
                pass
            self._drain_done(eng)
            if not self.chk_pause.isChecked():
                self._drain_terminal(eng)
            cur = eng.current
            if cur is not self.view and (cur.n > 0 or cur.saw_start):
                self.view = cur
                self._plot_sig = None
                if self.banner.isVisible() and self.banner_session is not cur:
                    self.banner.hide()
            now = time.time()
            self._rate.append((now, eng.total_lines, eng.total_bytes))
            while self._rate and now - self._rate[0][0] > 1.0:
                self._rate.popleft()
        self._update_stats()

    def _drain_terminal(self, eng: Engine) -> None:
        dq = eng.term
        if not dq:
            return
        lines = []
        try:
            while True:
                lines.append(dq.popleft())
        except IndexError:
            pass
        dropped = eng.term_dropped
        eng.term_dropped = 0
        if len(lines) > TERM_MAX_PER_TICK:
            dropped += len(lines) - TERM_MAX_PER_TICK
            lines = lines[-TERM_MAX_PER_TICK:]
        sb = self.term.verticalScrollBar()
        at_bottom = sb.value() >= sb.maximum() - 4
        if dropped:
            self._log(self.t("term_dropped", n=_fmt_int(dropped)), "muted", stamp=False)
        self.term.appendPlainText("\n".join(lines))
        if at_bottom:
            sb.setValue(sb.maximum())

    def _drain_done(self, eng: Engine) -> None:
        try:
            while True:
                s = eng.done_q.get_nowait()
                if s.n > 0 or s.saw_start or s.bad_lines:
                    self._on_session_done(s)
        except queue.Empty:
            pass

    def _on_session_done(self, s: Session) -> None:
        t = self.t
        self.banner_session = s
        if s.n == 0:
            txt = t("banner_done_empty")
            self._log(txt, "error")
            self._show_banner(txt, "bad", show_open=False)
            return
        self.view = s
        self._plot_sig = None
        if s.integrity_known and not s.integrity_ok:
            txt, state = t("banner_done_bad", n=_fmt_int(s.n), m=_fmt_int(s.missing), g=len(s.gaps)), "bad"
        elif s.integrity_known:
            txt, state = t("banner_done_ok", n=_fmt_int(s.n)), "ok"
        else:
            txt, state = t("banner_done_unknown", n=_fmt_int(s.n)), "info"
        if s.bad_lines:
            txt += "  ·  " + t("banner_bad_lines", b=_fmt_int(s.bad_lines))
            if state == "ok":
                state = "bad"
        self._log(txt, {"ok": "ok", "bad": "error"}.get(state, "info"))
        self._banner_base = txt
        if self.chk_auto.isChecked():
            fmt = self.seg_fmt.value()
            folder = self.folder_edit.text().strip() or self._default_folder()
            path = self._unique(os.path.join(folder, default_filename(s, self.prefix_edit.text(), fmt)))
            self._export_async(s, path, fmt)
            txt += "   ·   " + t("banner_saving")
        self._show_banner(txt, state, show_open=False)

    def _show_banner(self, text: str, state: str, show_open: bool) -> None:
        self.banner_lbl.setText(text)
        self.banner.setProperty("state", state)
        self.banner.style().unpolish(self.banner)
        self.banner.style().polish(self.banner)
        self.banner_open.setVisible(show_open)
        self.banner_folder.setVisible(show_open)
        self.banner.show()

    # ================================================================ İSTATİSTİK
    def _update_stats(self, force: bool = False) -> None:
        t = self.t
        s = self.view
        eng = self.engine
        n = s.n if s else 0
        if s and s.expected is not None:
            sub = t("rows_sub_expected", n=_fmt_int(s.expected))
        elif s and s.channels:
            sub = t("rows_sub_channels", n=len(s.channels))
        else:
            sub = " "
        self.tile_rows.set(_fmt_int(n), sub)

        if eng and len(self._rate) >= 2:
            (t0, l0, b0), (t1, l1, b1) = self._rate[0], self._rate[-1]
            dt = max(1e-3, t1 - t0)
            lps, kbs = (l1 - l0) / dt, (b1 - b0) / dt / 1024
            self.tile_rate.set(t("rate_fmt", lps=_fmt_int(int(round(lps)))), t("rate_sub", kbs=f"{kbs:.1f}"))
        else:
            self.tile_rate.set("—", " ")

        if s and s.integrity_known:
            m = s.missing
            bad = not s.integrity_ok
            self.tile_missing.set(_fmt_int(m), t("missing_bad_sub", g=len(s.gaps)) if bad else t("missing_ok_sub"),
                                  th.RED_TXT if bad else th.GREEN_TXT)
        else:
            self.tile_missing.set("—", t("missing_unknown_sub"))

        if eng:
            self.tile_dur.set(_fmt_dur(time.time() - self._conn_t0), " ")
        elif s and s.mode != "file":
            self.tile_dur.set(_fmt_dur(s.duration_s()), " ")
        else:
            self.tile_dur.set("—", " ")

        if eng:
            receiving = eng.last_rx and (time.perf_counter() - eng.last_rx) < 0.4
            if receiving:
                self.tile_status.set(t("status_receiving"), " ", th.BLUE_TXT)
            elif self.view is not None and self.view is not eng.current and self.view.n:
                self.tile_status.set(t("status_done"), " ", th.GREEN_TXT)
            else:
                self.tile_status.set(t("status_waiting"), " ", th.YELLOW_TXT)
            cur = eng.current
            if self._conn_info[2] == "dma" and cur.expected and cur.n < cur.expected:
                self.progress.setValue(int(cur.n * 1000 / max(1, cur.expected)))
                self.progress.setFormat(f"{_fmt_int(cur.n)} / {_fmt_int(cur.expected)}")
                self.progress.show()
            else:
                self.progress.hide()
        else:
            if s and s.mode == "file":
                self.tile_status.set(t("status_file"), s.port, th.BLUE_TXT)
            elif s and s.n:
                self.tile_status.set(t("status_done"), " ", th.GREEN_TXT)
            else:
                self.tile_status.set(t("status_idle"), " ", th.MUTED)

    def _set_status_dot(self, on: bool) -> None:
        self.status_dot.setStyleSheet(f"color: {th.GREEN_TXT if on else th.RED_TXT}; font-size: 11pt;")

    def _update_status_text(self) -> None:
        if self.engine is not None:
            port, baud, mode = self._conn_info
            self.status_lbl.setText(f"{port} @ {baud} baud  ·  {self.t('mode_' + mode)}")
        else:
            self.status_lbl.setText(self.t("status_idle"))

    # ================================================================ GRAFİK
    def _invalidate_plot(self, *_):
        self._plot_sig = None

    def _x_kind(self, s: Session) -> str:
        k = self.x_cb.currentData() or "auto"
        if k == "auto":
            k = "host" if s.mode == "live" else ("time" if s.sample_rate > 0 else "sample")
        if k == "time" and s.sample_rate <= 0:
            k = "sample"
        return k

    def _update_plot(self) -> None:
        s = self.view
        if s is None:
            return
        kind = self._x_kind(s)
        win = self.win_cb.currentData() if (s.mode == "live" and s.ended_at is None) else 0
        # Büyük veri alınırken grafiği çizim süresine göre seyrelt (arayüz akıcı kalsın)
        if s.ended_at is None and self._plot_sig is not None and self._plot_sig[0] == id(s):
            if time.perf_counter() - self._plot_t < max(0.2, 4 * self._plot_dur):
                return
        t_start = time.perf_counter()
        with s.lock:
            n = s.n
            sig = (id(s), n, kind, win, len(s.channels))
            if sig == self._plot_sig:
                return
            start = 0
            if win and n and len(s.t_host) >= n:
                start = bisect_left(s.t_host, s.t_host[n - 1] - win)
            names = list(s.channels)
            ys = [col[start:n] for col in s.cols]
            th0 = s.t_host[0] if len(s.t_host) else 0.0
            th_ = s.t_host[start:n] if kind == "host" else None
            seq = s.seq[start:n] if (s.has_seq and len(s.seq) >= n) else None
            seq0 = s.seq[0] if seq is not None and len(s.seq) else 0
            fs = s.sample_rate
        self._plot_sig = sig

        if kind == "host":
            x = np.frombuffer(th_, dtype=np.float64) - th0 if len(th_) else np.empty(0)
            xlabel = self.t("x_host")
        elif kind == "time":
            base = (np.frombuffer(seq, dtype=np.int64) - seq0) if seq is not None else np.arange(start, n)
            x = base / fs
            xlabel = self.t("x_time")
        else:
            x = np.frombuffer(seq, dtype=np.int64).astype(np.float64) if seq is not None else np.arange(start, n, dtype=np.float64)
            xlabel = self.t("x_sample")

        if self._curve_owner is not s:
            for c in self._curves.values():
                self.plot.removeItem(c)
            self._curves.clear()
            self.legend.clear()
            self._curve_owner = s
            self.plot.enableAutoRange()

        # Kayıp bölgeleri: çizgiyi kopar ve kırmızı ile işaretle (ara değer uydurma)
        for r in self._gap_items:
            self.plot.removeItem(r)
        self._gap_items = []
        gap_idx = None
        if seq is not None and len(seq) > 1:
            sq = np.frombuffer(seq, dtype=np.int64)
            gap_idx = np.nonzero(np.diff(sq) > 1)[0] + 1
            for gi in gap_idx[:100]:
                if gi < len(x):
                    reg = pg.LinearRegionItem((float(x[gi - 1]), float(x[gi])), movable=False,
                                              brush=pg.mkBrush(248, 81, 73, 45), pen=pg.mkPen(248, 81, 73, 110))
                    reg.setZValue(-10)
                    self.plot.addItem(reg)
                    self._gap_items.append(reg)
            if len(gap_idx):
                x = x.astype(np.float64)
                x = np.insert(x, gap_idx, x[gap_idx - 1])   # x sıralı kalır, y'de NaN ile çizgi kopar

        for i, name in enumerate(names):
            c = self._curves.get(name)
            if c is None:
                color = th.SERIES[i % len(th.SERIES)]
                c = self.plot.plot(pen=pg.mkPen(color, width=1.6), name=name, connect="finite")
                c.setDownsampling(auto=True, method="peak")
                c.setClipToView(True)
                self._curves[name] = c
            y = np.frombuffer(ys[i], dtype=np.float64) if len(ys[i]) else np.empty(0)
            if gap_idx is not None and len(gap_idx) and len(y) == len(x) - len(gap_idx):
                y = np.insert(y, gap_idx, np.nan)
            m = min(len(x), len(y))
            c.setData(x[:m], y[:m])
        self.legend.setVisible(bool(self._curves))
        self._plot_t = time.perf_counter()
        self._plot_dur = self._plot_t - t_start
        self.plot.getPlotItem().setLabel("bottom", xlabel)

    def _fit_plot(self) -> None:
        self.plot.enableAutoRange()

    def _save_png(self) -> None:
        from pyqtgraph.exporters import ImageExporter

        folder = self.folder_edit.text().strip() or self._default_folder()
        os.makedirs(folder, exist_ok=True)
        name = f"grafik_{_dt.datetime.now():%Y-%m-%d_%H-%M-%S}.png"
        path, _ = QFileDialog.getSaveFileName(self, self.t("save_png"), os.path.join(folder, name), "PNG (*.png)")
        if not path:
            return
        ex = ImageExporter(self.plot.getPlotItem())
        ex.parameters()["width"] = 1920
        ex.export(path)
        self.last_saved = path
        self._log(self.t("msg_png", path=path), "ok")

    # ================================================================ KAYIT
    def _unique(self, path: str) -> str:
        def taken(p):
            return os.path.exists(p) or os.path.normcase(p) in self._reserved

        if not taken(path):
            return path
        base, ext = os.path.splitext(path)
        i = 2
        while taken(f"{base}_{i}{ext}"):
            i += 1
        return f"{base}_{i}{ext}"

    def _export_async(self, s: Session, path: str, fmt: str) -> None:
        lang = self.lang
        self._reserved.add(os.path.normcase(path))

        def job():
            try:
                export_session(s, path, fmt, lang)
                self._export_q.put(("ok", path, s, path))
            except Exception as e:  # noqa: BLE001
                self._export_q.put(("err", f"{os.path.basename(path)}: {e}", s, path))

        th_ = threading.Thread(target=job, name="export", daemon=True)
        self._export_threads = [x for x in self._export_threads if x.is_alive()] + [th_]
        th_.start()

    def _drain_exports(self) -> None:
        try:
            while True:
                kind, val, s, path = self._export_q.get_nowait()
                self._reserved.discard(os.path.normcase(path))
                if kind == "ok":
                    self.last_saved = val
                    self.saved_btn.setText("💾 " + os.path.basename(val))
                    self.saved_btn.setToolTip(val)
                    self.saved_btn.show()
                    self._log(self.t("msg_saved", path=val), "ok")
                    if s is self.banner_session and self.banner.isVisible():
                        base = getattr(self, "_banner_base", "")
                        state = self.banner.property("state") or "info"
                        self._show_banner(f"{base}   ·   {self.t('banner_saved', name=os.path.basename(val))}",
                                          state, show_open=True)
                else:
                    self._log(self.t("msg_save_err", err=val), "error")
                    QMessageBox.critical(self, self.t("err_title"), self.t("msg_save_err", err=val))
        except queue.Empty:
            pass

    def _save_as(self) -> None:
        s = self.view
        if s is None or s.n == 0:
            QMessageBox.information(self, APP_NAME, self.t("msg_nodata"))
            return
        fmt = self.seg_fmt.value()
        folder = self.folder_edit.text().strip() or self._default_folder()
        os.makedirs(folder, exist_ok=True)
        filters = {"xlsx": "Excel (*.xlsx)", "csv": "CSV (*.csv)", "txt": "TXT (*.txt)"}
        order = [fmt] + [k for k in filters if k != fmt]
        path, chosen = QFileDialog.getSaveFileName(
            self, self.t("save_as"), os.path.join(folder, default_filename(s, self.prefix_edit.text(), fmt)),
            ";;".join(filters[k] for k in order))
        if not path:
            return
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if ext not in FORMATS:
            ext = next((k for k, f in filters.items() if f == chosen), fmt)
            path += FORMATS[ext]
        self._export_async(s, path, ext)

    def _browse_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, self.t("choose_folder"),
                                             self.folder_edit.text() or self._default_folder())
        if d:
            self.folder_edit.setText(d)

    def _open_folder(self) -> None:
        folder = self.folder_edit.text().strip() or self._default_folder()
        os.makedirs(folder, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _open_path(self, path: str | None) -> None:
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _open_saved_file(self) -> None:
        from ..importer import load_file

        folder = self.folder_edit.text().strip() or self._default_folder()
        path, _ = QFileDialog.getOpenFileName(self, self.t("open_title"), folder, self.t("file_filter"))
        if not path:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            s = load_file(path, channel_prefix=self.t("channel_prefix"))
        except Exception as e:  # noqa: BLE001
            QApplication.restoreOverrideCursor()
            msg = self.t("msg_nodata") if str(e) == "no-data" else str(e)
            self._log(self.t("msg_load_err", err=msg), "error")
            QMessageBox.warning(self, self.t("err_title"), self.t("msg_load_err", err=msg))
            return
        QApplication.restoreOverrideCursor()
        self.view = s
        self._plot_sig = None
        self.banner.hide()
        if s.sample_rate > 0 and self.fs_spin.value() == 0:
            self.fs_spin.setValue(s.sample_rate)
        self._log(self.t("msg_loaded", path=path, n=_fmt_int(s.n)), "ok")
        self._update_stats(force=True)

    # ================================================================ TERMİNAL
    def _send(self) -> None:
        if self.engine is None:
            return
        cmd = self.send_edit.text()
        eol = self.eol_cb.currentData() or ""
        try:
            self.engine.send((cmd + eol).encode("utf-8"))
            self._log(self.t("msg_sent", cmd=cmd or "⏎"), "info")
            self.send_edit.clear()
        except Exception as e:  # noqa: BLE001
            self._log(self.t("msg_send_err", err=e), "error")

    def _log(self, text: str, level: str = "info", stamp: bool = True) -> None:
        color = {"info": th.BLUE_TXT, "ok": th.GREEN_TXT, "warn": th.YELLOW_TXT,
                 "error": th.RED_TXT, "muted": th.FAINT}.get(level, th.MUTED)
        ts = f"[{_dt.datetime.now():%H:%M:%S}] " if stamp else ""
        sb = self.term.verticalScrollBar()
        at_bottom = sb.value() >= sb.maximum() - 4
        self.term.appendHtml(f'<span style="color:{th.FAINT}">{ts}</span>'
                             f'<span style="color:{color}">{html.escape(str(text))}</span>')
        cur = self.term.textCursor()
        cur.movePosition(QTextCursor.End)
        cur.setCharFormat(QTextCharFormat())
        self.term.setTextCursor(cur)
        if at_bottom:
            sb.setValue(sb.maximum())
        if level in ("ok", "error", "warn"):
            self.statusBar().showMessage(str(text), 6000)

    # ================================================================ KAPANIŞ
    def closeEvent(self, ev) -> None:
        if self.engine is not None:
            self._disconnect()
        for t in self._export_threads:
            t.join(timeout=60)
        self._drain_exports()
        self._save_settings()
        super().closeEvent(ev)

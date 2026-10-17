"""Tema: koyu / açık zemin + renk paleti (mavi, pembe, mor, yeşil, turuncu, turkuaz).

Renkler modül değişkeni olarak tutulur (th.BG, th.ACCENT ...). apply() bunları
değiştirir, build_qss() güncel renklerle stil sayfasını üretir. Arayüz renkleri
her seferinde th.<AD> diye okuduğu için tema anında değişir.
"""
from __future__ import annotations

MODES = ("system", "dark", "light")

# Zemin renkleri
BASES = {
    "dark": dict(
        BG="#0d1117", BG_PANEL="#161b22", BG_RAISED="#1c2333", BG_INPUT="#0d1117", BG_PLOT="#010409",
        BORDER="#30363d", BORDER_SOFT="#21262d", TEXT="#e6edf3", MUTED="#8b949e", FAINT="#6e7681",
        HOVER="#262f40", HOVER_BORDER="#3d4654", PRESSED="#1a2130", SCROLL_HOVER="#484f58",
        TERM_TEXT="#a5d6ff", LEGEND_BG=(22, 27, 34, 220),
        GREEN_TXT="#3fb950", RED_TXT="#f85149", YELLOW_TXT="#d29922",
        BANNER_OK="#0f2a1a", BANNER_BAD="#2d1215", BANNER_INFO="#121d2f", TIP_BG="#121d2f",
        SERIES=["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#e3b341",
                "#39c5cf", "#ff7b72", "#a5d6ff", "#7ee787", "#ffa657"],
    ),
    "light": dict(
        BG="#f6f8fa", BG_PANEL="#ffffff", BG_RAISED="#f3f4f6", BG_INPUT="#ffffff", BG_PLOT="#ffffff",
        BORDER="#d0d7de", BORDER_SOFT="#e5e7eb", TEXT="#1f2328", MUTED="#59636e", FAINT="#818b98",
        HOVER="#eaeef2", HOVER_BORDER="#afb8c1", PRESSED="#dde3ea", SCROLL_HOVER="#a3acb6",
        TERM_TEXT="#0b4a8b", LEGEND_BG=(255, 255, 255, 230),
        GREEN_TXT="#1a7f37", RED_TXT="#cf222e", YELLOW_TXT="#9a6700",
        BANNER_OK="#dafbe1", BANNER_BAD="#ffebe9", BANNER_INFO="#ddf4ff", TIP_BG="#eef6ff",
        SERIES=["#0969da", "#1a7f37", "#cf222e", "#8250df", "#9a6700",
                "#1b7c83", "#bc4c00", "#4d2d00", "#116329", "#d1242f"],
    ),
}

# Renk paletleri: (buton/seçili, üzerine gelince, yazı-koyu zemin, yazı-açık zemin)
ACCENTS = {
    "blue":   ("#1f6feb", "#388bfd", "#58a6ff", "#0969da"),
    "pink":   ("#db2777", "#ec4899", "#f472b6", "#be185d"),
    "purple": ("#7c3aed", "#8b5cf6", "#a78bfa", "#6d28d9"),
    "green":  ("#059669", "#10b981", "#34d399", "#047857"),
    "orange": ("#ea580c", "#f97316", "#fb923c", "#c2410c"),
    "teal":   ("#0891b2", "#06b6d4", "#22d3ee", "#0e7490"),
}

# Sabit durum renkleri (iki zeminde de okunur)
GREEN, GREEN_HI = "#238636", "#2ea043"
RED, RED_HI = "#b62324", "#da3633"

MODE = "dark"
ACCENT_NAME = "blue"


def apply(mode: str = "dark", accent: str = "blue") -> None:
    """mode: "dark" | "light" (system önceden çözülmüş olmalı)."""
    global MODE, ACCENT_NAME, BLUE, BLUE_HI, BLUE_TXT, ACCENT, ACCENT_HI, ACCENT_TXT, SERIES
    MODE = mode if mode in BASES else "dark"
    ACCENT_NAME = accent if accent in ACCENTS else "blue"
    g = globals()
    for k, v in BASES[MODE].items():
        g[k] = v
    a, hi, txt_dark, txt_light = ACCENTS[ACCENT_NAME]
    ACCENT, ACCENT_HI = a, hi
    ACCENT_TXT = txt_dark if MODE == "dark" else txt_light
    # eski adlar (arayüzün geri kalanı bunları kullanıyor)
    BLUE, BLUE_HI, BLUE_TXT = ACCENT, ACCENT_HI, ACCENT_TXT
    # ilk kanal paletin renginde; diğerleri ayırt edilebilir sabit sıra
    SERIES = [ACCENT_TXT] + [c for c in BASES[MODE]["SERIES"] if c.lower() != ACCENT_TXT.lower()]


def resolve_mode(mode: str) -> str:
    """"system" ise işletim sisteminin koyu/açık ayarını okur."""
    if mode in ("dark", "light"):
        return mode
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QGuiApplication

        scheme = QGuiApplication.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Light:
            return "light"
        if scheme == Qt.ColorScheme.Dark:
            return "dark"
    except Exception:  # noqa: BLE001
        pass
    return "dark"


apply("dark", "blue")

_QSS = """
* {{ outline: 0; }}
QWidget {{ background: {BG}; color: {TEXT}; font-size: 10pt; }}
QToolTip {{ background: {BG_RAISED}; color: {TEXT}; border: 1px solid {BORDER}; padding: 6px; }}

#Header {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
#TitleBlue {{ color: {ACCENT_TXT}; font-size: 18pt; font-weight: 700; background: transparent; }}
#TitleMain {{ color: {TEXT}; font-size: 18pt; font-weight: 700; background: transparent; }}
#Version {{ color: {FAINT}; font-size: 9pt; background: transparent; }}

#Sidebar, #SidebarInner {{ background: {BG}; }}
QScrollArea {{ border: none; background: {BG}; }}

#Card {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 10px; }}
#Card QLabel, #Card QCheckBox {{ background: transparent; }}
#CardTitle {{ font-weight: 700; font-size: 10.5pt; color: {TEXT}; padding-bottom: 2px; }}
#FieldLabel {{ color: {MUTED}; font-size: 9pt; }}
#Hint {{ color: {FAINT}; font-size: 8.5pt; }}

QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
    background: {BG_INPUT}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 5px 8px; min-height: 20px; selection-background-color: {ACCENT}; selection-color: white;
}}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{ border-color: {ACCENT_HI}; }}
QLineEdit:disabled, QComboBox:disabled, QDoubleSpinBox:disabled {{ color: {FAINT}; border-color: {BORDER_SOFT}; }}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{ subcontrol-origin: border; width: 0px; border: none; }}
QAbstractSpinBox QLineEdit, QComboBox QLineEdit {{ padding: 0; margin: 0; border: none; background: transparent; min-height: 0; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox::down-arrow {{ image: url(assets:chevron.svg); width: 10px; height: 10px; margin-right: 8px; }}
QComboBox QAbstractItemView {{ background: {BG_RAISED}; border: 1px solid {BORDER};
    selection-background-color: {ACCENT}; selection-color: white; padding: 4px; }}

QPushButton {{
    background: {BG_RAISED}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 6px 12px; color: {TEXT}; font-weight: 600;
}}
QPushButton:hover {{ background: {HOVER}; border-color: {HOVER_BORDER}; }}
QPushButton:pressed {{ background: {PRESSED}; }}
QPushButton:disabled {{ color: {FAINT}; background: {BG_PANEL}; border-color: {BORDER_SOFT}; }}
QPushButton#Primary {{ background: {GREEN}; border-color: {GREEN_HI}; color: white; padding: 9px; font-size: 10.5pt; }}
QPushButton#Primary:hover {{ background: {GREEN_HI}; }}
QPushButton#Danger {{ background: {RED}; border-color: {RED_HI}; color: white; padding: 9px; font-size: 10.5pt; }}
QPushButton#Danger:hover {{ background: {RED_HI}; }}
QPushButton#Accent {{ background: {ACCENT}; border-color: {ACCENT_HI}; color: white; }}
QPushButton#Accent:hover {{ background: {ACCENT_HI}; }}
QPushButton#Icon {{ padding: 5px 9px; min-width: 18px; }}
QPushButton#Link {{ background: transparent; border: none; color: {ACCENT_TXT}; padding: 2px 6px; }}
QPushButton#Link:hover {{ text-decoration: underline; }}

QPushButton#Seg {{ border-radius: 0; background: {BG_INPUT}; color: {MUTED}; padding: 6px 4px; font-weight: 600; }}
QPushButton#Seg:checked {{ background: {ACCENT}; border-color: {ACCENT_HI}; color: white; }}
QPushButton#Seg:hover:!checked {{ color: {TEXT}; }}
QPushButton#Seg[pos="l"] {{ border-top-left-radius: 6px; border-bottom-left-radius: 6px; }}
QPushButton#Seg[pos="r"] {{ border-top-right-radius: 6px; border-bottom-right-radius: 6px; }}

QCheckBox {{ spacing: 8px; color: {TEXT}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {BORDER}; border-radius: 4px; background: {BG_INPUT}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT_HI}; image: url(assets:check.svg); }}

#Tile {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 10px; }}
#Tile QLabel {{ background: transparent; }}
#TileLabel {{ color: {MUTED}; font-size: 8.5pt; font-weight: 600; }}
#TileValue {{ font-size: 17pt; font-weight: 700; }}
#TileSub {{ color: {FAINT}; font-size: 8.5pt; }}

#Panel {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 10px; }}
#PanelHeader {{ background: transparent; }}
#PanelHeader QLabel, #PanelHeader QCheckBox {{ background: transparent; }}
#PanelTitle {{ font-weight: 700; font-size: 10.5pt; }}

QPlainTextEdit {{
    background: {BG_PLOT}; border: 1px solid {BORDER_SOFT}; border-radius: 6px;
    color: {TERM_TEXT}; selection-background-color: {ACCENT}; selection-color: white; padding: 4px;
}}

QProgressBar {{ background: {BG_INPUT}; border: 1px solid {BORDER}; border-radius: 5px; height: 10px;
    text-align: center; color: {TEXT}; font-size: 8pt; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}

#Banner {{ border-radius: 10px; border: 1px solid {BORDER}; }}
#Banner QLabel {{ background: transparent; font-weight: 600; }}
#Banner[state="ok"] {{ background: {BANNER_OK}; border-color: {GREEN}; }}
#Banner[state="bad"] {{ background: {BANNER_BAD}; border-color: {RED_HI}; }}
#Banner[state="info"] {{ background: {BANNER_INFO}; border-color: {ACCENT}; }}

QSplitter::handle {{ background: {BG}; }}
QSplitter::handle:vertical {{ height: 8px; }}
QSplitter::handle:horizontal {{ width: 8px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {SCROLL_HOVER}; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 4px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QStatusBar {{ background: {BG_PANEL}; border-top: 1px solid {BORDER}; color: {MUTED}; }}
QStatusBar QLabel {{ background: transparent; color: {MUTED}; padding: 0 6px; }}
QStatusBar::item {{ border: none; }}
QMenu {{ background: {BG_RAISED}; border: 1px solid {BORDER}; padding: 4px; }}
QMenu::item {{ padding: 7px 22px 7px 14px; border-radius: 4px; }}
QMenu::item:selected {{ background: {ACCENT}; color: white; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}
QMenu::item:disabled {{ color: {FAINT}; }}
QToolButton#HelpBtn {{ background: {BG_RAISED}; border: 1px solid {BORDER}; border-radius: 15px;
    min-width: 28px; min-height: 28px; max-width: 28px; max-height: 28px; font-weight: 700; font-size: 11pt; color: {ACCENT_TXT}; }}
QToolButton#HelpBtn:hover {{ border-color: {ACCENT_HI}; }}
QToolButton#HelpBtn::menu-indicator {{ image: none; width: 0; }}
QListWidget {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 10px; padding: 6px; }}
QListWidget::item {{ padding: 9px 10px; border-radius: 6px; color: {MUTED}; }}
QListWidget::item:selected {{ background: {ACCENT}; color: white; }}
QListWidget::item:hover:!selected {{ background: {HOVER}; color: {TEXT}; }}
QTextBrowser {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 10px; padding: 10px 16px; }}
QScrollArea QLabel {{ background: {BG_PLOT}; }}
"""


def build_qss(assets_dir) -> str:
    """Stil sayfasını güncel renklerle üretir.

    SVG'ler dosya yoluyla değil Qt arama yolu ("assets:") ile verilir: uygulama
    boşluk / Türkçe karakter içeren bir klasörde (ör. "Masaüstü", "... (1)")
    çalışınca yol stil sayfasını bozup tüm temayı devre dışı bırakıyordu.
    """
    from PySide6.QtCore import QDir

    QDir.setSearchPaths("assets", [str(assets_dir)])
    g = globals()
    return _QSS.format(**{k: g[k] for k in (
        "BG", "BG_PANEL", "BG_RAISED", "BG_INPUT", "BG_PLOT", "BORDER", "BORDER_SOFT", "TEXT", "MUTED", "FAINT",
        "HOVER", "HOVER_BORDER", "PRESSED", "SCROLL_HOVER", "TERM_TEXT", "GREEN", "GREEN_HI", "RED", "RED_HI",
        "BANNER_OK", "BANNER_BAD", "BANNER_INFO", "ACCENT", "ACCENT_HI", "ACCENT_TXT")})


_HELP_CSS = """
body {{ color: {TEXT}; font-size: 10.5pt; }}
h2 {{ color: {TEXT}; font-size: 16pt; margin: 0 0 6px 0; }}
h3 {{ color: {ACCENT_TXT}; font-size: 11.5pt; margin: 16px 0 4px 0; }}
p, li {{ line-height: 150%; }}
code {{ color: {ACCENT_TXT}; background-color: {BG_RAISED}; }}
pre {{ color: {TERM_TEXT}; background-color: {BG_PLOT}; padding: 10px; font-size: 9.5pt; }}
table {{ border-collapse: collapse; margin: 6px 0; }}
th {{ background-color: {BG_RAISED}; color: {TEXT}; padding: 7px; text-align: left; }}
td {{ padding: 7px; vertical-align: top; }}
td.row {{ border-top: 1px solid {BORDER}; }}
td.num {{ background-color: #e3b341; color: #0d1117; font-weight: 700; text-align: center; }}
.tip {{ background-color: {TIP_BG}; padding: 10px; }}
.lead {{ color: {MUTED}; font-size: 11pt; }}
.cap {{ color: {FAINT}; font-size: 8.5pt; }}
a {{ color: {ACCENT_TXT}; }}
"""


def help_css() -> str:
    """Kılavuz penceresinin (QTextBrowser) stil sayfası, güncel temayla."""
    g = globals()
    return _HELP_CSS.format(**{k: g[k] for k in (
        "TEXT", "ACCENT_TXT", "BG_RAISED", "TERM_TEXT", "BG_PLOT", "BORDER", "TIP_BG", "MUTED", "FAINT")})

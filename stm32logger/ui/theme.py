"""Koyu tema renkleri ve Qt stil sayfası."""

BG = "#0d1117"
BG_PANEL = "#161b22"
BG_RAISED = "#1c2333"
BG_INPUT = "#0d1117"
BG_PLOT = "#010409"
BORDER = "#30363d"
BORDER_SOFT = "#21262d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
FAINT = "#6e7681"
BLUE = "#1f6feb"
BLUE_HI = "#388bfd"
BLUE_TXT = "#58a6ff"
GREEN = "#238636"
GREEN_HI = "#2ea043"
GREEN_TXT = "#3fb950"
RED = "#b62324"
RED_HI = "#da3633"
RED_TXT = "#f85149"
YELLOW_TXT = "#d29922"

# Grafik kanal renkleri (koyu zeminde ayırt edilebilir sıra)
SERIES = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#e3b341",
          "#39c5cf", "#ff7b72", "#a5d6ff", "#7ee787", "#ffa657"]

QSS = f"""
* {{ outline: 0; }}
QWidget {{ background: {BG}; color: {TEXT}; font-size: 10pt; }}
QToolTip {{ background: {BG_RAISED}; color: {TEXT}; border: 1px solid {BORDER}; padding: 6px; }}

#Header {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
#TitleBlue {{ color: {BLUE_TXT}; font-size: 18pt; font-weight: 700; background: transparent; }}
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
    padding: 5px 8px; min-height: 20px; selection-background-color: {BLUE};
}}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{ border-color: {BLUE_HI}; }}
QLineEdit:disabled, QComboBox:disabled, QDoubleSpinBox:disabled {{ color: {FAINT}; border-color: {BORDER_SOFT}; }}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{ subcontrol-origin: border; width: 0px; border: none; }}
QAbstractSpinBox QLineEdit, QComboBox QLineEdit {{ padding: 0; margin: 0; border: none; background: transparent; min-height: 0; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox::down-arrow {{ image: url(__CHEVRON__); width: 10px; height: 10px; margin-right: 8px; }}
QComboBox QAbstractItemView {{ background: {BG_RAISED}; border: 1px solid {BORDER};
    selection-background-color: {BLUE}; padding: 4px; }}

QPushButton {{
    background: {BG_RAISED}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 6px 12px; color: {TEXT}; font-weight: 600;
}}
QPushButton:hover {{ background: #262f40; border-color: #3d4654; }}
QPushButton:pressed {{ background: #1a2130; }}
QPushButton:disabled {{ color: {FAINT}; background: {BG_PANEL}; border-color: {BORDER_SOFT}; }}
QPushButton#Primary {{ background: {GREEN}; border-color: {GREEN_HI}; color: white; padding: 9px; font-size: 10.5pt; }}
QPushButton#Primary:hover {{ background: {GREEN_HI}; }}
QPushButton#Danger {{ background: {RED}; border-color: {RED_HI}; color: white; padding: 9px; font-size: 10.5pt; }}
QPushButton#Danger:hover {{ background: {RED_HI}; }}
QPushButton#Accent {{ background: {BLUE}; border-color: {BLUE_HI}; color: white; }}
QPushButton#Accent:hover {{ background: {BLUE_HI}; }}
QPushButton#Icon {{ padding: 5px 9px; min-width: 18px; }}
QPushButton#Link {{ background: transparent; border: none; color: {BLUE_TXT}; padding: 2px 6px; }}
QPushButton#Link:hover {{ text-decoration: underline; }}

QPushButton#Seg {{ border-radius: 0; background: {BG_INPUT}; color: {MUTED}; padding: 6px 4px; font-weight: 600; }}
QPushButton#Seg:checked {{ background: {BLUE}; border-color: {BLUE_HI}; color: white; }}
QPushButton#Seg:hover:!checked {{ color: {TEXT}; }}
QPushButton#Seg[pos="l"] {{ border-top-left-radius: 6px; border-bottom-left-radius: 6px; }}
QPushButton#Seg[pos="r"] {{ border-top-right-radius: 6px; border-bottom-right-radius: 6px; }}

QCheckBox {{ spacing: 8px; color: {TEXT}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {BORDER}; border-radius: 4px; background: {BG_INPUT}; }}
QCheckBox::indicator:checked {{ background: {BLUE}; border-color: {BLUE_HI};
    image: url(__CHECK__); }}

#Tile {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 10px; }}
#Tile QLabel {{ background: transparent; }}
#TileLabel {{ color: {MUTED}; font-size: 8.5pt; font-weight: 600; }}
#TileValue {{ font-size: 17pt; font-weight: 700; }}
#TileSub {{ color: {FAINT}; font-size: 8.5pt; }}

#Panel {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 10px; }}
#PanelHeader {{ background: transparent; }}
#PanelHeader QLabel {{ background: transparent; }}
#PanelTitle {{ font-weight: 700; font-size: 10.5pt; }}

QPlainTextEdit {{
    background: {BG_PLOT}; border: 1px solid {BORDER_SOFT}; border-radius: 6px;
    color: #a5d6ff; selection-background-color: {BLUE}; padding: 4px;
}}

QProgressBar {{ background: {BG_INPUT}; border: 1px solid {BORDER}; border-radius: 5px; height: 10px;
    text-align: center; color: {TEXT}; font-size: 8pt; }}
QProgressBar::chunk {{ background: {BLUE}; border-radius: 4px; }}

#Banner {{ border-radius: 10px; border: 1px solid {BORDER}; }}
#Banner QLabel {{ background: transparent; font-weight: 600; }}
#Banner[state="ok"] {{ background: #0f2a1a; border-color: {GREEN}; }}
#Banner[state="bad"] {{ background: #2d1215; border-color: {RED_HI}; }}
#Banner[state="info"] {{ background: #121d2f; border-color: {BLUE}; }}

QSplitter::handle {{ background: {BG}; }}
QSplitter::handle:vertical {{ height: 8px; }}
QSplitter::handle:horizontal {{ width: 8px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #484f58; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 4px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QStatusBar {{ background: {BG_PANEL}; border-top: 1px solid {BORDER}; color: {MUTED}; }}
QStatusBar QLabel {{ background: transparent; color: {MUTED}; padding: 0 6px; }}
QStatusBar::item {{ border: none; }}
QMenu {{ background: {BG_RAISED}; border: 1px solid {BORDER}; }}
QMenu::item:selected {{ background: {BLUE}; }}
"""


def build_qss(assets_dir) -> str:
    from pathlib import Path

    a = Path(assets_dir)
    return (QSS.replace("__CHECK__", (a / "check.svg").as_posix())
               .replace("__CHEVRON__", (a / "chevron.svg").as_posix()))

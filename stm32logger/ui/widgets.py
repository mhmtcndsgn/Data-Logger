"""Küçük, yeniden kullanılabilir arayüz parçaları."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton,
                               QVBoxLayout, QWidget)


class Card(QFrame):
    """Başlıklı yan panel kartı."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(14, 12, 14, 14)
        self.lay.setSpacing(6)
        self.title = QLabel()
        self.title.setObjectName("CardTitle")
        self.lay.addWidget(self.title)

    def label(self) -> QLabel:
        lbl = QLabel()
        lbl.setObjectName("FieldLabel")
        self.lay.addSpacing(2)
        self.lay.addWidget(lbl)
        return lbl

    def add(self, w):
        if isinstance(w, QWidget):
            self.lay.addWidget(w)
        else:
            self.lay.addLayout(w)
        return w


class Segmented(QWidget):
    """Yan yana, tek seçimli düğmeler (iOS tarzı segment)."""

    changed = Signal(str)

    def __init__(self, keys: list[str], parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}
        for i, k in enumerate(keys):
            b = QPushButton()
            b.setObjectName("Seg")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setProperty("pos", "l" if i == 0 else ("r" if i == len(keys) - 1 else "m"))
            self.group.addButton(b)
            self.buttons[k] = b
            lay.addWidget(b, 1)
            b.clicked.connect(lambda _=False, k=k: self.changed.emit(k))
        self.buttons[keys[0]].setChecked(True)

    def value(self) -> str:
        for k, b in self.buttons.items():
            if b.isChecked():
                return k
        return next(iter(self.buttons))

    def set_value(self, key: str) -> None:
        if key in self.buttons:
            self.buttons[key].setChecked(True)

    def set_texts(self, texts: dict[str, str]) -> None:
        for k, txt in texts.items():
            self.buttons[k].setText(txt)


class Tile(QFrame):
    """Üstteki istatistik kutucukları."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Tile")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(1)
        self.label = QLabel()
        self.label.setObjectName("TileLabel")
        self.value = QLabel("—")
        self.value.setObjectName("TileValue")
        self.sub = QLabel(" ")
        self.sub.setObjectName("TileSub")
        for w in (self.label, self.value, self.sub):
            w.setTextFormat(Qt.PlainText)   # dosya/port adı HTML olarak yorumlanmasın
            lay.addWidget(w)
        self._last = None

    def set(self, value: str, sub: str = " ", color: str | None = None) -> None:
        key = (value, sub, color)
        if key == self._last:
            return
        self._last = key
        self.value.setText(value)
        self.sub.setText(sub or " ")
        self.value.setStyleSheet(f"color: {color};" if color else "")


class PanelHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PanelHeader")
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(2, 0, 2, 4)
        self.lay.setSpacing(8)
        self.title = QLabel()
        self.title.setObjectName("PanelTitle")
        self.lay.addWidget(self.title)
        self.lay.addStretch(1)

    def add(self, w):
        self.lay.addWidget(w)
        return w


def hint_label() -> QLabel:
    lbl = QLabel()
    lbl.setObjectName("Hint")
    lbl.setWordWrap(True)
    return lbl


def hrow(*widgets, stretch_first=True) -> QHBoxLayout:
    lay = QHBoxLayout()
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)
    for i, w in enumerate(widgets):
        lay.addWidget(w, 1 if (i == 0 and stretch_first) else 0)
    return lay


class WheelGuard(QObject):
    """Odakta olmayan sayı kutusu / açılır listenin fare tekerleğini yok sayar.

    Böylece yan paneli kaydırırken imleç bir kutunun üstünden geçince değeri
    (ör. aktarım bitiş süresi) yanlışlıkla değişmez; tekerlek paneli kaydırır.
    """

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Wheel and not obj.hasFocus():
            ev.ignore()
            return True
        return False


def guard_wheel(*widgets) -> None:
    g = WheelGuard(widgets[0])
    for w in widgets:
        w.setFocusPolicy(Qt.StrongFocus)
        w.installEventFilter(g)

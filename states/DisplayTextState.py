from decimal import Context
from typing import Callable

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

from states.Context import ConfigContext
from states.State import State



class DisplayTextState(State):

    def __init__(self, state_manager, display_text: str, next: Callable[[], State], timeout: int, context: ConfigContext = ConfigContext()):
        super().__init__(state_manager=state_manager, main_widget=TextGUI(display_text), sub_widget=None)
        self.next = next
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.notify_state_update)
        self.timer.start(timeout*1000)
        self.context = context

    def next_state(self, *args) -> 'State':
        return self.next()

class TextGUI(QWidget):
    def __init__(self, display_text: str, parent: QWidget = None):
        super().__init__(parent)
        self.label = QLabel(display_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 64px;")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
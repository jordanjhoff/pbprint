from typing import Callable

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

from StateManager import StateManager
from management.Context import Config
from states.State import State


class DisplayText(State):
    """
    An intermediate state to display text and transition to other states.

    The next lambda argument allows for transition to another state, without initializing the next state until it's ready.
    """
    def __init__(
        self,
        state_manager: StateManager,
        config: Config,
        display_text: str,
        next_state_lambda: Callable[[], State],
        timeout: int,
    ) -> None:
        super().__init__(
            state_manager=state_manager,
            config=config,
            display_GUI=DisplayGUI(display_text),
            control_GUI=None
        )
        self.next = next_state_lambda
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.notify_state_update)
        self.timer.start(timeout*1000)

    def next_state(self, *args) -> 'State':
        return self.next()

class DisplayGUI(QWidget):
    def __init__(self, display_text: str, parent: QWidget = None):
        super().__init__(parent)
        self.label = QLabel(display_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 64px;")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
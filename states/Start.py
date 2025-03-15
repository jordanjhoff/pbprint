from typing import List

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QVBoxLayout

from StateManager import StateManager
from management.Context import Config
from management.PaymentManager import PaymentManager
from states.State import State


class Start(State):
    def __init__(self, state_manager: StateManager, config: Config):
        super().__init__(
            state_manager=state_manager,
            config = config,
            display_GUI=DisplayGUI(display_text="WELCOME!"),
            control_GUI=ControlGUI()
        )

        self.control_GUI.begin.clicked.connect(self.notify_transition_state)
        self.press_history = []
        self.control_GUI.top_left_signal.connect(lambda: self.record_press("top-left"))
        self.control_GUI.top_right_signal.connect(lambda: self.record_press("top-right"))
        self.control_GUI.bottom_left_signal.connect(lambda: self.record_press("bottom-left"))
        self.control_GUI.bottom_right_signal.connect(lambda: self.record_press("bottom-right"))

    def next_state(self, *args) -> 'State':
        from states.DevBypass import DevBypass
        from states.DisplayText import DisplayText
        from states.SelectTemplate import SelectTemplate

        if args and args[0] == "dev_bypass":
            return DevBypass(state_manager=self.state_manager, config=self.config)

        # Loads payment manager and goes into await_payment
        if self.config.ACCEPT_PAYMENT:
            return DisplayText(
                state_manager=self.state_manager,
                config=self.config,
                display_text="Loading",
                timeout=1,
                next_state_lambda=(lambda: self.determine_state()),
            )

        # Bypasses and goes directly to select template state
        return SelectTemplate(
            state_manager=self.state_manager,
            config=self.config,
        )
       

    
    def determine_state(self) -> State:
        """Initializes payment manager and returns to start if unable to initialize."""
        from states.DisplayText import DisplayText
        from states.AwaitPayment import AwaitPayment

        payment_manager = PaymentManager(self.config)
        if payment_manager.checkout_link is None:
            start = lambda: Start(state_manager=self.state_manager, config=self.config)
            return DisplayText(
                state_manager=self.state_manager,
                config=self.config,
                display_text="Unable to connect to internet",
                timeout=10,
                next_state_lambda=start,
            )
        else:
            return AwaitPayment(
                state_manager=self.state_manager,
                config=self.config,
                payment_manager=payment_manager)

    def record_press(self, text: str):
        self.press_history.append(text)
        print(self.press_history)
        if len(self.press_history) == 4 and self.validate_history(["top-left", "top-right", "bottom-left", "bottom-right"]):
            self.notify_transition_state("dev_bypass")
        elif len(self.press_history) >= 4:
            self.press_history = self.press_history[1:]

    def validate_history(self, passcode: List[str]) -> bool:
        if len(self.press_history) < len(passcode):
            return False
        for i, j in zip(passcode, self.press_history[-len(passcode):]):
            if i != j:
                return False

        return True

class ControlGUI(QWidget):
    """
    Widget with four invisible buttons in each corner and a visible "Begin" button in the center.
    """
    top_left_signal = pyqtSignal()
    top_right_signal = pyqtSignal()
    bottom_left_signal = pyqtSignal()
    bottom_right_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.top_left_button = CornerButton(self)
        self.top_right_button = CornerButton(self)
        self.bottom_left_button = CornerButton(self)
        self.bottom_right_button = CornerButton(self)

        self.begin = QPushButton("Begin", self)
        self.begin.setFixedSize(400, 300)
        self.begin.setStyleSheet("QPushButton {border: 10px solid black; font-size: 64px; background-color: gray; color: black;}")

        self.top_left_button.clicked_signal.connect(self.top_left_signal)
        self.top_right_button.clicked_signal.connect(self.top_right_signal)
        self.bottom_left_button.clicked_signal.connect(self.bottom_left_signal)
        self.bottom_right_button.clicked_signal.connect(self.bottom_right_signal)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.top_left_button, alignment=Qt.AlignLeft | Qt.AlignTop)
        top_layout.addStretch()
        top_layout.addWidget(self.top_right_button, alignment=Qt.AlignRight | Qt.AlignTop)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addWidget(self.bottom_left_button, alignment=Qt.AlignLeft | Qt.AlignBottom)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.bottom_right_button, alignment=Qt.AlignRight | Qt.AlignBottom)

        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(self.begin)
        center_layout.addStretch()

        self.layout.addLayout(top_layout)
        self.layout.addStretch()
        self.layout.addLayout(center_layout)
        self.layout.addStretch()
        self.layout.addLayout(bottom_layout)

class DisplayGUI(QWidget):
    """Displays a starting splash screen."""
    def __init__(self, parent=None, display_text=None):
        super().__init__(parent)
        self.label = QLabel(display_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()	
        layout.addWidget(self.label)
        self.setStyleSheet("QPushButton {border: 20px solid black; font-size: 64px; background-color: gray; color: black;}")

        self.setLayout(layout)


class CornerButton(QPushButton):
    """Invisible button."""
    clicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 200)
        self.setStyleSheet("background: transparent; border: none;")
        self.clicked.connect(self.emit_signal)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.BlankCursor)

    def emit_signal(self):
        self.clicked_signal.emit()


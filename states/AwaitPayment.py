
from typing import List

import os
from PyQt5.QtGui import QPixmap

from StateManager import StateManager
from management.Context import Config
from management.PaymentManager import PaymentManager
from states.State import State
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QThread

assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))

class AwaitPayment(State):
    """State to await user payments. If certain poll attempts reached, return to start."""
    def __init__(
        self,
        state_manager: StateManager,
        config: Config,
        payment_manager: PaymentManager,
    ) -> None:

        super().__init__(
            state_manager=state_manager,
            config=config,
            display_GUI=DisplayGUI(),
            control_GUI=ControlGUI()
        )
        self.press_history = []
        self.control_GUI.top_left_signal.connect(lambda: self.record_press("top-left"))
        self.control_GUI.top_right_signal.connect(lambda: self.record_press("top-right"))
        self.control_GUI.bottom_left_signal.connect(lambda: self.record_press("bottom-left"))
        self.control_GUI.bottom_right_signal.connect(lambda: self.record_press("bottom-right"))

        self.payment_manager = payment_manager
        if payment_manager.checkout_link is None:
            self.notify_transition_state("failed_payment")
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_payment_status)
        self.timer.start(5000)
        print("started timer")
        self.retries_reached = False
        self.retry_limit = 120


    def next_state(self, *args) -> 'State':
        from states.Start import Start
        from states.DisplayText import DisplayText
        from states.SelectTemplate import SelectTemplate
        from states.DevBypass import DevBypass

        if args and args[0] == "start":
            self.payment_manager.clean_payment_manager()
            return Start(state_manager=self.state_manager, config=self.config)
        if args and args[0] == "failed_payment":
            start = lambda: Start(state_manager=self.state_manager, config=self.config)
            return DisplayText(
                state_manager=self.state_manager,
                config=self.config,
                display_text="Unable to connect to internet",
                timeout=10,
                next_state_lambda=start,
            )
        if args and args[0] == "dev_bypass":
            return DevBypass(state_manager=self.state_manager, config=self.config)
        else:
            self.payment_manager.clean_payment_manager()
            return SelectTemplate(state_manager=self.state_manager, config=self.config)

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

    def check_payment_status(self) -> None:
        """
        Poll square API for successful payment at regular intervals.
        """
        print(f"checking payment status {self.retry_limit}")
        if self.retry_limit <= 0:
            print("retry limit reached, defaulting to start page")
            self.retries_reached = True
            self.notify_transition_state("start")
        if status := self.payment_manager.check_payment_status():
            print(f"status: {status}")
            if status == "OPEN":
                print("PAYMENT RECEIVED")
                self.notify_transition_state("continue")
        self.retry_limit -= 1



    
        


class ControlGUI(QWidget):
    """
    Widget with four invisible buttons in each corner.
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

        self.layout.addLayout(top_layout)
        self.layout.addStretch()
        self.layout.addLayout(bottom_layout)



class DisplayGUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image1_label = QLabel(self)
        self.image2_label = QLabel(self)

        self.image1_label.setPixmap(QPixmap(f"{assets_dir}/crest.jpg").scaled(300, 300, Qt.KeepAspectRatio))
        self.image2_label.setPixmap(QPixmap(f"{output_dir}/qrcode.png").scaled(300, 300, Qt.KeepAspectRatio))

        self.text_label = QLabel("Welcome to BGE PHOTOBOOTH! TO USE THIS PHOTOBOOTH, SCAN THE QR CODE TO PAY.", self)
        self.text_label.setStyleSheet("font-size: 32px;")

        self.text_label.setFixedWidth(800)
        self.text_label.setWordWrap(True)

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.image1_label)
        images_layout.addWidget(self.image2_label)
        images_layout.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(images_layout)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.text_label)

        self.setLayout(main_layout)
        self.setWindowTitle("Images and Text Example")
        self.resize(1200, 600)
        self.show()

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

from typing import List

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QVBoxLayout

from states.AwaitPayment import AwaitPayment, CornerButton
from states.Context import ConfigContext
from states.DevBypass import DevBypass
from states.DisplayTextState import DisplayTextState
from states.PaymentManager import PaymentManager
from states.SelectTemplate import SelectTemplate
from states.State import State

class Start(State):
    def __init__(self, state_manager, context: ConfigContext):
        super().__init__(state_manager=state_manager, main_widget=StartSplash(display_text="WELCOME!"), sub_widget=SubGUI())
        self.context = context
        self.sub_widget.begin.clicked.connect(self.notify_state_update)
        self.press_history = []
        self.sub_widget.top_left_signal.connect(lambda: self.record_press("top-left"))
        self.sub_widget.top_right_signal.connect(lambda: self.record_press("top-right"))
        self.sub_widget.bottom_left_signal.connect(lambda: self.record_press("bottom-left"))
        self.sub_widget.bottom_right_signal.connect(lambda: self.record_press("bottom-right"))

    def next_state(self, *args) -> 'State':
        if args and args[0] == "dev_bypass":
            return DevBypass(self.state_manager, context=self.context)

        if self.context.config.get("accept_payment"):
            return DisplayTextState(
                state_manager=self.state_manager,
                display_text="Loading",
                timeout=1,
                next=(lambda: self.determine_state()),
                context=self.context,
            )

        return SelectTemplate(
            state_manager=self.state_manager,
            context=self.context,
        )
       

    
    def determine_state(self) -> State:
        payment = PaymentManager()
        if payment.checkout_link is None:
            start = lambda: Start(self.state_manager)
            return DisplayTextState(state_manager=self.state_manager,
                                    display_text="Unable to connect to internet",
                                    timeout=10,
                                    next=start)
        else:
            return AwaitPayment(self.state_manager, payment, context=self.context)

    def record_press(self, text: str):
        self.press_history.append(text)
        print(self.press_history)
        if len(self.press_history) == 4 and self.validate_history(["top-left", "top-right", "bottom-left", "bottom-right"]):
            self.notify_state_update("dev_bypass")
        elif len(self.press_history) >= 4:
            self.press_history = self.press_history[1:]

    def validate_history(self, passcode: List[str]) -> bool:
        if len(self.press_history) < len(passcode):
            return False
        for i, j in zip(passcode, self.press_history[-len(passcode):]):
            if i != j:
                return False

        return True

class SubGUI(QWidget):
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

class StartSplash(QWidget):

    def __init__(self, parent=None, display_text=None):
        super().__init__(parent)
        self.label = QLabel(display_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()	
        layout.addWidget(self.label)
        self.setStyleSheet("QPushButton {border: 20px solid black; font-size: 64px; background-color: gray; color: black;}")

        self.setLayout(layout)



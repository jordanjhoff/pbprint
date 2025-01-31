from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QVBoxLayout

from states.AwaitPayment import AwaitPayment
from states.DisplayTextState import DisplayTextState
from states.PaymentManager import PaymentManager
from states.SelectTemplate import SelectTemplate
from states.State import State

class Start(State):
    def __init__(self, state_manager):
        super().__init__(state_manager=state_manager, main_widget=StartSplash(display_text="WELCOME!"), sub_widget=SubGUI())

        self.sub_widget.begin.clicked.connect(self.notify_state_update)

    def next_state(self, *args) -> 'State':
        return SelectTemplate(state_manager=self.state_manager)
        payment = PaymentManager()
        if payment.checkout_link is None:
            start = lambda: Start(self.state_manager)
            return DisplayTextState(state_manager=self.state_manager,
                                    display_text="Unable to connect to internet",
                                    timeout=10,
                                    next=start)
        return AwaitPayment(self.state_manager, payment_manager=payment)


class SubGUI(QWidget):
    """
    Widget with four invisible buttons in each corner.
    """
    begin = pyqtSignal()


    def __init__(self, parent=None):
        super().__init__(parent)

        self.begin = QPushButton("Begin", self)
        self.begin.setFixedSize(500, 300)
        self.begin.setStyleSheet("font-size: 32px;")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.begin)
        self.setLayout(button_layout)

class StartSplash(QWidget):

    def __init__(self, parent=None, display_text=None):
        super().__init__(parent)
        self.label = QLabel(display_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 64px;")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)



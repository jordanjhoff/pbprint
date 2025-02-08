import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit

from states.SelectTemplate import SelectTemplate
from states.State import State

password = "2121919"

class DevBypass(State):
    def __init__(self, state_manager):
        super().__init__(state_manager=state_manager, main_widget=None, sub_widget=Keypad())
        self.sub_widget.code_signal.connect(self.submit_code)

    def next_state(self, *args) -> State:
        if args[0] == password:
            return SelectTemplate(self.state_manager)
        else:
            print(f"Invalid code was entered:{args[0]}")
            from states.Start import Start
            return Start(self.state_manager)

    def submit_code(self, code):
        self.notify_state_update(code)


class Keypad(QWidget):

    code_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keypad Input")
        self.setGeometry(100, 100, 300, 400)


        layout = QVBoxLayout()
        self.textbox = QLineEdit(self)
        self.textbox.setReadOnly(True)
        self.textbox.setStyleSheet("font-size: 20px; padding: 10px;")
        layout.addWidget(self.textbox)
        keypad_layout = QGridLayout()
        buttons = {
            '1': (0, 0), '2': (0, 1), '3': (0, 2),
            '4': (1, 0), '5': (1, 1), '6': (1, 2),
            '7': (2, 0), '8': (2, 1), '9': (2, 2),
            '0': (3, 1)
        }

        for text, pos in buttons.items():
            button = QPushButton(text, self)
            button.setStyleSheet("font-size: 20px; padding: 15px;")
            button.clicked.connect(lambda checked, txt=text: self.append_digit(txt))
            keypad_layout.addWidget(button, *pos)

        back_button = QPushButton("Delete", self)
        back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        back_button.clicked.connect(self.remove_last_digit)
        keypad_layout.addWidget(back_button, 3, 0)

        select_button = QPushButton("Enter", self)
        select_button.setStyleSheet("font-size: 18px; padding: 10px;")
        select_button.clicked.connect(self.send_code)
        keypad_layout.addWidget(select_button, 3, 2)

        layout.addLayout(keypad_layout)
        self.setLayout(layout)

    def append_digit(self, digit):
        """ Append digit to the textbox """
        self.textbox.setText(self.textbox.text() + digit)

    def remove_last_digit(self):
        """ Remove the last digit """
        self.textbox.setText(self.textbox.text()[:-1])

    def send_code(self):
        code = self.textbox.text()
        self.code_signal.emit(code)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Keypad()
    window.show()
    sys.exit(app.exec_())
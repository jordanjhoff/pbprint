from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton

from states.Context import ConfigContext
from states.State import State


class DevControl(State):
    def __init__(self, state_manager, context: ConfigContext = ConfigContext()):
        super().__init__(state_manager=state_manager, main_widget=None, sub_widget=ControlPad(context=context))
        self.context = context
        self.sub_widget.done.clicked.connect(self.notify_state_update)

    def next_state(self, *args) -> State:
        from states.Start import Start
        return Start(self.state_manager, context=self.context)

    def submit_code(self, code):
        self.notify_state_update(code)

class ControlPad(QWidget):
    def __init__(self, context: ConfigContext = ConfigContext()):
        super().__init__()
        self.context = context
        layout = QVBoxLayout()
        self.done = QPushButton("Done", self)

        #Switch 1
        init_1_state = context.config.get("accept_payment")
        self.label1 = QLabel()
        self.switch1 = QCheckBox("Enable Payment")
        self.switch1.setChecked(init_1_state)
        self.switch1.stateChanged.connect(self.update_label1)

        #Switch 2
        init_2_state = context.config.get("templates") == context.config.get("template_group_2")
        self.label2 = QLabel()
        self.switch2 = QCheckBox("Alternate Templates")
        self.switch2.setChecked(init_2_state)
        self.switch2.stateChanged.connect(self.update_label2)

        self.update_label1(self.switch1.isChecked())
        self.update_label2(self.switch2.isChecked())

        layout.addWidget(self.switch1)
        layout.addWidget(self.switch2)
        layout.addWidget(self.done)

        self.setLayout(layout)
        self.setStyleSheet("""
                    QCheckBox {
                        font-size: 30px; /* Increase font size */
                        padding: 10px; /* Add padding */
                        color: black;
                    }
                    QCheckBox::indicator {
                        width: 40px;  /* Increase checkbox width */
                        height: 40px; /* Increase checkbox height */
                    }
                """)

    def update_label1(self, state: bool):
        self.context.config["accept_payment"] = state

    def update_label2(self, state: bool):
        self.context.config["templates"] = self.context.config["template_group_2"] if state else self.context.config["template_group_1"]


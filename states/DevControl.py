from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton

from StateManager import StateManager
from management.Context import Config
from states.State import State


class DevControl(State):
    """
    A state to allow developer controls during runtime.
    """
    def __init__(
        self,
        state_manager: StateManager,
        config: Config
    ):
        super().__init__(
            state_manager=state_manager,
            config=config,
            display_GUI=None,
            control_GUI=ControlGUI(config=config))

        self.control_GUI.done.clicked.connect(self.notify_transition_state)

    def next_state(self, *args) -> State:
        from states.Start import Start
        return Start(state_manager=self.state_manager, config=self.config)

    def submit_code(self, code):
        self.notify_transition_state(code)

class ControlGUI(QWidget):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        layout = QVBoxLayout()
        self.done = QPushButton("Done", self)

        # Accept payment toggle
        init_1_state = self.config.ACCEPT_PAYMENT
        self.label1 = QLabel()
        self.switch1 = QCheckBox("Enable Payment")
        self.switch1.setChecked(init_1_state)
        self.switch1.stateChanged.connect(self.update_accept_payment)

        # Template toggle
        init_2_state = self.config.CURRENT_TEMPLATES == self.config.template_group_alt
        self.label2 = QLabel()
        self.switch2 = QCheckBox("Alternate Templates")
        self.switch2.setChecked(init_2_state)
        self.switch2.stateChanged.connect(self.update_alt_templates)

        self.update_accept_payment(self.switch1.isChecked())
        self.update_alt_templates(self.switch2.isChecked())

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

    def update_accept_payment(self, state: bool):
        self.config.ACCEPT_PAYMENT = state

    def update_alt_templates(self, state: bool):
        self.config.CURRENT_TEMPLATES = self.config.template_group_alt if state else self.config.template_group_main


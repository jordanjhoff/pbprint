import os
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QLabel

from StateManager import StateManager
from management.Context import Config
from states.State import State
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QSize


assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))


class SelectTemplate(State):
    """
    State to allow users to select a template.
    """
    def __init__(self, state_manager: StateManager, config: Config):
        super().__init__(
            state_manager=state_manager,
            config=config,
            display_GUI=DisplayGUI(),
            control_GUI=ControlGUI()
        )
        self.templates = self.config.CURRENT_TEMPLATES
        self.current_index = 0
        self.display_GUI.set_images([item['border'] for item in self.templates])
        self.display_GUI.highlight_image(self.current_index)

        self.control_GUI.left_button.clicked.connect(self.prev_image)
        self.control_GUI.right_button.clicked.connect(self.next_image)
        self.control_GUI.select_button.clicked.connect(self.notify_transition_state)

    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.templates)
        self.update_image()

    def prev_image(self):
        self.current_index = (self.current_index - 1) % len(self.templates)
        self.update_image()

    def update_image(self):
        self.display_GUI.highlight_image(self.current_index)
        print(f"Template {self.current_index} selected.")

    def next_state(self, *args) -> 'State':
        from states.CaptureSequence import CaptureSequence
        from states.DisplayText import DisplayText
        return DisplayText(
            state_manager=self.state_manager,
            config=self.config,
            display_text="Ready?",
            timeout=7,
            next_state_lambda=(lambda: CaptureSequence(
                state_manager=self.state_manager,
                config=self.config,
                selected_template=self.templates[self.current_index])),
        )




class DisplayGUI(QWidget):
    """
    Displays images horizontally, with one image highlighted at a time and one text box under the images.
    """

    def __init__(self):
        super().__init__()
        self.labels = []
        self.layout = QVBoxLayout()
        self.image_layout = QHBoxLayout()
        self.text_label = QLabel("CHOOSE A TEMPLATE USING THE KEYPAD, AND PRESS SELECT", self)
        self.text_label.setStyleSheet("font-size: 32px;")
        self.text_label.setAlignment(Qt.AlignCenter)

        self.layout.addLayout(self.image_layout)
        self.layout.addWidget(self.text_label, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def set_images(self, images):
        """Set the images to be displayed and highlight the first one."""
        self.labels.clear()
        image_layout = QHBoxLayout()
        
        screen = QApplication.primaryScreen().availableGeometry()
        screen_width = screen.width()
        num_images = len(images)
        max_width_per_image = int(screen_width // num_images)
        max_height = int(screen.height() * 0.5) 

        for image_path in images:
            label = QLabel(self)
            pixmap = QPixmap(image_path)
            label.setPixmap(pixmap.scaled(max_width_per_image, max_height, Qt.KeepAspectRatio))
            label.setAlignment(Qt.AlignCenter)
            self.labels.append(label)
            image_layout.addWidget(label)


        self.layout.addLayout(image_layout)
        self.layout.addWidget(self.text_label)

    def highlight_image(self, index):
        """
        Highlight the image at the given index.
        """
        for i, label in enumerate(self.labels):
            if i == index:
                label.setStyleSheet("border: 10px solid red;")
            else:
                label.setStyleSheet("")


class ControlGUI(QWidget):
    """
    Contains left, right, and select buttons to navigate through images.
    """

    def __init__(self):
        super().__init__()
        self.left_button = QPushButton("", self)
        self.right_button = QPushButton("", self)
        self.select_button = QPushButton("Select", self)

        self.left_button.setFixedSize(300, 200)
        self.right_button.setFixedSize(300, 200)
        self.left_button.setIcon(QIcon(f'{assets_dir}/left.png'))
        self.right_button.setIcon(QIcon(f'{assets_dir}/right.png'))
        self.left_button.setIconSize(QSize(300, 200))
        self.right_button.setIconSize(QSize(300, 200))
        self.select_button.setFixedSize(300, 200)
        self.setStyleSheet("QPushButton {border: 10px solid black; font-size: 64px; background-color: gray; color: black;}")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.left_button)
        button_layout.addWidget(self.right_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)


        select_layout = QHBoxLayout()
        select_layout.addStretch()
        select_layout.addWidget(self.select_button)
        select_layout.addStretch()


        main_layout.addLayout(select_layout)
        self.setLayout(main_layout)
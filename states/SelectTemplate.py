import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

from states.CaptureSequence import CaptureSequence
from states.DisplayTextState import DisplayTextState
from states.State import State

assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))

vinny_template = {"num_images":3,
                  "image_size":(482, 435),
                  "starting_pos":(59,59),
                  "image_div":58,
                  "border":f"{assets_dir}/vinny2.png",
                  "orientation":"vertical"}

template_2 = {"num_images":4,
                  "image_size":(482, 322),
                  "starting_pos":(59,59),
                  "image_div":58,
                  "border":f"{assets_dir}/template_2.png",
              "orientation":"vertical"}

film_template = {"num_images":3,
                  "image_size":(414, 569),
                  "starting_pos":(91,23),
                  "image_div":10,
                  "border":f"{assets_dir}/film_strip.png",
                 "orientation":"horizontal"}

templates = [vinny_template, template_2, film_template]

class SelectTemplate(State):

    def __init__(self, state_manager):
        super().__init__(state_manager, main_widget=MainGUI(), sub_widget=SubGUI())
        """Manages the image selection and interaction between the two GUIs."""

        self.templates = templates
        self.current_index = 0
        self.main_widget.set_images([item['border'] for item in templates])
        self.main_widget.highlight_image(self.current_index)

        self.sub_widget.left_button.clicked.connect(self.prev_image)
        self.sub_widget.right_button.clicked.connect(self.next_image)
        self.sub_widget.select_button.clicked.connect(self.notify_state_update)

    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.templates)
        self.update_image()

    def prev_image(self):
        self.current_index = (self.current_index - 1) % len(self.templates)
        self.update_image()

    def update_image(self):
        self.main_widget.highlight_image(self.current_index)
        print(f"Template {self.current_index} selected.")

    def next_state(self, *args) -> 'State':
        return DisplayTextState(state_manager=self.state_manager,
                                display_text="Ready?",
                                timeout=7,
                                next=(lambda: CaptureSequence(state_manager=self.state_manager, template=self.templates[self.current_index])))



class MainGUI(QWidget):
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

        for image_path in images:
            label = QLabel(self)
            pixmap = QPixmap(image_path)
            label.setPixmap(pixmap.scaled(500, 500, Qt.KeepAspectRatio))
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


from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


class SubGUI(QWidget):
    """
    Contains left, right, and select buttons to navigate through images.
    """

    def __init__(self):
        super().__init__()
        self.left_button = QPushButton("Left", self)
        self.right_button = QPushButton("Right", self)
        self.select_button = QPushButton("Select", self)

        self.left_button.setFixedSize(300, 200)
        self.right_button.setFixedSize(300, 200)
        self.select_button.setFixedSize(300, 200)

        self.left_button.setStyleSheet("font-size: 32px;")
        self.right_button.setStyleSheet("font-size: 32px;")
        self.select_button.setStyleSheet("font-size: 32px;")

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
from abc import ABC, abstractmethod
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QState
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget


class State(QObject):
    """
    Abstract base class representing a state in the application.
    """
    def __init__(self, state_manager, main_widget: QWidget, sub_widget: QWidget):
        """
        Initialize the state with references to the main and sub widgets.

        :param main_widget: The main widget of the application.
        :param sub_widget: The sub widget of the application.
        """
        super().__init__()
        self.state_manager = state_manager
        self.main_widget = main_widget
        self.sub_widget = sub_widget
        self.state_changed_signal = pyqtSignal()

    @abstractmethod
    def next_state(self, *args) -> 'State':
        """
        Abstract method for transitioning to the next state.
        :param *args:
        :return: The next state.
        """
        pass

    def notify_state_update(self, *args) -> None:
        """
        Method to trigger when the state is updated.
        :param *args:
        """
        self.state_manager.advance_state(self.next_state(*args))

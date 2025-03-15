from __future__ import annotations

from abc import abstractmethod


from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget

from management.Context import Config
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    import StateManager



class State(QObject):
    """
    Abstract base class representing a state in the application.
    """
    def __init__(
        self,
        state_manager: StateManager,
        config: Config,
        display_GUI: Optional[QWidget] | None,
        control_GUI: Optional[QWidget] | None
    ) -> None:
        """
        Initialize the state with references to the main and sub widgets.

        :param display_GUI: The main widget of the application.
        :param control_GUI: The sub widget of the application.
        """
        super().__init__()
        self.display_GUI = display_GUI
        self.control_GUI = control_GUI
        self.config = config
        self.state_changed_signal = pyqtSignal()
        self.state_manager = state_manager

    @abstractmethod
    def next_state(self, *args) -> 'State':
        """
        Abstract method for determining the next state of the application.
        :param *args: Arguments received for more precise state control.
        :return: The next state.
        """
        pass

    def notify_transition_state(self, *args) -> None:
        """
        Method to trigger when the state is updated.
        :param *args: Arguments passed to the next state method.
        """
        self.state_manager.advance_state(self.next_state(*args))

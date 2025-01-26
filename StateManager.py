from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from states.Start import Start
from states.State import State


class StateManager(QObject):
    def __init__(self):
        super().__init__()
        self.current_state = Start(self)
        self.main_window = FullScreenWindow(monitor_index=0)
        self.main_window.setWindowTitle("Main")
        self.sub_window = FullScreenWindow(monitor_index=1)
        self.sub_window.setWindowTitle("Sub")
        self.sub_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.update_windows()

    def update_windows(self) -> None:
        """
        Update the main and sub windows to reflect the current state's widgets.
        """
        self.main_window.setCentralWidget(self.current_state.main_widget)
        self.sub_window.setCentralWidget(self.current_state.sub_widget)
        self.main_window.show()
        self.sub_window.show()

    def advance_state(self, next_state: State) -> None:
        """Transition to the next state."""
        if next_state:
            self.current_state = next_state
            self.main_window.activateWindow()
            self.update_windows()
            self.main_window.activateWindow()
            

class FullScreenWindow(QMainWindow):
    def __init__(self, monitor_index=0):
        super().__init__()
        app = QApplication.instance()
        screens = app.screens()
        if monitor_index < 0 or monitor_index >= len(screens):
            raise ValueError(f"Monitor index {monitor_index} is out of range. Available monitors: {len(screens)}")
        screen = screens[monitor_index]
        self.setGeometry(screen.geometry())
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)


if __name__ == "__main__":
    app = QApplication([])
    state_manager = StateManager()
    app.exec_()
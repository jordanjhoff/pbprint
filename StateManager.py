import sys

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

from management.Context import Config
from states.State import State
from getdevice import *


class StateManager(QObject):
    def __init__(self):
        target_device_name = "CTP_CONTROL"
        target_output_name = "HDMI-1"
        device_id = get_device_id(target_device_name)
        if device_id:
            map_device_to_output(device_id, target_output_name)
        
        super().__init__()
        from states.Start import Start
        self.current_state = Start(state_manager=self, config=Config())
        self.display_GUI = FullScreenWindow(monitor_index=1)
        self.display_GUI.setWindowTitle("Main")
        self.control_GUI = FullScreenWindow(monitor_index=0)
        self.control_GUI.setWindowTitle("Sub")
        self.control_GUI.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.update_windows()

    def update_windows(self) -> None:
        """
        Update the main and sub windows to reflect the current state's widgets.
        """
        self.display_GUI.setCentralWidget(self.current_state.display_GUI)
        self.control_GUI.setCentralWidget(self.current_state.control_GUI)
        self.display_GUI.show()
        self.control_GUI.show()

    def advance_state(self, next_state: State) -> None:
        """Transition to the next state."""
        if next_state:
            self.current_state = next_state
            self.display_GUI.activateWindow()
            self.update_windows()
            self.display_GUI.activateWindow()
            

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
        self.setStyleSheet("background-color: beige;")
        app.setStyleSheet("""
            QPushButton {
                background-color: darkgray;
                color: black;
                font-size: 18px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: gray;
            }
            QLabel, QLineEdit {
                color: black;
                font-size: 32px;
            }
        """)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            QApplication.quit()
            exit()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet("QPushButton {border: 20px solid black; font-size: 128px; background-color: gray; color: black;}")
    state_manager = StateManager()
    
    app.exec_()
    
    sys.exit(app.exec_())

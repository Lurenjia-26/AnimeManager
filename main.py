import sys
from PyQt6.QtWidgets import QApplication
from GUI_qt import Application
from ConfigManager import ConfigManager

if __name__ == "__main__":
    configManager = ConfigManager("config.json")
    app = QApplication(sys.argv)
    window = Application(configManager)
    window.show()
    sys.exit(app.exec())
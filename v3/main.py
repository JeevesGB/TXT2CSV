import sys
from PyQt6.QtWidgets import QApplication
from ui import CSVGeneratorApp
from utils import load_stylesheet

STYLE_FILE = "assets/styles/dark.qss"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    load_stylesheet(app, STYLE_FILE)

    win = CSVGeneratorApp()
    win.show()
    sys.exit(app.exec())

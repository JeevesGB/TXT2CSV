# ui.py
import sys
import os
import json
import base64
import shutil
import time
import subprocess  # <-- added

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeView, QFileDialog, QMessageBox,
    QScrollArea, QStatusBar, QGroupBox, QLineEdit, QProgressDialog,
    QSplitter, QFormLayout
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer, QProcess

try:
    from PyQt6.QtWidgets import QFileSystemModel
except ImportError:
    from PyQt6.QtGui import QFileSystemModel


# ---- Files ----
JSON_SCHEMA_FILE = "data/headers.json"
CAR_NAMES_FILE = "data/CarNames.json"
CONFIG_FILE = "data/config.json"
ICON_FILE = "assets/ICO.ico"
STYLE_FILE = "assets/styles/dark.qss"


ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA"
    "B3RJTUUH5QcGDC8Qv0k2VwAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAJ"
    "cEhZcwAACxMAAAsTAQCanBgAAAAZdEVYdFNvZnR3YXJlAEFkb2JlIEltYWdlUmVhZHlxyWU8AAAB"
    "K0lEQVQ4y2NgGAWjYBSMglEwCqQGJgYGBg+M8wMDAw8P///w8mJiYGBgYGRkZGBgYGBgYGBgYmJiY"
    "GJgYGBgYmBgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGBgYGJiYGBgY"
    "GJgYGBgYGJgYGBgYGAEAAwABBgAABrQAAQAAAABJRU5ErkJggg=="
)


# ---- Utility ----
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def load_stylesheet(app, filename):
    path = resource_path(filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Stylesheet not found: {path}")


# ---- Main App ----
class CSVGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GT2 SplitData CSV Generator")
        self.resize(1400, 850)
        self.setMinimumSize(1100, 700)

        self.entries = {}

        self.ensure_folders()
        self.ensure_icon_file()
        self.setWindowIcon(QIcon(resource_path(ICON_FILE)))

        self.schema = self.load_json(JSON_SCHEMA_FILE)
        self.car_names = self.load_json(CAR_NAMES_FILE, default=[])
        self.config = self.load_config()

        self.build_ui()

        split = self.config.get("split_data_path")
        if split and os.path.isdir(split):
            self.load_split_data(split)
        else:
            QTimer.singleShot(100, self.prompt_for_split_folder)

    # ---------- Helpers ----------
    def ensure_folders(self):
        for folder in ["data", "assets", "styles"]:
            os.makedirs(folder, exist_ok=True)

    def ensure_icon_file(self):
        if not os.path.isfile(ICON_FILE):
            with open(ICON_FILE, "wb") as f:
                f.write(base64.b64decode(ICON_B64))

    def load_json(self, path, default=None):
        full_path = resource_path(path)
        if os.path.isfile(full_path):
            try:
                with open(full_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load {path}: {e}")
        return default

    # ---------- UI ----------
    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ---- LEFT PANEL ----
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(12)

        # --- Split Data + CSV Buttons ---
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()

        self.open_btn = QPushButton("Open Split Folder")
        self.open_btn.clicked.connect(self.choose_split_folder)

        self.split_btn = QPushButton("Run GT2DataSplitter")
        self.split_btn.clicked.connect(self.run_splitter)
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.setShortcut("Ctrl+O")
        self.import_btn.clicked.connect(self.import_csv)

        self.export_btn = QPushButton("Generate CSV")
        self.export_btn.setShortcut("Ctrl+S")
        self.export_btn.clicked.connect(self.export_csv)

        controls_layout.addWidget(self.open_btn)
        controls_layout.addWidget(self.split_btn)
        controls_layout.addSpacing(8)
        controls_layout.addWidget(self.import_btn)
        controls_layout.addWidget(self.export_btn)

        controls_group.setLayout(controls_layout)
        left_layout.addWidget(controls_group)

        # --- Tree view ---
        browser_group = QGroupBox("Split Data Files")
        browser_layout = QVBoxLayout()

        self.model = QFileSystemModel()
        self.model.setRootPath("")

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.doubleClicked.connect(self.on_tree_double)
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(18)
        self.tree.setHeaderHidden(True)

        for i in range(1, self.model.columnCount()):
            self.tree.hideColumn(i)

        browser_layout.addWidget(self.tree)
        browser_group.setLayout(browser_layout)
        left_layout.addWidget(browser_group)

        splitter.addWidget(left_widget)

        # ---- RIGHT PANEL ----
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.scroll.setWidget(self.form_container)

        right_layout.addWidget(self.scroll)
        splitter.addWidget(right_widget)

        splitter.setSizes([350, 1000])

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

    # ---------- Split Data ----------
    def choose_split_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Split Data Folder")
        if not path:
            return
        self.load_split_data(path)
        self.config["split_data_path"] = path
        self.save_config(self.config)

    def prompt_for_split_folder(self):
        if QMessageBox.question(
            self, "Split Data Required", "Locate the Split Data folder now?"
        ) == QMessageBox.StandardButton.Yes:
            self.choose_split_folder()

    def load_split_data(self, path):
        self.tree.setRootIndex(self.model.index(path))
        self.status.showMessage(f"Loaded {path}")

    # ---------- CSV ----------
    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", filter="CSV Files (*.csv)")
        if path:
            self.load_csv_to_entries(path)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", filter="CSV Files (*.csv)")
        if not path:
            return

        headers = ['"' + h + '"' for h in self.entries.keys()]
        values = ['"' + e.text() + '"' for e in self.entries.values()]

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(",".join(headers) + "\n")
            f.write(",".join(values) + "\n")

        self.status.showMessage(f"Saved {os.path.basename(path)}")

    def on_tree_double(self, index):
        path = self.model.filePath(index)
        if path.lower().endswith(".csv"):
            self.load_csv_to_entries(path)

    def load_csv_to_entries(self, path):
        with open(path, "r", encoding="utf-8-sig") as f:
            lines = f.read().splitlines()

        headers = [h.strip().strip('"') for h in lines[0].split(",")]
        values = [v.strip().strip('"') for v in lines[1].split(",")] if len(lines) > 1 else []

        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.entries.clear()

        group = QGroupBox("CSV Fields")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for h, val in zip(headers, values):
            e = QLineEdit(val)
            form.addRow(h + ":", e)
            self.entries[h] = e

        self.form_layout.addWidget(group)
        self.form_layout.addStretch()

    # ---------- Splitter ----------
    def run_splitter(self):
        split_path = self.config.get("split_data_path")

        if not split_path or not os.path.isdir(split_path):
            QMessageBox.warning(self, "SplitData not set", "Please select your SplitData folder first.")
            return

        exe_path = resource_path("tool/GT2DataSplitter.exe")
        if not os.path.isfile(exe_path):
            QMessageBox.critical(self, "Error", f"GT2DataSplitter.exe not found:\n{exe_path}")
            return

        # Prompt user not to close main app
        QMessageBox.information(
            self,
            "GT2DataSplitter Running",
            "GT2DataSplitter will now run in a separate console.\nPlease DO NOT close this application until it finishes."
        )

        # Launch GT2DataSplitter in its own console window
        try:
            subprocess.Popen(
                [exe_path, split_path],
                cwd=split_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.status.showMessage("GT2DataSplitter launched in new console...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch GT2DataSplitter:\n{e}")

    # ---------- Config ----------
    def load_config(self):
        path = resource_path(CONFIG_FILE)
        if os.path.isfile(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def save_config(self, cfg):
        path = resource_path(CONFIG_FILE)
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)



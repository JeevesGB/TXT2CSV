import sys
import os
import json
import csv
import base64
import shutil
import time
import subprocess

# ---- PyQt imports ----
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeView, QFileDialog, QMessageBox,
    QScrollArea, QStatusBar, QGroupBox, QLineEdit, QProgressDialog
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer

# ---- PyQt6 QFileSystemModel compatibility ----
try:
    from PyQt6.QtWidgets import QFileSystemModel
except ImportError:
    # fallback for PyQt6 < 6.5 or missing QFileSystemModel
    from PyQt6.QtGui import QFileSystemModel

# ---- Files ----
JSON_SCHEMA_FILE = "data/headers.json"
CAR_NAMES_FILE = "data/CarNames.json"
CONFIG_FILE = "data/config.json"
ICON_FILE = "assets/ICO.png"
ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA"
    "B3RJTUUH5QcGDC8Qv0k2VwAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAJ"
    "cEhZcwAACxMAAAsTAQCanBgAAAAZdEVYdFNvZnR3YXJlAEFkb2JlIEltYWdlUmVhZHlxyWU8AAAB"
    "K0lEQVQ4y2NgGAWjYBSMglEwCqQGJgYGBg+M8wMDAw8P///w8mJiYGBgYGRkZGBgYGBgYGBgYmJiY"
    "GJgYGBgYmBgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGBgYGJiYGBgY"
    "GJgYGBgYGJgYGBgYGAEAAwABBgAABrQAAQAAAABJRU5ErkJggg=="
)

# ---- Main App ----
class CSVGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TXT → CSV")
        self.resize(900, 650)

        self.entries = {}
        self.ensure_folders()
        self.ensure_icon_file()
        self.setWindowIcon(QIcon(ICON_FILE))

        self.schema = self.load_json(JSON_SCHEMA_FILE)
        self.car_names = self.load_json(CAR_NAMES_FILE, default=[])
        self.config = self.load_config()

        self.build_ui()

        split = self.config.get("split_data_path")
        if split and os.path.isdir(split):
            self.load_split_data(split)
        else:
            QTimer.singleShot(100, self.prompt_for_split_folder)

    # ---- Helpers ----
    def ensure_folders(self):
        for folder in ["data", "assets"]:
            os.makedirs(folder, exist_ok=True)

    def ensure_icon_file(self):
        if not os.path.isfile(ICON_FILE):
            with open(ICON_FILE, "wb") as f:
                f.write(base64.b64decode(ICON_B64))

    def load_json(self, path, default=None):
        base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        full_path = os.path.join(base, path)
        if os.path.isfile(full_path):
            try:
                with open(full_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load {path}: {e}")
        return default

    def get_car_id(self, a, b):
        a, b = a.strip().lower(), b.strip().lower()
        for car in self.car_names:
            if car["CarNameFirstPart"].lower() == a and car["CarNameSecondPart"].lower() == b:
                return car["CarId"]
        return None

    # ---- UI ----
    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # LEFT PANEL
        left = QVBoxLayout()
        layout.addLayout(left, 1)

        left.addWidget(QLabel("Split Data"))
        btn = QPushButton("Choose Folder")
        btn.clicked.connect(self.choose_split_folder)
        left.addWidget(btn)

        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.doubleClicked.connect(self.on_tree_double)
        left.addWidget(self.tree)

        # RIGHT PANEL
        right = QVBoxLayout()
        layout.addLayout(right, 3)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.scroll.setWidget(self.form_container)
        right.addWidget(self.scroll)

        bottom = QHBoxLayout()
        right.addLayout(bottom)

        imp = QPushButton("Import CSV")
        imp.clicked.connect(self.import_csv)
        bottom.addWidget(imp)

        exp = QPushButton("Generate CSV")
        exp.clicked.connect(self.export_csv)
        bottom.addWidget(exp)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

    # ---- Split Data ----
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
        self.prompt_backup_split_data(path)
        self.tree.setRootIndex(self.model.index(path))
        self.status.showMessage(f"Loaded {path}")

    # ---- Backup ----
    def prompt_backup_split_data(self, path):
        backup = os.path.join(os.path.dirname(path), "SplitData-Copy")
        if os.path.exists(backup):
            return

        if QMessageBox.question(
            self, "Backup Split Data", "Create a backup copy?\n\nSplitData-Copy will be created."
        ) != QMessageBox.StandardButton.Yes:
            return

        self.copy_with_progress(path, backup)

    def copy_with_progress(self, src, dst):
        files = [os.path.join(root, f) for root, _, names in os.walk(src) for f in names]
        dlg = QProgressDialog("Copying Split Data…", None, 0, len(files), self)
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        dlg.show()

        start = time.time()
        for i, f in enumerate(files, 1):
            rel = os.path.relpath(f, src)
            out = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(f, out)

            elapsed = time.time() - start
            rate = i / elapsed if elapsed else 0
            eta = int((len(files) - i) / rate) if rate else 0

            dlg.setValue(i)
            dlg.setLabelText(f"{i}/{len(files)} files — ETA {eta}s")
            QApplication.processEvents()

        dlg.close()
        self.status.showMessage("Split Data backed up successfully")

    # ---- CSV ----
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
            w = self.form_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        self.entries.clear()

        group = QGroupBox("Fields")
        vlayout = QVBoxLayout(group)

        for h, val in zip(headers, values):
            row = QHBoxLayout()
            row.addWidget(QLabel(h))
            e = QLineEdit(val)
            row.addWidget(e)
            vlayout.addLayout(row)
            self.entries[h] = e
        self.form_layout.addWidget(group)
        self.form_layout.addStretch()



    # ---- Config ----
    def load_config(self):
        path = os.path.join(os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__), CONFIG_FILE)
        if os.path.isfile(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def save_config(self, cfg):
        path = os.path.join(os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__), CONFIG_FILE)
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)

# ---- Run ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CSVGeneratorApp()
    win.show()
    sys.exit(app.exec())

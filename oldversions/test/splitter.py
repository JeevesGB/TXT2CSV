import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QProcess
from utils import resource_path

def run_splitter(parent, split_path):
    if not split_path or not os.path.isdir(split_path):
        QMessageBox.warning(parent, "SplitData not set", "Please select your SplitData folder first.")
        return

    exe_path = resource_path("tool/GT2DataSplitter.exe")
    if not os.path.isfile(exe_path):
        QMessageBox.critical(parent, "Error", f"GT2DataSplitter.exe not found:\n{exe_path}")
        return

    process = QProcess(parent)
    process.setWorkingDirectory(split_path)
    success = process.startDetached(exe_path, [], split_path)
    if success:
        parent.status.showMessage("GT2DataSplitter launched")
    else:
        QMessageBox.critical(parent, "Error", "Failed to launch GT2DataSplitter")

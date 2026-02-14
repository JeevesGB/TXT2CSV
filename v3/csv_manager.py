import os
import csv
from PyQt6.QtWidgets import QLineEdit, QGroupBox, QFormLayout, QVBoxLayout

def load_csv(path, form_layout, entries):
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.read().splitlines()

    headers = [h.strip().strip('"') for h in lines[0].split(",")]
    values = [v.strip().strip('"') for v in lines[1].split(",")] if len(lines) > 1 else []

    while form_layout.count():
        item = form_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
    entries.clear()

    group = QGroupBox("CSV Fields")
    form = QFormLayout(group)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    for h, val in zip(headers, values):
        e = QLineEdit(val)
        form.addRow(h + ":", e)
        entries[h] = e

    form_layout.addWidget(group)
    form_layout.addStretch()

def export_csv(path, entries):
    headers = ['"' + h + '"' for h in entries.keys()]
    values = ['"' + e.text() + '"' for e in entries.values()]

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(",".join(headers) + "\n")
        f.write(",".join(values) + "\n")

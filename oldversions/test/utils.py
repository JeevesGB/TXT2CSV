import sys
import os
import base64

ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA"
    "B3RJTUUH5QcGDC8Qv0k2VwAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAJ"
    "cEhZcwAACxMAAAsTAQCanBgAAAAZdEVYdFNvZnR3YXJlAEFkb2JlIEltYWdlUmVhZHlxyWU8AAAB"
    "K0lEQVQ4y2NgGAWjYBSMglEwCqQGJgYGBg+M8wMDAw8P///w8mJiYGBgYGRkZGBgYGBgYGBgYmJiY"
    "GJgYGBgYmBgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGBgYGJiYGBgYGJgYGBgY"
    "GJgYGBgYGAEAAwABBgAABrQAAQAAAABJRU5ErkJggg=="
)

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

def ensure_icon_file(icon_path):
    if not os.path.isfile(icon_path):
        with open(icon_path, "wb") as f:
            f.write(base64.b64decode(ICON_B64))

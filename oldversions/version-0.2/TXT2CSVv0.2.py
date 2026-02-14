import json
import csv
import os
import base64
import sys
import shutil
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

JSON_SCHEMA_FILE = "headers.json"
CAR_NAMES_FILE = "carnames.json"
CONFIG_FILE = "config.json"
ICON_FILE = "icon.png"
ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA"
    "B3RJTUUH5QcGDC8Qv0k2VwAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAJ"
    "cEhZcwAACxMAAAsTAQCanBgAAAAZdEVYdFNvZnR3YXJlAEFkb2JlIEltYWdlUmVhZHlxyWU8AAAB"
    "K0lEQVQ4y2NgGAWjYBSMglEwCqQGJgYGBg+M8wMDAw8P///w8mJiYGBgYGRkZGBgYGBgYGBgYmJiY"
    "GJgYGBgYmBgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGJgYGBgYGBgYGJiYGBgY"
    "GJgYGBgYGJgYGBgYGAEAAwABBgAABrQAAQAAAABJRU5ErkJggg=="
)


class CollapsibleSection(ttk.Frame):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.visible = tk.BooleanVar(value=True)

        self.header = ttk.Checkbutton(
            self, text=title, variable=self.visible,
            command=self.toggle, style="Toolbutton"
        )
        self.header.pack(anchor="w", pady=(8, 2))

        self.body = ttk.Frame(self)
        self.body.pack(fill="x", expand=True)

    def toggle(self):
        if self.visible.get():
            self.body.pack(fill="x", expand=True)
        else:
            self.body.forget()


class CSVGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TXT → CSV")
        self.root.geometry("600x700")

        self.schema = self.load_schema()
        self.entries = {}
        self.car_names = self.load_car_names()

        try:
            self.ensure_icon_file()
        except Exception:
            pass

        self.build_ui()

        self.config = self.load_config()
        split = self.config.get("split_data_path")
        if split and os.path.isdir(split):
            self.load_split_data(split)
        else:
            self.root.after(100, self.prompt_for_split_folder)

    # ---------- JSON ----------
    def load_schema(self):
        base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        with open(os.path.join(base, JSON_SCHEMA_FILE), "r", encoding="utf-8") as f:
            return json.load(f)

    def load_car_names(self):
        try:
            base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
            with open(os.path.join(base, CAR_NAMES_FILE), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def get_car_id(self, name1, name2):
        name1 = name1.strip().lower()
        name2 = name2.strip().lower()
        for car in self.car_names:
            if (car["CarNameFirstPart"].lower() == name1 and
                car["CarNameSecondPart"].lower() == name2):
                return car["CarId"]
        return None

    # ---------- BACKUP WITH PROGRESS + ETA ----------
    def prompt_backup_split_data(self, split_path):
        parent = os.path.dirname(split_path)
        backup_path = os.path.join(parent, "SplitData-Copy")

        if os.path.exists(backup_path):
            return

        if not messagebox.askyesno(
            "Backup Split Data",
            "Split Data folder detected.\n\n"
            "Create a backup copy?\n\n"
            "A folder named 'SplitData-Copy' will be created."
        ):
            return

        self.copy_with_progress(split_path, backup_path)

    def copy_with_progress(self, src, dst):
        files = []
        for root, _, filenames in os.walk(src):
            for f in filenames:
                files.append(os.path.join(root, f))

        total = len(files)
        if total == 0:
            return

        win = tk.Toplevel(self.root)
        win.title("Creating Backup")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="Copying Split Data…").pack(padx=10, pady=(10, 4))
        info = ttk.Label(win, text="Starting…")
        info.pack(padx=10)

        bar = ttk.Progressbar(win, length=320, maximum=total)
        bar.pack(padx=10, pady=10)

        start_time = time.time()
        copied = 0

        for src_file in files:
            rel = os.path.relpath(src_file, src)
            dst_file = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

            shutil.copy2(src_file, dst_file)

            copied += 1
            bar["value"] = copied

            elapsed = time.time() - start_time
            rate = copied / elapsed if elapsed > 0 else 0
            remaining = int((total - copied) / rate) if rate > 0 else 0

            info.config(
                text=f"{copied}/{total} files  —  ETA: {remaining}s"
            )

            win.update_idletasks()

        win.destroy()
        self.status.set("Split Data backed up successfully")

    # ---------- UI ----------
    def build_ui(self):
        main = ttk.Panedwindow(self.root, orient="horizontal")
        main.pack(fill="both", expand=True, padx=10, pady=5)

        left = ttk.Frame(main)
        main.add(left, weight=1)

        ttk.Label(left, text="Split Data").pack(anchor="w")
        ttk.Button(left, text="Choose Folder", command=self.choose_split_folder).pack(anchor="w")

        self.tree = ttk.Treeview(left)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double)

        right = ttk.Frame(main)
        main.add(right, weight=3)

        self.canvas = tk.Canvas(right)
        self.scroll = ttk.Scrollbar(right, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.form_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Import CSV", command=self.import_csv).pack(side="left")
        ttk.Button(bottom, text="Generate CSV", command=self.export_csv).pack(side="right")

        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x")

    # ---------- Split Data ----------
    def choose_split_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self.load_split_data(path)
        self.config["split_data_path"] = path
        self.save_config(self.config)

    def prompt_for_split_folder(self):
        if messagebox.askyesno("Split Data Required", "Locate the Split Data folder now?"):
            self.choose_split_folder()

    def load_split_data(self, root_path):
        self.prompt_backup_split_data(root_path)
        self.tree.delete(*self.tree.get_children())

        root_id = self.tree.insert("", "end", text=os.path.basename(root_path), open=True, values=[root_path])
        path_map = {root_path: root_id}

        for dirpath, dirnames, filenames in os.walk(root_path):
            parent = path_map.get(dirpath, root_id)
            for d in dirnames:
                full = os.path.join(dirpath, d)
                path_map[full] = self.tree.insert(parent, "end", text=d, values=[full])
            for f in filenames:
                self.tree.insert(parent, "end", text=f, values=[os.path.join(dirpath, f)])

    # ---------- CSV ----------
    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        self.load_csv_to_entries(path)

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        headers = list(self.entries.keys())
        values = [self.entries[h][1].get() for h in headers]
        with open(path, "w", newline="") as f:
            csv.writer(f).writerows([headers, values])
        self.status.set(f"Saved {os.path.basename(path)}")

    def on_tree_double(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        path = self.tree.item(item, "values")[0]
        if path.lower().endswith(".csv"):
            self.load_csv_to_entries(path)

    def load_csv_to_entries(self, path):
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        headers = rows[0]
        values = rows[1] if len(rows) > 1 else []

        for w in self.form_frame.winfo_children():
            w.destroy()
        self.entries.clear()

        section = CollapsibleSection(self.form_frame, "Fields")
        section.pack(fill="x")

        for h, v in zip(headers, values):
            row = ttk.Frame(section.body)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=h, width=28).pack(side="left")
            e = ttk.Entry(row)
            e.insert(0, v)
            e.pack(side="left", fill="x", expand=True)
            self.entries[h] = (row, e)

        self.status.set(f"Imported {os.path.basename(path)}")

    # ---------- Config ----------
    def load_config(self):
        path = os.path.join(os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__), CONFIG_FILE)
        if os.path.isfile(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_config(self, cfg):
        path = os.path.join(os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__), CONFIG_FILE)
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)

    # ---------- Icon ----------
    def ensure_icon_file(self):
        base = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__)
        path = os.path.join(base, ICON_FILE)
        if not os.path.isfile(path):
            with open(path, "wb") as f:
                f.write(base64.b64decode(ICON_B64))


if __name__ == "__main__":
    root = tk.Tk()
    CSVGeneratorApp(root)
    root.mainloop()

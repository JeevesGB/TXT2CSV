import json
import csv
import os
import base64
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
            self,
            text=title,
            variable=self.visible,
            command=self.toggle,
            style="Toolbutton"
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
        self.root.minsize(500, 500)

        self.schema = self.load_schema()
        self.entries = {}
        self.car_names = self.load_car_names()  

        # ensure icon exists before building UI
        try:
            self.ensure_icon_file()
        except Exception:
            pass

        self.build_ui()

        self.config = self.load_config()
        split = self.config.get("split_data_path")
        if split and os.path.isdir(split):
            try:
                self.load_split_data(split)
            except Exception:
                pass
        else:

            try:
                self.root.after(100, self.prompt_for_split_folder)
            except Exception:

                self.prompt_for_split_folder()

    # ---------- Load JSON ----------
    def load_schema(self):
        try:
            with open(JSON_SCHEMA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Schema Error", f"Failed to load JSON:\n{e}")
            self.root.destroy()

    # ---------- Load Car Names JSON ----------
    def load_car_names(self):
        try:
            with open(CAR_NAMES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("CarNames Error", f"Failed to load CarNames JSON:\n{e}")
            return {}

    # ---------- Lookup CarId ----------
    def get_car_id(self, name1, name2):
        name1 = name1.strip().lower()
        name2 = name2.strip().lower()

        for car in self.car_names:
            if (car["CarNameFirstPart"].strip().lower() == name1 and
                car["CarNameSecondPart"].strip().lower() == name2):
                return car["CarId"]  

        return None

    # ---------- UI ----------
    def build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")


        main_paned = ttk.Panedwindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=10, pady=5)


        tree_container = ttk.Frame(main_paned, width=200)
        main_paned.add(tree_container, weight=1)
        ttk.Label(tree_container, text="Split Data: ").pack(anchor="w")
        btn_frame = ttk.Frame(tree_container)
        btn_frame.pack(fill="x", pady=(2, 6))
        ttk.Button(btn_frame, text="Choose Folder", command=self.choose_split_folder).pack(side="left")

        self.tree = ttk.Treeview(tree_container)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double)


        container = ttk.Frame(main_paned)
        main_paned.add(container, weight=4)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.form_frame = ttk.Frame(self.canvas)
        self.form_window = self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        self.form_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )


        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.form_window, width=e.width)
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)


        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Import CSV", command=self.import_csv).pack(side="left")
        ttk.Button(bottom, text="Generate CSV", command=self.export_csv).pack(side="right")

        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x")
        # set window icon (if available)
        try:
            self.set_window_icon()
        except Exception:
            pass

    # ---------- Mouse wheel ----------
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # ---------- Build Fields ----------
    def update_fields(self, *_):
        # kept for backward compatibility but not used now
        return

    # ---------- Search ----------
    def apply_filter(self):
        # Search removed
        return

    # ---------- CSV helpers ----------
    def flattened_headers(self):
        # Not used when building form from CSV headers
        return []

    # ---------- Import ----------
    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        self.load_csv_to_entries(path)

    def choose_split_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self.load_split_data(path)

        try:
            self.config['split_data_path'] = path
            self.save_config(self.config)
        except Exception:
            pass

    def prompt_for_split_folder(self):
        msg = "The Split Data folder is required for this tool, would you like to search for it now?"
        try:
            res = messagebox.askyesno("Split Data Required", msg)
        except Exception:
            return
        if res:
            self.choose_split_folder()

    def load_config(self):
        cfg_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        try:
            if os.path.isfile(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self, cfg):
        cfg_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        try:
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    # ---------- Icon / Splash helpers ----------
    def ensure_icon_file(self):
        try:
            base = os.path.dirname(__file__)
        except Exception:
            base = os.getcwd()
        path = os.path.join(base, ICON_FILE)
        if os.path.isfile(path):
            return path
        try:
            data = base64.b64decode(ICON_B64)
            with open(path, 'wb') as f:
                f.write(data)
            return path
        except Exception:
            return None

    

    def set_window_icon(self):
        try:
            icon_path = os.path.join(os.path.dirname(__file__), ICON_FILE)
            img = tk.PhotoImage(file=icon_path)
            # keep reference to avoid GC
            self.root.iconphoto(False, img)
            self._icon_img = img
        except Exception:
            pass

    def load_split_data(self, root_path):

        for i in self.tree.get_children():
            self.tree.delete(i)

        root_id = self.tree.insert("", "end", text=os.path.basename(root_path) or root_path, open=True, values=[root_path])
        path_map = {root_path: root_id}

        for dirpath, dirnames, filenames in os.walk(root_path):
            parent = path_map.get(dirpath, root_id)

            for d in sorted(dirnames):
                full = os.path.join(dirpath, d)
                item_id = self.tree.insert(parent, "end", text=d, open=False, values=[full])
                path_map[full] = item_id

            for f in sorted(filenames):
                full = os.path.join(dirpath, f)
                self.tree.insert(parent, "end", text=f, values=[full])

    def on_tree_select(self, event):

        return

    def on_tree_double(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        vals = self.tree.item(item, "values")
        if not vals:
            return
        path = vals[0]
        if os.path.isfile(path) and path.lower().endswith('.csv'):
            self.load_csv_to_entries(path)

    def load_csv_to_entries(self, path):
        try:
            with open(path, newline="") as f:
                rows = list(csv.reader(f))

            if not rows:
                raise ValueError("CSV is empty")


            headers = rows[0]
            values = rows[1] if len(rows) > 1 else []


            self.build_form_from_headers(headers)

            for h, v in zip(headers, values):
                header_key = h
                if isinstance(header_key, str):
                    header_key = header_key.strip().lstrip('\ufeff')
                key = header_key
                if key in self.entries:
                    entry = self.entries[key][1]
                    entry.delete(0, tk.END)
                    entry.insert(0, v)

            self.status.set(f"Imported {os.path.basename(path)}")

        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    # ---------- Export ----------
    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return

        if getattr(self, 'current_headers', None):
            headers = self.current_headers
        else:
            headers = list(self.entries.keys())

        data = [self.entries[h][1].get() if h in self.entries else "" for h in headers]

        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerow(data)

            self.status.set(f"Saved {os.path.basename(path)}")

        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def build_form_from_headers(self, headers):

        for w in self.form_frame.winfo_children():
            w.destroy()
        self.entries.clear()


        clean_headers = []
        for h in headers:
            hh = h if isinstance(h, str) else str(h)
            hh = hh.strip().lstrip('\ufeff')
            clean_headers.append(hh)

        self.current_headers = clean_headers

        section = CollapsibleSection(self.form_frame, "Fields")
        section.pack(fill="x", expand=True)

        for field in clean_headers:
            row = ttk.Frame(section.body)
            row.pack(fill="x", pady=2)

            label = ttk.Label(row, text=field, width=28)
            label.pack(side="left")

            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True, padx=5)

            self.entries[field] = (row, entry)


        if ("CarNameFirstPart" in self.entries and
            "CarNameSecondPart" in self.entries and
            "CarId" in self.entries):

            first_entry = self.entries["CarNameFirstPart"][1]
            second_entry = self.entries["CarNameSecondPart"][1]
            CarId_entry = self.entries["CarId"][1]

            def update_CarId(*_):
                name1 = first_entry.get()
                name2 = second_entry.get()
                car_id = self.get_car_id(name1, name2)
                CarId_entry.delete(0, tk.END)
                if car_id is not None:
                    CarId_entry.insert(0, str(car_id))
                else:
                    CarId_entry.insert(0, "")

            first_entry.bind("<KeyRelease>", update_CarId)
            second_entry.bind("<KeyRelease>", update_CarId)


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVGeneratorApp(root)
    root.mainloop()

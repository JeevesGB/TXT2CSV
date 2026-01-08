import json
import csv
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

JSON_SCHEMA_FILE = "headers.json"
CAR_NAMES_FILE = "carnames.json"  # <-- your downloaded CarNames JSON


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
        self.root.title("TXT → CSV ")
        self.root.geometry("600x700")
        self.root.minsize(500, 500)

        self.schema = self.load_schema()
        self.entries = {}
        self.car_names = self.load_car_names()  # load CarNames JSON

        self.build_ui()

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

    # ---------- Lookup CarID ----------
    def get_car_id(self, name1, name2):
        name1 = name1.strip().lower()
        name2 = name2.strip().lower()

        for car in self.car_names:
            if (car["CarNameFirstPart"].strip().lower() == name1 and
                car["CarNameSecondPart"].strip().lower() == name2):
                return car["CarID"]  # STRING like "a-a7r"

        return None

    # ---------- UI ----------
    def build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Data Type:").pack(anchor="w")

        self.tab_var = tk.StringVar()
        self.tab_dropdown = ttk.Combobox(
            top,
            textvariable=self.tab_var,
            values=list(self.schema.keys()),
            state="readonly"
        )
        self.tab_dropdown.pack(fill="x", pady=5)
        self.tab_dropdown.bind("<<ComboboxSelected>>", self.update_fields)

        ttk.Label(top, text="Search Fields:").pack(anchor="w", pady=(10, 0))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_filter())
        ttk.Entry(top, textvariable=self.search_var).pack(fill="x")

        # Scrollable area
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.form_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        self.form_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Bottom
        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Import CSV", command=self.import_csv).pack(side="left")
        ttk.Button(bottom, text="Generate CSV", command=self.export_csv).pack(side="right")

        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x")

    # ---------- Mouse wheel ----------
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # ---------- Build Fields ----------
    def update_fields(self, *_):
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.entries.clear()

        tab = self.tab_var.get()
        if not tab:
            return

        for section_name, fields in self.schema[tab].items():
            section = CollapsibleSection(self.form_frame, section_name)
            section.pack(fill="x", expand=True)

            for field in fields:
                row = ttk.Frame(section.body)
                row.pack(fill="x", pady=2)

                label = ttk.Label(row, text=field, width=28)
                label.pack(side="left")

                entry = ttk.Entry(row)
                entry.pack(side="left", fill="x", expand=True, padx=5)

                self.entries[field] = (row, entry)

        # ---------- CarID auto-fill ----------
        if ("CarNameFirstPart" in self.entries and
            "CarNameSecondPart" in self.entries and
            "CarID" in self.entries):

            first_entry = self.entries["CarNameFirstPart"][1]
            second_entry = self.entries["CarNameSecondPart"][1]
            carid_entry = self.entries["CarID"][1]
            def update_carid(*_):
                name1 = first_entry.get()
                name2 = second_entry.get()
                car_id = self.get_car_id(name1, name2)
                carid_entry.delete(0, tk.END)
                if car_id is not None:
                    carid_entry.insert(0, str(car_id))
                else:
                    carid_entry.insert(0, "")

            first_entry.bind("<KeyRelease>", update_carid)
            second_entry.bind("<KeyRelease>", update_carid)

        self.apply_filter()

    # ---------- Search ----------
    def apply_filter(self):
        term = self.search_var.get().strip().lower()

        for field, (row, _) in self.entries.items():
            if not term or term in field.lower():
                if not row.winfo_ismapped():
                    row.pack(fill="x", pady=2)
            else:
                if row.winfo_ismapped():
                    row.forget()

    # ---------- CSV helpers ----------
    def flattened_headers(self):
        tab = self.tab_var.get()
        headers = []
        for fields in self.schema[tab].values():
            headers.extend(fields)
        return headers

    # ---------- Import ----------
    def import_csv(self):
        if not self.tab_var.get():
            return

        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return

        try:
            with open(path, newline="") as f:
                rows = list(csv.reader(f))

            headers = rows[0]
            values = rows[1]

            entry_map = {k.lower(): k for k in self.entries}

            for h, v in zip(headers, values):
                key = h.lower()
                if key in entry_map:
                    entry_key = entry_map[key]
                    entry = self.entries[entry_key][1]
                    entry.delete(0, tk.END)
                    entry.insert(0, v)

            self.status.set(f"Imported {os.path.basename(path)}")

        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    # ---------- Export ----------
    def export_csv(self):
        if not self.tab_var.get():
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return

        headers = self.flattened_headers()
        data = [self.entries[h][1].get() if h in self.entries else "" for h in headers]

        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerow(data)

            self.status.set(f"Saved {os.path.basename(path)}")

        except Exception as e:
            messagebox.showerror("Save Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVGeneratorApp(root)
    root.mainloop()

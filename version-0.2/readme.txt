TXT2CSV — Quick Readme

1) Run the GUI (development)
   - Ensure Python 3 is installed and on PATH.
   - From the repository root run:
     python TXT2CSVv0.2.py
   - On first run you'll be prompted to locate your "Split Data" folder. The chosen path is saved in config.json.

2) Edit CSVs with the GUI
   - Click "Choose Folder" to load a Split Data folder (or double-click a CSV in the tree if already loaded).
   - Double-click a .csv in the tree to open it. The form is built from CSV headers and is editable.
   - Edit fields and click "Generate CSV" to save (you can save to a new path).
   - If `CarId` should auto-fill, ensure the opened CSV has headers `CarNameFirstPart` and `CarNameSecondPart` and that `carnames.json` is available.

3) Build a single executable (Windows)
   - Run the provided batch file from the repo root:
     build_exe.bat
   - The script creates/uses a .venv, installs PyInstaller, and bundles the app.
   - On success the EXE is placed at: release\TXT2CSVv0.2.exe
   - Requirements: Python on PATH. If you want console output in the EXE, remove `--noconsole` from the batch file.

4) Icon and images
   - If `icon.png` is missing, the tool will create a default placeholder next to the script/exe.
   - To use your own icon, place `icon.png` in the repo root before running the build; the batch tries to convert it to `icon.ico`.
   - Placeholder screenshots are in the `img/` folder.

5) Important files
   - `headers.json` and `CarNames.json`: used by the GUI (these are bundled into the EXE by the build script).
   - `config.json`: remembers the last selected Split Data folder.
   - `build_exe.bat`: helper to create a single-file exe using PyInstaller.

6) Troubleshooting
   - If the GUI can't find `headers.json` or `CarNames.json`, verify those files exist in the repo root or the same folder as the EXE when running the packaged app.
   - If builds fail, inspect the console output from PyInstaller for missing modules or data files.

If you want, I can also add a short INSTALL.txt or expand this into the main README with these instructions. Let me know which you prefer.

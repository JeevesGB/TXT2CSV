TXT2CSV — Quick Start for EXE Users

1) Running the app
   - Double-click the executable: `release\TXT2CSVv0.2.exe`.
   - On first run the app will ask: "The Split Data folder is required for this tool, would you like to search for it now?" — choose Yes and point to your Split Data folder.
   - The selected folder is remembered in `config.json` saved next to the EXE.

2) Basic workflow
   - Browse the left-hand tree to find CSV files inside the Split Data folder.
   - Double-click any `.csv` file in the tree to open it for editing; the form is built from the CSV headers.
   - Edit fields in the right-hand form and click "Generate CSV" to save changes to a chosen location.
   - If the CSV contains `CarNameFirstPart` and `CarNameSecondPart` headers and `CarNames.json` is present, the `CarId` field will auto-fill when you edit the name parts.

3) Files included with the EXE
   - `headers.json` and `CarNames.json` are bundled into the EXE (no separate files required), but if you run the unpacked script these files are expected in the same folder as the script.
   - `config.json` is created beside the EXE to remember your Split Data folder. Delete it to force the app to prompt again.

4) Troubleshooting
   - If the app cannot find your Split Data folder, click "Choose Folder" and point to it manually.
   - If `CarId` doesn't auto-populate, ensure the CSV headers include `CarNameFirstPart` and `CarNameSecondPart`.
   - If the EXE is blocked by antivirus, allow the file or add an exception for the `release` folder.

5) Want to change the remembered folder?
   - Close the app, delete `config.json` from the same folder as the EXE, then rerun the EXE and choose the desired folder when prompted.

6) Logs / advanced troubleshooting
   - The single-file EXE runs without a console window. If you need logs, run the non-compiled script (`TXT2CSVv0.2.py`) with Python to see console output.

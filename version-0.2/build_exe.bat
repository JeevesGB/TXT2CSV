@echo off
title TXT2CSV EXE Builder
echo ===============================
echo Building TXT2CSV EXE
echo ===============================

rmdir /s /q build
rmdir /s /q dist
del /q TXT2CSV.spec 2>nul

pyinstaller ^
 --onefile ^
 --windowed ^
 --name TXT2CSV ^
 --icon ICO.ico ^
 --add-data "headers.json;." ^
 --add-data "carnames.json;." ^
 TXT2CSVv0.2.py

echo.
echo ===============================
echo Build complete!
echo EXE is in the dist folder
echo ===============================
pause

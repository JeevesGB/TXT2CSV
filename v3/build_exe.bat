@echo off
title TXT2CSV EXE Builder

echo ===============================
echo Building TXT2CSV EXE
echo ===============================

REM --- Clean previous builds ---
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "GT2 CSV Generator V1.0.spec" del /q "GT2 CSV Generator V1.0.spec"

REM --- Run PyInstaller ---
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "GT2 CSV Generator V1.0" ^
    --icon "assets\ICO.ico" ^
    --add-data "data\CarNames.json;data" ^
    --add-data "data\config.json;data" ^
    --add-data "data\headers.json;data" ^
    --add-data "assets\ico.ico;assets" ^
    --add-data "assets/styles/dark.qss;assets/styles" ^
    main.py

REM --- Check if build succeeded ---
IF ERRORLEVEL 1 (
    echo.
    echo ===============================
    echo BUILD FAILED!
    echo ===============================
    pause
    exit /b 1
)

echo.
echo ===============================
echo Build complete!
echo EXE is in the dist folder
echo ===============================
pause

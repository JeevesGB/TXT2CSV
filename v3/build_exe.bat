@echo off
title TXT2CSV EXE Builder

echo ===============================
echo Building TXT2CSV EXE
echo ===============================

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q TXT2CSV.spec 2>nul

pyinstaller ^
 --onefile ^
 --windowed ^
 --name TXT2CSV ^
 --icon assets\ICO.ico ^
 --add-data=data\CarNames.json;data ^
 --add-data=data\config.json;data ^
 --add-data=data\headers.json;data ^
 --add-data=assets\ICO.ico;assets ^
 main.py

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

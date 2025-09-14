@echo off
echo 🎵 Discord Zene Bot indítása...
echo.

REM Ellenőrizzük, hogy Python 3.12 telepítve van-e
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Hiba: Python 3.12 nincs telepítve!
    echo Kérlek telepítsd a Python 3.12-t innen: https://python.org
    echo.
    echo Megjegyzés: Python 3.13+ nem támogatja a voice funkciókat!
    pause
    exit /b 1
)

echo ✅ Python 3.12 telepítve: 
py -3.12 --version

REM Függőségek telepítése Python 3.12-vel
echo.
echo 📦 Függőségek telepítése Python 3.12-vel...
py -3.12 -m pip install -r requirements.txt
py -3.12 -m pip install PyNaCl

REM Bot indítása Python 3.12-vel
echo.
echo 🚀 Teljes zene bot indítása Python 3.12-vel...
py -3.12 run.py

pause

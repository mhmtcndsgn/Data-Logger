@echo off
REM STM32 Veri Kaydedici - kaynak koddan calistirma (Windows)
REM Ilk calistirmada sanal ortam kurar ve kutuphaneleri indirir (1-2 dk).
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" goto calistir

REM --- Gercek bir Python var mi? (Microsoft Store kisayolu sayilmaz) ---
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
    python --version >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo.
    echo  Bilgisayarda Python kurulu degil.
    echo.
    echo  1^) Acilacak sayfadan Python'u indirip kurun.
    echo  2^) Kurulumun ILK ekraninda "Add python.exe to PATH" kutusunu isaretleyin.
    echo  3^) Kurulum bitince bu dosyaya tekrar cift tiklayin.
    echo.
    start "" "https://www.python.org/downloads/windows/"
    pause
    exit /b 1
)

echo Ilk kurulum yapiliyor, 1-2 dakika surebilir...
if exist ".venv" rmdir /s /q ".venv"
%PY% -m venv .venv
if not exist ".venv\Scripts\python.exe" (
    echo Sanal ortam olusturulamadi.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Kutuphaneler indirilemedi. Internet baglantisini kontrol edip tekrar deneyin.
    rmdir /s /q ".venv"
    pause
    exit /b 1
)

:calistir
start "" ".venv\Scripts\pythonw.exe" main.py

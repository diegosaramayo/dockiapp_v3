@echo off
title DockiApp - Instalador de Requerimientos

echo ===================================================
echo        DockiApp - Instalador de Requerimientos
echo ===================================================
echo.

cd /d "%~dp0"

set "FOUND_PYTHON="

REM 1. Buscar en %LOCALAPPDATA%\Programs\Python
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "FOUND_PYTHON=%%D\python.exe"
        goto :python_ready
    )
)

REM 2. Buscar en C:\Python*
for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        set "FOUND_PYTHON=%%D\python.exe"
        goto :python_ready
    )
)

REM 3. Buscar en C:\Program Files\Python*
for /d %%D in ("C:\Program Files\Python*") do (
    if exist "%%D\python.exe" (
        set "FOUND_PYTHON=%%D\python.exe"
        goto :python_ready
    )
)

REM 4. Probar comando py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "FOUND_PYTHON=py"
    goto :python_ready
)

REM 5. Probar comando python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "FOUND_PYTHON=python"
    goto :python_ready
)

:python_not_found
echo [ERROR] No se pudo encontrar Python instalado en tu sistema.
echo.
echo Causa principal:
echo 1. Python no esta instalado en Windows.
echo 2. El alias de Microsoft Store esta bloqueando el comando 'python'.
echo.
echo SOLUCION EN 2 PASOS:
echo.
echo PASO 1: Si ya tienes Python instalado en tu equipo:
echo   a) Ve al menu Inicio ^> Configuracion ^> Aplicaciones.
echo   b) Haz clic en "Alias de ejecucion de aplicaciones".
echo   c) DESACTIVA las casillas "Python" y "Python3" (Instalador de la aplicacion).
echo.
echo PASO 2: Si NO tienes Python instalado:
echo   a) Descargalo gratis desde: https://www.python.org/downloads/
echo   b) Durante la instalacion, MARCA la casilla "Add Python.exe to PATH".
echo.
pause
exit /b 1

:python_ready
echo [OK] Python detectado: "%FOUND_PYTHON%"
echo.

echo [1/3] Creando entorno virtual local .venv...
if not exist ".venv" (
    "%FOUND_PYTHON%" -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual .venv.
        pause
        exit /b 1
    )
) else (
    echo Entorno virtual .venv ya esta listo.
)

echo.
echo [2/3] Actualizando pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo.
echo [3/3] Instalando requerimientos (Flask, openpyxl, docx, pdf)...
.venv\Scripts\pip.exe install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Fallo la instalacion de requerimientos.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo [OK] Instalacion completada con exito.
echo Ya puedes ejecutar run.bat para iniciar la app.
echo ===================================================
echo.
pause

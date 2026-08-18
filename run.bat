@echo off
title DockiApp - Servidor Local

echo ===================================================
echo             DockiApp - Ejecutando App
echo ===================================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [AVISO] El entorno virtual .venv no existe o no esta completo.
    echo Ejecutando instalador.bat...
    echo.
    call instalador.bat
    echo.
)

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro .venv\Scripts\python.exe.
    echo Ejecuta primero instalador.bat.
    pause
    exit /b 1
)

echo [1/2] Abriendo navegador en http://127.0.0.1:5000...
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:5000"

echo [2/2] Iniciando servidor Flask...
echo.
echo Presiona Ctrl+C para detener el servidor.
echo ---------------------------------------------------
echo.

.venv\Scripts\python.exe app.py

if %errorlevel% neq 0 (
    echo.
    echo ===================================================
    echo [ERROR] El servidor Flask se detuvo.
    echo Revisa el mensaje de error anterior.
    echo ===================================================
    echo.
    pause
)

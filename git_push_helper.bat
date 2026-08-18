@echo off
echo ==================================================
echo         Subiendo cambios de DockiApp a GitHub
echo ==================================================

git add .
git commit -m "Actualizacion DockiApp lista para Render"
git push origin main

echo ==================================================
echo         ¡Cambios subidos a GitHub con éxito!
echo ==================================================
pause

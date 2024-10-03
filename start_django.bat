@echo off
REM Cambiar a la unidad D
D:

REM Activar el entorno virtual
call D:\ProyectosPython\PSCG-Management-Monitoring-and-Control-Platform\.venv\Scripts\activate.bat

REM Cambiar al directorio del proyecto
cd ProyectosPython\PSCG-Management-Monitoring-and-Control-Platform

REM Iniciar la aplicación con Waitress y redirigir salida a log
python run_waitress.py >> D:\ProyectosPython\PSCG-Management-Monitoring-and-Control-Platform\log.txt 2>&1

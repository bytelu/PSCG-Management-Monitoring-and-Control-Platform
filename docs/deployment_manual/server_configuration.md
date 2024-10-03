# Configuración del Servidor para Desplegar la Aplicación Django

Este documento detalla cómo configurar el servidor para ejecutar la aplicación Django utilizando `Waitress` y `nssm` (Non-Sucking Service Manager).

## Requisitos Previos

Antes de comenzar, asegúrate de tener los siguientes requisitos:

- **Sistema Operativo**: Windows 10 o superior.
- **Python**: Recomendado Python 3.8 o superior instalado y agregado a la variable de entorno PATH.
- **nssm**: Non-Sucking Service Manager descargado e instalado. [Descargar nssm](https://nssm.cc/download).
- **Código de la Aplicación**: Asegúrate de que el código esté disponible en la máquina donde se desplegará.

## Preparación de entorno
Para la preparación del entorno puedes seguir las instrucciones especificadas en el archivo de [preparación de entorno](./environment_setup.md). Asegurate de preparar todo antes de proseguir.

## Archivo para ejecutar el servidor
La ejecución del servidor se lleva a cabo mediante el archivo de configuración `start_django.bat` encontrado en la raíz del proyecto, este archivo contiene la siguiente configuración al momento de la descarga del proyecto:
```bat
@echo off
D:

call D:\ProyectosPython\PSCG-Management-Monitoring-and-Control-Platform\.venv\Scripts\activate.bat

cd ProyectosPython\PSCG-Management-Monitoring-and-Control-Platform

python run_waitress.py >> D:\ProyectosPython\PSCG-Management-Monitoring-and-Control-Platform\log.txt 2>&1
```
Asegurate de configurar correctamente dicho archivo para que el proyecto se ejecute correctamente:
1. Usa el comando `call` para hacer una llamada a la ruta del entorno virtual dentro de la carpeta raíz del proyecto para asi activar el entorno virtual.
2. Navega hacia el directorio del proyecto.
3. Sirve la aplicación por medio de `run_waitress.py`, configurado previamente para servir el proyecto. A continuación se muestra el contenido de dicho archivo:
```python
from waitress import serve
from ProyectoSCG.wsgi import application

serve(application, host='0.0.0.0', port=8000)
```

## Configuración de `nssm`
1. **Abrir la linea de comandos como administrador.**
2. **Instalar el servicio:**  
   - Navega al directorio donde se encuentra el servicio, en caso de que aun no lo tengas descargado, descargalo a través de https://nssm.cc/download y descomprime su contenido, para asi posteriormente acceder a el.
   ```bash
   cd C:\nssm\win64
   ```
   
   - Ejecuta el siguiente comando para instalar el servicio:
   ```bash
   nssm install IniciarDjango
   ```
3. **Configuraciones del servicio:**  
   - En la ventana que se abrirá, realiza las siguientes configuraciones:
     - Path: `C:\Windows\System32\cmd.exe`
     - Startup directory: `D:\ProyectosPython` o ruta correspondiente.
     - Arguments: `/c "start_django.bat"`
4. **Iniciar el servicio:**
   ```bash
   nssm start IniciarDjango
   ```

## Verificar el servicio
- Se puede verificar el estado del servicio en el "Administrador de tareas" o utilizando el siguiente comando en la línea de comandos:
   ```bash
  nssm status IniciarDjango
   ```
## Configuración Automática del Servicio
1. **Abrir el Administrador de Servicios:**
   - Presiona Windows + R, escribe services.msc y presiona Enter.
   
2. **Buscar tu Servicio:**
   - Busca IniciarDjango en la lista de servicios.
   
3. **Configurar el Tipo de Inicio:**
   - Haz clic derecho sobre tu servicio y selecciona Propiedades.
   - Asegúrate de que el Tipo de inicio esté configurado como Automático.
4. **Guardar Cambios:**
   - Si realizaste cambios, haz clic en Aceptar.

## Modificación y eliminación del Servicio 
- **Modificar:** Si se necesita cambiar alguna configuración al servicio:
```bash
nssm edit IniciarDjango
```
- **Eliminar:** Si ya no se necesita el servicio:
```bash
nssm remove IniciarDjango
```
# Configuración del Entorno para la Aplicación Django

Este documento describe cómo configurar el entorno de desarrollo para la aplicación.

## Requisitos Previos

- **Sistema Operativo**: Windows 10 o superior.
- **Python**: Recomendado: Python 3.8 o superior.
- **MySQL**: Base de datos MySQL instalada y funcionando.
- **Editor de Código**: Visual Studio Code, PyCharm, o cualquier editor de tu elección.

## Instalación de Python

1. Descarga el instalador de Python desde [python.org](https://www.python.org/downloads/).
2. Ejecuta el instalador y asegúrate de seleccionar la opción **Add Python to PATH**.
3. Completa la instalación.

## Creación del Entorno Virtual

1. Abre la línea de comandos (CMD).
2. Navega al directorio de tu proyecto, por ejemplo:
   ```bash
   cd D:\ProyectosPython\PSCG-Management-Monitoring-and-Control-Platform

3. Crea un entorno virtual
   ```bash
   python -m venv .venv

4. Activar el entorno virtual:
    - En Windows:
   ```bash
   .venv\Scripts\activate

## Instalación de dependencias

1. Asegurate de estar en el entorno virtual, de no ser el caso, activalo.
2. Instala las dependencias del archivo `requirements.py`:
   ```bash
   pip install -r requirements.txt

## Configuración de la base de datos

1. Crea una base de datos en MySQL:
   - Accede a MySQL o al gestor de bases de datos de tu preferencia y crea la base de datos:
      ```sql
      CREATE DATABASE nombre_de_la_base_de_datos;

2. Configuración en `settings.py`:  
   Abre el archivo `settings.py` de la carpeta del proyecto y configura la base de datos:
   ```python
   DATABASES = {
      'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'nombre_de_la_base_de_datos',
         'USER': 'tu_usuario',
         'PASSWORD': 'tu_contraseña',
         'HOST': 'localhost',
         'PORT': '3306',
      }
   }
   ```
3. Migrar las tablas a la base de datos:  
   En la consola ejecuta el siguiente comando con tu entorno virtual activado:
   ```bash
   python manage.py migrate

4. Cargar datos iniciales:  
   Asegúrate de tener el archivo `initial_data.json` en la carpeta del proyecto y ejecuta:
   ```bash
   python manage.py loaddata initial_data.json

## Ejecución de la aplicación
Para ejecutar la aplicación localmente en modo de desarrollo:
```bash
python manage.py runserver
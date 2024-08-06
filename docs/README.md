<p style="text-align: center;">
  <img alt="Static Badge" src="https://img.shields.io/badge/Status-En%20desarrollo-blue?style=for-the-badge">
</p>

<hr>

<h1 style="text-align: center;">PSCG</h1>

<hr>

**PSCG** es una aplicación integral desarrollada con Django, diseñada para optimizar la gestión y supervisión en el
ámbito de actividades de fiscalización. Esta plataforma ofrece herramientas avanzadas para:

- **Gestión de Datos**: Administra y organiza datos relacionados con auditorías, controles internos e intervenciones.
- **Supervisión Eficiente**: Facilita la supervisión de actividades mediante una interfaz centralizada y herramientas
  especializadas.
- **Generación de Archivos**: Permite la generación de archivos necesarios para llevar a cabo las actividades de
  supervisión de fiscalización de manera efectiva.

Con **PSCG**, se podrá mejorar la eficiencia de la realización de los procesos de supervisión de fiscalización,
asegurando un control riguroso y detallado de las actividades.

## Tabla de Contenidos

- [Introducción](#introducción)
- [Instalación](#instalación)
- [Uso](#uso)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Introducción

**PSCG** (Plataforma de Supervisión y Control de Gestión) es una herramienta integral desarrollada con Django, diseñada
para optimizar la gestión y supervisión en el ámbito de actividades de fiscalización. Esta plataforma ofrece un conjunto
completo de funcionalidades para administrar, organizar y supervisar auditorías, intervenciones y controles internos de
manera eficiente y centralizada.

**PSCG** permite a los usuarios:

- **Gestionar Datos de Auditorías**: Administra y organiza todos los datos relacionados con auditorías, incluyendo la
  capacidad de agregar, editar y eliminar registros de manera intuitiva.
- **Supervisión de Actividades**: Facilita la supervisión de actividades mediante una interfaz centralizada y
  herramientas especializadas para las distintas actividades de fiscalización, asegurando que todos los procesos cumplan
  con los estándares requeridos.
- **Generación de Archivos para Supervisión**: Genera automáticamente los archivos necesarios para llevar a cabo
  actividades de supervisión de fiscalización de manera efectiva, ahorrando tiempo y minimizando errores.

Con **PSCG**, se puede mejorar la eficiencia y efectividad de los procesos de fiscalización, asegurando un control
riguroso y detallado de todas las actividades.

Esta documentación te guiará a través de los siguientes aspectos del proyecto:

- Instalación: Cómo instalar y configurar **PSCG** en tu entorno local.
- Uso: Una guía detallada sobre cómo utilizar las diversas funcionalidades de la plataforma.
- Contribución: Instrucciones sobre cómo contribuir al desarrollo de **PSCG**, incluyendo cómo reportar problemas y
  enviar mejoras.

Esperamos que esta herramienta sea de gran ayuda e invitamos a contribuir para su mantenimiento y mejora.

## Instalación

### Requisitos

- Python: Versión 3.12 o superior.
- Django: Versión 5.0.4.
- Base de datos: PostgreSQL, MySQL o similar.

### Pasos para la Instalación

1. Clona el repositorio:

    ```shell
    git clone https://github.com/bytelu/PSCG.git
    cd tu_repositorio
    ```

2. Crear y activar un entorno virtual:  
   Es recomendable usar un entorno virtual para gestionar las dependencias del proyecto. Para crear y activar un entorno
   virtual, ejecuta los siguientes comandos:

    ```shell
    python3 -m venv .venv
    source .venv/bin/activate  # En Windows usa `.venv\Scripts\activate`
    ```

3. Instalar dependencias:

    ```shell
    pip install -r requirements.txt
    ```

4. Configurar la base de datos:  
   En el archivo `settings.py`, configura tu base de datos:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',  # O el correspondiente a tu base de datos
            'NAME': 'nombre_de_tu_base_de_datos',
            'USER': 'tu_usuario',
            'PASSWORD': 'tu_contraseña',
            'HOST': 'localhost',
            'PORT': '3306',  # O el puerto correspondiente a tu base de datos
        }
    }
    ```

5. Aplicar las migraciones:  
   Aplica las migraciones para crear las tablas necesarias en la base de datos:

    ```shell
    python manage.py migrate
    ```

6. Crear un superusuario:  
   Sigue las instrucciones indicadas después de ejecutar el siguiente comando:

    ```shell
    python manage.py createsuperuser
    ```

7. Cargar datos iniciales:  
   Carga los datos iniciales para el correcto funcionamiento:

    ```shell
    python manage.py loaddata initial_data.json
    ```

8. Ejecutar el servidor de desarrollo:

    ```shell
    python manage.py runserver
    ```

   Accede a la aplicación en tu navegador en: [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Uso

Una vez que el proyecto esté instalado y corriendo, puedes usar las siguientes funcionalidades:

Con las claves del superusuario se puede acceder a la página principal del sistema en la página de login, para ello
ingresa a [http://127.0.0.1:8000](http://127.0.0.1:8000), esto te redirigirá automáticamente a la pantalla de login. Una
vez dentro, simplemente prueba a ingresar tus claves.

![Interfaz de login](images/Login%20Screen.png)

Con esto se ingresará al sistema y serás dirigido a la página de home:

![Interfaz de home](images/Home%20Screen.png)

Una vez dentro, puedes acceder a las funcionalidades implementadas con el botón de sidebar ubicado en la parte superior
izquierda de la página, o arrastrando con el mouse desde la parte izquierda.

![Side Bar Panel](images/Side%20Bar%20Panel.png)

Dentro de estas opciones se cuenta con:

- Home
- Auditorías
- Intervenciones
- Controles Internos
- Personal

Cada una de estas opciones, a excepción de home, cuenta con un menú desplegable, con el cual se puede acceder a
distintas interfaces.

En primera instancia se encuentran las actividades principales que son auditorías, intervenciones y controles internos.
Estas tienen una sección a la cual se accede presionando el botón correspondiente y seleccionando la opción **Mostrar "
Nombre correspondiente"**, donde se puede visualizar cada una de las que han sido registradas en el sistema. Se cuenta
con un filtro en cada una de ellas para filtrar por OIC y Año para una búsqueda más rápida y sencilla.

![Filtro por año y OIC](images/Year%20and%20OIC%20filter.png)

A un costado de cada una de estas páginas, en la parte superior derecha, se encuentra un botón con la simbología
de <img src="images/plus-solid.svg" alt="plus" width="10" height="10">, al cual al darle clic redirecciona a una página
de subida de archivo, en donde se podrá subir un archivo de acuerdo a los formatos utilizados en la dirección de la
contraloría, para subir la correspondiente actividad de fiscalización, ya sea auditoría, control interno o intervención.
Una vez subido, se debería visualizar en su correspondiente sección, y al darle clic, se deberían mostrar sus detalles
por medio de un formulario el cual permite modificarlos de acuerdo a cualquier necesidad, para poder guardar los datos
si es que se modificaron con el botón de la parte inferior, o en su otro caso, borrar la actividad con el símbolo
de <img src="images/left-arrow.svg" alt="left arrow" width="10" height="10">, se muestra un ejemplo del formulario:

![Formulario Auditoría](images/Formulario%20Auditoria.jpeg)

Al tener actividades registradas, se puede acceder a un menú a un lado de la actividad con el
símbolo <img src="images/plus-solid.svg" alt="plus" width="10" height="10"> en el ítem dentro del listado. Este
despliega un modal desde el cual el usuario accede a las funcionalidades de supervisión de la actividad de
fiscalización, ya sea que se opte por la realización de una minuta de supervisión o una cédula de supervisión, estos
conteniendo su estructura dependiendo de las actividades que realiza un OIC durante el mes para las minutas, o una
cédula para cada actividad realizada, siendo ambos tipos de archivos divididos para su realización por mes durante la
duración del periodo del trimestre, en donde cada uno de los archivos cuenta con un formulario específico por mes el
cual podrá generar un archivo para su posterior uso. Siendo estos archivos generados, plantillas usadas en la dirección
de coordinación.

###### Modal de acceso a actividades de supervisión:

![Modal de acceso a actividades de supervisión](images/Modal%20Activity.png)

###### Panel de selección de mes de minuta

![Panel de selección de mes de minuta](images/Panel%20Minuta.png)

###### Formulario de relleno de datos correspondientes a cédula

![Formulario de relleno de datos correspondientes a cédula](images/Formulario%20Cedula.png)

Para la realización de las actividades de supervisión en la sección de las minutas se necesita que los datos de los
interesados de las minutas se encuentren presentes dentro de la base de datos. Por ello se realizó un sistema de gestión
de usuarios con asignación de roles para las firmas de las minutas, los cuales se deben agregar en la sección de
personal. Aquí se encuentra el listado de los mismos, donde se cuenta con un filtro por nombre para una búsqueda más
rápida, donde al darle clic se muestra un formulario con todos los datos del personal, además de roles de usuario, y los
cuales se puede eliminar o modificar.

###### Panel de OIC's

![Panel de oics](images/Panel%20OICs.png)

###### Panel de personal de OIC

![Personal OIC](images/Panel%20de%20personal%20de%20oic.png)

###### Formulario de creación de titular

![Formulario titular oic](images/Formulario%20de%20titular%20oic.png)

###### Formulario de creación de personal de OIC

![Formulario personal OIC](images/Formulario%20personal%20oic.png)

###### Panel de edición de personal con asignación de cargos

![Panel de edición de personal de OIC](images/Panel%20de%20edicion%20de%20personal%20asignacion%20de%20cargos.png)

Por último, en la esquina superior derecha de la página, se encuentran dos botones los cuales permiten cerrar la sesión,
o acceder a la información de perfil del usuario, respectivamente.

![Interfaz de Profile y Logout](images/Profile%20and%20logout.png)

![Panel de perfil](images/Panel%20profile.png)

## Licencia

**PSCG** es un software con todos los derechos reservados. Para más información, consulta el archivo LICENSE.md incluido
en este repositorio.

## Contacto

Si tienes alguna pregunta, sugerencia o necesitas soporte, por favor contacta a nuestro equipo a través de:

- Correo electrónico: [luan78hihe@gmail.com](mailto:luan78hihe@gmail.com)
- Teléfono: +52 5620830450

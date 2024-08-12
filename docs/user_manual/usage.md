# Uso

## Indice
- [Acceso](#acceso)
- [Pagina de inicio](#pagina-de-inicio)
- [Vista de actividades](#vista-de-actividades)
- [Creación de archivos de supervisión](#creación-de-archivos-de-supervisión)
  - [Minuta](#minuta)
  - [Cedula](#cédula)
- [Personal](#personal)
- [Sesión](#sesión)

## Acceso

Con las claves del superusuario se puede acceder a la página principal del sistema en la página de login, para ello
ingresa a [http://127.0.0.1:8000](http://127.0.0.1:8000), para un uso corriendo el programa en el sistema local, o a la
dirección IP del PC en el que se encuentre el servidor, seguido del puerto designado, por default el puerto sera el
8000, esto te redirigirá automáticamente a la pantalla de login. Una vez dentro, simplemente prueba a ingresar tus
claves.

![Interfaz de login](../images/Login%20Screen.png)

## Pagina de inicio

Con esto se ingresará al sistema y serás dirigido a la página de home, donde obtendrás la bienvenida al sistema y donde
puedes consultar el manual de usuario con el botón de "Mas información".

![Interfaz de home](../images/Home%20Screen.png)

Una vez dentro, puedes acceder a las funcionalidades implementadas con el botón de sidebar ubicado en la parte superior
izquierda de la página, o arrastrando con el mouse desde la parte izquierda. Esto desplegara las funciones principales a
las que puede acceder el usuario.

![Side Bar Panel](../images/Side%20Bar%20Panel.png)

Dentro de estas opciones se cuenta con:

- Home
- Auditorías
- Intervenciones
- Controles Internos
- Personal

Cada una de estas opciones, a excepción de home, cuenta con un menú desplegable, con el cual se puede acceder a
distintas interfaces.

## Vista de actividades

En primera instancia se encuentran las actividades principales que son auditorías, intervenciones y controles internos.
Estas tienen una sección a la cual se accede presionando el botón correspondiente y seleccionando la opción **Mostrar
** ~auditorias~, ~intervenciones~, ~controles internos~ o ~personal~,
donde se puede visualizar, para las tres primeras mencionadas, un listado de las actividades correspondientes, ordenado
por año de manera decreciente, el cual puede ser filtrado por medio de controles de filtro por año y órgano interno de
control. Ademas, en la parte inferior se muestra una paginación, que muestra los 10 primeros resultados encontrados, y
donde se puede navegar entre los distintos resultados de la búsqueda.

![Filtro por año y OIC](../images/Year%20and%20OIC%20filter.png)

A un costado de cada una de estas páginas, a excepción de la pagina de personal, en la parte superior derecha, se
encuentra un botón con la simbología de <img src="../images/plus-solid.svg" alt="plus" width="10" height="10">, al cual
al darle clic redirecciona a una página de subida de archivo, en donde se podrá subir un archivo de acuerdo a los
formatos utilizados en la dirección de la contraloría, para subir la correspondiente actividad de fiscalización, ya sea
auditoría, control interno o intervención. Una vez subido, se debería visualizar en su correspondiente sección, y al
darle clic, se deberían mostrar sus detalles por medio de un formulario el cual permite modificarlos de acuerdo a
cualquier necesidad, para poder guardar los datos si es que se modificaron con el botón de la parte inferior, o en su
otro caso, borrar la actividad con el símbolo
de <img src="../images/left-arrow.svg" alt="left arrow" width="10" height="10">. Se tiene que tomar en cuenta que al
borrar una actividad, ya sea auditoria, intervención o control interno, se borraran todos los registros asociados a
ella, y absolutamente todos los datos donde haya estado involucrada, esto para no generar discrepancias internas dentro
de la base de datos y que no hayan problemas de la consistencia de la misma.

![Formulario Auditoría](../images/Formulario%20Auditoria.jpeg)

## Creación de archivos de supervisión

###### Modal de acceso a actividades de supervisión:

Al tener actividades registradas, se puede acceder a un menú a un lado de cada actividad con el
símbolo <img src="../images/plus-solid.svg" alt="plus" width="10" height="10"> en el ítem dentro del listado. Este
despliega un modal desde el cual el usuario accede a las funcionalidades de supervisión de la actividad de
fiscalización, ya sea que se opte por la realización de una minuta de supervisión o una cédula de supervisión, estos
conteniendo su estructura dependiendo de las actividades que realiza un OIC durante el mes para las minutas, o una
cédula para cada actividad realizada, siendo ambos tipos de archivos divididos para su realización por mes durante la
duración del periodo del trimestre, en donde cada uno de los archivos cuenta con un formulario específico por mes el
cual podrá generar un archivo para su posterior uso. Siendo estos archivos generados, plantillas usadas en la dirección
de coordinación.

![Modal de acceso a actividades de supervisión](../images/Modal%20Activity.png)

### Minuta

###### Panel de selección de mes de minuta

Al estar dentro del panel de creación de minuta, se muestra la actividad de fiscalización actual, la cual podrá generar
una minuta dependiendo del mes que se requiera.

![Panel de selección de mes de minuta](../images/Panel%20Minuta.png)

###### Formulario de relleno de datos correspondientes a minuta

Al entrar dentro del mes deseado, se mostrara un formulario, el cual contendrá los datos de las actividades de
fiscalizacion llevadas ese mes, ademas del personal que va a intervenir dentro de la minuta, el cual sera personal
guardado dentro de la base de datos. Para que posteriormente pueda guardar los datos y se genere el archivo de
supervisión, el cual se almacenara en las descargas del usuario.

> En caso de que falte algún personal requerido para la realización de la minuta,
> sera redirigido a la creación del personal, la información de la creación de personal se puede consultar
> en [personal](#personal).

![Formulario de relleno de datos correspondiente a minuta](../images/Formulario%20Minuta.png)

En caso de que la minuta sea perteneciente al tercer mes, se mostrara un formulario mas detallado para conceptos de
supervisión que se podrán llenar para tenerlos disponibles y tener el archivo completo dentro de la supervisión.

![Formulario de mes tres de minuta](../images/Formulario%20detallado%20minuta.png)

Al tener cualquier archivo ya generado, este quedara disponible para su futuro acceso, disponible con un botón de
descarga en la parte superior, de la siguiente manera:
![Botón de descarga](../images/Boton%20de%20descarga.png)

### Cédula

#### Encabezado de datos

Al ingresar a la sección de actividad de supervisión de cédula, este redirigirá a un formulario en este caso que
corresponderá únicamente a uno por actividad y no a un formulario por toda la fiscalización correspondiente como en la
realización de las minutas, en donde se recopilaran en primer instancia, los datos principales de la actividad, para
posteriormente guardar el registro que se desee y se genere el archivo que quedara guardado tanto para el usuario como
dentro de la base de datos para su posterior ingreso como en el archivo de minuta.

![Encabezado de cédula](../images/Formulario%20encabezado%20cedula.png)

#### Formulario de cédula por mes

Pero ademas de lo anterior descrito, se cuenta con el selector de mes, el cual permite el ingreso del usuario a la
selección del mes correspondiente donde se realiza la actividad de supervisión, teniendo conceptos distintos por
supervisar con cada mes, por ello, se pueden llenar los datos, lo cual generara el archivo completo para la realización
de la cédula, en donde se realizara una inserción de datos dentro de un archivo de tipo Excel, con una plantilla ya
predefinida, que contendrá todos los conceptos requeridos, ademas de ello, al estar dentro del mismo apartado, los datos
se iran guardando y el archivo ira creciendo, por ello todos los datos guardados se generaran como en un abanico de
datos dentro de la base de datos con los datos almacenados de cada mes.

![Formulario de relleno de datos correspondientes a cédula](../images/Formulario%20Cedula.png)

## Personal

###### Panel de acceso a personal

Se cuenta con dos apartados, entre los que se puede seleccionar a que tipo de personal se
accederá, si al panel del directorio de el personal de la dirección o al panel del directorio del personal de cada OIC.

![Panel de acceso a personal](../images/Panel%20personal%20general.png)

###### Panel de OIC's

Al acceder al panel del personal de OIC's, se podrá visualizar una lista de cards con los nombres de cada uno de los
OICs que se encuentran dentro de la base de datos, cada uno de estos OICs, contara con un directorio personal, el cual
podrá almacenar cada uno de los datos de su respectivo personal y al cual se podrá acceder dando clic al OIC
correspondiente.

![Panel de OICs](../images/Panel%20OICs.png)

###### Panel de personal de OIC

Una vez que se le de clic a la tarjeta de algún OIC, sera redirigido al panel del directorio con el personal de dicho
OIC, donde se podrá acceder a la información especifica de cada una de las personas que se encuentren registradas, pero
ademas se podrá agregar personal de acuerdo al personal faltante por registrar, o limpiar el personal en caso de que
todo el personal vaya a ser sustituido. Se tiene que tener en cuenta que si se elimina algún personal, este no sera
eliminado permanentemente, simplemente quedara en estado de inactivo y no se volverá a mostrar, únicamente quedara
dentro del sistema para usos en funciones que haya realizado previamente.

![Personal OIC](../images/Panel%20de%20personal%20de%20oic.png)

Al ingresar a la creación de algún usuario, ya sea titular o personal, se mostrara un formulario simple, con el cual se
podrán registrar los datos de su apellido, su nombre y su honorífico, ademas en la creación del titular, una previa de
el nombre de su cargo para que pueda ser modificado según necesidades especificas que se puedan presentar.

###### Formulario de creación de titular

![Formulario titular oic](../images/Formulario%20de%20titular%20oic.png)

###### Formulario de creación de personal de OIC

![Formulario personal OIC](../images/Formulario%20personal%20oic.png)

Al tener registrado personal, se podrá acceder a los detalles de dicho personal del OIC, donde se podrán asignar los
cargos dependiendo del tipo de persona, para el titular del OIC, se podrá acceder a los cargos de:

- Autoridad investigadora
- Autoridad substanciadora
- Autoridad resolutora

Ademas de que no se podrá remover su cargo principal de titular de OIC, por ello se divide en apartados distintos,
ademas de que dentro del formulario, se podrá modificar el nombre de su cargo.  
Para el personal del OIC, se podrán asignar, ademas de los cargos anteriormente dichos, el cargo de Personal Estructura
de fiscalización, el cual sera el personal responsable dentro de las minutas de supervision de las distintas actividades
de supervision, rol el cual debe de ser asignado para la realización de las mismas, ademas de la asignación del nombre
de su cargo.  
Para el personal de la dirección, el nombre del cargo de director no podrá ser modificado, y en cuanto al personal,
solamente sera un apartado para el personal de JUD, por lo cual no se asignaran mas cargos y el formulario sera mas
simple, ademas de tener la posibilidad de modificar el nombre del cargo en este caso.

###### Panel de edición de personal con asignación de cargos

![Panel de edición de personal de OIC](../images/Panel%20de%20edicion%20de%20personal%20asignacion%20de%20cargos.png)

## Sesión

Por último, en la esquina superior derecha de la página, se encuentran dos botones los cuales permiten cerrar la sesión,
o acceder a la información de perfil del usuario, respectivamente.

![Interfaz de Profile y Logout](../images/Profile%20and%20logout.png)

Al acceder a la información del usuario, este podrá modificar tanto sus claves de inicio de sesión, las cuales son su
nombre de usuario y su contraseña, como su información personal, que corresponden a su nombre y apellidos. Para el
cambio de la información, se tendrá que verificar la contraseña actual, escribiendo esta en el campo correspondiente, y
para el cambio de contraseña, se tendrá que verificar que la contraseña cumpla con los requerimientos descritos y se
tendrá que volver a confirmar, o volver a escribir la contraseña, esto para evitar errores que puedan suceder al
escribir la contraseña, y para que se cuente con una contraseña segura.

![Panel de perfil](../images/Panel%20profile.png)

Con esto se cumple la descripción de la mayoría de funcionalidades. 
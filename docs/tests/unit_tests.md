## Unit Tests en PSCG

### Pruebas de Vistas

#### LoginViewTest
Este conjunto de tests verifica que la vista `login_view` maneje correctamente la autenticación de usuarios.

- **test_login_success**: Verifica que un usuario con credenciales válidas sea redirigido a la página de inicio.
- **test_login_failure**: Verifica que un usuario con credenciales incorrectas reciba un mensaje de error.

#### HomeViewTest
Este conjunto de tests asegura que la vista `home_view` esté protegida y solo accesible para usuarios autenticados.

- **test_home_authenticated**: Verifica que un usuario autenticado pueda acceder a la vista de inicio.
- **test_home_unauthenticated**: Verifica que un usuario no autenticado sea redirigido a la página de inicio de sesión.

#### ConvertToDateTest
Este conjunto de tests verifica la función `convert_to_date`.

- **test_convert_valid_date**: Verifica que una cadena válida sea correctamente convertida en una fecha.
- **test_convert_invalid_date**: Asegura que una cadena vacía o nula no genere errores y devuelva `None`.

#### GetFilteredObjectsTest
Este conjunto de tests verifica que la función `get_filtered_objects` maneje correctamente el filtrado, la paginación, y el contexto de las vistas `auditorias_view`, `control_interno_view`, e `intervenciones_view`.

- **test_auditoria_filter**: Verifica que los objetos de auditoría sean correctamente filtrados según el OIC y el año.
- **test_control_interno_filter**: Verifica el filtrado para la vista de control interno.
- **test_intervencion_filter**: Verifica el filtrado para la vista de intervenciones.
- **test_no_filter**: Verifica que todos los objetos sean devueltos cuando no se aplica ningún filtro.

#### AuditoriasViewTest, ControlInternoViewTest, IntervencionesViewTest
Estos conjuntos de tests aseguran que cada vista específica (`auditorias_view`, `control_interno_view`, `intervenciones_view`) llame correctamente a la función `get_filtered_objects` y utilice la plantilla adecuada.

- **test_auditorias_view**: Verifica que la vista `auditorias_view` renderice la plantilla `auditorias.html`.
- **test_control_interno_view**: Verifica que la vista `control_interno_view` renderice la plantilla `control_interno.html`.
- **test_intervenciones_view**: Verifica que la vista `intervenciones_view` renderice la plantilla `intervenciones.html`.
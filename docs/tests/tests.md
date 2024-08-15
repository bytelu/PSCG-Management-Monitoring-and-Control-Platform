# Tests

![Estado de pruebas](https://img.shields.io/badge/Pruebas-En%20proceso-blue?style=for-the-badge)

Este documento describe las pruebas implementadas en el proyecto PSCG. Las pruebas están diseñadas para
garantizar que las funcionalidades críticas del sistema se comporten como se espera y que los cambios en el código no
introduzcan errores.

## 1. Descripción General

Las pruebas en PSCG cubren tanto las pruebas unitarias como las pruebas de integración. Se utiliza el
framework de Django TestCase para implementar y ejecutar estas pruebas.

## 2. Pruebas unitarias

## 2.1 LoginViewTest

Este conjunto de tests verifica que la vista `login_view` maneje correctamente la autenticación de usuarios.

- **setUp**: Establece un usuario inicial para la prueba.
  ```python
  def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(username='testuser', password='12345')

- **test_login_success**: Verifica que un usuario con credenciales válidas sea redirigido a la página de inicio.
  ```python
  def test_login_success(self):
    response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
    self.assertRedirects(response, reverse('home'))

- **test_login_failure**: Verifica que un usuario con credenciales incorrectas reciba un mensaje de error.
  ```python
  def test_login_failure(self):
    response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
    self.assertContains(response, 'Usuario o contraseña invalidos')  

## 2.2 HomeViewTest

Este conjunto de tests asegura que la vista `home_view` esté protegida y solo accesible para usuarios autenticados.

- **setUp**: Establece un usuario inicial para la prueba.
  ```python
  def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(username='testuser', password='12345')

- **test_home_authenticated**: Verifica que un usuario autenticado pueda acceder a la vista de inicio.
  ```python
  def test_home_authenticated(self):
    self.client.login(username='testuser', password='12345')
    response = self.client.get(reverse('home'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'home.html')

- **test_home_unauthenticated**: Verifica que un usuario no autenticado sea redirigido a la página de inicio de sesión.
  ```python
  def test_home_unauthenticated(self):
    response = self.client.get(reverse('home'))
    self.assertRedirects(response, reverse('login') + '?next=/OICSec/home/')

## 2.3 ConvertToDateTest

Este conjunto de tests verifica la función `convert_to_date`.

- **test_convert_valid_date**: Verifica que una cadena válida sea correctamente convertida en una fecha.
  ```python
  def test_convert_valid_date(self):
    date_str = '14/08/2024'
    date_obj = convert_to_date(date_str)
    self.assertEqual(date_obj, datetime.date(2024, 8, 14))

- **test_convert_invalid_date**: Asegura que una cadena vacía o nula no genere errores y devuelva `None`.
  ```python
  def test_convert_invalid_date(self):
    date_str = ''
    date_obj = convert_to_date(date_str)
    self.assertIsNone(date_obj)

## 2.4 GetFilteredObjectsTest

Este conjunto de tests verifica que la función `get_filtered_objects` maneje correctamente el filtrado, la paginación, y
el contexto de las vistas `auditorias_view`, `control_interno_view`, e `intervenciones_view`.

- **setUp**: Se realiza un login con un usuario valido y se crea una auditoria, un control interno y una intervención
  con las misma actividad de fiscalización.
  ```python
  def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(username='testuser', password='12345')
    self.client.login(username='testuser', password='12345')
    self.oic = Oic.objects.create(nombre="OIC1")
    self.actividad_fiscalizacion = ActividadFiscalizacion.objects.create(id_oic=self.oic, anyo=2024)
    self.auditoria = Auditoria.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)
    self.control_interno = ControlInterno.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)
    self.intervencion = Intervencion.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)

- **test_auditoria_filter**: Verifica que los objetos de auditoría sean correctamente filtrados según el OIC y el año.
  ```python
  def test_auditoria_filter(self):
      response = self.client.get(reverse('auditorias'), {'oic_id': self.oic.id, 'anyo': 2024})
      self.assertEqual(response.status_code, 200)
      self.assertContains(response, self.auditoria)

- **test_control_interno_filter**: Verifica el filtrado para la vista de control interno.
  ```python
  def test_control_interno_filter(self):
      response = self.client.get(reverse('controlInterno'), {'oic_id': self.oic.id, 'anyo': 2024})
      self.assertEqual(response.status_code, 200)
      self.assertContains(response, self.control_interno)

- **test_intervencion_filter**: Verifica el filtrado para la vista de intervenciones.
  ```python
  def test_intervencion_filter(self):
    response = self.client.get(reverse('intervenciones'), {'oic_id': self.oic.id, 'anyo': 2024})
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.intervencion)

- **test_no_filter**: Verifica que todos los objetos sean devueltos cuando no se aplica ningún filtro.
  ```python
  def test_no_filter(self):
    response = self.client.get(reverse('auditorias'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.auditoria)
    self.assertNotContains(response, "No matching records found.")

    response = self.client.get(reverse('intervenciones'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.intervencion)
    self.assertNotContains(response, "No matching records found.")

    response = self.client.get(reverse('controlInterno'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.control_interno)
    self.assertNotContains(response, "No matching records found.")

## 2.5 AuditoriasViewTest, ControlInternoViewTest, IntervencionesViewTest

Estos conjuntos de tests aseguran que cada vista específica (`auditorias_view`, `control_interno_view`,
`intervenciones_view`) llame correctamente a la función `get_filtered_objects` y utilice la plantilla adecuada.

- **setUp**: Se realiza un login con un usuario valido.
  ```python
  def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(username='testuser', password='12345')
    self.client.login(username='testuser', password='12345')
- **test_auditorias_view**: Verifica que la vista `auditorias_view` renderice la plantilla `auditorias.html`.
  ```python
  def test_auditorias_view(self):
    response = self.client.get(reverse('auditorias'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'auditorias.html')

- **test_control_interno_view**: Verifica que la vista `control_interno_view` renderice la plantilla
  `control_interno.html`.
  ```python
  def test_control_interno_view(self):
    response = self.client.get(reverse('controlInterno'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'control_interno.html')  

- **test_intervenciones_view**: Verifica que la vista `intervenciones_view` renderice la plantilla
  `intervenciones.html`.
  ```python
  def test_intervenciones_view(self):
    response = self.client.get(reverse('intervenciones'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'intervenciones.html')

## 2.6 HandleDetailViewTest

Este conjunto de tests verifica que la función `handle_detail_view` maneje correctamente la vista de detalle y edición
de objetos para las vistas `auditoria_detalle_view`, `control_interno_detalle_view`, e `intervencion_detalle_view`, asi
como verifica que el cambio de actividades de fiscalización se maneje correctamente, de acuerdo al método de save de los
formularios, teniendo casos distintos repartidos en cada una de las pruebas.

- **setUp**: Se realiza un login con un usuario valido, ademas de crear una auditoria, un control interno y una
  intervención, con sus respectivas actividades de fiscalización.
  ```python
  def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(username='testuser', password='12345')
    self.client.login(username='testuser', password='12345')
    self.oic = Oic.objects.create(nombre="OIC1")
    self.actividad_fiscalizacion = ActividadFiscalizacion.objects.create(id_oic=self.oic, anyo=2024)
    self.actividad_fiscalizacion_2 = ActividadFiscalizacion.objects.create(id_oic=self.oic, anyo=2025)
    self.auditoria = Auditoria.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)
    self.control_interno = ControlInterno.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion_2)
    self.intervencion = Intervencion.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion_2)

- **test_get_auditoria_detail**: Verifica que la vista de detalle de auditoría cargue correctamente el formulario.
  ```python
  def test_get_auditoria_detail(self):
    response = self.client.get(reverse('auditoria_detalle', args=[self.auditoria.id]))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'auditoria_detalle.html')
    self.assertIsInstance(response.context['form'], AuditoriaForm)
    self.assertEqual(response.context['form'].instance, self.auditoria)

- **test_post_valid_auditoria_detail**: Verifica que una solicitud POST con datos válidos actualice la auditoría,
  teniendo el caso en el que cambia de actividad de fiscalización, por una nueva, eliminando la que ya no se ocupa.
  ```python
  def test_post_auditoria_detail(self):
    response = self.client.post(reverse('auditoria_detalle', args=[self.auditoria.id]), {
        'anyo': '2026',
        'id_oic': self.oic.id
    })
    self.assertEqual(response.status_code, 200)
    self.auditoria.refresh_from_db()
    self.assertEqual(ActividadFiscalizacion.objects.filter(id=self.actividad_fiscalizacion.id).first(), None)
    self.assertEqual(self.auditoria.id_actividad_fiscalizacion.anyo, 2026)

- **test_get_control_interno_detail**: Verifica que la vista de detalle de control interno cargue correctamente el
  formulario.
  ```python
  def test_get_control_interno_detail(self):
    response = self.client.get(reverse('control_detalle', args=[self.control_interno.id]))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'control_detalle.html')
    self.assertIsInstance(response.context['form'], ControlForm)
    self.assertEqual(response.context['form'].instance, self.control_interno)

- **test_post_control_interno_detail**: Verifica que una solicitud POST con datos válidos actualice el control interno,
  teniendo el caso en el que cambia de actividad de fiscalización, por una existente anteriormente, viéndose que la
  actividad que tenia es ocupada por otra instancia y por lo tanto no eliminándola.

  ```python
  def test_post_control_interno_detail(self):
    response = self.client.post(reverse('control_detalle', args=[self.control_interno.id]), {
        'anyo': '2024',
        'id_oic': self.oic.id
    })
    self.assertEqual(response.status_code, 200)
    self.control_interno.refresh_from_db()
    self.assertEqual(self.control_interno.id_actividad_fiscalizacion, self.actividad_fiscalizacion)
    self.assertNotEqual(ActividadFiscalizacion.objects.filter(id=self.actividad_fiscalizacion_2.id).first(), None)

- **test_get_intervencion_detail**: Verifica que la vista de detalle de intervención cargue correctamente el formulario.
  ```python
  def test_get_intervencion_detail(self):
    response = self.client.get(reverse('intervencion_detalle', args=[self.intervencion.id]))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'intervencion_detalle.html')
    self.assertIsInstance(response.context['form'], IntervencionForm)
    self.assertEqual(response.context['form'].instance, self.intervencion)

- **test_post_intervencion_detail**: Verifica que una solicitud POST con datos válidos actualice la intervención,
  teniendo el caso en el que no cambia la actividad de fiscalización manteniendo la misma.
  ````python
  def test_post_intervencion_detail(self):
    response = self.client.post(reverse('intervencion_detalle', args=[self.intervencion.id]), {
        'anyo': '2025',
        'id_oic': self.oic.id
    })
    self.assertEqual(response.status_code, 200)
    self.intervencion.refresh_from_db()
    self.assertEqual(self.intervencion.id_actividad_fiscalizacion, self.actividad_fiscalizacion_2)

## 2.7 AuditoriaDetalleViewTest, ControlInternoDetalleViewTest, IntervencionDetalleViewTest

Estos conjuntos de tests aseguran que cada vista específica (`auditoria_detalle_view`, `control_interno_detalle_view`,
`intervencion_detalle_view`) llame correctamente a la función `handle_detail_view` y utilice la plantilla adecuada.

- **setUp**: Se realiza un login con un usuario valido, ademas de crear una auditoria, un control interno y una
  intervención.
  ```python
  def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(username='testuser', password='12345')
    self.client.login(username='testuser', password='12345')
    Auditoria.objects.create()
    ControlInterno.objects.create()
    Intervencion.objects.create()

- **test_auditoria_detalle_view**: Verifica que la vista `auditoria_detalle_view` renderice la plantilla
  `auditoria_detalle.html`.
  ```python
  def test_auditoria_detalle_view(self):
    response = self.client.get(reverse('auditoria_detalle', args=[1]))  # Test with a sample ID
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'auditoria_detalle.html')

- **test_control_interno_detalle_view**: Verifica que la vista `control_interno_detalle_view` renderice la plantilla
  `control_detalle.html`.
  ```python
  def test_control_interno_detalle_view(self):
    response = self.client.get(reverse('control_detalle', args=[1]))  # Test with a sample ID
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'control_detalle.html')

- **test_intervencion_detalle_view**: Verifica que la vista `intervencion_detalle_view` renderice la plantilla
  `intervencion_detalle.html`.
  ```python
  def test_intervencion_detalle_view(self):
    response = self.client.get(reverse('intervencion_detalle', args=[1]))  # Test with a sample ID
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'intervencion_detalle.html')

## 3. Pruebas de integración

## 4. Ejecución de pruebas

- Puedes ejecutar estas pruebas utilizando el siguiente comando estando en la raíz del proyecto:

  ```bash
  python manage.py test

## 5. Cobertura de las pruebas

En la cobertura de las pruebas se encontrara el rango de funciones y código cubierto por las pruebas, esto detallado en
un reporte completo generado por medio de la libreria `coverage`, para mas información prueba a
visitar [Covertura de las pruebas](coverage.md).

## 6. Herramientas utilizadas

- **Django TestCase**: Para la creación y ejecución de las pruebas.
- **Coverage**: Para la generación del reporte de cobertura de las pruebas. 


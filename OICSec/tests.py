import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .forms import AuditoriaForm, ControlForm, IntervencionForm
from .models import ActividadFiscalizacion, Oic, Auditoria, ControlInterno, Intervencion
from .views import convert_to_date


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        self.assertRedirects(response, reverse('home'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertContains(response, 'Usuario o contraseña invalidos')


class HomeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_home_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_unauthenticated(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login') + '?next=/OICSec/home/')


class ConvertToDateTest(TestCase):

    def test_convert_valid_date(self):
        date_str = '14/08/2024'
        date_obj = convert_to_date(date_str)
        self.assertEqual(date_obj, datetime.date(2024, 8, 14))

    def test_convert_invalid_date(self):
        date_str = ''
        date_obj = convert_to_date(date_str)
        self.assertIsNone(date_obj)


class GetFilteredObjectsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.oic = Oic.objects.create(nombre="OIC1")
        self.actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
            id_oic=self.oic, anyo=2024)
        self.auditoria = Auditoria.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)
        self.control_interno = ControlInterno.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)
        self.intervencion = Intervencion.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)

    def test_auditoria_filter(self):
        response = self.client.get(reverse('auditorias'), {'oic_id': self.oic.id, 'anyo': 2024})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.auditoria)

    def test_control_interno_filter(self):
        response = self.client.get(reverse('controlInterno'), {'oic_id': self.oic.id, 'anyo': 2024})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.control_interno)

    def test_intervencion_filter(self):
        response = self.client.get(reverse('intervenciones'), {'oic_id': self.oic.id, 'anyo': 2024})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intervencion)

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


class AuditoriasViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_auditorias_view(self):
        response = self.client.get(reverse('auditorias'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auditorias.html')


class ControlInternoViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_control_interno_view(self):
        response = self.client.get(reverse('controlInterno'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'control_interno.html')


class IntervencionesViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_intervenciones_view(self):
        response = self.client.get(reverse('intervenciones'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'intervenciones.html')


class HandleDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Setup data
        self.oic = Oic.objects.create(nombre="OIC1")
        self.actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
            id_oic=self.oic, anyo=2024)
        self.actividad_fiscalizacion_2 = ActividadFiscalizacion.objects.create(
            id_oic=self.oic, anyo=2025)
        self.auditoria = Auditoria.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion)
        self.control_interno = ControlInterno.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion_2)
        self.intervencion = Intervencion.objects.create(id_actividad_fiscalizacion=self.actividad_fiscalizacion_2)

    def test_get_auditoria_detail(self):
        response = self.client.get(reverse('auditoria_detalle', args=[self.auditoria.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auditoria_detalle.html')
        self.assertIsInstance(response.context['form'], AuditoriaForm)
        self.assertEqual(response.context['form'].instance, self.auditoria)

    def test_post_auditoria_detail(self):
        response = self.client.post(reverse('auditoria_detalle', args=[self.auditoria.id]), {
            'anyo': '2026',
            'id_oic': self.oic.id
        })
        self.assertEqual(response.status_code, 200)
        self.auditoria.refresh_from_db()
        self.assertEqual(ActividadFiscalizacion.objects.filter(id=self.actividad_fiscalizacion.id).first(), None)
        self.assertEqual(self.auditoria.id_actividad_fiscalizacion.anyo, 2026)

    def test_get_control_interno_detail(self):
        response = self.client.get(reverse('control_detalle', args=[self.control_interno.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'control_detalle.html')
        self.assertIsInstance(response.context['form'], ControlForm)
        self.assertEqual(response.context['form'].instance, self.control_interno)

    def test_post_control_interno_detail(self):
        response = self.client.post(reverse('control_detalle', args=[self.control_interno.id]), {
            'anyo': '2024',
            'id_oic': self.oic.id
        })
        self.assertEqual(response.status_code, 200)
        self.control_interno.refresh_from_db()
        self.assertEqual(self.control_interno.id_actividad_fiscalizacion, self.actividad_fiscalizacion)
        self.assertNotEqual(ActividadFiscalizacion.objects.filter(id=self.actividad_fiscalizacion_2.id).first(), None)

    def test_get_intervencion_detail(self):
        response = self.client.get(reverse('intervencion_detalle', args=[self.intervencion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'intervencion_detalle.html')
        self.assertIsInstance(response.context['form'], IntervencionForm)
        self.assertEqual(response.context['form'].instance, self.intervencion)

    def test_post_intervencion_detail(self):
        response = self.client.post(reverse('intervencion_detalle', args=[self.intervencion.id]), {
            'anyo': '2025',
            'id_oic': self.oic.id
        })
        self.assertEqual(response.status_code, 200)
        self.intervencion.refresh_from_db()
        self.assertEqual(self.intervencion.id_actividad_fiscalizacion, self.actividad_fiscalizacion_2)


class AuditoriaDetalleViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        Auditoria.objects.create()

    def test_auditoria_detalle_view(self):
        response = self.client.get(reverse('auditoria_detalle', args=[1]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auditoria_detalle.html')


class ControlInternoDetalleViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        ControlInterno.objects.create()

    def test_control_interno_detalle_view(self):
        response = self.client.get(reverse('control_detalle', args=[1]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'control_detalle.html')


class IntervencionDetalleViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        Intervencion.objects.create(id=1)

    def test_intervencion_detalle_view(self):
        response = self.client.get(reverse('intervencion_detalle', args=[1]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'intervencion_detalle.html')


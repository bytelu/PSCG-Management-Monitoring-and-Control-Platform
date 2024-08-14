import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

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

        # Setup data
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


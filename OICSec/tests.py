import datetime
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from .forms import AuditoriaForm, ControlForm, IntervencionForm
from .models import ActividadFiscalizacion, Oic, Auditoria, ControlInterno, Intervencion
from .views import convert_to_date


class LoggedIn(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')


class LoginViewTest(LoggedIn):

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        self.assertRedirects(response, reverse('home'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertContains(response, 'Usuario o contraseña invalidos')


class HomeViewTest(LoggedIn):

    def test_home_authenticated(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login') + '?next=/OICSec/home/')


class ConvertToDateTest(TestCase):

    def test_convert_valid_date(self):
        date_str = '14/08/2024'
        date_obj = convert_to_date(date_str)
        self.assertEqual(date_obj, datetime.date(2024, 8, 14))

    def test_convert_void_date(self):
        date_str = ''
        date_obj = convert_to_date(date_str)
        self.assertIsNone(date_obj)

    def test_convert_invalid_date(self):
        date_str = 'invalid'
        date_obj = convert_to_date(date_str)
        self.assertIsNone(date_obj)


class GetFilteredObjectsTest(LoggedIn):

    def setUp(self):
        super().setUp()
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

    def test_incomplete_filter(self):
        # No OIC
        response = self.client.get(reverse('auditorias'), {'anyo': 2024})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.auditoria)
        # No year
        response = self.client.get(reverse('controlInterno'), {'oic_id': self.oic.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.control_interno)
        # Void
        response = self.client.get(reverse('intervenciones'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intervencion)


class AuditoriasViewTest(LoggedIn):

    def test_auditorias_view(self):
        response = self.client.get(reverse('auditorias'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auditorias.html')


class ControlInternoViewTest(LoggedIn):

    def test_control_interno_view(self):
        response = self.client.get(reverse('controlInterno'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'control_interno.html')


class IntervencionesViewTest(LoggedIn):

    def test_intervenciones_view(self):
        response = self.client.get(reverse('intervenciones'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'intervenciones.html')


class HandleDetailViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
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

    def test_post_auditoria_detail_invalid(self):
        response = self.client.post(reverse('auditoria_detalle', args=[self.auditoria.id]), {
            'anyo': 'invalid',
            'id_oic': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auditoria_detalle.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('error', response.context)

    def test_post_control_interno_detail_invalid(self):
        response = self.client.post(reverse('control_detalle', args=[self.control_interno.id]), {
            'anyo': 'invalid',
            'id_oic': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'control_detalle.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('error', response.context)

    def test_post_intervencion_detail_invalid(self):
        response = self.client.post(reverse('intervencion_detalle', args=[self.intervencion.id]), {
            'anyo': 'invalid',
            'id_oic': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'intervencion_detalle.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('error', response.context)


class AuditoriaDetalleViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
        Auditoria.objects.create()

    def test_auditoria_detalle_view(self):
        response = self.client.get(reverse('auditoria_detalle', args=[1]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auditoria_detalle.html')


class ControlInternoDetalleViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
        ControlInterno.objects.create()

    def test_control_interno_detalle_view(self):
        response = self.client.get(reverse('control_detalle', args=[1]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'control_detalle.html')


class IntervencionDetalleViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
        Intervencion.objects.create(id=1)

    def test_intervencion_detalle_view(self):
        response = self.client.get(reverse('intervencion_detalle', args=[1]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'intervencion_detalle.html')


class UploadPaaViewTest(LoggedIn):
    def setUp(self):
        super().setUp()
        self.oic = Oic.objects.create(nombre="OIC Test")

        fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_documents')
        excel_file_path = os.path.join(fixtures_dir, 'test_paa.xlsx')
        with open(excel_file_path, 'rb') as excel_file:
            self.valid_excel_data = excel_file.read()

        excel_file_path = os.path.join(fixtures_dir, 'test_paa_invalid.xlsx')
        with open(excel_file_path, 'rb') as excel_file:
            self.invalid_excel_data = excel_file.read()

    def test_get_upload_paa_view(self):
        response = self.client.get(reverse('uploadPaa'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload_paa.html')
        self.assertIn('lista_oics', response.context)

    def test_post_valid_upload_paa_view(self):
        response = self.client.post(reverse('uploadPaa'), {
            'excel_file': SimpleUploadedFile('test_paa.xlsx', self.valid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Auditoria.objects.exists())
        self.assertIn('excel_processing_result', response.context)

    def test_post_invalid_upload_paa_view(self):
        response = self.client.post(reverse('uploadPaa'), {
            'excel_file': SimpleUploadedFile('test_paa_invalid.xlsx', self.invalid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('excel_processing_error', response.context)
        self.assertIn('Error al procesar el archivo Excel', response.context['excel_processing_error'])


class UploadPaciViewTest(LoggedIn):
    def setUp(self):
        super().setUp()
        self.oic = Oic.objects.create(nombre="OIC Test")

        fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_documents')
        excel_file_path = os.path.join(fixtures_dir, 'test_paci.xlsx')
        with open(excel_file_path, 'rb') as excel_file:
            self.valid_excel_data = excel_file.read()

        excel_file_path = os.path.join(fixtures_dir, 'test_paci_invalid.xlsx')
        with open(excel_file_path, 'rb') as excel_file:
            self.invalid_excel_data = excel_file.read()

    def test_get_upload_paci_view(self):
        response = self.client.get(reverse('uploadPaci'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload_paci.html')
        self.assertIn('lista_oics', response.context)

    def test_post_valid_upload_paci_view(self):
        response = self.client.post(reverse('uploadPaci'), {
            'excel_file': SimpleUploadedFile('test_paci.xlsx', self.valid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ControlInterno.objects.exists())
        self.assertIn('excel_processing_result', response.context)

    def test_post_invalid_upload_paci_view(self):
        response = self.client.post(reverse('uploadPaci'), {
            'excel_file': SimpleUploadedFile('test_paci_invalid.xlsx', self.invalid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('excel_processing_error', response.context)
        self.assertIn('Error al procesar el archivo Excel', response.context['excel_processing_error'])

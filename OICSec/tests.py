import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse

from .forms import AuditoriaForm, ControlForm, IntervencionForm
from .models import ActividadFiscalizacion, Oic, Auditoria, ControlInterno, Intervencion, TipoIntervencion, Cedula, \
    ConceptoCedula, Minuta, ConceptoMinuta, Archivo, Persona, Personal, CargoPersonal, TipoCargo
from .signals import is_last_record_in_activity
from .views import convert_to_date, clean_oic_text, get_most_similar_tipo_intervencion, get_cedula_conceptos


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


class ActividadesViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
        # Crear un OIC y Actividades de Fiscalización para pruebas
        self.oic = Oic.objects.create(nombre="OIC Test")
        self.actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
            id_oic=self.oic, anyo=2024, trimestre=1)
        self.actividad_fiscalizacion_incompleta = ActividadFiscalizacion.objects.create(
            id_oic=self.oic, anyo=None, trimestre=None)

    def test_actividades_view_status_code(self):
        # Comprobar que la vista se carga correctamente
        response = self.client.get(reverse('actividades'))
        self.assertEqual(response.status_code, 200)

    def test_actividades_view_template_used(self):
        # Verificar que se utiliza la plantilla correcta
        response = self.client.get(reverse('actividades'))
        self.assertTemplateUsed(response, 'actividades.html')

    def test_actividades_view_with_oic_and_year_filter(self):
        # Probar filtro por OIC y año
        response = self.client.get(reverse('actividades'), {'oic_id': self.oic.id, 'anyo': 2024})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.actividad_fiscalizacion)
        self.assertNotContains(response, self.actividad_fiscalizacion_incompleta)

    def test_actividades_view_without_filters(self):
        # Probar sin filtros, debe mostrar todas las actividades
        response = self.client.get(reverse('actividades'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.actividad_fiscalizacion)
        self.assertContains(response, self.actividad_fiscalizacion_incompleta)

    def test_incomplete_activities_identification(self):
        # Verificar que se identifican las actividades con datos incompletos
        response = self.client.get(reverse('actividades'))
        self.assertEqual(response.status_code, 200)
        elementos_incompletos = response.context['elementos_incompletos']
        self.assertIn(self.actividad_fiscalizacion_incompleta, elementos_incompletos)

    def test_pagination(self):
        # Probar la paginación creando más de 20 actividades
        for i in range(25):
            ActividadFiscalizacion.objects.create(id_oic=self.oic, anyo=2025, trimestre=2)

        response = self.client.get(reverse('actividades'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertEqual(len(response.context['page_obj'].object_list), 20)  # Debe haber 20 en la primera página

        # Comprobar segunda página
        response = self.client.get(reverse('actividades') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['page_obj'].has_next())  # No debe haber más páginas

    def test_partial_filter_oic_only(self):
        # Probar con solo el filtro de OIC
        response = self.client.get(reverse('actividades'), {'oic_id': self.oic.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.actividad_fiscalizacion)


class HandleDetailViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
        self.oic = Oic.objects.create(nombre="OIC1")
        self.actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
            id_oic=self.oic, anyo=2024, trimestre=3)
        self.actividad_fiscalizacion_2 = ActividadFiscalizacion.objects.create(
            id_oic=self.oic, anyo=2025, trimestre=3)
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
            'id_oic': self.oic.id,
            'trimestre': 3
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
            'id_oic': self.oic.id,
            'trimestre': 3
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
            'id_oic': self.oic.id,
            'trimestre': 3
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
        self.auditoria = Auditoria.objects.create()

    def test_auditoria_detalle_view(self):
        response = self.client.get(reverse('auditoria_detalle', args=[self.auditoria.id]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auditoria_detalle.html')


class ControlInternoDetalleViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
        self.control_interno = ControlInterno.objects.create()

    def test_control_interno_detalle_view(self):
        response = self.client.get(reverse('control_detalle', args=[self.control_interno.id]))  # Test with a sample ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'control_detalle.html')


class IntervencionDetalleViewTest(LoggedIn):

    def setUp(self):
        super().setUp()
        self.intervencion = Intervencion.objects.create(id=1)

    def test_intervencion_detalle_view(self):
        response = self.client.get(reverse('intervencion_detalle', args=[self.intervencion.id]))  # Test with a sample ID
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
            'excel_files': SimpleUploadedFile('test_paa.xlsx', self.valid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Auditoria.objects.exists())
        self.assertIn('excel_processing_result', response.context)

    def test_post_invalid_upload_paa_view(self):
        response = self.client.post(reverse('uploadPaa'), {
            'excel_files': SimpleUploadedFile('test_paa_invalid.xlsx', self.invalid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('excel_processing_error', response.context)

    def test_post_update_existing_auditoria(self):
        actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
            id_oic=self.oic,
            anyo=2024,
            trimestre=1
        )

        auditoria = Auditoria.objects.create(
            denominacion="Denominación Original",
            numero=1,
            objetivo="Objetivo Original",
            alcance="Alcance Original",
            ejercicio="2023",
            unidad="Unidad Original",
            id_actividad_fiscalizacion=actividad_fiscalizacion,
        )

        response = self.client.post(reverse('uploadPaa'), {
            'excel_files': SimpleUploadedFile('test_paa.xlsx', self.valid_excel_data)
        })

        auditoria.refresh_from_db()
        self.assertEqual(auditoria.denominacion, "test")
        self.assertEqual(auditoria.objetivo, "test")
        self.assertEqual(auditoria.alcance, "test")
        self.assertEqual(auditoria.unidad, "test")
        self.assertEqual(response.status_code, 200)
        self.assertIn('excel_processing_result', response.context)


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
            'excel_files': SimpleUploadedFile('test_paci.xlsx', self.valid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ControlInterno.objects.exists())
        self.assertIn('excel_processing_result', response.context)

    def test_post_invalid_upload_paci_view(self):
        response = self.client.post(reverse('uploadPaci'), {
            'excel_files': SimpleUploadedFile('test_paci_invalid.xlsx', self.invalid_excel_data)
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('excel_processing_error', response.context)

    def test_post_update_existing_control_interno(self):
        actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
            id_oic=self.oic,
            anyo=2024,
            trimestre=2
        )

        control_interno = ControlInterno.objects.create(
            denominacion="Denominación Original",
            numero=1,
            objetivo="Objetivo Original",
            ejercicio="2023",
            area="Unidad Original",
            id_actividad_fiscalizacion=actividad_fiscalizacion,
        )

        response = self.client.post(reverse('uploadPaci'), {
            'excel_files': SimpleUploadedFile('test_paci.xlsx', self.valid_excel_data)
        })

        control_interno.refresh_from_db()
        self.assertEqual(control_interno.denominacion, "test")
        self.assertEqual(control_interno.objetivo, "test")
        self.assertEqual(control_interno.area, "test")
        self.assertEqual(response.status_code, 200)
        self.assertIn('excel_processing_result', response.context)


class CleanOicTextTestCase(TestCase):

    def test_clean_oic_text(self):
        self.assertEqual(clean_oic_text('Órgano Interno de Control en la Secretaría de Salud'),
                         'la secretaría de salud')
        self.assertEqual(
            clean_oic_text('Órgano Interno de Control en la Secretaría de la Defensa Nacional de la Ciudad de México'),
            'la secretaría de la defensa nacional')

        self.assertEqual(clean_oic_text('Secretaría de Hacienda y Crédito Público'),
                         'secretaría de hacienda y crédito público')

        self.assertEqual(clean_oic_text('Órgano Interno de Control'), 'órgano interno de control')


class GetMostSimilarTipoIntervencionTestCase(TestCase):

    def setUp(self):
        self.tipo1 = TipoIntervencion.objects.create(tipo='Financiera')
        self.tipo2 = TipoIntervencion.objects.create(tipo='Gestión')
        self.tipo3 = TipoIntervencion.objects.create(tipo='Cumplimiento')

    def test_get_most_similar_tipo_intervencion(self):
        # Entrada exacta
        result = get_most_similar_tipo_intervencion('Financiera')
        self.assertEqual(result, self.tipo1)

        # Entrada similar
        result = get_most_similar_tipo_intervencion('Financiera')
        self.assertEqual(result, self.tipo1)

        # Entrada parcialmente similar
        result = get_most_similar_tipo_intervencion('Auditoría de Cumplimiento')
        self.assertEqual(result, self.tipo3)


class UploadPintViewTestCase(LoggedIn):

    def setUp(self):
        super().setUp()
        self.oic = Oic.objects.create(nombre='OIC Test')
        self.tipo_intervencion = TipoIntervencion.objects.create(clave='14', tipo='Verificación')

    def test_upload_pint_view(self):
        fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_documents')
        excel_file_path = os.path.join(fixtures_dir, 'test_pint.docx')
        with open(excel_file_path, 'rb') as word_file:
            file_content = word_file.read()
        word_file = SimpleUploadedFile("test_pint.docx", file_content,
                                       content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response = self.client.post(reverse('uploadPint'), {'word_files': [word_file]})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Intervencion.objects.exists())
        self.assertTrue(Cedula.objects.exists())
        self.assertTrue(ConceptoCedula.objects.exists())

    def test_upload_pint_view_no_files(self):
        response = self.client.post(reverse('uploadPint'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Error al procesar los archivos')

    def test_post_update_existing_intervencion(self):
        actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
            id_oic=self.oic,
            anyo=2024,
            trimestre=3
        )

        intervencion = Intervencion.objects.create(
            numero=4,
            id_tipo_intervencion=self.tipo_intervencion,
            id_actividad_fiscalizacion=actividad_fiscalizacion,
            denominacion="Denominación Original",
            objetivo="Objetivo Original"
        )

        fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_documents')
        excel_file_path = os.path.join(fixtures_dir, 'test_pint.docx')
        with open(excel_file_path, 'rb') as word_file:
            file_content = word_file.read()
        word_file = SimpleUploadedFile("test_pint.docx", file_content,
                                       content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = self.client.post(reverse('uploadPint'), {'word_files': [word_file]})

        intervencion.refresh_from_db()
        self.assertEqual(intervencion.denominacion, "test")
        self.assertEqual(intervencion.objetivo, "test")
        self.assertEqual(response.status_code, 200)
        self.assertIn('word_processing_result', response.context)


def create_and_register_file(related_instance, filename):
    file_path = ''
    if isinstance(related_instance, Cedula):
        file_path = os.path.join(settings.BASE_DIR, 'media', 'cedulas', filename)
    elif isinstance(related_instance, Minuta):
        file_path = os.path.join(settings.BASE_DIR, 'media', 'minutas', filename)

    with open(file_path, 'w') as f:
        f.write(filename)

    archivo = Archivo.objects.create(
        archivo=file_path,
        nombre=filename,
    )

    related_instance.id_archivo = archivo
    related_instance.save()

    return file_path


class DeleteViewTests(LoggedIn):
    def setUp(self):
        super().setUp()
        self.actividadA = ActividadFiscalizacion.objects.create()
        self.actividadB = ActividadFiscalizacion.objects.create()

        self.cedulaAuditoria = Cedula.objects.create()
        ConceptoCedula.objects.create(id_cedula=self.cedulaAuditoria)

        self.cedulaIntervencion = Cedula.objects.create()
        ConceptoCedula.objects.create(id_cedula=self.cedulaIntervencion)

        self.cedulaControl = Cedula.objects.create()
        ConceptoCedula.objects.create(id_cedula=self.cedulaControl)

        self.minutaA = Minuta.objects.create(id_actividad_fiscalizacion=self.actividadA)
        ConceptoMinuta.objects.create(id_minuta=self.minutaA)
        self.minutaB = Minuta.objects.create(id_actividad_fiscalizacion=self.actividadB)
        ConceptoMinuta.objects.create(id_minuta=self.minutaB)

        self.auditoria = Auditoria.objects.create(id_actividad_fiscalizacion=self.actividadA, id_cedula=self.cedulaAuditoria)
        self.intervencion = Intervencion.objects.create(id_actividad_fiscalizacion=self.actividadA, id_cedula=self.cedulaIntervencion)
        self.controlinterno = ControlInterno.objects.create(id_actividad_fiscalizacion=self.actividadB, id_cedula=self.cedulaControl)

        self.file_auditoria_path = create_and_register_file(self.cedulaAuditoria, 'cedula_auditoria.xlsx')
        self.file_intervencion_path = create_and_register_file(self.cedulaIntervencion, 'cedula_intervencion.xlsx')
        self.file_control_path = create_and_register_file(self.cedulaControl, 'cedula_control.xlsx')
        self.file_minutaA_path = create_and_register_file(self.minutaA, 'minuta_a.docx')
        self.file_minutaB_path = create_and_register_file(self.minutaB, 'minuta_b.docx')

    def tearDown(self):
        files_to_delete = [
            self.file_auditoria_path,
            self.file_intervencion_path,
            self.file_control_path,
            self.file_minutaA_path,
            self.file_minutaB_path,
        ]

        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)

    def assert_common_deletion_checks(self, instance, cedula, file_path, minuta, minuta_file_path, still_exists=True):
        self.assertFalse(type(instance).objects.filter(pk=instance.pk).exists())
        self.assertFalse(Cedula.objects.filter(pk=cedula.pk).exists())
        self.assertFalse(ConceptoCedula.objects.filter(id_cedula=cedula).exists())
        self.assertFalse(Archivo.objects.filter(pk=cedula.id_archivo.id).exists())
        self.assertFalse(os.path.exists(file_path))

        if still_exists:
            self.assertTrue(Minuta.objects.filter(pk=minuta.pk).exists())
            self.assertTrue(ConceptoMinuta.objects.filter(id_minuta=minuta).exists())
            self.assertTrue(os.path.exists(minuta_file_path))
        else:
            self.assertFalse(Minuta.objects.filter(pk=minuta.pk).exists())
            self.assertFalse(ConceptoMinuta.objects.filter(id_minuta=minuta).exists())
            self.assertFalse(os.path.exists(minuta_file_path))

    def test_delete_auditoria_view(self):
        response = self.client.post(reverse('auditoria-delete', kwargs={'pk': self.auditoria.pk}))
        self.assertEqual(response.status_code, 302)
        self.assert_common_deletion_checks(
            self.auditoria,
            self.cedulaAuditoria,
            self.file_auditoria_path,
            self.minutaA,
            self.file_minutaA_path,
            still_exists=True
        )

    def test_delete_intervencion_view(self):
        response = self.client.post(reverse('intervencion-delete', kwargs={'pk': self.intervencion.pk}))
        self.assertEqual(response.status_code, 302)
        self.assert_common_deletion_checks(
            self.intervencion,
            self.cedulaIntervencion,
            self.file_intervencion_path,
            self.minutaA,
            self.file_minutaA_path,
            still_exists=True
        )

    def test_delete_controlinterno_view(self):
        response = self.client.post(reverse('controlinterno-delete', kwargs={'pk': self.controlinterno.pk}))
        self.assertEqual(response.status_code, 302)
        self.assert_common_deletion_checks(
            self.controlinterno,
            self.cedulaControl,
            self.file_control_path,
            self.minutaB,
            self.file_minutaB_path,
            still_exists=False
        )

    def test_is_last_record_in_activity(self):
        self.assertFalse(is_last_record_in_activity(self.auditoria))
        self.intervencion.delete()
        self.assertTrue(is_last_record_in_activity(self.auditoria))
        self.assertTrue(is_last_record_in_activity(self.controlinterno))


class GetCedulaConceptosTestCase(LoggedIn):
    def setUp(self):
        super().setUp()
        self.oic = Oic.objects.create(nombre="OIC Test")

        self.cedula = Cedula.objects.create()

        self.concepto1 = ConceptoCedula.objects.create(
            id_cedula=self.cedula,
            celda='A1',
            estado=1,
            comentario='Comentario 1'
        )
        self.concepto2 = ConceptoCedula.objects.create(
            id_cedula=self.cedula,
            celda='A2',
            estado=2,
            comentario=None  # Comentario vacío
        )

        self.auditoria = Auditoria.objects.create(
            id_cedula=self.cedula,
        )

    def test_get_cedula_conceptos(self):
        cedula, conceptos, conceptos_dict = get_cedula_conceptos(self.auditoria)

        # Verifica que se haya recuperado la cedula correctamente
        self.assertEqual(cedula.id, self.cedula.id)

        # Verifica que se hayan recuperado los conceptos correctamente
        self.assertIn(self.concepto1, conceptos)
        self.assertIn(self.concepto2, conceptos)

        # Verifica el diccionario de conceptos
        expected_dict = {
            'A1': {'estado': 1, 'comentario': 'Comentario 1'},
            'A2': {'estado': 2, 'comentario': ''}
        }
        self.assertEqual(conceptos_dict, expected_dict)


class CedulaViewTests(LoggedIn):

    def setUp(self):
        super().setUp()
        self.oic = Oic.objects.create(nombre="OIC Test")

        self.actividad = ActividadFiscalizacion.objects.create(id_oic=self.oic)

        # Creación de los objetos necesarios para las pruebas
        self.cedula = Cedula.objects.create()
        self.concepto0 = ConceptoCedula.objects.create(
            id_cedula=self.cedula,
            celda='0',
            estado=0,
            comentario='Comentario 1'
        )
        self.concepto1 = ConceptoCedula.objects.create(
            id_cedula=self.cedula,
            celda='1',
            estado=1,
            comentario=None  # Comentario vacío
        )
        self.concepto2 = ConceptoCedula.objects.create(
            id_cedula=self.cedula,
            celda='2',
            estado=3,
            comentario=None  # Comentario vacío
        )
        self.concepto3 = ConceptoCedula.objects.create(
            id_cedula=self.cedula,
            celda='3',
            estado=2,
            comentario=None  # Comentario vacío
        )
        self.concepto4 = ConceptoCedula.objects.create(
            id_cedula=self.cedula,
            celda='4',
            estado=4,
            comentario=None  # Comentario vacío
        )

        self.auditoria = Auditoria.objects.create(
            id_cedula=self.cedula,
            id_actividad_fiscalizacion=self.actividad
        )

        self.url = reverse('auditoria_cedula', kwargs={'auditoria_id': self.auditoria.id})

    def test_cedula_view_get(self):
        response = self.client.get(self.url)

        # Verifica que la respuesta sea correcta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cedula.html')

        # Verificar que los conceptos se pasaron correctamente al contexto
        conceptos_dict = response.context['conceptos']
        expected_dict = {
            '0': {'estado': 0, 'comentario': 'Comentario 1'},
            '1': {'estado': 1, 'comentario': ''},
            '2': {'estado': 3, 'comentario': ''},
            '3': {'estado': 2, 'comentario': ''},
            '4': {'estado': 4, 'comentario': ''},
        }
        self.assertEqual(conceptos_dict, expected_dict)

    def test_cedula_view_post(self):
        post_data = {
            'estado-0': '4',
            'comentario-0': 'Nuevo comentario A0',
            'estado-1': '3',
            'comentario-1': 'Nuevo comentario A1',
            'estado-2': '2',
            'comentario-2': 'Nuevo comentario A2',
            'estado-3': '1',
            'comentario-3': 'Nuevo comentario A3',
            'estado-4': '0',
            'comentario-4': 'Nuevo comentario A4',
            'fecha': '2024-09-25'
        }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, 200)

        # Verifica que la respuesta contiene un archivo adjunto
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertIn('attachment; filename=', response['Content-Disposition'])

        # Verifica el tipo MIME para archivos Excel
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # Verifica que el archivo tenga algún contenido
        self.assertGreater(len(response.content), 0)

        # Verifica que los conceptos se actualizaron en la base de datos
        concepto1_actualizado = ConceptoCedula.objects.get(celda='0')
        self.assertEqual(concepto1_actualizado.comentario, 'Nuevo comentario A0')

        concepto2_actualizado = ConceptoCedula.objects.get(celda='1')
        self.assertEqual(concepto2_actualizado.comentario, 'Nuevo comentario A1')


    def test_cedula_view_con_intervencion(self):
        intervencion = Intervencion.objects.create(id_cedula=self.cedula)
        url_intervencion = reverse('intervencion_cedula', kwargs={'intervencion_id': intervencion.id})

        response = self.client.get(url_intervencion)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cedula.html')

        # Verificar que los conceptos se pasaron correctamente al contexto
        conceptos_dict = response.context['conceptos']
        expected_dict = {
            '0': {'estado': 0, 'comentario': 'Comentario 1'},
            '1': {'estado': 1, 'comentario': ''},
            '2': {'estado': 3, 'comentario': ''},
            '3': {'estado': 2, 'comentario': ''},
            '4': {'estado': 4, 'comentario': ''},
        }
        self.assertEqual(conceptos_dict, expected_dict)

    def test_cedula_view_con_control_interno(self):
        control_interno = ControlInterno.objects.create(id_cedula=self.cedula)
        url_control_interno = reverse('control_cedula', kwargs={'control_id': control_interno.id})

        response = self.client.get(url_control_interno)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cedula.html')

        # Verificar que los conceptos se pasaron correctamente al contexto
        conceptos_dict = response.context['conceptos']
        expected_dict = {
            '0': {'estado': 0, 'comentario': 'Comentario 1'},
            '1': {'estado': 1, 'comentario': ''},
            '2': {'estado': 3, 'comentario': ''},
            '3': {'estado': 2, 'comentario': ''},
            '4': {'estado': 4, 'comentario': ''},
        }
        self.assertEqual(conceptos_dict, expected_dict)


class MinutaViewGetTest(LoggedIn):

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'OICSec/fixtures/initial_data.json')
        self.oic = Oic.objects.get(pk=1)
        self.actividad = ActividadFiscalizacion.objects.create(id_oic=self.oic)

    def test_minuta_view(self):
        response = self.client.get(reverse('minuta', args=[self.actividad.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'minuta.html')

    def test_minuta_mes_view(self):
        self.direccion_oic = Oic.objects.get(pk=53)
        # Crear personas
        self.persona_director = Persona.objects.create(honorifico='Sr.', nombre='Juan', apellido='Pérez')
        self.persona_judc = Persona.objects.create(honorifico='Dra.', nombre='Ana', apellido='López')
        self.persona_titular = Persona.objects.create(honorifico='Lic.', nombre='Luis', apellido='Gómez')
        self.persona_oic = Persona.objects.create(honorifico='Ing.', nombre='María', apellido='Fernández')

        # Crear personal
        self.personal_director = Personal.objects.create(estado=1, id_oic=self.direccion_oic,
                                                         id_persona=self.persona_director)
        self.personal_judc = Personal.objects.create(estado=1, id_oic=self.direccion_oic, id_persona=self.persona_judc)
        self.personal_titular = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_titular)
        self.personal_oic = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_oic)

        # Crear cargos de personal
        CargoPersonal.objects.create(nombre='Director', id_tipo_cargo=TipoCargo.objects.get(id=1),
                                     id_personal=self.personal_director)
        CargoPersonal.objects.create(nombre='JUDC', id_tipo_cargo=TipoCargo.objects.get(id=2),
                                     id_personal=self.personal_judc)
        CargoPersonal.objects.create(nombre='Titular', id_tipo_cargo=TipoCargo.objects.get(id=6),
                                     id_personal=self.personal_titular)
        CargoPersonal.objects.create(nombre='Personal OIC', id_tipo_cargo=TipoCargo.objects.get(id=7),
                                     id_personal=self.personal_oic)

        mes = 3
        response = self.client.get(reverse('minuta_mes', args=[self.actividad.id, mes]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'minuta_mes.html')
        self.assertIn('mes', response.context)
        self.assertEqual(response.context['mes'], mes)
        self.assertIn('actividades', response.context)
        self.assertIn('oic', response.context)

    def test_redireccion_error_personal_direccion(self):
        self.direccion_oic = Oic.objects.get(pk=53)
        # Crear personas sin personal de dirección
        # self.persona_director = Persona.objects.create(honorifico='Sr.', nombre='Juan', apellido='Pérez')
        # self.persona_judc = Persona.objects.create(honorifico='Dra.', nombre='Ana', apellido='López')
        self.persona_titular = Persona.objects.create(honorifico='Lic.', nombre='Luis', apellido='Gómez')
        self.persona_oic = Persona.objects.create(honorifico='Ing.', nombre='María', apellido='Fernández')

        # Crear personal
        # self.personal_director = Personal.objects.create(estado=1, id_oic=self.direccion_oic, id_persona=self.persona_director)
        # self.personal_judc = Personal.objects.create(estado=1, id_oic=self.direccion_oic, id_persona=self.persona_judc)
        self.personal_titular = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_titular)
        self.personal_oic = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_oic)

        # Crear cargos de personal
        # CargoPersonal.objects.create(nombre='Director', id_tipo_cargo=TipoCargo.objects.get(id=1), id_personal=self.personal_director)
        # CargoPersonal.objects.create(nombre='JUDC', id_tipo_cargo=TipoCargo.objects.get(id=2), id_personal=self.personal_judc)
        CargoPersonal.objects.create(nombre='Titular', id_tipo_cargo=TipoCargo.objects.get(id=6), id_personal=self.personal_titular)
        CargoPersonal.objects.create(nombre='Personal OIC', id_tipo_cargo=TipoCargo.objects.get(id=7), id_personal=self.personal_oic)

        mes = 3
        # Hacer la llamada a la vista que procesa esta lógica
        response = self.client.get(reverse('minuta_mes', args=[self.actividad.id, mes]))

        # Comprobar que se redirige a la URL correcta
        self.assertRedirects(response, reverse('personal_direccion', args=[self.direccion_oic.id_direccion.direccion]))
        # Comprobar que el mensaje de error está en la respuesta
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),'Hubo un error con el personal de la dirección, verifica que estos esten registrados correctamente.')

    def test_redireccion_por_error_personal_oic(self):
        self.direccion_oic = Oic.objects.get(pk=53)
        # Crear personas sin personal de oic
        self.persona_director = Persona.objects.create(honorifico='Sr.', nombre='Juan', apellido='Pérez')
        self.persona_judc = Persona.objects.create(honorifico='Dra.', nombre='Ana', apellido='López')
        # self.persona_titular = Persona.objects.create(honorifico='Lic.', nombre='Luis', apellido='Gómez')
        # self.persona_oic = Persona.objects.create(honorifico='Ing.', nombre='María', apellido='Fernández')

        # Crear personal
        self.personal_director = Personal.objects.create(estado=1, id_oic=self.direccion_oic, id_persona=self.persona_director)
        self.personal_judc = Personal.objects.create(estado=1, id_oic=self.direccion_oic, id_persona=self.persona_judc)
        # self.personal_titular = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_titular)
        # self.personal_oic = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_oic)

        # Crear cargos de personal
        CargoPersonal.objects.create(nombre='Director', id_tipo_cargo=TipoCargo.objects.get(id=1), id_personal=self.personal_director)
        CargoPersonal.objects.create(nombre='JUDC', id_tipo_cargo=TipoCargo.objects.get(id=2), id_personal=self.personal_judc)
        # CargoPersonal.objects.create(nombre='Titular', id_tipo_cargo=TipoCargo.objects.get(id=6), id_personal=self.personal_titular)
        # CargoPersonal.objects.create(nombre='Personal OIC', id_tipo_cargo=TipoCargo.objects.get(id=7), id_personal=self.personal_oic)

        mes = 3
        # Hacer la llamada a la vista que procesa esta lógica
        response = self.client.get(reverse('minuta_mes', args=[self.actividad.id, mes]))

        # Comprobar que se redirige a la URL correcta
        self.assertRedirects(response, reverse('personal_oic', args=[self.oic.id]))
        # Comprobar que el mensaje de error está en la respuesta
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Hubo un error con el personal del OIC, verifica que estos esten registrados correctamente.')


class MinutaViewPostTests(LoggedIn):

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'OICSec/fixtures/initial_data.json')
        self.oic = Oic.objects.get(pk=1)
        self.actividad = ActividadFiscalizacion.objects.create(id_oic=self.oic)
        self.direccion_oic = Oic.objects.get(pk=53)
        self.auditoria = Auditoria.objects.create(id_actividad_fiscalizacion=self.actividad)
        self.intervencion = Intervencion.objects.create(id_actividad_fiscalizacion=self.actividad)
        self.control = ControlInterno.objects.create(id_actividad_fiscalizacion=self.actividad)

        self.persona_director = Persona.objects.create(honorifico='Sr.', nombre='Juan', apellido='Pérez')
        self.persona_judc = Persona.objects.create(honorifico='Dra.', nombre='Ana', apellido='López')
        self.persona_titular = Persona.objects.create(honorifico='Lic.', nombre='Luis', apellido='Gómez')
        self.persona_oic = Persona.objects.create(honorifico='Ing.', nombre='María', apellido='Fernández')

        self.personal_director = Personal.objects.create(estado=1, id_oic=self.direccion_oic, id_persona=self.persona_director)
        self.personal_judc = Personal.objects.create(estado=1, id_oic=self.direccion_oic, id_persona=self.persona_judc)
        self.personal_titular = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_titular)
        self.personal_oic = Personal.objects.create(estado=1, id_oic=self.oic, id_persona=self.persona_oic)

        CargoPersonal.objects.create(nombre='Director', id_tipo_cargo=TipoCargo.objects.get(id=1), id_personal=self.personal_director)
        CargoPersonal.objects.create(nombre='JUDC', id_tipo_cargo=TipoCargo.objects.get(id=2), id_personal=self.personal_judc)
        CargoPersonal.objects.create(nombre='Titular', id_tipo_cargo=TipoCargo.objects.get(id=6), id_personal=self.personal_titular)
        CargoPersonal.objects.create(nombre='Personal OIC', id_tipo_cargo=TipoCargo.objects.get(id=7), id_personal=self.personal_oic)

    def test_minuta_mes_view_post(self):
        mes = 3
        self.url = reverse('minuta_mes', args=[self.actividad.id, mes])
        # Siempre se preparan previamente datos en el metodo get antes de pasar al post
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)

        post_data = {
            'estado-A1': '4',
            'comentario-A1': 'Comentario actualizado B0',
            'estado-A2': '2',
            'comentario-A2': 'Comentario actualizado B1',
            'fecha': '2024-09-25',
            'JUDC': self.personal_judc.id,
            'personal': self.personal_oic.id,
            'inicio': "2024-09-26T14:30",
            'fin': "2024-09-26T14:30"
        }

        # Realiza la solicitud POST con los datos del formulario
        response = self.client.post(self.url, data=post_data)

        # Verifica que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)

        # Si la vista genera un archivo o realiza una acción similar
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertIn('attachment; filename=', response['Content-Disposition'])

        # Verifica el tipo MIME del archivo generado (si aplica)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Verifica que el archivo tenga algún contenido
        self.assertGreater(len(response.content), 0)

        # Verifica que los conceptos de la minuta mensual se actualizaron en la base de datos
        concepto_actualizado = ConceptoMinuta.objects.get(clave='1', id_minuta=Minuta.objects.get(id_actividad_fiscalizacion=self.actividad), tipo_concepto=1)
        self.assertEqual(concepto_actualizado.comentario, 'Comentario actualizado B0')


class PerfilViewTests(LoggedIn):

    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user(username='testuser2', password='12345')
        self.url = reverse('perfil')

    def test_perfil_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_perfil_view_post_successful_profile_update(self):
        post_data = {
            'username': 'new_username',
            'first_name': 'NuevoNombre',
            'last_name': 'NuevoApellido',
            'password': '12345',  # Contraseña actual correcta
            'new_password': ''    # No se actualiza la contraseña
        }

        # Realiza la solicitud POST
        response = self.client.post(self.url, data=post_data)

        # Verifica que la respuesta redirige a la vista de perfil
        self.assertRedirects(response, self.url)

        # Verifica que el usuario ha sido actualizado
        user_actualizado = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_actualizado.username, 'new_username')
        self.assertEqual(user_actualizado.first_name, 'NuevoNombre')
        self.assertEqual(user_actualizado.last_name, 'NuevoApellido')

        # Verifica que no se cambió la contraseña
        self.assertTrue(self.client.login(username='new_username', password='12345'))

    def test_perfil_view_post_successful_password_update(self):
        post_data = {
            'username': 'testuser',
            'first_name': 'NuevoNombre',
            'last_name': 'NuevoApellido',
            'password': '12345',         # Contraseña actual correcta
            'new_password': 'new_pass'   # Se actualiza la contraseña
        }

        # Realiza la solicitud POST
        response = self.client.post(self.url, data=post_data)

        # Verifica que la respuesta redirige a la vista de perfil
        self.assertRedirects(response, self.url)

        # Verifica que el usuario ha sido actualizado
        user_actualizado = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_actualizado.first_name, 'NuevoNombre')
        self.assertEqual(user_actualizado.last_name, 'NuevoApellido')

        # Verifica que la contraseña se ha actualizado
        self.assertTrue(self.client.login(username='testuser', password='new_pass'))

    def test_perfil_view_post_wrong_current_password(self):
        post_data = {
            'username': 'testuser',
            'first_name': 'NuevoNombre',
            'last_name': 'NuevoApellido',
            'password': 'wrong_password',  # Contraseña incorrecta
            'new_password': 'new_pass'
        }

        # Realiza la solicitud POST
        response = self.client.post(self.url, data=post_data)

        # Verifica que la vista regresa un error de contraseña incorrecta
        self.assertEqual(response.status_code, 200)
        self.assertIn('La contraseña es incorrecta.', response.content.decode())

        # Verifica que el usuario no se actualizó
        user_no_actualizado = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_no_actualizado.first_name, '')

    def test_perfil_view_post_repited_username(self):
        post_data = {
            'username': 'username2',
            'first_name': '',
            'last_name': '',
            'password': '12345',  # Contraseña actual correcta
            'new_password': ''  # No se actualiza la contraseña
        }

        # Realiza la solicitud POST
        response = self.client.post(self.url, data=post_data)

        # Verifica que la respuesta redirige a la vista de perfil
        self.assertRedirects(response, self.url)

        # Verifica que el usuario no ha sido actualizado
        user_actualizado = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_actualizado.username, 'username2')

        # Verifica que no se cambió la contraseña
        self.assertTrue(self.client.login(username='username', password='12345'))

        # Verifica que se da un mensaje de advertencia al usuario
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('El nombre de usuario "username2" ya está en uso. Elige otro.', [str(msg) for msg in messages])

import datetime
import os
import re
from difflib import SequenceMatcher
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from num2words import num2words

from OICSec.forms import AuditoriaForm, ControlForm, IntervencionForm, PersonaForm, CargoPersonalForm, CrearTitularForm
from OICSec.funcs.Actividad import get_actividades
from OICSec.funcs.Cedula import SupervisionData, ConceptosLista, Concepto
from OICSec.funcs.Cedula import cedula as create_cedula
from OICSec.funcs.Minuta import create_revision, minuta as create_minuta_doc
from OICSec.funcs.PAA import extract_paa
from OICSec.funcs.PACI import extract_paci
from OICSec.funcs.PINT import extract_pint
from OICSec.models import *


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña invalidos')
            return render(request, 'login.html')
    else:
        if request.user.is_authenticated:
            return redirect('home')
        else:
            # Si no está autenticado, renderizar la página de inicio de sesión
            return render(request, 'login.html')


@login_required
def home_view(request):
    return render(request, 'home.html')


def convert_to_date(date_str):
    try:
        if date_str:
            return datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
        else:
            return None
    except ValueError:
        return None


@login_required
def get_filtered_objects(request, model, template_name):
    mapping = {
        Auditoria: "auditorias",
        ControlInterno: "controles_internos",
        Intervencion: "intervenciones",
        ActividadFiscalizacion: "actividad_fiscalizacion"
    }
    mode = mapping.get(model) == 'actividad_fiscalizacion'
    if mode:
        oics_name_query = 'id_oic__nombre'
        order_query = 'trimestre'
    else:
        oics_name_query = 'id_actividad_fiscalizacion__id_oic__nombre'
        order_query = 'id_actividad_fiscalizacion__anyo'

    nombres_oics = model.objects.values_list(oics_name_query, flat=True).distinct()
    lista_oics = Oic.objects.filter(nombre__in=nombres_oics).distinct()
    lista_anyos = ActividadFiscalizacion.objects.values('anyo').distinct()

    oic_id = request.GET.get('oic_id')
    anyo = request.GET.get('anyo')

    if mode:
        if oic_id and anyo:
            objects = model.objects.filter(id_oic=oic_id,
                                           anyo=anyo)
        elif oic_id:
            objects = model.objects.filter(id_oic=oic_id)
        elif anyo:
            objects = model.objects.filter(anyo=anyo)
        else:
            objects = model.objects.all()
    else:
        if oic_id and anyo:
            objects = model.objects.filter(id_actividad_fiscalizacion__id_oic=oic_id,
                                           id_actividad_fiscalizacion__anyo=anyo)
        elif oic_id:
            objects = model.objects.filter(id_actividad_fiscalizacion__id_oic=oic_id)
        elif anyo:
            objects = model.objects.filter(id_actividad_fiscalizacion__anyo=anyo)
        else:
            objects = model.objects.all()

    paginator = Paginator(objects.order_by(order_query), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'lista_oics': lista_oics,
        'lista_anyos': lista_anyos,
        'oic_id': oic_id,
        'anyo': anyo,
    }

    context.update({mapping.get(model): objects})

    return render(request, template_name, context)


@login_required
def auditorias_view(request):
    return get_filtered_objects(request, Auditoria, 'auditorias.html')


@login_required
def control_interno_view(request):
    return get_filtered_objects(request, ControlInterno, 'control_interno.html')


@login_required
def intervenciones_view(request):
    return get_filtered_objects(request, Intervencion, 'intervenciones.html')


@login_required
def handle_detail_view(request, model, form_class, object_id, template_name):
    obj = get_object_or_404(model, pk=object_id)
    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, template_name, {
                'form': form,
                'result': 'result',
                'object_id': object_id
            })
        else:
            return render(request, template_name, {
                'form': form,
                'error': form.errors,
                'object_id': object_id
            })
    else:
        form = form_class(instance=obj)
        return render(request, template_name, {'form': form, 'object_id': object_id})


@login_required
def auditoria_detalle_view(request, auditoria_id):
    return handle_detail_view(request, Auditoria, AuditoriaForm, auditoria_id, 'auditoria_detalle.html')


@login_required
def control_interno_detalle_view(request, control_interno_id):
    return handle_detail_view(request, ControlInterno, ControlForm, control_interno_id, 'control_detalle.html')


@login_required
def intervencion_detalle_view(request, intervencion_id):
    return handle_detail_view(request, Intervencion, IntervencionForm, intervencion_id, 'intervencion_detalle.html')


@login_required
def upload_paa_view(request):
    lista_oics = Oic.objects.all()

    if request.method == 'POST':
        return handle_post_request(request, lista_oics)
    elif request.method == 'GET':
        return render(request, 'upload_paa.html', {'lista_oics': lista_oics})


@login_required
def handle_post_request(request, lista_oics):
    excel_file = request.FILES.get('excel_file')
    try:
        data = extract_paa(excel_file)
        if data is None:
            return render_error(request, lista_oics, 'Error al procesar el archivo Excel | Nombre de error: '
                                                     'None-results | Consulte manual de usuario para más información.')

        with transaction.atomic():
            process_excel_data(data, lista_oics)

        return render(request, 'upload_paa.html', {
            'excel_processing_result': data,
            'lista_oics': lista_oics,
        })

    except Exception as e:
        return render_error(request, lista_oics,
                            f'Error al procesar el archivo Excel | Nombre de error: {str(e)} | Consulte manual de '
                            f'usuario para más información.')


@login_required
def render_error(request, lista_oics, error_message):
    return render(request, 'upload_paa.html', {
        'excel_processing_error': error_message,
        'lista_oics': lista_oics,
    })


def process_excel_data(data, lista_oics):
    for excel_processing_result in data:
        similar_oic = find_most_similar_oic(excel_processing_result[0], lista_oics)

        for auditoria_data in excel_processing_result[1]:
            actividad_fiscalizacion = get_or_create_actividad_fiscalizacion(
                auditoria_data['Año'], auditoria_data['Trimestre'], similar_oic)

            auditoria = create_auditoria(auditoria_data, actividad_fiscalizacion)

            create_conceptos_cedula(auditoria.id_cedula)


def find_most_similar_oic(excel_oic_name, lista_oics):
    max_similarity = 0
    similar_oic = None
    for oic in lista_oics:
        similarity = SequenceMatcher(None, excel_oic_name, oic.nombre).ratio()
        if similarity > max_similarity:
            max_similarity = similarity
            similar_oic = oic
    return similar_oic


def get_or_create_actividad_fiscalizacion(anyo, trimestre, oic):
    actividad_fiscalizacion, created = ActividadFiscalizacion.objects.get_or_create(
        anyo=anyo,
        trimestre=trimestre,
        id_oic=oic
    )
    return actividad_fiscalizacion


def create_auditoria(auditoria_data, actividad_fiscalizacion):
    materia_obj = Materia.objects.get(id=auditoria_data["Materia"])
    programacion_obj = Programacion.objects.get(id=auditoria_data["Programacion"])
    enfoque_obj = Enfoque.objects.get(id=auditoria_data["Enfoque"])
    temporalidad_obj = Temporalidad.objects.get(id=auditoria_data["Temporalidad"])
    cedula_obj = Cedula.objects.create()
    auditoria = Auditoria.objects.create(
        denominacion=auditoria_data["Denominacion"],
        numero=auditoria_data["Numero"],
        objetivo=auditoria_data["Objetivo"],
        alcance=auditoria_data["Alcance"],
        ejercicio=auditoria_data["Ejercicio"],
        unidad=auditoria_data["Unidad"],
        id_actividad_fiscalizacion=actividad_fiscalizacion,
        id_materia=materia_obj,
        id_programacion=programacion_obj,
        id_enfoque=enfoque_obj,
        id_temporalidad=temporalidad_obj,
        id_cedula=cedula_obj
    )
    return auditoria


def create_conceptos_cedula(cedula):
    ConceptoCedula.objects.bulk_create([
        ConceptoCedula(celda=str(i), id_cedula=cedula)
        for i in range(60)
    ])


@login_required
def upload_paci_view(request):
    lista_oics = Oic.objects.all()

    similar_oic = None

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        try:
            data = extract_paci(excel_file)
            if data is None:
                return render(request, 'upload_paci.html', {
                    'excel_processing_error': 'Error al procesar el archivo Excel | Nombre de error: None-results | '
                                              'Consulte manual de usuario para mas información.',
                    'lista_oics': lista_oics, 'similar_oic': similar_oic})
            else:
                for excel_processing_result in data:
                    max_similarity = 0
                    for oic in lista_oics:
                        similarity = SequenceMatcher(None, excel_processing_result[0], oic.nombre).ratio()
                        if similarity > max_similarity:
                            max_similarity = similarity
                            similar_oic = oic

                    oic_selected = similar_oic if similar_oic else None
                    for control_data in excel_processing_result[1]:
                        # Se verifica que hay actividad de fiscalización
                        actividad_fiscalizacion = ActividadFiscalizacion.objects.filter(
                            anyo=control_data['Año'],
                            trimestre=control_data['Trimestre'],
                            id_oic=oic_selected
                        ).first()
                        # Si no existe, se crea una actividad de fiscalización
                        if not actividad_fiscalizacion:
                            actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
                                anyo=control_data['Año'],
                                trimestre=control_data['Trimestre'],
                                id_oic=oic_selected
                            )

                        # Se crea un control interno nuevo con la actividad de fiscalización
                        tipo_revision_obj = None
                        programa_revision_obj = None
                        if control_data["tipo_revision"]:
                            tipo_revision_obj = TipoRevision.objects.get(id=control_data["tipo_revision"])
                        if control_data["programa_revision"]:
                            programa_revision_obj = ProgramaRevision.objects.get(id=control_data["programa_revision"])

                        cedula_obj = Cedula.objects.create()
                        ControlInterno.objects.create(
                            numero=control_data["Numero"],
                            area=control_data["Area"],
                            denominacion=control_data["Denominacion"],
                            objetivo=control_data["Objetivo"],
                            id_actividad_fiscalizacion=actividad_fiscalizacion,
                            id_tipo_revision=tipo_revision_obj,
                            id_programa_revision=programa_revision_obj,
                            id_cedula=cedula_obj
                        )

                        for i in range(55):
                            ConceptoCedula.objects.create(
                                celda=str(i),
                                estado=None,
                                comentario=None,
                                id_cedula=cedula_obj
                            )

                return render(request, 'upload_paci.html',
                              {'excel_processing_result': data,
                               'lista_oics': lista_oics,
                               'similar_oic': similar_oic})
        except Exception as e:
            excel_processing_error = (f'Error al procesar el archivo Excel | Nombre de error: {str(e)} | Consulte '
                                      f'manual de usuario para mas información')
            return render(request, 'upload_paa.html',
                          {'excel_processing_error': excel_processing_error, 'lista_oics': lista_oics,
                           'similar_oic': similar_oic})

    if request.method == 'GET':
        return render(request, 'upload_paci.html')


def clean_oic_text(organo: str):
    phrases_to_remove = [
        'órgano interno de control en',
        'de la ciudad de méxico'
    ]

    text = organo.lower()

    for phrase in phrases_to_remove:
        text = re.sub(re.escape(phrase), '', text)

    return text.strip()


@login_required
def upload_pint_view(request):
    lista_oics = Oic.objects.all()
    similar_oic = None
    context = {
        'lista_oics': lista_oics,
        'similar_oic': similar_oic
    }
    word_result = 'Se procesaron los siguientes archivos'
    result_band = False
    word_error = 'Hubo un error al procesar los archivos'
    error_band = False

    if request.method == 'POST':
        word_files = request.FILES.getlist('word_files')
        if not word_files:
            context.update(
                {
                    'word_processing_error': 'Error al procesar los archivos | Nombre de error: None-files | '
                                             'Consulte manual de usuario para más información.'
                }
            )
            return render(request, 'upload_pint.html', context=context)

        try:
            for word_file in word_files:
                word_processing_result = extract_pint(word_file)
                if word_processing_result is None:
                    word_error += f'\n{word_file.name}'
                    error_band = True
                else:
                    word_result += f'\n{word_file.name}'
                    result_band = True
                    max_similarity = 0
                    for oic in lista_oics:
                        similarity = SequenceMatcher(None, clean_oic_text(word_processing_result.get('Ente Público')),
                                                     oic.nombre).ratio()
                        if similarity > max_similarity:
                            max_similarity = similarity
                            similar_oic = oic
                    oic_selected = similar_oic if similar_oic else None

                    # Verifica que hay actividad de fiscalización
                    actividad_fiscalizacion = ActividadFiscalizacion.objects.filter(
                        anyo=word_processing_result['Año'],
                        trimestre=word_processing_result['Trimestre'],
                        id_oic=oic_selected
                    ).first()
                    # Si no existe, crea una actividad de fiscalización
                    if not actividad_fiscalizacion:
                        actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
                            anyo=word_processing_result['Año'],
                            trimestre=word_processing_result['Trimestre'],
                            id_oic=oic_selected
                        )

                    # Crea una intervención nueva con la actividad de fiscalización
                    tipo_intervencion_obj = None
                    if word_processing_result["Clave"]:
                        tipo_intervencion_obj = TipoIntervencion.objects.get(clave=word_processing_result["Clave"])

                    cedula_obj = Cedula.objects.create()
                    Intervencion.objects.create(
                        unidad=word_processing_result.get('Área'),
                        numero=word_processing_result.get('Numero'),
                        denominacion=word_processing_result.get('Denominación'),
                        ejercicio=word_processing_result.get('Ejercicio'),
                        alcance=word_processing_result.get('Alcance y periodo'),
                        antecedentes=word_processing_result.get('Antecedentes'),
                        fuerza_auditores=word_processing_result.get('Auditores'),
                        fuerza_responsables=word_processing_result.get('Responsable'),
                        fuerza_supervision=word_processing_result.get('Supervisión'),
                        inicio=convert_to_date(word_processing_result.get('Inicio')),
                        termino=convert_to_date(word_processing_result.get('Termino')),
                        objetivo=word_processing_result.get('Objetivo'),
                        id_actividad_fiscalizacion=actividad_fiscalizacion,
                        id_tipo_intervencion=tipo_intervencion_obj,
                        id_cedula=cedula_obj
                    )

                    for i in range(54):
                        ConceptoCedula.objects.create(
                            celda=str(i),
                            estado=None,
                            comentario=None,
                            id_cedula=cedula_obj
                        )
            if result_band:
                context.update({'word_processing_result': word_result})
            if error_band:
                context.update({'word_processing_error': word_error})
            return render(request, 'upload_pint.html', context=context)
        except Exception as e:
            word_error = (f'Error al procesar los archivos Word\n Nombre de error: {str(e)} | Consulte '
                          f'el manual de usuario para más información')
            context.update({'word_processing_error': word_error})
            return render(request, 'upload_pint.html', context=context)

    if request.method == 'GET':
        return render(request, 'upload_pint.html', context=context)


@login_required
def delete_auditoria(request, pk):
    auditoria = get_object_or_404(Auditoria, pk=pk)
    auditoria.delete()
    return redirect('auditorias')


@login_required
def delete_intervencion(request, pk):
    intervencion = get_object_or_404(Intervencion, pk=pk)
    intervencion.delete()
    return redirect('intervenciones')


@login_required
def delete_controlinterno(request, pk):
    controlinterno = get_object_or_404(ControlInterno, pk=pk)
    controlinterno.delete()
    return redirect('controlInterno')


def get_cedula_conceptos(model_instance):
    cedula = get_object_or_404(Cedula, pk=model_instance.id_cedula_id)
    conceptos = ConceptoCedula.objects.filter(id_cedula=cedula.id)
    conceptos_dict = {
        concepto.celda: {
            'estado': concepto.estado,
            'comentario': concepto.comentario if concepto.comentario is not None else ''
        }
        for concepto in conceptos
    }
    return cedula, conceptos, conceptos_dict


def update_conceptos(conceptos, request):
    data = []
    for i in range(60):
        estado = request.POST.get(f'estado-{i}') if request.POST.get(f'estado-{i}') != 'Selecciona una opción' else None
        comentario = request.POST.get(f'comentario-{i}')
        # Se actualizan los valores en la base de datos
        try:
            concepto = conceptos.get(celda=str(i))
            concepto.estado = estado
            concepto.comentario = comentario
            concepto.save()
        except ConceptoCedula.DoesNotExist:
            pass
        # Se preparan para la generación del archivo
        data.append((estado, comentario))
    conceptos_lista = ConceptosLista(
        Conceptos=[Concepto(Estado=estado, Comentario=comentario) for estado, comentario in data]
    )
    return conceptos_lista


def get_supervision_data(kind, model_instance, fiscalizacion, request):
    data = None
    if kind == 1:
        materia = model_instance.id_materia.clave
        programacion = model_instance.id_programacion.clave
        enfoque = model_instance.id_enfoque.clave
        temporalidad = model_instance.id_temporalidad.clave
        data = SupervisionData(
            OIC=str(
                model_instance.id_actividad_fiscalizacion.id_oic.nombre)
            if model_instance.id_actividad_fiscalizacion.id_oic.nombre else '',
            Numero=f'A-{model_instance.numero}/{fiscalizacion.anyo}' if all(
                [model_instance.numero, fiscalizacion.anyo]) else '',
            Nombre=str(model_instance.denominacion) if model_instance.denominacion else '',
            Fecha=datetime.datetime.strptime(request.POST.get('fecha'), '%Y-%m-%d').strftime(
                '%d/%m/%Y') if request.POST.get('fecha') else '',
            Clave=(
                f'{materia}-{programacion}-{enfoque}-{temporalidad}'
                if all(
                    [model_instance.id_materia.clave, model_instance.id_programacion.clave,
                     model_instance.id_enfoque.clave, model_instance.id_temporalidad.clave]) else ''),
            Anyo_Trimestre=f'0{fiscalizacion.trimestre}/{fiscalizacion.anyo}' if fiscalizacion.trimestre else '',
            Objetivo=model_instance.objetivo if model_instance.objetivo else '',
            Area=model_instance.unidad if model_instance.unidad else '',
            Ejercicio=model_instance.ejercicio if model_instance.ejercicio else ''
        )
    elif kind == 2:
        clave = 'R' if model_instance.id_tipo_intervencion.clave == 13 else (
            'V' if model_instance.id_tipo_intervencion.clave == 14 else 'O')
        data = SupervisionData(
            OIC=str(
                model_instance.id_actividad_fiscalizacion.id_oic.nombre)
            if model_instance.id_actividad_fiscalizacion.id_oic.nombre else '',
            Numero=f'{clave}-{model_instance.numero}/{fiscalizacion.anyo}',
            Nombre=str(model_instance.denominacion) if model_instance.denominacion else '',
            Fecha=datetime.datetime.strptime(request.POST.get('fecha'), '%Y-%m-%d').strftime(
                '%d/%m/%Y') if request.POST.get('fecha') else '',
            Clave=f'{model_instance.id_tipo_intervencion.clave}',
            Anyo_Trimestre=f'0{fiscalizacion.trimestre}/{fiscalizacion.anyo}' if fiscalizacion.trimestre else '',
            Objetivo=model_instance.objetivo if model_instance.objetivo else '',
            Area=model_instance.unidad if model_instance.unidad else '',
            Ejercicio=model_instance.ejercicio if model_instance.ejercicio else ''
        )
    elif kind == 3:
        data = SupervisionData(
            OIC=str(
                model_instance.id_actividad_fiscalizacion.id_oic.nombre)
            if model_instance.id_actividad_fiscalizacion.id_oic.nombre else '',
            Numero=f'CI {model_instance.numero}/{fiscalizacion.anyo}',
            Nombre=str(model_instance.denominacion) if model_instance.denominacion else '',
            Fecha=datetime.datetime.strptime(request.POST.get('fecha'), '%Y-%m-%d').strftime(
                '%d/%m/%Y') if request.POST.get('fecha') else '',
            Clave=f'{model_instance.id_tipo_revision.clave}-{model_instance.id_programa_revision.clave}',
            Anyo_Trimestre=f'0{fiscalizacion.trimestre}/{fiscalizacion.anyo}' if fiscalizacion.trimestre else '',
            Objetivo=model_instance.objetivo if model_instance.objetivo else '',
            Area=model_instance.area if model_instance.area else '',
            Ejercicio=model_instance.ejercicio if model_instance.ejercicio else ''
        )
    return data


def save_minuta_and_respond(file_path, model_instance):
    archivo = model_instance.id_archivo
    file_name = ''
    if file_path:
        file_name = os.path.basename(file_path)
    if not archivo:
        archivo = Archivo.objects.create(
            archivo=file_path,
            nombre=file_name
        )
        model_instance.id_archivo = archivo
        model_instance.save()

    if file_path:
        # Cargar el archivo y enviarlo como respuesta para descargar
        with open(file_path, 'rb') as file:
            response = HttpResponse(
                file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file_name = os.path.basename(file_path)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        # Manejar el caso en el que no se haya generado el archivo
        return HttpResponse("No se pudo generar la minuta.", status=500)


def save_file_and_respond(file_path, model_instance, data):
    archivo = model_instance.id_archivo
    if not archivo:
        archivo = Archivo.objects.create(
            archivo=file_path,
            nombre=f"Supervision - {data.Numero} - {data.OIC} - {data.Anyo_Trimestre}.xlsx"
        )
        model_instance.id_archivo = archivo
        model_instance.save()

    if file_path:
        # Cargar el archivo y enviarlo como respuesta para descargar
        with open(file_path, 'rb') as file:
            response = HttpResponse(
                file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file_name = os.path.basename(file_path)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        # Manejar el caso en el que no se haya generado el archivo
        return HttpResponse("No se pudo generar la cédula.", status=500)


@login_required
def cedula_view(request, model, id_model):
    mapping = {
        Auditoria: 1,
        Intervencion: 2,
        ControlInterno: 3,
    }
    kind = mapping.get(model)
    model_instance = get_object_or_404(model, pk=id_model)
    fiscalizacion = model_instance.id_actividad_fiscalizacion

    context = {
        'auditoria': model_instance if kind == 1 else None,
        'intervencion': model_instance if kind == 2 else None,
        'control_interno': model_instance if kind == 3 else None,
        'fiscalizacion': fiscalizacion
    }
    if request.method == 'GET':
        _, _, conceptos_dict = get_cedula_conceptos(model_instance)
        context.update({'conceptos': conceptos_dict})
        context.update({'archivo': model_instance.id_cedula.id_archivo})
        return render(request, 'cedula.html', context)

    if request.method == 'POST':
        cedula, conceptos, _ = get_cedula_conceptos(model_instance)
        conceptos_lista = update_conceptos(conceptos, request)
        supervision_data = get_supervision_data(kind, model_instance, fiscalizacion, request)
        if supervision_data:
            # Se guarda en el sistema de archivos
            file_path = create_cedula(kind=kind, data=supervision_data, conceptos=conceptos_lista)
            return save_file_and_respond(file_path, cedula, supervision_data)
        else:
            return HttpResponse("No se pudo generar la cédula.", status=500)


@login_required
def auditoria_cedula_view(request, auditoria_id):
    return cedula_view(request, model=Auditoria, id_model=auditoria_id)


@login_required
def control_cedula_view(request, control_id):
    return cedula_view(request, model=ControlInterno, id_model=control_id)


@login_required
def intervencion_cedula_view(request, intervencion_id):
    return cedula_view(request, model=Intervencion, id_model=intervencion_id)


@login_required
def minuta_view(request, fiscalizacion_id):
    fiscalizacion = get_object_or_404(ActividadFiscalizacion, pk=fiscalizacion_id)
    context = {
        'fiscalizacion': fiscalizacion
    }
    return render(request, 'minuta.html', context)


def get_or_create_minuta_personal(minuta, tipo_personal, cargo_id, oic=None):
    minuta_personal = MinutaPersonal.objects.filter(id_minuta=minuta, tipo_personal=tipo_personal).first()
    if not minuta_personal:
        cargo = TipoCargo.objects.filter(id=cargo_id).first()
        personal_actual = Personal.objects.filter(id_oic=oic, estado=1, cargopersonal__id_tipo_cargo=cargo).first()
        if not personal_actual:
            return 'Error'
        minuta_personal = MinutaPersonal.objects.create(
            tipo_personal=tipo_personal,
            id_minuta=minuta,
            id_personal=personal_actual
        )
    return minuta_personal


def get_personal_list(oic, cargo_id, minuta_personal):
    personal_list = Personal.objects.filter(id_oic=oic, estado=1, cargopersonal__id_tipo_cargo=cargo_id)
    if minuta_personal.id_personal.estado == 0:
        personal_list = (personal_list | Personal.objects.filter(id=minuta_personal.id_personal.id)).distinct()
    return personal_list


def update_conceptos_minuta(request, conceptos, auditoria_band, control_band, intervencion_band):
    estados = {
        '0': 'Cumple',
        '1': 'No cumple',
        '2': 'No aplica',
        '3': 'Pendiente'
    }

    def process_conceptos(conceptos_instance, prefix, count):
        conceptos_list = []
        for i in range(1, count + 1):
            estado = request.POST.get(f'estado-{prefix}{i}') if request.POST.get(
                f'estado-{prefix}{i}') != 'Selecciona una opción' else None
            comentario = request.POST.get(f'comentario-{prefix}{i}') if request.POST.get(
                f'comentario-{prefix}{i}') else ''
            # Se actualizan los valores en la base de datos
            try:
                concepto = conceptos_instance.get(clave=str(i))
                concepto.estatus = estado
                concepto.comentario = comentario
                concepto.save()
            except ConceptoMinuta.DoesNotExist:
                pass
            # Se preparan para la generación del archivo
            conceptos_list.append((estados.get(estado) if estado else '', comentario))
        return None if not conceptos_list else conceptos_list

    # Procesar conceptos por tipo
    auditoria_list = process_conceptos(conceptos.filter(tipo_concepto=1), 'A', 20) if auditoria_band else None
    intervencion_list = process_conceptos(conceptos.filter(tipo_concepto=2), 'I', 25) if intervencion_band else None
    control_list = process_conceptos(conceptos.filter(tipo_concepto=3), 'C', 23) if control_band else None

    revision = create_revision(
        auditoria_values=auditoria_list,
        intervencion_values=intervencion_list,
        control_interno_values=control_list
    )
    return revision


def limpiar_cadena(cadena):
    patron_parentesis = r'\([^)]*\)'
    cadena_sin_parentesis = re.sub(patron_parentesis, '', cadena)
    cadena_limpia = re.sub(r'\s+', ' ', cadena_sin_parentesis).strip()
    return cadena_limpia


def update_data_minuta(request, minuta, mes, actividades):
    # Se borra el anterior personal y se coloca uno nuevo
    MinutaPersonal.objects.filter(id_minuta=minuta, tipo_personal=2).delete()
    id_judc = request.POST.get('JUDC', None)
    judc = get_object_or_404(Personal, id=id_judc)
    MinutaPersonal.objects.create(
        tipo_personal=2,
        id_minuta=minuta,
        id_personal=judc
    )
    MinutaPersonal.objects.filter(id_minuta=minuta, tipo_personal=4).delete()
    id_personal = request.POST.get('personal', None)
    personal = get_object_or_404(Personal, id=id_personal)
    MinutaPersonal.objects.create(
        tipo_personal=4,
        id_minuta=minuta,
        id_personal=personal
    )
    inicio_str = request.POST.get("inicio")
    fin_str = request.POST.get("fin")
    time_inicio = timezone.make_aware(datetime.datetime.strptime(inicio_str, "%Y-%m-%dT%H:%M"))
    time_fin = timezone.make_aware(datetime.datetime.strptime(fin_str, "%Y-%m-%dT%H:%M"))
    if inicio_str:
        minuta.inicio = time_inicio
    if fin_str:
        minuta.fin = time_fin
    minuta.save()
    # Una vez ya teniendo actualizados los datos de la minuta, preparamos los datos para la generacion del archivo
    director = MinutaPersonal.objects.get(id_minuta=minuta, tipo_personal=1).id_personal
    titular = MinutaPersonal.objects.get(id_minuta=minuta, tipo_personal=3).id_personal
    fiscalizacion = minuta.id_actividad_fiscalizacion
    # Se acomodan de acuerdo a la documentacion
    meses_word = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    posicion_word = {
        1: 'primer',
        2: 'segundo',
        3: 'tercero',
        4: 'cuarto'
    }

    lista_actividades, text_numero_actividades = get_actividades_lista(actividades)

    data = [
        num2words(time_inicio.hour, lang='es'),  # P01
        num2words(time_inicio.day, lang='es'),  # P02
        meses_word.get(time_inicio.month),  # P03
        num2words(time_inicio.year, lang='es'),  # P04
        "el/la",  # P05
        director.id_persona.honorifico,  # P06
        f'{director.id_persona.nombre} {director.id_persona.apellido}',  # P07
        CargoPersonal.objects.get(id_personal=director).nombre,  # P08
        "el/la",  # P09
        judc.id_persona.honorifico,  # P10
        f'{judc.id_persona.nombre} {judc.id_persona.apellido}',  # P11
        CargoPersonal.objects.get(id_personal=judc).nombre,  # P12
        "el/la",  # P13
        titular.id_persona.honorifico,  # P14
        f'{titular.id_persona.nombre} {titular.id_persona.apellido}',  # P15
        CargoPersonal.objects.get(id_personal=titular).nombre,  # P16
        "el/la",  # P17
        personal.id_persona.honorifico,  # P18
        f'{personal.id_persona.nombre} {personal.id_persona.apellido}',  # P19
        CargoPersonal.objects.get(id_personal=personal).nombre,  # P20
        num2words(mes, lang='es'),  # P21
        posicion_word.get(fiscalizacion.trimestre),  # P22
        num2words(fiscalizacion.anyo, lang='es'),  # P23
        limpiar_cadena(fiscalizacion.id_oic.nombre),  # P24
        text_numero_actividades,  # P25
        lista_actividades,  # P26
        num2words(time_fin.hour, lang='es'),  # P27
        num2words(time_fin.day, lang='es'),  # P28
        meses_word.get(time_fin.month),  # P29
        time_fin.year  # P30
    ]

    # Caso de mes 1 y 2
    if mes == 1:
        data.append('DOCUMENTACIÓN')  # P31
        data.append('la documentacion')  # P32
    elif mes == 2:
        data.append('PAPELES DE TRABAJO')  # P31
        data.append('los papeles de trabajo')  # P32

    return data


def get_actividades_lista(actividades):
    lista_actividades = ''
    numero_actividades = len(actividades)
    for n in range(numero_actividades):
        tipo = actividades[n].tipo
        denominacion = actividades[n].denominacion
        numero = actividades[n].numero
        articulo = "el" if tipo == "control interno" else "la"
        articulo_final = "o" if tipo == "control interno" else "a"
        lista_actividades += f"{articulo} {tipo} numero {numero} denominad{articulo_final} {denominacion}"
        if n == numero_actividades - 2:
            lista_actividades += " y "
        elif n < numero_actividades - 2:
            lista_actividades += ", "
    lista_actividades += " misma"
    if numero_actividades > 1:
        lista_actividades += "s que se ejecutan"
    else:
        lista_actividades += " que se ejecuta"
    text_numero_actividades = 'está'
    if numero_actividades > 1:
        text_numero_actividades += 'n'
        numero_text = num2words(numero_actividades, lang='es')
    else:
        numero_text = 'una'
    text_numero_actividades += f' ejecutando {numero_text} actividad'
    if numero_actividades > 1:
        text_numero_actividades += 'es'
    return lista_actividades, text_numero_actividades


@login_required
def minuta_mes_view(request, fiscalizacion_id, mes):
    fiscalizacion = get_object_or_404(ActividadFiscalizacion, pk=fiscalizacion_id)
    auditoria = Auditoria.objects.filter(id_actividad_fiscalizacion=fiscalizacion)
    intervencion = Intervencion.objects.filter(id_actividad_fiscalizacion=fiscalizacion)
    control_interno = ControlInterno.objects.filter(id_actividad_fiscalizacion=fiscalizacion)
    oic = fiscalizacion.id_oic
    auditoria_band = auditoria.first() is not None
    intervencion_band = intervencion.first() is not None
    control_band = control_interno.first() is not None

    minuta = Minuta.objects.filter(id_actividad_fiscalizacion=fiscalizacion, mes=mes).first()
    if not minuta:
        minuta = Minuta.objects.create(
            inicio=None,
            fin=None,
            id_actividad_fiscalizacion=fiscalizacion,
            id_archivo=None,
            mes=mes
        )

    actividades = get_actividades(auditoria, intervencion, control_interno)
    trimestre_opts = {1: 'primer', 2: 'segundo', 3: 'tercer', 4: 'cuarto'}
    trimestre_word = trimestre_opts.get(fiscalizacion.trimestre)
    anyo = fiscalizacion.anyo

    if request.method == 'POST':
        # Actualizar la minuta con los datos del formulario
        data = update_data_minuta(request, minuta, mes, actividades)
        revision = None
        kind = True
        if mes == 3:
            kind = False
            conceptos, _ = get_minuta_conceptos(minuta)
            revision = update_conceptos_minuta(request, conceptos, auditoria_band, control_band, intervencion_band)
        output_path = create_minuta_doc(
            data=data,
            kind=kind,
            oic=fiscalizacion.id_oic.nombre,
            mes=mes,
            trimestre=str(fiscalizacion.trimestre),
            anyo=str(anyo),
            revision=revision
        )
        return save_minuta_and_respond(output_path, minuta)

    else:
        minuta_inicio = minuta.inicio if minuta.inicio else datetime.datetime.now()
        minuta_fin = minuta.fin if minuta.fin else datetime.datetime.now()

        minuta_director = get_or_create_minuta_personal(minuta, 1, 1)
        minuta_judc = get_or_create_minuta_personal(minuta, 2, 2)
        minuta_titular = get_or_create_minuta_personal(minuta, 3, 6, oic)
        minuta_personaloic = get_or_create_minuta_personal(minuta, 4, 7, oic)
        if minuta_director == 'Error' or minuta_judc == 'Error':
            messages.error(request,
                           'Hubo un error con el personal de la dirección, verifica que estos esten registrados '
                           'correctamente.')
            return redirect('personal_direccion')
        if minuta_titular == 'Error' or minuta_personaloic == 'Error':
            messages.error(request,
                           'Hubo un error con el personal del OIC, verifica que estos esten registrados correctamente.')
            return redirect('personal_oic', oic.id)
        judc = get_personal_list(None, 2, minuta_judc)
        personal = get_personal_list(oic, 7, minuta_personaloic)

        context = {
            'mes': mes,
            'actividades': actividades,
            'oic': fiscalizacion.id_oic.nombre,
            'trimestre_word': trimestre_word,
            'anyo': anyo,
            'director': minuta_director.id_personal.id_persona,
            'titular': minuta_titular.id_personal.id_persona,
            'JUDC_actual': minuta_judc.id_personal.id_persona,
            'personal_actual': minuta_personaloic.id_personal.id_persona,
            'JUDC': judc,
            'personal': personal,
            'minuta_inicio': minuta_inicio,
            'minuta_fin': minuta_fin,
            'auditoria_band': auditoria_band,
            'intervencion_band': intervencion_band,
            'control_band': control_band
        }

        if mes == 3:
            _, conceptos_dic = get_minuta_conceptos(minuta)
            # Crea conceptos si no los hay y los agrega al dict de ser necesario
            band = False
            # Si no hay conceptos de la actividad de fiscalizacion se necesitan crearlos
            if auditoria_band:
                if conceptos_dic.get('Auditoria') == {}:
                    band = True
                    for i in range(1, 21):
                        ConceptoMinuta.objects.create(
                            clave=str(i),
                            estatus=None,
                            comentario=None,
                            tipo_concepto=1,
                            id_minuta=minuta
                        )
            if intervencion_band:
                if conceptos_dic.get('Intervención') == {}:
                    band = True
                    for i in range(1, 26):
                        ConceptoMinuta.objects.create(
                            clave=str(i),
                            estatus=None,
                            comentario=None,
                            tipo_concepto=2,
                            id_minuta=minuta
                        )
            if control_band:
                if conceptos_dic.get('Control') == {}:
                    band = True
                    for i in range(1, 24):
                        ConceptoMinuta.objects.create(
                            clave=str(i),
                            estatus=None,
                            comentario=None,
                            tipo_concepto=3,
                            id_minuta=minuta
                        )
            # Se reescriben en caso de que se hayan generado nuevos conceptos
            if band:
                _, conceptos_dic = get_minuta_conceptos(minuta)
            context.update({'conceptos': conceptos_dic})
        context.update({'archivo': minuta.id_archivo})
        return render(request, 'minuta_mes.html', context)


def get_minuta_conceptos(minuta):
    conceptos = ConceptoMinuta.objects.filter(id_minuta=minuta.id)
    conceptos_dict = {
        'Auditoria': {},
        'Intervención': {},
        'Control': {}
    }
    for concepto in conceptos:
        tipo = dict(ConceptoMinuta.TIPO_CHOICES).get(concepto.tipo_concepto)
        if tipo:
            conceptos_dict[tipo][concepto.clave] = {
                'estado': concepto.estatus,
                'comentario': concepto.comentario if concepto.comentario is not None else ''
            }

    return conceptos, conceptos_dict


@login_required
def perfil_view(request):
    if request.method == 'POST':
        # Se obtiene el usuario autenticado
        user = request.user
        # Se obtienen los valores del formulario
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')

        # Verificar contraseñas
        user = authenticate(username=user.username, password=password)
        if user is not None:  # La contraseña actual es correcta
            if username != user.username:
                if User.objects.filter(username=username).exists():
                    return render(request, 'profile.html', {
                        'duplicated_profile': f'El nombre de usuario "{username}" ya se encuentra en uso, favor de '
                                              f'escoger otro.'})
            # Se verifica si se han ingresado una nueva contraseña y confirmar contraseña
            if new_password:
                # Guardar nueva contraseña
                user.set_password(new_password)
                user.save()
                # Actualizar los datos del usuario
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                # Se actualiza la sesión de autenticación
                update_session_auth_hash(request, user)
                return render(request, 'profile.html', {'success_password': 'Perfil actualizado correctamente.'})
            else:
                # Se actualizan unicamente los datos del usuario
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                return render(request, 'profile.html', {'success_password': 'Perfil actualizado correctamente.'})
        else:
            # Contraseña actual incorrecta
            return render(request, 'profile.html', {'error_password': 'La contraseña es incorrecta.'})
    else:
        return render(request, 'profile.html')


@login_required
def personal_view(request):
    return render(request, 'personal.html')


@login_required
def oics_view(request):
    oics = Oic.objects.all()
    return render(request, 'oics.html', {'oics': oics})


@login_required
def personal_oic_view(request, oic_id):
    oic = get_object_or_404(Oic, pk=oic_id)
    personal = Personal.objects.filter(id_oic=oic_id, estado=1)

    try:
        titular = CargoPersonal.objects.get(id_personal__in=personal, id_tipo_cargo=6).id_personal
    except CargoPersonal.DoesNotExist:
        titular = None

    if titular:
        personal = personal.exclude(id=titular.id)

    context = {
        'oic': oic,
        'titular': titular,
        'personal': personal
    }

    return render(request, 'personal_oic.html', context)


@login_required
def personal_direccion_view(request):
    personal = Personal.objects.filter(id_oic=None, estado=1)
    try:
        director = CargoPersonal.objects.get(id_personal__in=personal, id_tipo_cargo=1).id_personal
    except CargoPersonal.DoesNotExist:
        director = None

    if director:
        personal = personal.exclude(id=director.id)

    context = {
        'director': director,
        'personal': personal
    }

    return render(request, 'personal_direccion.html', context)


@login_required
def editar_titular_view(request, personal_id):
    personal = get_object_or_404(Personal, id=personal_id)
    persona = personal.id_persona

    # Obtener el cargo personal con id_tipo_cargo igual a 6
    tipo_cargo_titular = get_object_or_404(TipoCargo, id=6)
    cargo_personal_titular = get_object_or_404(CargoPersonal, id_personal=personal, id_tipo_cargo=tipo_cargo_titular)

    if request.method == 'POST':
        if 'persona_form' in request.POST:
            persona_form = PersonaForm(request.POST, instance=persona)
            if persona_form.is_valid():
                persona_form.save()
                return redirect('editar_titular_view', personal_id=personal_id)
        elif 'cargo_form' in request.POST:
            cargo_form = CargoPersonalForm(request.POST, instance=cargo_personal_titular)
            if cargo_form.is_valid():
                cargo_form.save()

                # Actualizar el nombre en el resto de cargos del personal
                CargoPersonal.objects.filter(id_personal=personal).update(nombre=cargo_form.cleaned_data['nombre'])

                return redirect('editar_titular_view', personal_id=personal_id)
    else:
        persona_form = PersonaForm(instance=persona)
        cargo_form = CargoPersonalForm(instance=cargo_personal_titular)

        tipo_cargos = TipoCargo.objects.filter(id__in=[3, 4, 5])
        cargos_asignados = CargoPersonal.objects.filter(id_personal=personal).values_list('id_tipo_cargo', flat=True)

        return render(request, 'editar_titular.html', {
            'persona_form': persona_form,
            'cargo_form': cargo_form,
            'personal': personal,
            'tipo_cargos': tipo_cargos,
            'cargos_asignados': list(cargos_asignados),
        })


@login_required
def editar_director_view(request, personal_id):
    personal = get_object_or_404(Personal, id=personal_id)
    persona = personal.id_persona

    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, instance=persona)
        if persona_form.is_valid():
            persona_form.save()
            return redirect('editar_director', personal_id=personal_id)
    else:
        persona_form = PersonaForm(instance=persona)

    return render(request, 'editar_director.html', {
        'persona_form': persona_form,
        'personal': personal
    })


@login_required
def asignar_cargo_titular(request, personal_id, tipo_cargo_id):
    personal = get_object_or_404(Personal, id=personal_id)
    tipo_cargo = get_object_or_404(TipoCargo, id=tipo_cargo_id)

    tipo_cargo_titular = get_object_or_404(TipoCargo, id=6)
    cargo_personal_titular = get_object_or_404(CargoPersonal, id_personal=personal, id_tipo_cargo=tipo_cargo_titular)

    cargo_personal, created = CargoPersonal.objects.get_or_create(id_personal=personal, id_tipo_cargo=tipo_cargo,
                                                                  defaults={'nombre': cargo_personal_titular.nombre})

    if not created:
        cargo_personal.delete()
    else:
        cargo_personal.nombre = cargo_personal_titular.nombre
        cargo_personal.save()

    return redirect('editar_titular_view', personal_id=personal_id)


@login_required
def eliminar_personal_view(request, personal_id, redirect_url, *args, **kwargs):
    personal = get_object_or_404(Personal, id=personal_id)
    personal.estado = 0
    personal.save()
    return redirect(redirect_url, *args, **kwargs)


@login_required
def eliminar_titular_view(request, personal_id):
    personal = get_object_or_404(Personal, id=personal_id)
    return eliminar_personal_view(request, personal_id, 'personal_oic', personal.id_oic_id)


@login_required
def eliminar_director_view(request, personal_id):
    return eliminar_personal_view(request, personal_id, 'personal_direccion')


@login_required
def eliminar_personal_oic_view(request, personal_id):
    personal = get_object_or_404(Personal, id=personal_id)
    return eliminar_personal_view(request, personal_id, 'personal_oic', personal.id_oic_id)


@login_required
def eliminar_personal_direccion_view(request, personal_id):
    return eliminar_personal_view(request, personal_id, 'personal_direccion')


@login_required
def editar_personal_view(request, personal_id):
    personal = get_object_or_404(Personal, id=personal_id)
    persona = personal.id_persona

    # Obtener todos los cargos asignados al personal
    cargos_asignados = CargoPersonal.objects.filter(id_personal=personal)

    if request.method == 'POST':
        if 'persona_form' in request.POST:
            persona_form = PersonaForm(request.POST, instance=persona)
            if persona_form.is_valid():
                persona_form.save()
                return redirect('editar_personal_view', personal_id=personal_id)
        elif 'cargo_form' in request.POST:
            cargo_form = CargoPersonalForm(request.POST)
            if cargo_form.is_valid():
                cargo_nombre = cargo_form.cleaned_data['nombre']
                cargos_asignados.update(nombre=cargo_nombre)
                return redirect('editar_personal_view', personal_id=personal_id)
    else:
        persona_form = PersonaForm(instance=persona)
        initial = {'nombre': cargos_asignados.first().nombre} if cargos_asignados.exists() else {}
        cargo_form = CargoPersonalForm(initial=initial)

        tipo_cargos = TipoCargo.objects.filter(id__in=[3, 4, 5, 7])
        cargos_asignados_ids = cargos_asignados.values_list('id_tipo_cargo', flat=True)

        return render(request, 'editar_personal.html', {
            'persona_form': persona_form,
            'cargo_form': cargo_form,
            'personal': personal,
            'tipo_cargos': tipo_cargos,
            'cargos_asignados': list(cargos_asignados_ids),
        })


@login_required
def editar_personal_direccion_view(request, personal_id):
    personal = get_object_or_404(Personal, id=personal_id)
    persona = personal.id_persona

    # Obtener todos los cargos asignados al personal
    cargos_asignados = CargoPersonal.objects.filter(id_personal=personal)

    if request.method == 'POST':
        if 'persona_form' in request.POST:
            persona_form = PersonaForm(request.POST, instance=persona)
            if persona_form.is_valid():
                persona_form.save()
                return redirect('editar_personal_direccion_view', personal_id=personal_id)
        elif 'cargo_form' in request.POST:
            cargo_form = CargoPersonalForm(request.POST)
            if cargo_form.is_valid():
                cargo_nombre = cargo_form.cleaned_data['nombre']
                cargos_asignados.update(nombre=cargo_nombre)
                return redirect('editar_personal_direccion_view', personal_id=personal_id)
    else:
        persona_form = PersonaForm(instance=persona)
        initial = {'nombre': cargos_asignados.first().nombre} if cargos_asignados.exists() else {}
        cargo_form = CargoPersonalForm(initial=initial)

        return render(request, 'editar_personal_direccion.html', {
            'persona_form': persona_form,
            'cargo_form': cargo_form,
            'personal': personal,
        })


@login_required
def asignar_cargo_personal(request, personal_id, tipo_cargo_id):
    personal = get_object_or_404(Personal, id=personal_id)
    tipo_cargo = get_object_or_404(TipoCargo, id=tipo_cargo_id)

    cargo_personal, created = CargoPersonal.objects.get_or_create(id_personal=personal, id_tipo_cargo=tipo_cargo)

    if not created:
        cargo_personal.delete()
    else:
        existing_cargo = CargoPersonal.objects.filter(id_personal=personal).first()
        if existing_cargo:
            cargo_personal.nombre = existing_cargo.nombre
            cargo_personal.save()

    return redirect('editar_personal_view', personal_id=personal_id)


@login_required
def crear_titular_view(request, oic_id):
    oic = get_object_or_404(Oic, id=oic_id)
    default_cargo_nombre = f'Titular del Órgano Interno de Control en {oic.nombre}'

    if request.method == 'POST':
        titular_form = CrearTitularForm(request.POST)
        if titular_form.is_valid():
            titular = titular_form.save()

            # Buscar y desactivar el titular actual
            tipo_cargo_titular = get_object_or_404(TipoCargo, id=6)
            personal_actual = Personal.objects.filter(id_oic=oic_id, cargopersonal__id_tipo_cargo=tipo_cargo_titular,
                                                      estado=1).first()
            if personal_actual:
                personal_actual.estado = 0
                personal_actual.save()

            # Crear el nuevo personal con el nuevo titular
            nuevo_personal = Personal.objects.create(
                estado=1,
                id_oic_id=oic_id,
                id_persona=titular
            )

            # Obtener el nombre del cargo del formulario
            cargo_nombre = titular_form.cleaned_data['cargo_nombre']

            # Asignar el cargo de titular al nuevo personal
            CargoPersonal.objects.create(
                nombre=cargo_nombre,
                id_tipo_cargo=tipo_cargo_titular,
                id_personal=nuevo_personal
            )

            return redirect('personal_oic', oic_id)

    else:
        # Establecer el valor predeterminado para el campo de nombre del cargo
        titular_form = CrearTitularForm(initial={'cargo_nombre': default_cargo_nombre})

    context = {
        'oic_id': oic_id,
        'titular_form': titular_form
    }
    return render(request, 'crear_titular.html', context)


@login_required
def crear_director_view(request):
    if request.method == 'POST':
        director_form = PersonaForm(request.POST)
        if director_form.is_valid():
            director = director_form.save()

            # Buscar y desactivar el director actual
            tipo_cargo_director = get_object_or_404(TipoCargo, id=1)
            personal_actual = Personal.objects.filter(id_oic=None, cargopersonal__id_tipo_cargo=tipo_cargo_director,
                                                      estado=1).first()
            if personal_actual:
                personal_actual.estado = 0
                personal_actual.save()

            # Crear el nuevo personal con el nuevo titular
            nuevo_personal = Personal.objects.create(
                estado=1,
                id_oic_id=None,
                id_persona=director
            )

            # Asignar el cargo de director al nuevo personal
            CargoPersonal.objects.create(
                nombre='Director de Coordinación de Órganos Internos de Control Sectorial “C”',
                id_tipo_cargo=tipo_cargo_director,
                id_personal=nuevo_personal
            )

            return redirect('personal_direccion')

    else:
        director_form = PersonaForm()

    context = {
        'titular_form': director_form
    }
    return render(request, 'crear_director.html', context)


@login_required
def crear_personal_view(request, oic_id):
    if request.method == 'POST':
        personal_form = PersonaForm(request.POST)
        if personal_form.is_valid():
            personal = personal_form.save()

            # Crear el nuevo personal con el nuevo titular
            Personal.objects.create(
                estado=1,
                id_oic_id=oic_id,
                id_persona=personal
            )

            return redirect('personal_oic', oic_id)

    else:
        personal_form = PersonaForm()

    context = {
        'oic_id': oic_id,
        'titular_form': personal_form
    }
    return render(request, 'crear_personal.html', context)


@login_required
def crear_personal_direccion_view(request):
    if request.method == 'POST':
        personal_form = CrearTitularForm(request.POST)
        if personal_form.is_valid():
            personal = personal_form.save()

            tipo_cargo_personal_direccion = get_object_or_404(TipoCargo, id=2)

            new_personal = Personal.objects.create(
                estado=1,
                id_oic=None,
                id_persona=personal
            )

            # Obtener el nombre del cargo del formulario
            cargo_nombre = personal_form.cleaned_data['cargo_nombre']

            CargoPersonal.objects.create(
                nombre=cargo_nombre,
                id_personal=new_personal,
                id_tipo_cargo=tipo_cargo_personal_direccion
            )

            return redirect('personal_direccion')

    else:
        personal_form = CrearTitularForm()

    context = {
        'personal_form': personal_form
    }
    return render(request, 'crear_personal_direccion.html', context)


@login_required
def download_archivo(request, archivo_id):
    archivo = get_object_or_404(Archivo, id=archivo_id)

    if not archivo.archivo:
        raise Http404("Archivo no encontrado")

    file_handle = archivo.archivo.open('rb')
    response = FileResponse(file_handle, as_attachment=True)

    # Use quote to properly encode the filename for the Content-Disposition header
    file_name = quote(archivo.nombre.encode('utf-8'))
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response


@login_required
def limpiar_personal_oic(request, oic_id):
    personal = Personal.objects.filter(id_oic=oic_id)
    personal.update(estado=0)
    return redirect('personal_oic', oic_id)


@login_required
def limpiar_personal_direccion(request):
    personal = Personal.objects.filter(id_oic=None)
    personal.update(estado=0)
    return redirect('personal_direccion')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

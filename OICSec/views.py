import datetime
import os
from difflib import SequenceMatcher
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from OICSec.forms import AuditoriaForm, ControlForm, IntervencionForm
from OICSec.funcs.Cedula import SupervisionData, ConceptosLista, Concepto
from OICSec.funcs.Cedula import cedula as create_cedula
from OICSec.funcs.PAA import extract_paa
from OICSec.funcs.PACI import extract_paci
from OICSec.funcs.PINT import extract_pint
from OICSec.models import Oic, Auditoria, ActividadFiscalizacion, Materia, Programacion, Enfoque, Temporalidad, \
    ControlInterno, TipoRevision, ProgramaRevision, Intervencion, TipoIntervencion, Cedula, ConceptoCedula, Archivo


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


def upload_paa_view(request):
    lista_oics = Oic.objects.all()

    similar_oic = None

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        try:
            data = extract_paa(excel_file)
            if data is None:
                return render(request, 'upload_paa.html', {
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
                    for auditoria_data in excel_processing_result[1]:
                        # Verificar si ya existe una auditoría con los mismos atributos

                        # Se verifica que hay actividad de fiscalización
                        actividad_fiscalizacion = ActividadFiscalizacion.objects.filter(
                            anyo=auditoria_data['Año'],
                            trimestre=auditoria_data['Trimestre'],
                            id_oic=oic_selected
                        ).first()
                        # Si no existe, se crea una actividad de fiscalización
                        if not actividad_fiscalizacion:
                            actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
                                anyo=auditoria_data['Año'],
                                trimestre=auditoria_data['Trimestre'],
                                id_oic=oic_selected
                            )

                        # Se crea una auditoria nueva con la actividad de fiscalización
                        materia_obj = Materia.objects.get(id=auditoria_data["Materia"])
                        programacion_obj = Programacion.objects.get(id=auditoria_data["Programacion"])
                        enfoque_obj = Enfoque.objects.get(id=auditoria_data["Enfoque"])
                        temporalidad_obj = Temporalidad.objects.get(id=auditoria_data["Temporalidad"])
                        cedula_obj = Cedula.objects.create()
                        Auditoria.objects.create(
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

                        for i in range(60):
                            ConceptoCedula.objects.create(
                                celda=str(i),
                                estado=None,
                                comentario=None,
                                id_cedula=cedula_obj
                            )

                return render(request, 'upload_paa.html',
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
        return render(request, 'upload_paa.html')


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


@login_required
def upload_pint_view(request):
    lista_oics = Oic.objects.all()

    similar_oic = None

    if request.method == 'POST':
        word_file = request.FILES.get('word_file')
        if word_file is None:
            return render(request, 'upload_pint.html', {
                'word_processing_error': 'Error al procesar el archivo Word | Nombre de error: None-results | '
                                         'Consulte manual de usuario para mas información.',
                'lista_oics': lista_oics, 'similar_oic': similar_oic})
        try:
            word_processing_result = extract_pint(word_file)
            if word_processing_result is None:
                return render(request, 'upload_pint.html', {
                    'word_processing_error': 'Error al procesar el archivo Word | Nombre de error: None-results | '
                                             'Consulte manual de usuario para mas información.',
                    'lista_oics': lista_oics, 'similar_oic': similar_oic})
            else:
                max_similarity = 0
                for oic in lista_oics:
                    similarity = SequenceMatcher(None, word_processing_result.get('Ente Público'), oic.nombre).ratio()
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_oic = oic
                oic_selected = similar_oic if similar_oic else None

                # Se verifica que hay actividad de fiscalización
                actividad_fiscalizacion = ActividadFiscalizacion.objects.filter(
                    anyo=word_processing_result['Año'],
                    trimestre=word_processing_result['Trimestre'],
                    id_oic=oic_selected
                ).first()
                # Si no existe, se crea una actividad de fiscalización
                if not actividad_fiscalizacion:
                    actividad_fiscalizacion = ActividadFiscalizacion.objects.create(
                        anyo=word_processing_result['Año'],
                        trimestre=word_processing_result['Trimestre'],
                        id_oic=oic_selected
                    )

                # Se crea una intervencion nueva con la actividad de fiscalización
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

                return render(request, 'upload_pint.html',
                              {'word_processing_result': word_processing_result,
                               'lista_oics': lista_oics,
                               'similar_oic': similar_oic})
        except Exception as e:
            word_processing_error = (f'Error al procesar el archivo Word | Nombre de error: {str(e)} | Consulte '
                                     f'manual de usuario para mas información')
            return render(request, 'upload_pint.html',
                          {'word_processing_error': word_processing_error, 'lista_oics': lista_oics,
                           'similar_oic': similar_oic})

    if request.method == 'GET':
        return render(request, 'upload_pint.html')


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


def save_file_and_respond(file_path, cedula, data):
    archivo = cedula.id_archivo
    if not archivo:
        archivo = Archivo.objects.create(
            archivo=file_path,
            nombre=f"Supervision - {data.Numero} - {data.OIC} - {data.Anyo_Trimestre}.xlsx"
        )
        cedula.id_archivo = archivo
        cedula.save()

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
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

from difflib import SequenceMatcher

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from OICSec.forms import AuditoriaForm
from OICSec.funcs.PAA import extract_paa
from OICSec.funcs.PACI import extract_paci
from OICSec.models import Oic, Auditoria, ActividadFiscalizacion, Materia, Programacion, Enfoque, Temporalidad, \
    ControlInterno, TipoRevision, ProgramaRevision


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


@login_required
def auditorias_view(request):
    nombres_oics = Auditoria.objects.values_list('id_actividad_fiscalizacion__id_oic__nombre', flat=True).distinct()
    lista_oics = Oic.objects.filter(nombre__in=nombres_oics).distinct()
    lista_anyos = ActividadFiscalizacion.objects.values('anyo').distinct()

    oic_id = request.GET.get('oic_id')
    anyo = request.GET.get('anyo')

    if oic_id and anyo:
        auditorias = Auditoria.objects.filter(id_actividad_fiscalizacion__id_oic=oic_id,
                                              id_actividad_fiscalizacion__anyo=anyo)
    elif oic_id:
        auditorias = Auditoria.objects.filter(id_actividad_fiscalizacion__id_oic=oic_id)
    elif anyo:
        auditorias = Auditoria.objects.filter(id_actividad_fiscalizacion__anyo=anyo)
    else:
        auditorias = Auditoria.objects.all()

    paginator = Paginator(auditorias.order_by('id_actividad_fiscalizacion__anyo'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'lista_oics': lista_oics,
        'lista_anyos': lista_anyos,
        'oic_id': oic_id,
        'anyo': anyo,
        'auditorias': auditorias,
    }

    return render(request, 'auditorias.html', context)


@login_required
def control_interno_view(request):
    nombres_oics = ControlInterno.objects.values_list('id_actividad_fiscalizacion__id_oic__nombre', flat=True).distinct()
    lista_oics = Oic.objects.filter(nombre__in=nombres_oics).distinct()
    lista_anyos = ActividadFiscalizacion.objects.values('anyo').distinct()

    oic_id = request.GET.get('oic_id')
    anyo = request.GET.get('anyo')

    if oic_id and anyo:
        controles_internos = ControlInterno.objects.filter(id_actividad_fiscalizacion__id_oic=oic_id,
                                                           id_actividad_fiscalizacion__anyo=anyo)
    elif oic_id:
        controles_internos = ControlInterno.objects.filter(id_actividad_fiscalizacion__id_oic=oic_id)
    elif anyo:
        controles_internos = ControlInterno.objects.filter(id_actividad_fiscalizacion__anyo=anyo)
    else:
        controles_internos = ControlInterno.objects.all()

    paginator = Paginator(controles_internos.order_by('id_actividad_fiscalizacion__anyo'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'lista_oics': lista_oics,
        'lista_anyos': lista_anyos,
        'oic_id': oic_id,
        'anyo': anyo,
        'controles_internos': controles_internos,
    }

    return render(request, 'control_interno.html', context)


@login_required
def auditoria_detalle_view(request, auditoria_id):
    auditoria = get_object_or_404(Auditoria, pk=auditoria_id)

    if request.method == 'POST':
        form = AuditoriaForm(request.POST, instance=auditoria)
        if form.is_valid():
            form.save()
            return render(request, 'auditoria_detalle.html',
                          {'form': form, 'result': 'result', 'auditoria_id': auditoria_id})
        else:
            return render(request, 'auditoria_detalle.html',
                          {'form': form, 'error': form.errors, 'auditoria_id': auditoria_id})
    else:
        form = AuditoriaForm(instance=auditoria)
        return render(request, 'auditoria_detalle.html', {'form': form, 'auditoria_id': auditoria_id})


def upload_paa_view(request):
    lista_oics = Oic.objects.all()

    similar_oic = None

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES.get('excel_file')
        try:
            excel_processing_result = extract_paa(excel_file)
            if excel_processing_result is None:
                return render(request, 'upload_paa.html', {
                    'excel_processing_error': 'Error al procesar el archivo Excel | Nombre de error: None-results | '
                                              'Consulte manual de usuario para mas información.',
                    'lista_oics': lista_oics, 'similar_oic': similar_oic})
            else:
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

                    )

                return render(request, 'upload_paa.html',
                              {'excel_processing_result': excel_processing_result,
                               'lista_oics': lista_oics,
                               'similar_oic': similar_oic})
        except Exception as e:
            excel_processing_error = f'Error al procesar el archivo Excel | Nombre de error: {str(e)} | Consulte manual de usuario para mas información'
            return render(request, 'upload_paa.html',
                          {'excel_processing_error': excel_processing_error, 'lista_oics': lista_oics,
                           'similar_oic': similar_oic})

    if request.method == 'GET':
        return render(request, 'upload_paa.html')


@login_required
def upload_paci_view(request):
    lista_oics = Oic.objects.all()
    tipos_revision = TipoRevision.objects.all()
    programa_revision = ProgramaRevision.objects.all()

    similar_oic = None

    if request.method == 'POST' and request.FILES.get('excel_file'):
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

                        ControlInterno.objects.create(
                            numero=control_data["Numero"],
                            area=control_data["Area"],
                            denominacion=control_data["Denominacion"],
                            objetivo=control_data["Objetivo"],
                            id_actividad_fiscalizacion=actividad_fiscalizacion,
                            id_tipo_revision=tipo_revision_obj,
                            id_programa_revision=programa_revision_obj
                        )

                return render(request, 'upload_paci.html',
                              {'excel_processing_result': data,
                               'lista_oics': lista_oics,
                               'similar_oic': similar_oic})
        except Exception as e:
            excel_processing_error = f'Error al procesar el archivo Excel | Nombre de error: {str(e)} | Consulte manual de usuario para mas información'
            return render(request, 'upload_paa.html',
                          {'excel_processing_error': excel_processing_error, 'lista_oics': lista_oics,
                           'similar_oic': similar_oic})

    if request.method == 'GET':
        return render(request, 'upload_paci.html')


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
        confirm_password = request.POST.get('confirm_password')

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
def minutas_view(request):
    return render(request, 'minuta.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

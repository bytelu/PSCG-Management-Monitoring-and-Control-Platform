from django.db.models import Sum
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django.contrib import messages
from axes.signals import user_login_failed
from axes.models import AccessAttempt
from django.utils.translation import gettext as _

from .models import Auditoria, Intervencion, ControlInterno, ConceptoCedula, Minuta, ConceptoMinuta, AuditoriaArchivos, \
    IntervencionArchivos, ControlArchivos


def delete_cedula_related_records(cedula):
    # Eliminar ConceptoCedula relacionados
    ConceptoCedula.objects.filter(id_cedula=cedula).delete()

    # Eliminar el Archivo relacionado si existe
    if cedula.id_archivo:
        archivo = cedula.id_archivo
        archivo.delete()

    # Eliminar la Cedula
    cedula.delete()


def delete_activity_files(instance):
    # Eliminar archivos de Auditoria relacionados
    if isinstance(instance, Auditoria):
        auditoria_archivos = AuditoriaArchivos.objects.filter(id_auditoria=instance).exclude(tipo=0)
        for auditoria_archivo in auditoria_archivos:
            if auditoria_archivo.id_archivo:
                auditoria_archivo.id_archivo.delete()
            auditoria_archivo.delete()

    # Eliminar archivos de Intervencion relacionados
    if isinstance(instance, Intervencion):
        intervencion_archivos = IntervencionArchivos.objects.filter(id_intervencion=instance)
        for intervencion_archivo in intervencion_archivos:
            if intervencion_archivo.id_archivo:
                intervencion_archivo.id_archivo.delete()
            intervencion_archivo.delete()

    # Eliminar archivos de ControlInterno relacionados
    if isinstance(instance, ControlInterno):
        control_archivos = ControlArchivos.objects.filter(id_control=instance).exclude(tipo=0)
        for control_archivo in control_archivos:
            if control_archivo.id_archivo:
                control_archivo.id_archivo.delete()
            control_archivo.delete()


def delete_minuta_related_records(actividad):
    minuta = Minuta.objects.filter(id_actividad_fiscalizacion=actividad).first()
    if minuta:
        ConceptoMinuta.objects.filter(id_minuta=minuta).delete()
        if minuta.id_archivo:
            archivo = minuta.id_archivo
            archivo.delete()
        minuta.delete()
    actividad.delete()


def is_last_record_in_activity(instance):
    actividad = instance.id_actividad_fiscalizacion
    exclude_instance_id = instance.id

    if isinstance(instance, Auditoria):
        remaining_auditoria = (Auditoria.objects.filter(id_actividad_fiscalizacion=actividad)
                               .exclude(id=exclude_instance_id).exists())
    else:
        remaining_auditoria = Auditoria.objects.filter(id_actividad_fiscalizacion=actividad).exists()

    if isinstance(instance, Intervencion):
        remaining_intervencion = (Intervencion.objects.filter(id_actividad_fiscalizacion=actividad)
                                  .exclude(id=exclude_instance_id).exists())
    else:
        remaining_intervencion = Intervencion.objects.filter(id_actividad_fiscalizacion=actividad).exists()

    if isinstance(instance, ControlInterno):
        remaining_controlinterno = (ControlInterno.objects.filter(id_actividad_fiscalizacion=actividad)
                                    .exclude(id=exclude_instance_id).exists())
    else:
        remaining_controlinterno = ControlInterno.objects.filter(id_actividad_fiscalizacion=actividad).exists()

    return not (remaining_auditoria or remaining_intervencion or remaining_controlinterno)


@receiver(pre_delete, sender=Auditoria)
@receiver(pre_delete, sender=Intervencion)
@receiver(pre_delete, sender=ControlInterno)
def delete_related_files(sender, instance, **kwargs):
    delete_activity_files(instance)


@receiver(post_delete, sender=Auditoria)
@receiver(post_delete, sender=Intervencion)
@receiver(post_delete, sender=ControlInterno)
def delete_related_records(sender, instance, **kwargs):
    # Eliminar registros relacionados con Cedula si existen
    if instance.id_cedula:
        delete_cedula_related_records(instance.id_cedula)

    # Verificar si es el último registro en la actividad
    if is_last_record_in_activity(instance):
        actividad = instance.id_actividad_fiscalizacion
        delete_minuta_related_records(actividad)


@receiver(user_login_failed)
def check_failed_attempts(sender, credentials, request, **kwargs):
    ip_address = request.META.get('REMOTE_ADDR')

    attempts = AccessAttempt.objects.filter(ip_address=ip_address).aggregate(total_failures=Sum('failures_since_start'))['total_failures'] or 0

    failure_limit = 5

    if attempts == failure_limit - 3:
        request.session['warning_message'] = _("Advertencia: Tienes tres intentos más antes de ser bloqueado.")
    if attempts == failure_limit - 2:
        request.session['warning_message'] = _("Advertencia: Tienes dos intentos más antes de ser bloqueado.")
    if attempts == failure_limit - 1:
        request.session['warning_message'] = _("Advertencia: Tienes solo un intento antes de ser bloqueado.")

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Auditoria, Intervencion, ControlInterno, ConceptoCedula, Minuta, ConceptoMinuta


def delete_cedula_related_records(cedula):
    # Eliminar ConceptoCedula relacionados
    ConceptoCedula.objects.filter(id_cedula=cedula).delete()

    # Eliminar el Archivo relacionado si existe
    if cedula.id_archivo:
        archivo = cedula.id_archivo
        archivo.delete()

    # Eliminar la Cedula
    cedula.delete()


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


@receiver(post_delete, sender=Auditoria)
@receiver(post_delete, sender=Intervencion)
@receiver(post_delete, sender=ControlInterno)
def delete_related_records(sender, instance, **kwargs):
    # Eliminar registros relacionados con Cedula si existen
    if instance.id_cedula:
        delete_cedula_related_records(instance.id_cedula)

    actividad = instance.id_actividad_fiscalizacion

    # Verificar si es el último registro en la actividad
    if is_last_record_in_activity(instance):
        delete_minuta_related_records(actividad)

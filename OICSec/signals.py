from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Auditoria, Intervencion, ControlInterno, ConceptoCedula


@receiver(post_delete, sender=Auditoria)
@receiver(post_delete, sender=Intervencion)
@receiver(post_delete, sender=ControlInterno)
def delete_related_records(sender, instance, **kwargs):
    if instance.id_cedula:
        cedula = instance.id_cedula

        # Eliminar ConceptoCedula relacionados
        ConceptoCedula.objects.filter(id_cedula=cedula).delete()

        # Eliminar el Archivo relacionado si existe
        if cedula.id_archivo:
            archivo = cedula.id_archivo
            archivo.delete()

        # Eliminar la Cedula
        cedula.delete()
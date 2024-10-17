from django.db import models


class AccionesCorrectivas(models.Model):
    ESTADO_CHOICES = [
        (0, 'No atendida'),
        (1, 'Atendida')
    ]
    id = models.AutoField(primary_key=True)
    denominacion = models.CharField(max_length=100, blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    id_observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'acciones_correctivas'

    def __str__(self):
        return str(self.denominacion)


class AccionesPreventivas(models.Model):
    ESTADO_CHOICES = [
        (0, 'No atendida'),
        (1, 'Atendida')
    ]
    id = models.AutoField(primary_key=True)
    denominacion = models.CharField(max_length=100, blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    id_observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'acciones_preventivas'


class ActividadFiscalizacion(models.Model):
    id = models.AutoField(primary_key=True)
    anyo = models.IntegerField(blank=True, null=True)
    trimestre = models.IntegerField(blank=True, null=True)
    id_oic = models.ForeignKey('Oic', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'actividad_fiscalizacion'

    def __str__(self):
        return f'{self.id_oic} | 0{self.trimestre}/{self.anyo}'


class Archivo(models.Model):
    id = models.AutoField(primary_key=True)
    archivo = models.FileField(upload_to='archivos/', max_length=1000, blank=True, null=True)
    nombre = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        db_table = 'archivo'

    def delete(self, *args, **kwargs):
        self.archivo.delete(save=False)
        super().delete(*args, **kwargs)


class Auditoria(models.Model):
    ESTADO_CHOICES = [
        (0, 'Cancelada'),
        (1, 'Activa')
    ]
    id = models.AutoField(primary_key=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES, blank=True, null=True)
    denominacion = models.CharField(max_length=2000, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    objetivo = models.CharField(max_length=2000, blank=True, null=True)
    oportunidad = models.CharField(max_length=2000, blank=True, null=True)
    alcance = models.CharField(max_length=2000, blank=True, null=True)
    ejercicio = models.CharField(max_length=4, blank=True, null=True)
    unidad = models.CharField(max_length=500, blank=True, null=True)
    id_actividad_fiscalizacion = models.ForeignKey('ActividadFiscalizacion', on_delete=models.CASCADE, blank=True,
                                                   null=True)
    id_materia = models.ForeignKey('Materia', on_delete=models.CASCADE, blank=True, null=True)
    id_enfoque = models.ForeignKey('Enfoque', on_delete=models.CASCADE, blank=True, null=True)
    id_programacion = models.ForeignKey('Programacion', on_delete=models.CASCADE, blank=True, null=True)
    id_temporalidad = models.ForeignKey('Temporalidad', on_delete=models.CASCADE, blank=True, null=True)
    id_cedula = models.ForeignKey('Cedula', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'auditoria'

    def __str__(self):
        oic_nombre = None
        if self.id_actividad_fiscalizacion:
            oic_nombre = self.id_actividad_fiscalizacion.id_oic.nombre \
                if self.id_actividad_fiscalizacion and self.id_actividad_fiscalizacion.id_oic \
                else 'Sin OIC'
        return f'A-{self.numero if self.numero else None}/{self.id_actividad_fiscalizacion.anyo if self.id_actividad_fiscalizacion else None} | {oic_nombre}'


class AuditoriaArchivos(models.Model):
    TIPO_CHOICES = [
        (0, 'PAA'),
        (1, 'Incorporación'),
        (2, 'Cancelación'),
        (3, 'Modificación')
    ]
    id = models.AutoField(primary_key=True)
    tipo = models.IntegerField(choices=TIPO_CHOICES, blank=True, null=True)
    id_auditoria = models.ForeignKey('Auditoria', on_delete=models.CASCADE, blank=True, null=True)
    id_archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'auditoria_archivos'


class AuditoriaObservacion(models.Model):
    id = models.AutoField(primary_key=True)
    id_observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE, blank=True, null=True)
    id_auditoria = models.ForeignKey('Auditoria', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'auditoria_observacion'


class Cedula(models.Model):
    id = models.AutoField(primary_key=True)
    realizacion = models.DateTimeField(blank=True, null=True)
    id_archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'cedula'


class Clasificacion(models.Model):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'clasificacion'

    def __str__(self):
        return str(self.tipo)


class ConceptoCedula(models.Model):
    id = models.AutoField(primary_key=True)
    celda = models.CharField(max_length=3)
    estado = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=500, blank=True, null=True)
    id_cedula = models.ForeignKey('Cedula', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'concepto_cedula'


class ControlInterno(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.CharField(max_length=500, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    denominacion = models.CharField(max_length=200, blank=True, null=True)
    objetivo = models.CharField(max_length=2000, blank=True, null=True)
    ejercicio = models.CharField(max_length=4, blank=True, null=True)
    id_tipo_revision = models.ForeignKey('TipoRevision', on_delete=models.CASCADE, blank=True, null=True)
    id_programa_revision = models.ForeignKey('ProgramaRevision', on_delete=models.CASCADE, blank=True, null=True)
    id_actividad_fiscalizacion = models.ForeignKey('ActividadFiscalizacion', on_delete=models.CASCADE, blank=True,
                                                   null=True)
    id_cedula = models.ForeignKey('Cedula', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'control_interno'

    def __str__(self):
        if self.id_actividad_fiscalizacion:
            return f'CI {self.numero}/{self.id_actividad_fiscalizacion.anyo} | {self.id_actividad_fiscalizacion.id_oic}'
        else:
            return f'CI {self.numero}/None | None'


class ControlArchivos(models.Model):
    TIPO_CHOICES = [
        (0, 'PACI'),
        (1, 'Incorporación'),
        (2, 'Cancelación'),
        (3, 'Modificación')
    ]
    id = models.AutoField(primary_key=True)
    tipo = models.IntegerField(choices=TIPO_CHOICES, blank=True, null=True)
    id_control = models.ForeignKey('ControlInterno', on_delete=models.CASCADE, blank=True, null=True)
    id_archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'control_archivos'


class ControlInternoObservacion(models.Model):
    id = models.AutoField(primary_key=True)
    id_observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE, blank=True, null=True)
    id_control_interno = models.ForeignKey('ControlInterno', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'control_interno_observacion'


class Direccion(models.Model):
    id = models.AutoField(primary_key=True)
    direccion = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])

    class Meta:
        db_table = 'direccion'

    def __str__(self):
        return f'{self.direccion}'


class Enfoque(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.tipo)

    class Meta:
        db_table = 'enfoque'


class EstatusObservacion(models.Model):
    id = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'estatus_observacion'

    def __str__(self):
        return str(self.estado)


class Intervencion(models.Model):
    id = models.AutoField(primary_key=True)
    unidad = models.TextField(max_length=500, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    denominacion = models.TextField(max_length=5000, blank=True, null=True)
    inicio = models.DateField(blank=True, null=True)
    termino = models.DateField(blank=True, null=True)
    objetivo = models.TextField(max_length=5000, blank=True, null=True)
    alcance = models.TextField(max_length=5000, blank=True, null=True)
    antecedentes = models.TextField(max_length=5000, blank=True, null=True)
    ejercicio = models.CharField(max_length=4, blank=True, null=True)
    fuerza_supervision = models.IntegerField(blank=True, null=True)
    fuerza_responsables = models.IntegerField(blank=True, null=True)
    fuerza_auditores = models.IntegerField(blank=True, null=True)
    id_tipo_intervencion = models.ForeignKey('TipoIntervencion', on_delete=models.CASCADE, blank=True, null=True)
    id_actividad_fiscalizacion = models.ForeignKey('ActividadFiscalizacion', on_delete=models.CASCADE, blank=True, null=True)
    id_cedula = models.ForeignKey('Cedula', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'intervencion'

    def __str__(self):
        character = None
        if self.id_tipo_intervencion is not None:
            character = "R" if self.id_tipo_intervencion.clave == 13 else (
                "V" if self.id_tipo_intervencion.clave == 14 else "O")
        anyo = None
        oic = None
        if self.id_actividad_fiscalizacion:
            anyo = self.id_actividad_fiscalizacion.anyo
            oic = self.id_actividad_fiscalizacion.id_oic
        return f"{character}-{self.numero}/{anyo} | {oic}"


class IntervencionArchivos(models.Model):
    TIPO_CHOICES = [
        (0, 'PINT'),
        (1, 'Incorporación'),
        (2, 'Cancelación'),
        (3, 'Modificación')
    ]
    id = models.AutoField(primary_key=True)
    tipo = models.IntegerField(choices=TIPO_CHOICES, blank=True, null=True)
    id_intervencion = models.ForeignKey('Intervencion', on_delete=models.CASCADE, blank=True, null=True)
    id_archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'intervencion_archivos'


class IntervencionObservacion(models.Model):
    id = models.AutoField(primary_key=True)
    id_observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE, blank=True, null=True)
    id_intervencion = models.ForeignKey('Intervencion', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'intervencion_observacion'


class Materia(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.tipo)

    class Meta:
        db_table = 'materia'


class Minuta(models.Model):
    id = models.AutoField(primary_key=True)
    inicio = models.DateTimeField(blank=True, null=True)
    fin = models.DateTimeField(blank=True, null=True)
    mes = models.IntegerField(blank=True, null=True)
    id_actividad_fiscalizacion = models.ForeignKey('ActividadFiscalizacion', on_delete=models.CASCADE, blank=True,
                                                   null=True)
    id_archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'minuta'


class ConceptoMinuta(models.Model):
    TIPO_CHOICES = [
        (1, 'Auditoria'),
        (2, 'Intervención'),
        (3, 'Control')
    ]
    id = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=3)
    estatus = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=500, blank=True, null=True)
    tipo_concepto = models.IntegerField(choices=TIPO_CHOICES, blank=True, null=True)
    id_minuta = models.ForeignKey('Minuta', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'concepto_minuta'


class MinutaPersonal(models.Model):
    TIPO_CHOICES = [
        (1, 'Director Coordinación'),
        (2, 'JUD Coordinación'),
        (3, 'Titular OIC'),
        (4, 'Personal OIC')
    ]
    id = models.AutoField(primary_key=True)
    tipo_personal = models.IntegerField(choices=TIPO_CHOICES, blank=True, null=True)
    id_minuta = models.ForeignKey('Minuta', on_delete=models.CASCADE, blank=True, null=True)
    id_personal = models.ForeignKey('Personal', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'minuta_personal'


class CedulaPersonal(models.Model):
    TIPO_CHOICES = [
        (1, 'Director Coordinación'),
        (2, 'Titular OIC'),
    ]
    id = models.AutoField(primary_key=True)
    tipo_personal = models.IntegerField(choices=TIPO_CHOICES, blank=True, null=True)
    id_cedula = models.ForeignKey('Cedula', on_delete=models.CASCADE, blank=True, null=True)
    id_personal = models.ForeignKey('Personal', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'cedula_personal'


class Observacion(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=2, blank=True, null=True)
    denominacion = models.CharField(max_length=500, blank=True, null=True)
    monto_observado = models.FloatField(blank=True, null=True)
    monto_aclarado = models.FloatField(blank=True, null=True)
    monto_recuperado = models.FloatField(blank=True, null=True)
    fecha_incurrencia = models.DateField(blank=True, null=True)
    fecha_compromiso = models.DateField(blank=True, null=True)
    clave = models.CharField(max_length=2, blank=True, null=True)
    id_clasificacion = models.ForeignKey('Clasificacion', on_delete=models.CASCADE, blank=True, null=True)
    id_estatus_observacion = models.ForeignKey('EstatusObservacion', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'observacion'


class Oic(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, blank=True, null=True)
    id_direccion = models.ForeignKey('Direccion', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'oic'

    def __str__(self):
        return str(self.nombre)


class Programacion(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.tipo)

    class Meta:
        db_table = 'programacion'


class ProgramaRevision(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=2, blank=True, null=True)
    tipo = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'programa_revision'

    def __str__(self):
        return str(self.tipo)


class Temporalidad(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.tipo)

    class Meta:
        db_table = 'temporalidad'


class TipoIntervencion(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'tipo_intervencion'

    def __str__(self):
        return str(self.tipo)


class TipoRevision(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=2, blank=True, null=True)
    tipo = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'tipo_revision'

    def __str__(self):
        return str(self.tipo)


class Persona(models.Model):
    id = models.AutoField(primary_key=True)
    honorifico = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    apellido = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'persona'


class Personal(models.Model):
    ESTADO_CHOICES = [
        (0, 'Inactivo'),
        (1, 'Activo')
    ]
    id = models.AutoField(primary_key=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES)
    id_oic = models.ForeignKey('Oic', on_delete=models.CASCADE, blank=True, null=True)
    id_persona = models.ForeignKey('Persona', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'personal'


class TipoCargo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'tipo_cargo'


class CargoPersonal(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    id_tipo_cargo = models.ForeignKey('TipoCargo', on_delete=models.CASCADE, blank=True, null=True)
    id_personal = models.ForeignKey('Personal', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'cargo_personal'

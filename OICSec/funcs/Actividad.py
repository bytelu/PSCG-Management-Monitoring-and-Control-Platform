class Actividad:
    def __init__(self, tipo, denominacion, numero):
        self.tipo = tipo
        self.denominacion = denominacion
        self.numero = numero


def get_actividades(auditoria, intervencion, control_interno):
    actividades = []

    for aud in auditoria:
        tipo = "auditoría"
        denominacion = aud.denominacion
        numero = f"A-{aud.numero}/{aud.id_actividad_fiscalizacion.anyo}"
        actividad = Actividad(tipo, denominacion, numero)
        actividades.append(actividad)

    for intv in intervencion:
        tipo = "intervención"
        denominacion = intv.denominacion
        character = ("R" if intv.id_tipo_intervencion.clave == 13 else (
            "V" if intv.id_tipo_intervencion.clave == 14 else "O")) if intv.id_tipo_intervencion else ''
        numero = f"{character}-{intv.numero}/{intv.id_actividad_fiscalizacion.anyo}"
        actividad = Actividad(tipo, denominacion, numero)
        actividades.append(actividad)

    for ctrl in control_interno:
        tipo = "control interno"
        denominacion = ctrl.denominacion
        numero = f"CI {ctrl.numero}/{ctrl.id_actividad_fiscalizacion.anyo}"
        actividad = Actividad(tipo, denominacion, numero)
        actividades.append(actividad)

    return actividades
from django import forms

from .models import *


class BaseForm(forms.ModelForm):
    anyo = forms.IntegerField(
        label='Año de actividad de fiscalización',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    trimestre = forms.IntegerField(
        label='Trimestre de actividad de fiscalización',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    id_oic = forms.ModelChoiceField(
        queryset=Oic.objects.all(),
        label='OIC',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id_actividad_fiscalizacion:
            self.fields['anyo'].initial = self.instance.id_actividad_fiscalizacion.anyo
            self.fields['trimestre'].initial = self.instance.id_actividad_fiscalizacion.trimestre
            self.fields['id_oic'].initial = self.instance.id_actividad_fiscalizacion.id_oic

    def save(self, commit=True):
        instance = super().save(commit=False)
        actividad_actual = instance.id_actividad_fiscalizacion

        # Verifica si ya hay una actividad con los mismos datos proporcionados
        actividad_existente = ActividadFiscalizacion.objects.filter(
            anyo=self.cleaned_data.get('anyo'),
            trimestre=self.cleaned_data.get('trimestre'),
            id_oic=self.cleaned_data.get('id_oic')
        ).first()

        # Si no existe tal actividad, crear una nueva
        if not actividad_existente:
            nueva_actividad = ActividadFiscalizacion.objects.create(
                anyo=self.cleaned_data.get('anyo'),
                trimestre=self.cleaned_data.get('trimestre'),
                id_oic=self.cleaned_data.get('id_oic')
            )
            instance.id_actividad_fiscalizacion = nueva_actividad
        else:
            instance.id_actividad_fiscalizacion = actividad_existente

        if commit:
            instance.save()

        if actividad_actual and actividad_actual != instance.id_actividad_fiscalizacion:
            is_used_elsewhere = (
                    Auditoria.objects.filter(id_actividad_fiscalizacion=actividad_actual).exists() or
                    Intervencion.objects.filter(id_actividad_fiscalizacion=actividad_actual).exists() or
                    ControlInterno.objects.filter(id_actividad_fiscalizacion=actividad_actual).exists())

            # Si no está asociada a ninguna otra entidad, eliminarla
            if not is_used_elsewhere:
                actividad_actual.delete()

        return instance


class AuditoriaForm(BaseForm):
    class Meta:
        model = Auditoria
        fields = [
            'denominacion', 'numero', 'objetivo', 'oportunidad', 'alcance', 'ejercicio',
            'unidad', 'id_materia', 'id_enfoque', 'id_programacion', 'id_temporalidad'
        ]
        labels = {
            'denominacion': 'Denominación:',
            'numero': 'Número:',
            'objetivo': 'Objetivo:',
            'oportunidad': 'Oportunidad:',
            'alcance': 'Alcance:',
            'ejercicio': 'Año de ejercicio:',
            'unidad': 'Unidad:',
            'id_materia': 'Materia:',
            'id_enfoque': 'Enfoque:',
            'id_programacion': 'Programación:',
            'id_temporalidad': 'Temporalidad:'
        }
        widgets = {
            'denominacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'oportunidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ejercicio': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'id_materia': forms.Select(attrs={'class': 'form-control select2'}),
            'id_enfoque': forms.Select(attrs={'class': 'form-control select2'}),
            'id_programacion': forms.Select(attrs={'class': 'form-control select2'}),
            'id_temporalidad': forms.Select(attrs={'class': 'form-control select2'})
        }


class ControlForm(BaseForm):
    class Meta:
        model = ControlInterno
        fields = [
            'numero', 'area', 'ejercicio', 'denominacion', 'objetivo', 'id_tipo_revision',
            'id_programa_revision'
        ]
        labels = {
            'numero': 'Número:',
            'area': 'Area:',
            'ejercicio': 'Ejercicio:',
            'denominacion': 'Denominación:',
            'objetivo': 'Objetivo:',
            'id_tipo_revision': 'Tipo de revision:',
            'id_programa_revision': 'Programa de revision:'
        }
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'ejercicio': forms.NumberInput(attrs={'class': 'form-control'}),
            'denominacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'id_tipo_revision': forms.Select(attrs={'class': 'form-control select2'}),
            'id_programa_revision': forms.Select(attrs={'class': 'form-control select2'})
        }


class IntervencionForm(BaseForm):
    class Meta:
        model = Intervencion
        fields = [
            'numero', 'unidad', 'denominacion', 'ejercicio', 'alcance', 'antecedentes',
            'fuerza_auditores', 'fuerza_responsables', 'fuerza_supervision', 'inicio',
            'termino', 'objetivo', 'id_tipo_intervencion'
        ]
        labels = {
            'numero': 'Número:',
            'unidad': 'Unidad:',
            'ejercicio': 'Ejercicio:',
            'denominacion': 'Denominación:',
            'alcance': 'Alcance:',
            'antecedentes': 'Antecedentes:',
            'fuerza_auditores': 'Numero de Auditores',
            'fuerza_responsables': 'Numero de responsables',
            'fuerza_supervision': 'Numero de supervisores',
            'inicio': 'Inicio:',
            'termino': 'Termino:',
            'objetivo': 'Objetivo:',
            'id_tipo_intervencion': 'Tipo de Intervencion:'
        }
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'ejercicio': forms.NumberInput(attrs={'class': 'form-control'}),
            'denominacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'antecedentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fuerza_auditores': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuerza_responsables': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuerza_supervision': forms.NumberInput(attrs={'class': 'form-control'}),
            'inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'id_tipo_intervencion': forms.Select(attrs={'class': 'form-control select2'})
        }


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['honorifico', 'nombre', 'apellido']
        widgets = {
            'honorifico': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CrearTitularForm(forms.ModelForm):
    cargo_nombre = forms.CharField(
        label="Nombre del Cargo",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Persona
        fields = ['honorifico', 'nombre', 'apellido']

        widgets = {
            'honorifico': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CargoPersonalForm(forms.ModelForm):
    class Meta:
        model = CargoPersonal
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

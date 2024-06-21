from django import forms

from .models import Auditoria


class AuditoriaForm(forms.ModelForm):
    class Meta:
        model = Auditoria
        fields = '__all__'  # Incluye todos los campos del modelo

        # Cambia los labels de los campos según tus necesidades
        labels = {
            'denominacion': 'Denominación:',
            'numero': 'Número:',
            'objetivo': 'Objetivo:',
            'oportunidad': 'Oportunidad:',
            'alcance': 'Alcance:',
            'ejercicio': 'Año de ejercicio:',
            'unidad': 'Unidad:',
            'id_actividad_fiscalizacion': 'Actividad de fiscalizacion:',
            'id_materia': 'Materia:',
            'id_enfoque': 'Enfoque:',
            'id_programacion': 'Programación:',
            'id_temporalidad': 'Temporalidad:'
        }

        # Agrega clases de Bootstrap a los campos del formulario
        widgets = {
            'denominacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'oportunidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ejercicio': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'id_actividad_fiscalizacion': forms.Select(attrs={'class': 'form-control select2'}),
            'id_materia': forms.Select(attrs={'class': 'form-control select2'}),
            'id_enfoque': forms.Select(attrs={'class': 'form-control select2'}),
            'id_programacion': forms.Select(attrs={'class': 'form-control select2'}),
            'id_temporalidad': forms.Select(attrs={'class': 'form-control select2'})
        }
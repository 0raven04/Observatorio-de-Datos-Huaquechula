from django import forms
from .models import RegistroVisita, PersonaVisita, EncuestaResidente, EncuestaComercio 
from django.forms import inlineformset_factory

class RegistroVisitaForm(forms.ModelForm):
    class Meta:
        model = RegistroVisita
        exclude = ['id_encuestador', 'fecha']

PersonaFormSet = inlineformset_factory(
    RegistroVisita,
    PersonaVisita,
    fields=('edad', 'sexo'),
    extra=1,
    can_delete=False
)

class EncuestaResidenteForm(forms.ModelForm):
    class Meta:
        model = EncuestaResidente
        exclude = ['encuestador', 'fecha']
        widgets = {
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'barrio_colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'confianza_policia': forms.Select(attrs={'class': 'form-select'}),
            'percepcion_inseguridad': forms.Select(attrs={'class': 'form-select'}),
            'tension_festividades': forms.Select(attrs={'class': 'form-select'}),
            'acceso_servicios_festividades': forms.Select(attrs={'class': 'form-select'}),
            'perdida_tradicion': forms.Select(attrs={'class': 'form-select'}),
            'calidad_aire': forms.Select(attrs={'class': 'form-select'}),
            'gestion_residuos': forms.Select(attrs={'class': 'form-select'}),
        }

class EncuestaComercioForm(forms.ModelForm):
    class Meta:
        model = EncuestaComercio
        exclude = ['encuestador', 'fecha']
        widgets = {
            'tipo_comercio': forms.Select(attrs={'class': 'form-select'}),
            'participacion_decisiones': forms.Select(attrs={'class': 'form-select'}),
            'capacitacion_turistica': forms.Select(attrs={'class': 'form-select'}),
            'integracion_turistica': forms.Select(attrs={'class': 'form-select'}),
        }

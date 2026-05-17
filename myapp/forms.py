from django import forms
from .models import RegistroVisita, EncuestaResidente, EncuestaComercio 
from django.forms import inlineformset_factory

class RegistroVisitaForm(forms.ModelForm):
    class Meta:
        model = RegistroVisita
        fields = [
            'estancia_dias',
            'motivo_visita',
            'tipo_transporte',
            'procedencia',
            'pais_origen',
            'es_extranjero',
            'clave_encuestador',
            # Campos de distribución por edad y género
            'mujeres_0_15',
            'mujeres_16_30',
            'mujeres_31_45',
            'mujeres_46_60',
            'mujeres_61_75',
            'mujeres_76_mas',
            'hombres_0_15',
            'hombres_16_30',
            'hombres_31_45',
            'hombres_46_60',
            'hombres_61_75',
            'hombres_76_mas',
        ]
        widgets = {
            'estancia_dias': forms.NumberInput(attrs={
                'min': 1,
                'max': 255,
                'class': 'form-control',
                'placeholder': 'Días de estancia'
            }),
            'motivo_visita': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo_transporte': forms.Select(attrs={
                'class': 'form-control'
            }),
            'procedencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Ciudad de México',
                'maxlength': 100
            }),
            'pais_origen': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País de origen',
                'maxlength': 100
            }),
            'es_extranjero': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'clave_encuestador': forms.Select(attrs={
                'class': 'form-control'
            }),
            # Campos de distribución con estilo similar
            'mujeres_0_15': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '0_15',
                'data-gender': 'mujeres'
            }),
            'mujeres_16_30': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '16_30',
                'data-gender': 'mujeres'
            }),
            'mujeres_31_45': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '31_45',
                'data-gender': 'mujeres'
            }),
            'mujeres_46_60': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '46_60',
                'data-gender': 'mujeres'
            }),
            'mujeres_61_75': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '61_75',
                'data-gender': 'mujeres'
            }),
            'mujeres_76_mas': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '76_mas',
                'data-gender': 'mujeres'
            }),
            'hombres_0_15': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '0_15',
                'data-gender': 'hombres'
            }),
            'hombres_16_30': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '16_30',
                'data-gender': 'hombres'
            }),
            'hombres_31_45': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '31_45',
                'data-gender': 'hombres'
            }),
            'hombres_46_60': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '46_60',
                'data-gender': 'hombres'
            }),
            'hombres_61_75': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '61_75',
                'data-gender': 'hombres'
            }),
            'hombres_76_mas': forms.NumberInput(attrs={
                'min': 0,
                'max': 255,
                'class': 'form-control age-input',
                'data-group': '76_mas',
                'data-gender': 'hombres'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que al menos haya una persona
        total_mujeres = sum([
            cleaned_data.get('mujeres_0_15', 0),
            cleaned_data.get('mujeres_16_30', 0),
            cleaned_data.get('mujeres_31_45', 0),
            cleaned_data.get('mujeres_46_60', 0),
            cleaned_data.get('mujeres_61_75', 0),
            cleaned_data.get('mujeres_76_mas', 0),
        ])
        
        total_hombres = sum([
            cleaned_data.get('hombres_0_15', 0),
            cleaned_data.get('hombres_16_30', 0),
            cleaned_data.get('hombres_31_45', 0),
            cleaned_data.get('hombres_46_60', 0),
            cleaned_data.get('hombres_61_75', 0),
            cleaned_data.get('hombres_76_mas', 0),
        ])
        
        total_personas = total_mujeres + total_hombres
        
        if total_personas == 0:
            raise forms.ValidationError("Debe ingresar al menos una persona para registrar.")
        
        # Si es extranjero, validar que se especifique país
        es_extranjero = cleaned_data.get('es_extranjero', False)
        pais_origen = cleaned_data.get('pais_origen', '')
        
        if es_extranjero and not pais_origen:
            self.add_error('pais_origen', 'Si es extranjero, debe especificar el país de origen.')
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer valores por defecto
        for field in [
            'mujeres_0_15', 'mujeres_16_30', 'mujeres_31_45',
            'mujeres_46_60', 'mujeres_61_75', 'mujeres_76_mas',
            'hombres_0_15', 'hombres_16_30', 'hombres_31_45',
            'hombres_46_60', 'hombres_61_75', 'hombres_76_mas'
        ]:
            if not self.initial.get(field):
                self.initial[field] = 0
        
        # Hacer que el campo país sea requerido condicionalmente
        self.fields['pais_origen'].required = False
        exclude = ['id_encuestador', 'fecha']



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

from django import forms
from .models import RegistroVisita, PersonaVisita, EncuestaResidente, EncuestaInstitucional, EncuestaVisitante
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
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 127, 'placeholder': 'Edad en años'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'barrio_colonia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Centro, San Martín...'}),
            'alteracion_rutina': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'acceso_servicios_festividades': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'desvirtuacion_tradicion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'participacion_preservacion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'participacion_decisiones': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'capacitacion_turistica': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'beneficio_economico': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'interes_jovenes': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quitar la opción vacía "---------" de los campos tipo RadioSelect
        for field_name in [
            'alteracion_rutina', 'acceso_servicios_festividades',
            'desvirtuacion_tradicion', 'participacion_preservacion',
            'participacion_decisiones', 'capacitacion_turistica',
            'beneficio_economico', 'interes_jovenes'
        ]:
            if field_name in self.fields:
                self.fields[field_name].choices = [
                    c for c in self.fields[field_name].choices if c[0] not in ('', None)
                ]

class EncuestaInstitucionalForm(forms.ModelForm):
    # Opciones para el campo de selección múltiple (canales_difusion)
    CANALES_DIFUSION_CHOICES = [
        ('Campañas digitales y uso de redes sociales institucionales', 'Campañas digitales y uso de redes sociales institucionales'),
        ('Vinculación con agencias de viaje o secretarías de turismo estatal/federal', 'Vinculación con agencias de viaje o secretarías de turismo estatal/federal'),
        ('Publicaciones académicas, folletería impresa y guías locales', 'Publicaciones académicas, folletería impresa y guías locales'),
        ('Eventos, ferias de turismo o intercambios culturales exteriores', 'Eventos, ferias de turismo o intercambios culturales exteriores'),
        ('Ninguno', 'Ninguno')
    ]
    canales_difusion = forms.MultipleChoiceField(
        choices=CANALES_DIFUSION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='2. ¿Cuáles son los canales oficiales y mecanismos institucionales implementados en el último año para la difusión nacional e internacional del PCI de Huaquechula?'
    )

    class Meta:
        model = EncuestaInstitucional
        exclude = ['encuestador', 'fecha']
        widgets = {
            'registro_pci': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'mecanismos_regulacion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'plan_desarrollo': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'porcentaje_comunidades': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'visitantes_ano': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ej. 15000'}),
            'visitantes_tradicion': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Ej. 5000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quitar la opción vacía "---------" de los campos tipo RadioSelect
        for field_name in [
            'registro_pci', 'mecanismos_regulacion',
            'plan_desarrollo', 'porcentaje_comunidades'
        ]:
            if field_name in self.fields:
                self.fields[field_name].choices = [
                    c for c in self.fields[field_name].choices if c[0] not in ('', None)
                ]


class EncuestaVisitanteForm(forms.ModelForm):
    zonas_visitadas = forms.MultipleChoiceField(
        choices=EncuestaVisitante.ZONAS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='¿Cuáles zonas visitaste o piensas visitar?',
    )
    actividades = forms.MultipleChoiceField(
        choices=EncuestaVisitante.ACTIVIDADES_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='¿Qué actividades realizaste durante tu estancia?',
    )

    class Meta:
        model = EncuestaVisitante
        exclude = ['encuestador', 'fecha']
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 127, 'placeholder': 'Edad en años'}),
            'grupo_viaje': forms.Select(attrs={'class': 'form-select'}),
            'ciudad_origen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Ciudad de Puebla'}),
            'estado_origen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Puebla'}),
            'pais_origen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. México'}),
            'calificacion': forms.RadioSelect(attrs={'class': 'star-rating-input'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Cuéntanos brevemente tu experiencia...'}),
        }


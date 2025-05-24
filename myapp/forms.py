from django import forms
from .models import RegistroVisita, PersonaVisita 
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
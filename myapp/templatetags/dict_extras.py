"""
Filtros de template personalizados para el Observatorio.
Permite acceder a valores de un diccionario usando una clave dinámica en templates.

Uso:
    {% load dict_extras %}
    {{ indicators_data|get_item:indicador.pk }}
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Permite acceder a un dict con clave dinámica en el template: dict|get_item:key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

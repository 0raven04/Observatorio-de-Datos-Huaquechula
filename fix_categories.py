import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Categoria

def fix_categories():
    """
    Corrige los nombres de las categorías con problemas de codificación.
    """
    corrections = {
        "Documentos hist?ricos": "Documentos históricos",
        "Galer?a de videos": "Galería de videos",
        "Documentos t?cnicos": "Documentos técnicos",
        "Gu?as": "Guías",
        "Pol?ticas": "Políticas"
    }
    
    count = 0
    for bad_name, good_name in corrections.items():
        # Buscar categorías que contengan el nombre "malo" o sean exactamente el nombre malo
        # Usamos icontains para ser más flexibles, o exact para ser precisos.
        # Dado que el usuario reportó "Documentos hist?ricos", usaremos exact o filter.
        
        # Intentar buscar coincidencia exacta primero
        cats = Categoria.objects.filter(nombre__icontains=bad_name)
        
        for cat in cats:
            print(f"Corrigiendo: '{cat.nombre}' -> '{good_name}'")
            cat.nombre = good_name
            cat.save()
            count += 1
            
    # También buscar cualquier categoría con '?' y tratar de adivinar o reportar
    others = Categoria.objects.filter(nombre__contains='?')
    for cat in others:
        print(f"ADVERTENCIA: Categoría con '?' encontrada y no corregida automáticamente: '{cat.nombre}'")

    print(f"Total de categorías corregidas: {count}")

if __name__ == '__main__':
    fix_categories()

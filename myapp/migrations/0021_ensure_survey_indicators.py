from django.db import migrations


def seed_survey_indicators(apps, schema_editor):
    CategoriaIndicador = apps.get_model('myapp', 'CategoriaIndicador')
    Indicador = apps.get_model('myapp', 'Indicador')
    
    # Obtener categorías existentes
    cat_gestion = CategoriaIndicador.objects.filter(id=4).first()
    if not cat_gestion:
        cat_gestion = CategoriaIndicador.objects.first()
    
    cat_pci = CategoriaIndicador.objects.filter(id=3).first() or cat_gestion

    # Asegurar indicadores requeridos para los agregados de encuestas
    indicators = [
        (57, "Índice de satisfacción de visitantes", "Escala 1 a 5", cat_gestion),
        (55, "Afluencia durante la tradición", "Visitantes", cat_pci),
        (56, "Visitantes anuales", "Personas", cat_pci),
    ]

    for ind_id, nombre, unidad, cat in indicators:
        if not Indicador.objects.filter(id=ind_id).exists():
            Indicador.objects.create(
                id=ind_id,
                categoria=cat,
                nombre=nombre,
                unidad_medida=unidad,
                descripcion=f"Indicador calculado a partir de encuestas ({nombre})",
                data_source="manual"
            )


def run_survey_indicator_calculation(apps, schema_editor):
    try:
        from myapp.utils_surveys import update_survey_indicators
        update_survey_indicators()
    except Exception as e:
        print(f"Aviso durante cálculo de encuestas en migración: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_encuestaresidente_beneficio_economico_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_survey_indicators, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(run_survey_indicator_calculation, reverse_code=migrations.RunPython.noop),
    ]

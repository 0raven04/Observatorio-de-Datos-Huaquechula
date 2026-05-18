# State-only migration: sync Django's model state with the DB schema
# The actual DB changes were already done in 0007_recreate_encuestaresidente.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_recreate_encuestaresidente'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                # Remove old fields
                migrations.RemoveField(model_name='encuestaresidente', name='confianza_policia'),
                migrations.RemoveField(model_name='encuestaresidente', name='percepcion_inseguridad'),
                migrations.RemoveField(model_name='encuestaresidente', name='tension_festividades'),
                migrations.RemoveField(model_name='encuestaresidente', name='perdida_tradicion'),
                migrations.RemoveField(model_name='encuestaresidente', name='calidad_aire'),
                migrations.RemoveField(model_name='encuestaresidente', name='gestion_residuos'),

                # Add new fields
                migrations.AddField(
                    model_name='encuestaresidente',
                    name='alteracion_rutina',
                    field=models.PositiveSmallIntegerField(choices=[(1, 'No altera nada'), (2, 'Altera poco'), (3, 'Altera de forma regular'), (4, 'Altera mucho')], default=1, verbose_name='1. ¿Qué tanto considera que la afluencia de visitantes altera negativamente su rutina diaria durante las festividades?'),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='encuestaresidente',
                    name='desvirtuacion_tradicion',
                    field=models.PositiveSmallIntegerField(choices=[(1, 'Sí, se ha comercializado excesivamente y pierde su esencia comunitaria'), (2, 'Parcialmente, conviven la tradición y el comercio de forma equilibrada'), (3, 'No, la tradición se mantiene intacta y fuerte')], default=1, verbose_name='3. ¿Considera que el turismo ha provocado cambios que desvirtúan el significado original de nuestras tradiciones?'),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='encuestaresidente',
                    name='participacion_preservacion',
                    field=models.PositiveSmallIntegerField(choices=[(1, 'Sí, participo activamente de manera directa'), (2, 'No participo directamente, pero apoyo la organización local'), (3, 'No participo en absoluto')], default=1, verbose_name='4. ¿Participa usted de forma activa en actividades de preservación (artesanías, cocina tradicional, altares monumentales)?'),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='encuestaresidente',
                    name='participacion_decisiones',
                    field=models.PositiveSmallIntegerField(choices=[(1, 'Sí, asisto con regularidad y se toman en cuenta mis opiniones'), (2, 'He sido convocado, pero no asisto o no se toman en cuenta las opiniones'), (3, 'Nunca he sido convocado ni informado sobre estas decisiones')], default=1, verbose_name='5. ¿Ha participado o ha sido convocado a reuniones para decidir cómo debe gestionarse el turismo en su localidad?'),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='encuestaresidente',
                    name='capacitacion_turistica',
                    field=models.PositiveSmallIntegerField(choices=[(1, 'Sí, he recibido capacitación continua'), (2, 'Recibí información aislada, pero no capacitación formal'), (3, 'No he recibido ninguna información ni capacitación')], default=1, verbose_name='6. ¿Ha recibido capacitación o información clara sobre cómo emprender o atender al turismo de manera responsable?'),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='encuestaresidente',
                    name='beneficio_economico',
                    field=models.PositiveSmallIntegerField(choices=[(1, 'Sí, es nuestra fuente de ingresos principal'), (2, 'Sí, funciona como una actividad económica complementaria'), (3, 'No, no percibimos ningún beneficio directo de la actividad turística')], default=1, verbose_name='7. ¿Su hogar percibe un beneficio económico o social directo derivado de algún proyecto turístico local?'),
                    preserve_default=False,
                ),

                # Update existing field choices
                migrations.AlterField(
                    model_name='encuestaresidente',
                    name='acceso_servicios_festividades',
                    field=models.PositiveSmallIntegerField(choices=[(1, 'Excelente (Los servicios operan con normalidad)'), (2, 'Regular (Se nota escasez o retrasos temporales)'), (3, 'Deficiente (Hay cortes de servicios o fallas graves debido al turismo)')], verbose_name='2. ¿Cómo califica el acceso y disponibilidad de servicios públicos durante las temporadas festivas?'),
                ),
            ]
        )
    ]

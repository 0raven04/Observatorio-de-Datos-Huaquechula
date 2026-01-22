"""
Comando de gestión Django para sincronizar indicadores con la API del INEGI.

Uso:
    python manage.py sync_inegi                    # Sincronizar todos los indicadores
    python manage.py sync_inegi --indicator-id 5   # Sincronizar un indicador específico
    python manage.py sync_inegi --dry-run          # Simular sin guardar cambios
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from myapp.models import Indicador
from myapp.services.inegi_service import INEGIService, INEGI_INDICATOR_MAPPING


class Command(BaseCommand):
    help = 'Sincroniza indicadores del Observatorio con datos de la API del INEGI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--indicator-id',
            type=int,
            help='ID específico del indicador local a sincronizar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la sincronización sin guardar cambios'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la sincronización incluso si no hay ID de INEGI configurado'
        )

    def handle(self, *args, **options):
        # Verificar configuración del token
        token = getattr(settings, 'INEGI_API_TOKEN', None)
        
        if not token or token == 'your_token_here':
            self.stdout.write(
                self.style.ERROR(
                    '❌ Token de INEGI no configurado.\n'
                    'Por favor, configura INEGI_API_TOKEN en settings.py o como variable de entorno.\n'
                    'Obtén tu token en: https://www.inegi.org.mx/app/api/indicadores/'
                )
            )
            return
        
        # Inicializar servicio
        service = INEGIService(token)
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando sincronización con INEGI...\n')
        )
        
        # Sincronizar indicador específico o todos
        if options['indicator_id']:
            self._sync_single_indicator(service, options['indicator_id'], options['dry_run'])
        else:
            self._sync_all_indicators(service, options['dry_run'], options['force'])

    def _sync_single_indicator(self, service, indicator_id, dry_run):
        """Sincroniza un indicador específico."""
        try:
            indicador = Indicador.objects.get(id=indicator_id)
        except Indicador.DoesNotExist:
            raise CommandError(f'Indicador con ID {indicator_id} no existe')
        
        self.stdout.write(f'\n📊 Sincronizando: {indicador.nombre}')
        
        # Verificar si tiene ID de INEGI configurado
        if not hasattr(indicador, 'inegi_indicator_id') or not indicador.inegi_indicator_id:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Este indicador no tiene ID de INEGI configurado.\n'
                    f'   Puedes agregarlo editando el modelo o usando el mapeo manual.'
                )
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 Modo DRY-RUN: No se guardarán cambios')
            )
            # Simular consulta
            data = service.fetch_indicator_data(indicador.inegi_indicator_id)
            if data:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Se obtendrían {len(data)} períodos de datos'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No se pudieron obtener datos')
                )
        else:
            count = service.sync_indicator_from_inegi(indicador, indicador.inegi_indicator_id)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Sincronizados {count} nuevos registros'
                )
            )

    def _sync_all_indicators(self, service, dry_run, force):
        """Sincroniza todos los indicadores que tengan ID de INEGI."""
        # Buscar indicadores con ID de INEGI
        if hasattr(Indicador, 'inegi_indicator_id'):
            indicadores = Indicador.objects.filter(
                data_source='inegi',
                inegi_indicator_id__isnull=False
            ).exclude(inegi_indicator_id='')
        else:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  El modelo Indicador no tiene el campo inegi_indicator_id.\n'
                    '   Usando mapeo manual de indicadores...\n'
                )
            )
            # Usar mapeo manual
            indicadores = []
        
        if not indicadores and not force:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  No hay indicadores configurados para sincronizar con INEGI.\n'
                    '   Usa --force para intentar sincronizar usando el mapeo manual.'
                )
            )
            return
        
        total_synced = 0
        total_indicators = len(indicadores)
        
        self.stdout.write(f'\n📈 Sincronizando {total_indicators} indicadores...\n')
        
        for indicador in indicadores:
            self.stdout.write(f'  • {indicador.nombre}... ', ending='')
            
            if dry_run:
                data = service.fetch_indicator_data(indicador.inegi_indicator_id)
                if data:
                    self.stdout.write(
                        self.style.SUCCESS(f'OK ({len(data)} períodos)')
                    )
                else:
                    self.stdout.write(self.style.ERROR('ERROR'))
            else:
                try:
                    count = service.sync_indicator_from_inegi(
                        indicador, 
                        indicador.inegi_indicator_id
                    )
                    total_synced += count
                    self.stdout.write(
                        self.style.SUCCESS(f'OK (+{count})')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'ERROR: {str(e)}')
                    )
        
        # Resumen final
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Simulación completada para {total_indicators} indicadores'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Sincronización completada!\n'
                    f'   Total de nuevos registros: {total_synced}'
                )
            )

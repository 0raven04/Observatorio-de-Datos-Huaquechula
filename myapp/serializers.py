"""
Serializers DRF para la API Móvil del Observatorio de Datos Huaquechula.
Convierten los modelos Django a JSON y viceversa para la app móvil.
"""
from rest_framework import serializers
from .models import (
    Usuario, Encuestador,
    RegistroVisita,
    Eje, CategoriaIndicador, Indicador, Medicion,
    EncuestaResidente, EncuestaInstitucional
)


# ─── Usuarios ─────────────────────────────────────────────────────────────────

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'ap', 'am', 'nombre_usuario', 'email', 'tipo']
        read_only_fields = ['id_usuario']


# ─── Registros de Visita ───────────────────────────────────────────────────────

class RegistroVisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroVisita
        fields = [
            'id_registro', 'fecha',
            'estancia_dias', 'visitas_previas', 'motivo_visita', 'tipo_transporte',
            'procedencia', 'pais_origen', 'es_extranjero', 'clave_encuestador',
            'mujeres_0_15', 'mujeres_16_30', 'mujeres_31_45',
            'mujeres_46_60', 'mujeres_61_75', 'mujeres_76_mas',
            'hombres_0_15', 'hombres_16_30', 'hombres_31_45',
            'hombres_46_60', 'hombres_61_75', 'hombres_76_mas',
        ]
        read_only_fields = ['id_registro', 'fecha']


# ─── Indicadores del Observatorio ─────────────────────────────────────────────

class MedicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicion
        fields = ['id', 'periodo', 'valor', 'fecha_registro']


class IndicadorSerializer(serializers.ModelSerializer):
    mediciones = MedicionSerializer(many=True, read_only=True)

    class Meta:
        model = Indicador
        fields = [
            'id', 'nombre', 'descripcion', 'unidad_medida',
            'data_source', 'last_sync', 'encuesta_tipo', 'encuesta_pregunta', 'mediciones'
        ]


class CategoriaIndicadorSerializer(serializers.ModelSerializer):
    indicadores = IndicadorSerializer(many=True, read_only=True)

    class Meta:
        model = CategoriaIndicador
        fields = ['id', 'nombre', 'indicadores']


class EjeSerializer(serializers.ModelSerializer):
    categorias = CategoriaIndicadorSerializer(many=True, read_only=True)

    class Meta:
        model = Eje
        fields = ['id', 'nombre', 'descripcion', 'categorias']


# ─── Encuestas (alimentación manual del Observatorio) ─────────────────────────

class EncuestaResidenteSerializer(serializers.ModelSerializer):
    """
    Serializer para encuestas de Residentes Locales.
    - GET: incluye fecha y encuestador (clave).
    - POST: acepta las respuestas; encuestador se asigna en la vista.
    """
    encuestador_clave = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EncuestaResidente
        fields = [
            'id', 'fecha', 'encuestador_clave',
            'edad', 'genero', 'barrio_colonia',
            'alteracion_rutina', 'acceso_servicios_festividades',
            'desvirtuacion_tradicion', 'participacion_preservacion',
            'participacion_decisiones', 'capacitacion_turistica',
            'beneficio_economico', 'interes_jovenes',
        ]
        read_only_fields = ['id', 'fecha', 'encuestador_clave']

    def get_encuestador_clave(self, obj):
        return obj.encuestador.clave_encuestador if obj.encuestador else None


class EncuestaInstitucionalSerializer(serializers.ModelSerializer):
    """
    Serializer para encuestas Institucionales.
    """
    encuestador_clave = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EncuestaInstitucional
        fields = [
            'id', 'fecha', 'encuestador_clave',
            'registro_pci', 'canales_difusion', 'mecanismos_regulacion',
            'plan_desarrollo', 'porcentaje_comunidades',
            'visitantes_ano', 'visitantes_tradicion',
        ]
        read_only_fields = ['id', 'fecha', 'encuestador_clave']

    def get_encuestador_clave(self, obj):
        return obj.encuestador.clave_encuestador if obj.encuestador else None

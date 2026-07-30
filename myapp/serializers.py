"""
Serializers DRF para la API Móvil del Observatorio de Datos Huaquechula.
Convierten los modelos Django a JSON y viceversa para la app móvil.
"""
from rest_framework import serializers
from .models import (
    Usuario, Encuestador,
    RegistroVisita,
    Eje, CategoriaIndicador, Indicador, Medicion,
    EncuestaVisitante, EncuestaResidente, EncuestaInstitucional, EncuestaComercio,
    Encuesta, Pregunta, OpcionPregunta
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
            'data_source', 'last_sync', 'mediciones'
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

class EncuestaVisitanteSerializer(serializers.ModelSerializer):
    """
    Serializer para Encuesta: Perfil del Visitante.
    """
    encuestador_clave = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EncuestaVisitante
        fields = [
            'id', 'fecha', 'encuestador_clave',
            'genero', 'edad', 'viaja_con',
            'residencia_ciudad', 'residencia_estado', 'residencia_pais',
            'zonas_visitadas', 'actividades',
            'satisfaccion', 'lo_que_mas_gusto',
        ]
        read_only_fields = ['id', 'fecha', 'encuestador_clave']

    def get_encuestador_clave(self, obj):
        return obj.encuestador.clave_encuestador if obj.encuestador else None


class EncuestaResidenteSerializer(serializers.ModelSerializer):
    """
    Serializer para encuestas de Residentes Locales.
    """
    encuestador_clave = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EncuestaResidente
        fields = [
            'id', 'fecha', 'encuestador_clave',
            'edad', 'genero', 'barrio_colonia',
            'confianza_policia', 'percepcion_inseguridad',
            'tension_festividades', 'acceso_servicios_festividades', 'perdida_tradicion',
            'participacion_preservacion', 'participacion_decisiones', 'capacitacion_turistica',
            'beneficio_economico', 'interes_jovenes',
        ]
        read_only_fields = ['id', 'fecha', 'encuestador_clave']

    def get_encuestador_clave(self, obj):
        return obj.encuestador.clave_encuestador if obj.encuestador else None


class EncuestaInstitucionalSerializer(serializers.ModelSerializer):
    """
    Serializer para Encuesta: Institucional / Gobernanza.
    """
    encuestador_clave = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EncuestaInstitucional
        fields = [
            'id', 'fecha', 'encuestador_clave',
            'seguimiento_salvaguardia', 'canales_difusion', 'visitantes_festividades',
            'regulacion', 'gestion_tecnica', 'integracion_territorial', 'visitantes_anual',
        ]
        read_only_fields = ['id', 'fecha', 'encuestador_clave']

    def get_encuestador_clave(self, obj):
        return obj.encuestador.clave_encuestador if obj.encuestador else None


class EncuestaComercioSerializer(serializers.ModelSerializer):
    """
    Serializer para encuestas de Comercios / Artesanos.
    """
    encuestador_clave = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EncuestaComercio
        fields = [
            'id', 'fecha', 'encuestador_clave',
            'tipo_comercio',
            'participacion_decisiones', 'capacitacion_turistica', 'integracion_turistica',
        ]
        read_only_fields = ['id', 'fecha', 'encuestador_clave']

    def get_encuestador_clave(self, obj):
        return obj.encuestador.clave_encuestador if obj.encuestador else None


# ─── Encuestas Creadas / Dinámicas ─────────────────────────────────────────────

class OpcionPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionPregunta
        fields = ['id', 'texto', 'orden']


class PreguntaSerializer(serializers.ModelSerializer):
    opciones = OpcionPreguntaSerializer(many=True, read_only=True)

    class Meta:
        model = Pregunta
        fields = ['id', 'texto', 'tipo_pregunta', 'requerida', 'orden', 'opciones']


class EncuestaCreadaSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True)

    class Meta:
        model = Encuesta
        fields = ['id', 'titulo', 'descripcion', 'activa', 'anonima', 'fecha_creacion', 'preguntas']

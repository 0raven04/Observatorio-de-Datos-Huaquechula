"""
Serializers DRF para la API Móvil del Observatorio de Datos Huaquechula.
Convierten los modelos Django a JSON y viceversa para la app móvil.
"""
from rest_framework import serializers
from .models import (
    Usuario, Encuestador,
    RegistroVisita, PersonaVisita,
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

class PersonaVisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaVisita
        fields = ['id_persona', 'edad', 'sexo']
        read_only_fields = ['id_persona']


class RegistroVisitaSerializer(serializers.ModelSerializer):
    """
    Serializer completo del registro de visita.
    - En lectura (GET): incluye las personas anidadas y la clave del encuestador.
    - En escritura (POST/PUT): acepta la lista de personas para crearlas automáticamente.
    """
    personas = PersonaVisitaSerializer(
        many=True,
        source='personas_visita',
        read_only=True
    )
    personas_input = PersonaVisitaSerializer(
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = RegistroVisita
        fields = [
            'id_registro', 'fecha',
            'tamanio_grupo', 'es_extranjero', 'pais_origen', 'procedencia',
            'tipo_transporte', 'motivo_visita', 'estancia_dias', 'numero_visitas',
            'id_encuestador',
            'personas',         # read-only (respuesta)
            'personas_input',   # write-only (entrada)
        ]
        read_only_fields = ['id_registro', 'fecha']

    def create(self, validated_data):
        personas_data = validated_data.pop('personas_input', [])
        registro = RegistroVisita.objects.create(**validated_data)

        personas_objs = [
            PersonaVisita(id_registro=registro, **p)
            for p in personas_data
            if p.get('edad') is not None and p.get('sexo') in ['Hombre', 'Mujer', 'Otro']
        ]
        if personas_objs:
            PersonaVisita.objects.bulk_create(personas_objs)

        return registro

    def update(self, instance, validated_data):
        personas_data = validated_data.pop('personas_input', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if personas_data is not None:
            PersonaVisita.objects.filter(id_registro=instance).delete()
            personas_objs = [
                PersonaVisita(id_registro=instance, **p)
                for p in personas_data
                if p.get('edad') is not None and p.get('sexo') in ['Hombre', 'Mujer', 'Otro']
            ]
            if personas_objs:
                PersonaVisita.objects.bulk_create(personas_objs)

        return instance


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

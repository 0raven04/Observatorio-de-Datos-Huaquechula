from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario, Encuesta, Pregunta, OpcionPregunta, RespuestaEncuesta, RespuestaPregunta

class EncuestasDynamicTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear un usuario administrador
        self.admin_user = Usuario.objects.create_user(
            nombre_usuario="admin_test",
            email="admin@test.com",
            nombre="Admin",
            ap="Test",
            tipo="admin",
            password="secure_password_123"
        )
        
        # Crear una encuesta de prueba
        self.encuesta = Encuesta.objects.create(
            titulo="Encuesta de Satisfacción",
            descripcion="Descripción de prueba",
            anonima=True,
            activa=True,
            creador=self.admin_user
        )
        
        # Crear preguntas
        self.p_texto = Pregunta.objects.create(
            encuesta=self.encuesta,
            texto="¿Cuál es tu nombre?",
            tipo_pregunta="TEXTO",
            requerida=True,
            orden=0
        )
        
        self.p_multiple = Pregunta.objects.create(
            encuesta=self.encuesta,
            texto="¿Te gusta la app?",
            tipo_pregunta="OPCION_MULTIPLE",
            requerida=False,
            orden=1
        )
        
        self.opt1 = OpcionPregunta.objects.create(
            pregunta=self.p_multiple,
            texto="Sí",
            orden=0
        )
        self.opt2 = OpcionPregunta.objects.create(
            pregunta=self.p_multiple,
            texto="No",
            orden=1
        )

    def test_model_creation(self):
        self.assertEqual(Encuesta.objects.count(), 1)
        self.assertEqual(Pregunta.objects.count(), 2)
        self.assertEqual(OpcionPregunta.objects.count(), 2)
        
    def test_public_survey_fill(self):
        # Enviar respuestas mediante POST
        response_url = reverse('responder_encuesta', args=[self.encuesta.id])
        post_data = {
            f'pregunta_{self.p_texto.id}': 'Juan Pérez',
            f'pregunta_{self.p_multiple.id}': 'Sí'
        }
        
        response = self.client.post(response_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "¡Gracias por participar!")
        
        # Verificar que se hayan creado los registros en la base de datos
        self.assertEqual(RespuestaEncuesta.objects.count(), 1)
        self.assertEqual(RespuestaPregunta.objects.count(), 2)
        
        resp_texto = RespuestaPregunta.objects.get(pregunta=self.p_texto)
        self.assertEqual(resp_texto.valor_texto, "Juan Pérez")
        
        resp_mult = RespuestaPregunta.objects.get(pregunta=self.p_multiple)
        self.assertEqual(resp_mult.valor_texto, "Sí")


class CircuitosTuristicosTestCase(TestCase):
    def test_tsp_2opt_optimizacion(self):
        from myapp.services.circuit_service import resolver_tsp_2opt
        nodos = [
            {'id_punto': 0, 'nombre': 'Origen', 'lat': 18.769895, 'lng': -98.544040, 'es_origen': True},
            {'id_punto': 1, 'nombre': 'Punto A', 'lat': 18.771200, 'lng': -98.542100, 'es_origen': False},
            {'id_punto': 2, 'nombre': 'Punto B', 'lat': 18.768100, 'lng': -98.546000, 'es_origen': False},
            {'id_punto': 3, 'nombre': 'Punto C', 'lat': 18.773000, 'lng': -98.541000, 'es_origen': False},
        ]
        ruta, dist = resolver_tsp_2opt(nodos, circuito_cerrado=True)
        # El origen debe ser siempre el primer elemento
        self.assertEqual(ruta[0]['id_punto'], 0)
        self.assertEqual(len(ruta), 4)
        self.assertGreater(dist, 0)

    def test_api_circuito_endpoint(self):
        url = reverse('api_generar_circuito_turistico')
        response = self.client.get(url, {'categoria': 'ofrenda'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('resumen', data)
        self.assertIn('paradas', data)



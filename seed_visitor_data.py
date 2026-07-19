import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(r'c:\Users\BORRE117\Downloads\Huaquechula P\Observatorio-de-Datos-Huaquechula')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Usuario, Encuestador, RegistroVisita, EncuestaVisitante
from django.utils import timezone

def seed_data():
    print("Iniciando la generación de datos de prueba para estadísticas...")
    
    # 1. Obtener o crear un Encuestador
    user, created = Usuario.objects.get_or_create(
        nombre_usuario="encuestador_demo",
        defaults={
            "nombre": "Demo",
            "ap": "Encuestador",
            "email": "demo@observatorio.com",
            "tipo": "encuestador",
            "is_active": True
        }
    )
    if created:
        user.set_password("demo1234")
        user.save()
        print("Creado usuario encuestador_demo.")
    
    encuestador, created = Encuestador.objects.get_or_create(id_usuario=user)
    if created:
        print("Creado perfil de Encuestador para el demo.")

    # Limpiar datos previos si el usuario quiere una demo fresca (opcional, pero mejor añadir para no duplicar demasiado)
    # RegistroVisita.objects.all().delete()
    # EncuestaVisitante.objects.all().delete()
    # print("Datos anteriores limpiados.")

    # 2. Generar RegistroVisita a lo largo de los últimos 12 meses
    procedencias_mex = [
        ("Puebla", "Puebla", "México", False),
        ("Ciudad de México", "CDMX", "México", False),
        ("Atlixco", "Puebla", "México", False),
        ("Izúcar de Matamoros", "Puebla", "México", False),
        ("Cuernavaca", "Morelos", "México", False),
        ("Monterrey", "Nuevo León", "México", False),
        ("Guadalajara", "Jalisco", "México", False),
        ("Veracruz", "Veracruz", "México", False),
        ("Oaxaca", "Oaxaca", "México", False),
    ]
    
    procedencias_ext = [
        ("New York", "New York", "Estados Unidos", True),
        ("Los Angeles", "California", "Estados Unidos", True),
        ("Madrid", "Madrid", "España", True),
        ("París", "Île-de-France", "Francia", True),
        ("Bogotá", "Cundinamarca", "Colombia", True),
        ("Berlín", "Berlín", "Alemania", True),
    ]

    motivos = ['turismo', 'negocios', 'visita_familiar', 'estudios', 'otros']
    transportes = ['automovil', 'autobus', 'avion', 'tren', 'otros']
    
    hoy = timezone.now()
    total_registros_creados = 0
    total_encuestas_creadas = 0

    print("Generando registros de visitas (RegistroVisita)...")
    for i in range(12): # Últimos 12 meses
        # Calcular fecha del mes
        mes_offset = hoy - timedelta(days=30 * i)
        
        # Generar entre 10 y 20 registros de visita por mes
        num_registros = random.randint(10, 20)
        for _ in range(num_registros):
            # 15% de probabilidad de ser extranjero
            if random.random() < 0.15:
                ciudad, estado, pais, extranjero = random.choice(procedencias_ext)
            else:
                ciudad, estado, pais, extranjero = random.choice(procedencias_mex)
                
            # Distribución aleatoria de personas por edad y género
            muj_0_15 = random.randint(0, 2)
            muj_16_30 = random.randint(0, 4)
            muj_31_45 = random.randint(0, 3)
            muj_46_60 = random.randint(0, 2)
            muj_61_75 = random.randint(0, 1)
            muj_76_mas = random.randint(0, 1)
            
            hom_0_15 = random.randint(0, 2)
            hom_16_30 = random.randint(0, 3)
            hom_31_45 = random.randint(0, 4)
            hom_46_60 = random.randint(0, 2)
            hom_61_75 = random.randint(0, 1)
            hom_76_mas = random.randint(0, 1)
            
            # Asegurarse de tener al menos 1 persona
            if (muj_0_15 + muj_16_30 + muj_31_45 + muj_46_60 + muj_61_75 + muj_76_mas +
                hom_0_15 + hom_16_30 + hom_31_45 + hom_46_60 + hom_61_75 + hom_76_mas) == 0:
                muj_16_30 = 2
                
            registro = RegistroVisita.objects.create(
                estancia_dias=random.randint(1, 4),
                visitas_previas=random.randint(1, 3),
                motivo_visita=random.choice(motivos),
                tipo_transporte=random.choice(transportes),
                procedencia=ciudad,
                pais_origen=pais,
                es_extranjero=extranjero,
                clave_encuestador=encuestador,
                mujeres_0_15=muj_0_15,
                mujeres_16_30=muj_16_30,
                mujeres_31_45=muj_31_45,
                mujeres_46_60=muj_46_60,
                mujeres_61_75=muj_61_75,
                mujeres_76_mas=muj_76_mas,
                hombres_0_15=hom_0_15,
                hombres_16_30=hom_16_30,
                hombres_31_45=hom_31_45,
                hombres_46_60=hom_46_60,
                hombres_61_75=hom_61_75,
                hombres_76_mas=hom_76_mas
            )
            
            # Backdate la fecha del registro (bypasseando auto_now_add con .update)
            fecha_aleatoria = mes_offset - timedelta(days=random.randint(0, 27), hours=random.randint(0, 23))
            RegistroVisita.objects.filter(pk=registro.pk).update(fecha=fecha_aleatoria)
            total_registros_creados += 1

    print("Generando encuestas de visitante (EncuestaVisitante)...")
    viajas = ['Solo / Sola', 'En pareja', 'En familia (con niños)', 'Con amigos / familiares (adultos)', 'Grupo organizado / Excursión']
    zonas = ["Ex-convento de San Martín", "Plaza Principal (Zócalo)", "Mercado de Artesanías", "Camino a las Ofrendas", "Talleres de hojalatería y cera"]
    actividades_list = ["Fotografía de monumentos", "Compra de artesanías", "Degustación de cecina y pan local", "Recorrido guiado de leyendas", "Observación de altares tradicionales"]
    gustos = [
        "La calidez de los habitantes y la deliciosa comida típica.",
        "Los altares monumentales y la historia del convento.",
        "La tranquilidad del pueblo y las artesanías de cera.",
        "Los guías locales y la explicación de las tradiciones prehispánicas.",
        "El mole tradicional y las fachadas de las casas antiguas."
    ]

    for i in range(12): # Últimos 12 meses
        mes_offset = hoy - timedelta(days=30 * i)
        
        # Generar entre 4 y 10 encuestas por mes
        num_encuestas = random.randint(4, 10)
        for _ in range(num_encuestas):
            if random.random() < 0.15:
                ciudad, estado, pais, _ = random.choice(procedencias_ext)
            else:
                ciudad, estado, pais, _ = random.choice(procedencias_mex)
                
            genero = random.choice(['Femenino', 'Masculino', 'No binario / Otro', 'Prefiero no decirlo'])
            edad = random.randint(18, 70)
            
            # Zonas visitadas aleatorias (unir de 1 a 3 zonas)
            visitadas = ", ".join(random.sample(zonas, k=random.randint(1, 3)))
            # Actividades aleatorias (unir de 1 a 3 actividades)
            acts = ", ".join(random.sample(actividades_list, k=random.randint(1, 3)))
            
            encuesta = EncuestaVisitante.objects.create(
                encuestador=encuestador,
                genero=genero,
                edad=edad,
                viaja_con=random.choice(viajas),
                residencia_ciudad=ciudad,
                residencia_estado=estado,
                residencia_pais=pais,
                zonas_visitadas=visitadas,
                actividades=acts,
                satisfaccion=random.randint(3, 5), # De ⭐⭐⭐ Regular a ⭐⭐⭐⭐⭐ Excelente
                lo_que_mas_gusto=random.choice(gustos)
            )
            
            # Backdate la fecha de la encuesta
            fecha_aleatoria = mes_offset - timedelta(days=random.randint(0, 27), hours=random.randint(0, 23))
            EncuestaVisitante.objects.filter(pk=encuesta.pk).update(fecha=fecha_aleatoria)
            total_encuestas_creadas += 1

    print(f"Éxito: Se crearon {total_registros_creados} registros de visita e históricos.")
    print(f"Éxito: Se crearon {total_encuestas_creadas} encuestas de visitante de prueba.")
    print("Los indicadores clave y gráficas del landing page ahora deberían mostrar datos completos.")

if __name__ == "__main__":
    seed_data()

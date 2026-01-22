"""
Script de prueba para verificar la conexión con la API del INEGI.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.services.inegi_service import INEGIService

# Crear instancia del servicio
token = '142a3684-a55f-b0d4-b991-26843e97642d'
service = INEGIService(token)

print("🔍 Probando conexión con API del INEGI...")
print(f"Token configurado: {token[:20]}...")
print(f"Código geográfico Huaquechula: {service.HUAQUECHULA_CODE}")
print()

# Probar con indicador de Población Total
print("📊 Consultando indicador: Población Total (ID: 1002000001)")
data = service.fetch_indicator_data('1002000001')

if data:
    print(f"✅ Conexión exitosa!")
    print(f"   Períodos obtenidos: {len(data)}")
    print(f"   Datos:")
    for periodo, valor in sorted(data.items())[:5]:  # Mostrar primeros 5
        print(f"      {periodo}: {valor:,.0f}")
    if len(data) > 5:
        print(f"      ... y {len(data) - 5} períodos más")
else:
    print("❌ No se pudieron obtener datos")
    print("   Verifica que el token sea válido y que tengas conexión a internet")

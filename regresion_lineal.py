"""
regresion_lineal.py
===================
Regresión Lineal Múltiple — Observatorio de Datos Huaquechula
-------------------------------------------------------------
Predicción de días de estancia de visitantes a partir de:
  X1 = tamanio_grupo   → tamaño del grupo de visita
  X2 = numero_visitas  → número de veces que ha visitado el lugar
  X3 = es_extranjero   → 1 si el visitante es extranjero, 0 si es nacional

Los datos de prueba se generan dentro del script para demostrar
el flujo completo de Machine Learning con regresión lineal múltiple.

Librerías: numpy, matplotlib, scikit-learn
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# ── 1. Generar datos de prueba ────────────────────────────────────
np.random.seed(42)
N = 200   # número de registros de visita simulados

tamanio_grupo  = np.random.randint(1, 15, size=N).astype(float)
numero_visitas = np.random.randint(1, 12, size=N).astype(float)
es_extranjero  = np.random.choice([0, 1], size=N, p=[0.75, 0.25]).astype(float)

# Relación lineal con ruido realista:
# Más personas en el grupo → más días
# Visitante frecuente      → más días
# Extranjero               → bastante más días
ruido = np.random.normal(0, 0.8, size=N)
estancia_dias = (
    1.0
    + 0.25 * tamanio_grupo
    + 0.20 * numero_visitas
    + 2.50 * es_extranjero
    + ruido
).clip(1).round().astype(float)

# Matriz de features y vector objetivo
X = np.column_stack([tamanio_grupo, numero_visitas, es_extranjero])
y = estancia_dias

feature_names = ['Tamaño de grupo', 'Número de visitas', 'Es extranjero']

# ── 2. Resumen de los datos ───────────────────────────────────────
print("=" * 58)
print("  Regresión Lineal Múltiple — Estancia de Visitantes")
print("  Observatorio de Datos Huaquechula")
print("=" * 58)
print(f"\nDatos de prueba generados: {N} registros")
print(f"  Tamaño de grupo:   min={tamanio_grupo.min():.0f}  max={tamanio_grupo.max():.0f}  media={tamanio_grupo.mean():.1f}")
print(f"  Número de visitas: min={numero_visitas.min():.0f}  max={numero_visitas.max():.0f}  media={numero_visitas.mean():.1f}")
print(f"  Extranjeros:       {int(es_extranjero.sum())} de {N} ({es_extranjero.mean()*100:.0f}%)")
print(f"  Estancia (días):   min={y.min():.0f}  max={y.max():.0f}  media={y.mean():.1f}")

# ── 3. División entrenamiento / prueba ────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nDivisión 80/20  →  entrenamiento: {len(X_train)}  |  prueba: {len(X_test)}")

# ── 4. Entrenar modelo ────────────────────────────────────────────
modelo = LinearRegression()
modelo.fit(X_train, y_train)

print(f"\n--- Modelo entrenado ---")
print(f"  Intercepto : {modelo.intercept_:.4f}")
for name, coef in zip(feature_names, modelo.coef_):
    print(f"  {name:22s}: {coef:+.4f} días por unidad")

ecuacion = (
    f"  estancia = {modelo.intercept_:.2f}"
    f" + {modelo.coef_[0]:.2f}·(grupo)"
    f" + {modelo.coef_[1]:.2f}·(visitas)"
    f" + {modelo.coef_[2]:.2f}·(extranjero)"
)
print(f"\nEcuación ajustada:\n{ecuacion}")

# ── 5. Evaluar modelo ─────────────────────────────────────────────
y_pred = modelo.predict(X_test)
r2   = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"\n--- Métricas (conjunto de prueba) ---")
print(f"  R²   = {r2:.4f}  (1.0 = predicción perfecta)")
print(f"  RMSE = {rmse:.4f} días de error promedio")

# Ejemplos de predicción
print("\n--- Ejemplos de predicción ---")
ejemplos = [
    ([2,  1, 0], "Pareja nacional, 1ª visita"),
    ([5,  3, 0], "Familia nacional, 3ª visita"),
    ([2,  1, 1], "Pareja extranjera, 1ª visita"),
    ([10, 1, 0], "Grupo escolar (10 personas)"),
    ([3,  8, 0], "Trío de visitantes frecuentes"),
    ([4,  2, 1], "Grupo extranjero, 2ª visita"),
]
for vals, desc in ejemplos:
    pred = modelo.predict([vals])[0]
    print(f"  · {desc:40s} → ≈ {pred:.1f} días")

# ── 6. Gráficas ────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10))
fig.suptitle(
    "Regresión Lineal Múltiple — Predicción de Días de Estancia\n"
    "Observatorio de Datos Huaquechula  (datos de prueba sintéticos)",
    fontsize=14, fontweight='bold', y=0.98
)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.32)

COLORES = ['#4C72B0', '#DD8452', '#55A868']

# Gráfica 1: Real vs Predicho ─────────────────────────────────────
ax0 = fig.add_subplot(gs[0, :2])
ax0.scatter(y_test, y_pred, color='#2ecc71', edgecolors='#27ae60',
            s=60, alpha=0.8, zorder=3, label='Predicciones (prueba)')
lim = [min(y_test.min(), y_pred.min()) - 0.5,
       max(y_test.max(), y_pred.max()) + 0.5]
ax0.plot(lim, lim, '--', color='gray', linewidth=1.5, label='Predicción perfecta')
ax0.text(0.04, 0.95,
         f"R²   = {r2:.4f}\nRMSE = {rmse:.2f} días",
         transform=ax0.transAxes, va='top',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#fffbe6',
                   edgecolor='#f0c040', alpha=0.9),
         fontsize=11)
ax0.set_xlabel("Días de estancia ", fontsize=11)
ax0.set_ylabel("Perfil de edad", fontsize=11)
ax0.set_title("Valores Reales vs. Predichos (conjunto de prueba)", fontsize=12)
ax0.legend(fontsize=9)
ax0.grid(True, alpha=0.3)

# Gráfica 2: Coeficientes ─────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 2])
colores_coef = ['#3498db'] * 3
bars = ax1.barh(feature_names, modelo.coef_, color=colores_coef,
                edgecolor='white', height=0.5)
ax1.axvline(0, color='black', linewidth=0.8, linestyle='--')
for bar, val in zip(bars, modelo.coef_):
    ax1.text(val + 0.02, bar.get_y() + bar.get_height() / 2,
             f"{val:+.3f}", va='center', ha='left', fontsize=10)
ax1.set_xlabel("Coeficiente (días/unidad)", fontsize=10)
ax1.set_title("Importancia de Variables\n(coeficientes del modelo)", fontsize=11)
ax1.grid(True, alpha=0.3, axis='x')

# Gráficas 3-5: Cada X_i vs Y con tendencia parcial ──────────────
for i, (feat, color) in enumerate(zip(feature_names, COLORES)):
    ax = fig.add_subplot(gs[1, i])
    xi    = X[:, i]
    jit   = np.random.uniform(-0.15, 0.15, size=xi.shape)
    ax.scatter(xi + jit, y, color=color, alpha=0.3, s=20, zorder=2)

    xi_range  = np.linspace(xi.min(), xi.max(), 100).reshape(-1, 1)
    X_parcial = np.tile(X.mean(axis=0), (100, 1))
    X_parcial[:, i] = xi_range.ravel()
    ax.plot(xi_range, modelo.predict(X_parcial),
            color='black', linewidth=2, label='Tendencia parcial')

    ax.set_xlabel(feat, fontsize=10)
    ax.set_ylabel("Estancia (días)" if i == 0 else "", fontsize=10)
    ax.set_title(f"{feat} vs Estancia", fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    if feat == 'Es extranjero':
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Nacional', 'Extranjero'])

plt.savefig('regresion_lineal_resultado.png', dpi=150, bbox_inches='tight')
print("\nGráfica guardada: regresion_lineal_resultado.png")
plt.show()
print("\n✅ Script completado.")

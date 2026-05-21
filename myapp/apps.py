from django.apps import AppConfig
from django.conf import settings
import os
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

class ResenasConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    
    detector_toxicidad = None

    def ready(self):
        # ML_MODEL_PATH puede ser:
        #   "disabled"  → no cargar modelo (solo reglas de palabras)
        #   ""          → usar ruta local por defecto
        #   "usuario/repo" → descargar desde Hugging Face Hub
        #   "/ruta/local"  → cargar desde disco
        model_path_env = os.environ.get('ML_MODEL_PATH', '')

        if model_path_env.strip().lower() == 'disabled':
            logger.warning("Modelo de moderación desactivado por ML_MODEL_PATH=disabled.")
            return

        # Si la variable está vacía usa la ruta local del repositorio
        ruta_modelo = model_path_env.strip() or os.path.join(
            settings.BASE_DIR, self.name, 'ml_models', 'mi_modelo_moderador'
        )

        try:
            self.detector_toxicidad = pipeline(
                "text-classification",
                model=ruta_modelo,
                tokenizer=ruta_modelo,
                device=-1,   # CPU
            )
            logger.info("¡Modelo de moderación cargado con éxito desde: %s!", ruta_modelo)
        except Exception as e:
            logger.error("Error al cargar el modelo de moderación: %s", e)
            logger.warning("El sistema seguirá funcionando usando solo el filtro de palabras prohibidas.")


    def classify_review(self, text: str, score_threshold: float = 0.70) -> dict:
        """Clasifica un texto (apodo+comentario) usando el pipeline cargado.

        Retorna un dict con keys: `estado` ('aprobada'|'pendiente'),
        `label` (etiqueta bruta), `score` (confianza), `reason` (texto corto).
        Maneja con gracia cuando el pipeline no está disponible.
        """
        if not text:
            return {'estado': 'aprobada', 'label': None, 'score': 0.0, 'reason': 'empty'}

        detector = getattr(self, 'detector_toxicidad', None)
        # Lista flexible de etiquetas negativas que podrían indicar toxicidad/spam
        negative_labels = {'LABEL_1', 'TOXIC', 'NEGATIVE', 'INSULT', 'ABUSE', 'OFFENSIVE'}

        # Lista simple de palabrotas localmente bloqueadas
        banned_words = {'puto', 'mierda', 'pendejo', 'idiota'}

        # Check banned words first (fast rule-based)
        if any(w in text.lower() for w in banned_words):
            return {'estado': 'pendiente', 'label': 'banned_word', 'score': 1.0, 'reason': 'banned_word'}

        if not detector:
            return {'estado': 'pendiente', 'label': None, 'score': 0.0, 'reason': 'no_model'}

        try:
            max_chars = 5000
            if len(text) > max_chars:
                text = text[:max_chars]

            out = detector(text, truncation=True, max_length=512)
            if isinstance(out, list) and len(out) > 0:
                res = out[0]
                label = res.get('label')
                score = float(res.get('score', 0.0))
                if label in negative_labels and score >= score_threshold:
                    return {'estado': 'pendiente', 'label': label, 'score': score, 'reason': 'model_negative'}
                # Default: approve
                return {'estado': 'aprobada', 'label': label, 'score': score, 'reason': 'model_ok'}
        except Exception as e:
            logger.exception('Error al clasificar reseña: %s', e)
            return {'estado': 'pendiente', 'label': None, 'score': 0.0, 'reason': 'error'}

        return {'estado': 'aprobada', 'label': None, 'score': 0.0, 'reason': 'unknown'}
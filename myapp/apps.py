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
        try:
            # Ruta exacta a tu carpeta local
            ruta_modelo = os.path.join(settings.BASE_DIR, self.name, 'ml_models', 'mi_modelo_moderador')
            
            # Carga TU modelo en CPU (device=-1) para evitar uso inesperado de GPU
            self.detector_toxicidad = pipeline(
                "text-classification",
                model=ruta_modelo,
                tokenizer=ruta_modelo,
                device=-1,
            )
            logger.info("¡Modelo PROPIO cargado con éxito!")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")

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
/**
 * encuestasService.js — Servicios para enviar encuestas del Observatorio
 * con soporte resiliente offline (Store-and-Forward) y telemetría de retardo.
 */
import api from './api';
import offlineQueue from './offlineQueue';

/**
 * Determina si un error es originado por desconexión o fallo temporal de red.
 */
function esErrorDeRed(error) {
    if (!error.response) return true; // Timeout, sin conexión, DNS error, Network Error
    const status = error.response.status;
    return status >= 500 || status === 408 || status === 504 || status === 502;
}

/**
 * Intenta enviar la encuesta directamente; si no hay cobertura de red en Huaquechula,
 * la almacena en la cola local de AsyncStorage preservando la fecha exacta de captura.
 */
async function enviarConFallbackOffline(endpoint, datos, tipo) {
    const payload = {
        ...datos,
        fecha_captura_local: datos.fecha_captura_local || new Date().toISOString(),
    };

    try {
        const response = await api.post(endpoint, payload);
        return { success: true, offline: false, data: response.data };
    } catch (error) {
        if (esErrorDeRed(error)) {
            console.warn(`[Offline Mode] Sin cobertura celular al enviar ${tipo}. Encolando localmente...`);
            const encolado = await offlineQueue.enqueue({
                endpoint,
                payload,
                tipo,
            });
            return {
                success: true,
                offline: true,
                id: encolado.id,
                message: 'Encuesta guardada en la memoria local por falta de cobertura. Se enviará al recuperar señal.'
            };
        }
        // Si es 400 (Bad Request / validación de campos), re-lanzar para que la UI informe los campos incorrectos
        throw error;
    }
}

export const encuestasService = {
    /** GET /api/mobile/mis-encuestas/ — Lista unificada de encuestas realizadas por el usuario */
    async getMisEncuestas() {
        const response = await api.get('/api/mobile/mis-encuestas/');
        return response.data;
    },

    /** POST /api/mobile/encuestas/visitante/ — Guarda encuesta de visitante con resiliencia offline */
    async crearEncuestaVisitante(datos) {
        return await enviarConFallbackOffline('/api/mobile/encuestas/visitante/', datos, 'visitante');
    },

    /** POST /api/mobile/encuestas/residente/ — Guarda encuesta de residente con resiliencia offline */
    async crearEncuestaResidente(datos) {
        return await enviarConFallbackOffline('/api/mobile/encuestas/residente/', datos, 'residente');
    },

    /** POST /api/mobile/encuestas/institucional/ — Guarda encuesta institucional con resiliencia offline */
    async crearEncuestaInstitucional(datos) {
        return await enviarConFallbackOffline('/api/mobile/encuestas/institucional/', datos, 'institucional');
    },

    /** POST /api/mobile/encuestas/comercio/ — Guarda encuesta de comercio con resiliencia offline */
    async crearEncuestaComercio(datos) {
        return await enviarConFallbackOffline('/api/mobile/encuestas/comercio/', datos, 'comercio');
    },

    /** GET /api/mobile/encuestas/residente/ — Lista encuestas de residentes */
    async getEncuestasResidente() {
        const response = await api.get('/api/mobile/encuestas/residente/');
        return response.data;
    },

    /** GET /api/mobile/encuestas/comercio/ — Lista encuestas de comercios */
    async getEncuestasComercio() {
        const response = await api.get('/api/mobile/encuestas/comercio/');
        return response.data;
    },

    /** GET /api/mobile/encuestas-creadas/ — Lista encuestas dinámicas activas */
    async getEncuestasCreadas() {
        const response = await api.get('/api/mobile/encuestas-creadas/');
        return response.data;
    },

    /** POST /api/mobile/encuestas-creadas/<id>/responder/ — Guarda respuestas de encuesta dinámica */
    async responderEncuestaCreada(id, respuestas) {
        return await enviarConFallbackOffline(
            `/api/mobile/encuestas-creadas/${id}/responder/`,
            { respuestas },
            'dinamica'
        );
    },

    /** Métodos de supervisión de la cola offline */
    async obtenerPendientesOffline() {
        return await offlineQueue.getQueueCount();
    },

    async sincronizarColaOffline(onProgress) {
        return await offlineQueue.syncQueue(onProgress);
    },

    async limpiarColaOffline() {
        return await offlineQueue.clearQueue();
    }
};

export default encuestasService;

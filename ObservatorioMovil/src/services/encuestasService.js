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
    /** GET /api/mobile/mis-encuestas/ — Lista unificada con soporte offline resiliente */
    async getMisEncuestas() {
        let remotas = [];
        try {
            const response = await api.get('/api/mobile/mis-encuestas/');
            remotas = response.data || [];
        } catch (error) {
            console.warn('[encuestasService] Sin conexión con el servidor para mis-encuestas, mostrando cola local:', error.message);
        }

        // Obtener elementos pendientes en cola offline
        let localesPendientes = [];
        try {
            const cola = await offlineQueue.getQueue();
            localesPendientes = cola.map(item => {
                const payload = item.payload || {};
                let tipoLabel = 'Encuesta';
                let icono = '📋';
                let resumen = 'Guardada localmente (pendiente de sincronización)';

                if (item.tipo === 'visitante') {
                    tipoLabel = 'Encuesta: Perfil del Visitante';
                    icono = '🗺️';
                    resumen = `Origen: ${payload.residencia_ciudad || ''}, ${payload.residencia_estado || ''} | Guardada en dispositivo`;
                } else if (item.tipo === 'residente') {
                    tipoLabel = 'Encuesta: Residente Local';
                    icono = '🏠';
                    resumen = `Región: ${payload.region_origen || payload.barrio_colonia || ''} | Guardada en dispositivo`;
                } else if (item.tipo === 'institucional') {
                    tipoLabel = 'Encuesta: Institucional';
                    icono = '🏛️';
                    resumen = `Visitantes Festividades: ${payload.visitantes_festividades || 0} | Guardada en dispositivo`;
                } else if (item.tipo === 'comercio') {
                    tipoLabel = 'Encuesta: Comercio';
                    icono = '🏪';
                    resumen = `Comercio: ${payload.tipo_comercio || ''} | Guardada en dispositivo`;
                } else if (item.tipo === 'visita') {
                    tipoLabel = 'Registro de Visitantes (Afluencia)';
                    icono = '👥';
                    resumen = `Lugar: ${payload.lugar_visita || ''} | Procedencia: ${payload.procedencia || ''} | Personas: ${payload.numero_personas || 1}`;
                } else if (item.tipo === 'dinamica') {
                    tipoLabel = 'Encuesta Dinámica';
                    icono = '📋';
                    resumen = 'Respuestas guardadas localmente en dispositivo';
                }

                return {
                    id: item.id,
                    tipo: tipoLabel,
                    tipo_codigo: item.tipo,
                    icono: icono,
                    fecha: payload.fecha_captura_local || item.fecha_guardado_local || new Date().toISOString(),
                    cargado_bd: false,
                    resumen: resumen,
                };
            });
        } catch (e) {
            console.error('Error procesando cola offline para mis-encuestas:', e);
        }

        // Combinar encuestas locales pendientes y remotas
        const combinadas = [...localesPendientes, ...remotas];
        combinadas.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
        return combinadas;
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

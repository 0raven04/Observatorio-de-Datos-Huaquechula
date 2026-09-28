/**
 * visitasService.js — Servicios para el CRUD de registros de visitas con resiliencia offline.
 */
import api from './api';
import offlineQueue from './offlineQueue';

function esErrorDeRed(error) {
    if (!error.response) return true; // Timeout, sin conexión, DNS error, Network Error
    const status = error.response.status;
    return status >= 500 || status === 408 || status === 504 || status === 502;
}

export const visitasService = {
    /** GET /api/mobile/visitas/ — Lista todas las visitas del encuestador */
    async getVisitas() {
        const response = await api.get('/api/mobile/visitas/');
        return response.data;
    },

    /**
     * POST /api/mobile/visitas/ — Crea un nuevo registro de visita con soporte offline.
     * @param {object} registro - Datos del registro incluyendo array `personas_input`
     */
    async crearVisita(registro) {
        const payload = {
            ...registro,
            fecha_captura_local: registro.fecha_captura_local || new Date().toISOString(),
        };

        try {
            const response = await api.post('/api/mobile/visitas/', payload);
            return { success: true, offline: false, data: response.data };
        } catch (error) {
            if (esErrorDeRed(error)) {
                console.warn('[Offline Mode] Sin red. Encolando registro de visita...');
                const encolado = await offlineQueue.enqueue({
                    endpoint: '/api/mobile/visitas/',
                    payload,
                    tipo: 'visita',
                });
                return {
                    success: true,
                    offline: true,
                    id: encolado.id,
                    message: 'Registro de visita guardado localmente por falta de cobertura.'
                };
            }
            throw error;
        }
    },

    /** GET /api/mobile/visitas/:id/ — Obtiene detalle de una visita */
    async getVisita(id) {
        const response = await api.get(`/api/mobile/visitas/${id}/`);
        return response.data;
    },

    /** PUT /api/mobile/visitas/:id/ — Actualiza una visita existente */
    async actualizarVisita(id, datos) {
        const response = await api.put(`/api/mobile/visitas/${id}/`, datos);
        return response.data;
    },

    /** DELETE /api/mobile/visitas/:id/ — Elimina una visita */
    async eliminarVisita(id) {
        await api.delete(`/api/mobile/visitas/${id}/`);
    },
};

export default visitasService;

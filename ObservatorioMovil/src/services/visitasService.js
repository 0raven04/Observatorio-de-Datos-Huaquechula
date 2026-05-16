/**
 * visitasService.js — Servicios para el CRUD de registros de visitas.
 */
import api from './api';

export const visitasService = {
    /** GET /api/mobile/visitas/ — Lista todas las visitas del encuestador */
    async getVisitas() {
        const response = await api.get('/api/mobile/visitas/');
        return response.data;
    },

    /**
     * POST /api/mobile/visitas/ — Crea un nuevo registro de visita.
     * @param {object} registro - Datos del registro incluyendo array `personas_input`
     */
    async crearVisita(registro) {
        const response = await api.post('/api/mobile/visitas/', registro);
        return response.data;
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

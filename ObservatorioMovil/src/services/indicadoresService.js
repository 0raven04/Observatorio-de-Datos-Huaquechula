/**
 * indicadoresService.js — Servicios para obtener indicadores y dashboard.
 */
import api from './api';

export const indicadoresService = {
    /** GET /api/mobile/indicadores/ — Todos los ejes con categorías, indicadores y mediciones */
    async getIndicadores() {
        const response = await api.get('/api/mobile/indicadores/');
        return response.data;
    },

    /** GET /api/mobile/dashboard/ — Resumen compacto: último valor de cada indicador */
    async getDashboard() {
        const response = await api.get('/api/mobile/dashboard/');
        return response.data;
    },
};

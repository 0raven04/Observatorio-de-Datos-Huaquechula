/**
 * encuestasService.js — Servicios para enviar encuestas de residentes y comercios.
 */
import api from './api';

export const encuestasService = {
    /** POST /api/mobile/encuestas/residente/ — Guarda encuesta de residente */
    async crearEncuestaResidente(datos) {
        const response = await api.post('/api/mobile/encuestas/residente/', datos);
        return response.data;
    },

    /** POST /api/mobile/encuestas/comercio/ — Guarda encuesta de comercio */
    async crearEncuestaComercio(datos) {
        const response = await api.post('/api/mobile/encuestas/comercio/', datos);
        return response.data;
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
};

/**
 * encuestasService.js — Servicios para enviar encuestas de residentes y comercios.
 */
import api from './api';

export const encuestasService = {
    /** GET /api/mobile/mis-encuestas/ — Lista unificada de encuestas realizadas por el usuario */
    async getMisEncuestas() {
        const response = await api.get('/api/mobile/mis-encuestas/');
        return response.data;
    },

    /** POST /api/mobile/encuestas/visitante/ — Guarda encuesta de visitante */
    async crearEncuestaVisitante(datos) {
        const response = await api.post('/api/mobile/encuestas/visitante/', datos);
        return response.data;
    },

    /** POST /api/mobile/encuestas/residente/ — Guarda encuesta de residente */
    async crearEncuestaResidente(datos) {
        const response = await api.post('/api/mobile/encuestas/residente/', datos);
        return response.data;
    },

    /** POST /api/mobile/encuestas/institucional/ — Guarda encuesta institucional */
    async crearEncuestaInstitucional(datos) {
        const response = await api.post('/api/mobile/encuestas/institucional/', datos);
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

    /** GET /api/mobile/encuestas-creadas/ — Lista encuestas dinámicas activas */
    async getEncuestasCreadas() {
        const response = await api.get('/api/mobile/encuestas-creadas/');
        return response.data;
    },

    /** POST /api/mobile/encuestas-creadas/<id>/responder/ — Guarda respuestas de encuesta dinámica */
    async responderEncuestaCreada(id, respuestas) {
        const response = await api.post(`/api/mobile/encuestas-creadas/${id}/responder/`, { respuestas });
        return response.data;
    },
};

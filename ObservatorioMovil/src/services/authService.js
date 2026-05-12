/**
 * authService.js — Servicios de autenticación para la app del Observatorio.
 * Maneja login, logout y almacenamiento seguro de tokens JWT.
 */
import storage from './storage';
import api from './api';

export const authService = {
    /**
     * Inicia sesión con usuario y contraseña.
     * Guarda los tokens JWT en SecureStore.
     * @returns {{ access, refresh, usuario }} datos del usuario autenticado
     */
    async login(username, password) {
        const response = await api.post('/api/mobile/login/', { username, password });
        const { access, refresh, usuario } = response.data;

        await storage.setItem('access_token', access);
        await storage.setItem('refresh_token', refresh);
        await storage.setItem('usuario', JSON.stringify(usuario));

        return usuario;
    },

    /**
     * Cierra sesión: elimina todos los tokens almacenados.
     */
    async logout() {
        await storage.deleteItem('access_token');
        await storage.deleteItem('refresh_token');
        await storage.deleteItem('usuario');
    },

    /**
     * Recupera el usuario almacenado localmente (sin llamar al servidor).
     * @returns {object|null} datos del usuario o null si no hay sesión
     */
    async getUsuarioGuardado() {
        const raw = await storage.getItem('usuario');
        return raw ? JSON.parse(raw) : null;
    },

    /**
     * Comprueba si hay una sesión activa (token presente).
     * @returns {boolean}
     */
    async estaAutenticado() {
        const token = await storage.getItem('access_token');
        return !!token;
    },
};

/**
 * api.js — Instancia base de Axios para el Observatorio API.
 * Configura baseURL, headers por defecto e interceptores para adjuntar el JWT.
 *
 * IMPORTANTE: Cambia BASE_URL a la IP de tu PC en la red local cuando
 * pruebes desde un teléfono físico (ej: "http://192.168.1.X:8000").
 * Para emulador Android usa "http://10.0.2.2:8000".
 */
import axios from 'axios';
import storage from './storage';
import { Platform } from 'react-native';

// ── Configuración de la URL base ──────────────────────────────────────────────
// Para web (navegador) usa localhost; para celular usa la IP WiFi de la PC.
const WIFI_IP = '192.168.1.72';  // ← IP de tu PC en la red WiFi

export const BASE_URL = Platform.OS === 'web'
    ? 'http://localhost:8000'       // Navegador en la misma PC
    : `http://${WIFI_IP}:8000`;     // Teléfono físico en la red WiFi

const api = axios.create({
    baseURL: BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ── Interceptor: adjunta el token JWT en cada petición ────────────────────────
api.interceptors.request.use(
    async (config) => {
        const token = await storage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// ── Interceptor: si el token expiró (401), intenta hacer refresh ──────────────
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refresh = await storage.getItem('refresh_token');
                if (!refresh) return Promise.reject(error);

                const res = await axios.post(`${BASE_URL}/api/mobile/token/refresh/`, {
                    refresh,
                });
                const newAccess = res.data.access;
                await storage.setItem('access_token', newAccess);
                originalRequest.headers.Authorization = `Bearer ${newAccess}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh también falló — la sesión expiró
                await storage.deleteItem('access_token');
                await storage.deleteItem('refresh_token');
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;

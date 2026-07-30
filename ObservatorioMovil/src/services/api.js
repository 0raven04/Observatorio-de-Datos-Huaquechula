/**
 * api.js — Instancia base de Axios para el Observatorio API.
 * Configura baseURL, headers por defecto e interceptores para adjuntar el JWT.
 *
 * ──────────────────────────────────────────────────────────────────────────────
 *  CONFIGURACIÓN DE URL  (ajusta antes de compilar el APK)
 * ──────────────────────────────────────────────────────────────────────────────
 *
 *  RED LOCAL WIFI (pruebas con teléfono físico en la misma red que el servidor):
 *    → Cambia WIFI_IP a la IP de la PC donde corre el servidor Django.
 *    → Ejemplo: '192.168.1.45' o '10.1.4.231'
 *    → Encuentra tu IP con: ipconfig (Windows) | ifconfig (Mac/Linux)
 *
 *  EMULADOR ANDROID STUDIO:
 *    → Usa la IP especial '10.0.2.2' para referirse a localhost de la PC host.
 *
 *  PRODUCCIÓN (servidor desplegado con dominio o IP pública):
 *    → Cambia USE_PRODUCTION a true y escribe la URL completa en PRODUCTION_URL.
 *    → Ejemplo: 'https://observatorio.tudominio.com'
 *
 * ──────────────────────────────────────────────────────────────────────────────
 */
import axios from 'axios';
import storage from './storage';
import { Platform } from 'react-native';

// ── Configuración — ajusta estos valores antes de compilar ────────────────────

const WIFI_IP = '192.168.1.71';       // ← IP de tu PC en la red local
const PRODUCTION_URL = 'https://observatorio-huaquechula.loca.lt';                   // ← URL de túnel público localtunnel
const USE_PRODUCTION = true;          // ← Habilitado túnel público localtunnel

// ── Resolución automática de la URL base ──────────────────────────────────────
function resolveBaseURL() {
    if (USE_PRODUCTION && PRODUCTION_URL) {
        return PRODUCTION_URL;
    }
    if (Platform.OS === 'web') {
        return 'http://localhost:8000';   // Navegador en la misma PC
    }
    return `http://${WIFI_IP}:8000`;      // Teléfono físico en la red WiFi
}

export const BASE_URL = resolveBaseURL();

const api = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'bypass-tunnel-reminder': 'true',
        'ngrok-skip-browser-warning': 'true',
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
                }, {
                    headers: { 'ngrok-skip-browser-warning': 'true', 'Accept': 'application/json' }
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

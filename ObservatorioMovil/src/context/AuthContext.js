/**
 * AuthContext.js — Estado global de autenticación para la app del Observatorio.
 * Provee: usuario actual, funciones de login/logout, y estado de carga inicial.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [usuario, setUsuario] = useState(null);
    const [cargando, setCargando] = useState(true);

    // Al iniciar la app, comprueba si hay sesión guardada
    useEffect(() => {
        async function verificarSesion() {
            try {
                const u = await authService.getUsuarioGuardado();
                const autenticado = await authService.estaAutenticado();
                if (u && autenticado) {
                    setUsuario(u);
                }
            } catch (e) {
                console.error('Error verificando sesión:', e);
            } finally {
                setCargando(false);
            }
        }
        verificarSesion();
    }, []);

    const login = async (username, password) => {
        const u = await authService.login(username, password);
        setUsuario(u);
        return u;
    };

    const logout = async () => {
        await authService.logout();
        setUsuario(null);
    };

    return (
        <AuthContext.Provider value={{ usuario, cargando, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

/** Hook para usar el contexto de autenticación en cualquier pantalla */
export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth debe usarse dentro de <AuthProvider>');
    return ctx;
}

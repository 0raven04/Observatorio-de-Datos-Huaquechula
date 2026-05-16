/**
 * LoginScreen.js — Pantalla de inicio de sesión del Observatorio de Datos Huaquechula.
 * Diseño profesional con colores del observatorio, validación de campos y manejo de errores.
 */
import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity,
    StyleSheet, ActivityIndicator, KeyboardAvoidingView,
    Platform, Image, Alert, ScrollView,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

// Paleta del Observatorio (alineada con el sitio web)
const DORADO = '#FFC300';
const TEXTO_OSCURO = '#212529';
const FONDO = '#eef1f5';
const BLANCO = '#ffffff';
const GRIS_INPUT = '#f5f5f5';
const GRIS_BORDE = '#dee2e6';
const AZUL_INSTITUCIONAL = '#1a7abf';

export default function LoginScreen() {
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [cargando, setCargando] = useState(false);

    const handleLogin = async () => {
        if (!username.trim() || !password.trim()) {
            Alert.alert('Campos requeridos', 'Por favor ingresa tu usuario y contraseña.');
            return;
        }

        setCargando(true);
        try {
            await login(username.trim(), password);
            // La navegación ocurre automáticamente via AuthContext → AppNavigator
        } catch (error) {
            const msg = error.response?.data?.error || 'Error de conexión. Verifica el servidor.';
            Alert.alert('Error al iniciar sesión', msg);
        } finally {
            setCargando(false);
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
                {/* Encabezado */}
                <View style={styles.header}>
                    <View style={styles.logoCircle}>
                        <Text style={styles.logoText}>🏛️</Text>
                    </View>
                    <Text style={styles.titulo}>Observatorio de Datos</Text>
                    <Text style={styles.subtitulo}>Huaquechula, Puebla</Text>
                </View>

                {/* Tarjeta de login */}
                <View style={styles.card}>
                    <Text style={styles.cardTitle}>Iniciar Sesión</Text>

                    <Text style={styles.label}>Usuario</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="Nombre de usuario"
                        placeholderTextColor="#aaa"
                        value={username}
                        onChangeText={setUsername}
                        autoCapitalize="none"
                        autoCorrect={false}
                        testID="input-usuario"
                    />

                    <Text style={styles.label}>Contraseña</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="Contraseña"
                        placeholderTextColor="#aaa"
                        value={password}
                        onChangeText={setPassword}
                        secureTextEntry
                        testID="input-password"
                    />

                    <TouchableOpacity
                        style={[styles.boton, cargando && styles.botonDeshabilitado]}
                        onPress={handleLogin}
                        disabled={cargando}
                        testID="btn-login"
                    >
                        {cargando ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text style={styles.botonTexto}>Entrar</Text>
                        )}
                    </TouchableOpacity>
                </View>

                <Text style={styles.footer}>
                    Sistema de Registro Turístico Municipal
                </Text>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: FONDO,
    },
    scroll: {
        flexGrow: 1,
        justifyContent: 'center',
        padding: 24,
    },
    header: {
        alignItems: 'center',
        marginBottom: 32,
    },
    logoCircle: {
        width: 84,
        height: 84,
        borderRadius: 42,
        backgroundColor: BLANCO,
        borderWidth: 3,
        borderColor: DORADO,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 16,
        elevation: 4,
        shadowColor: DORADO,
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
    },
    logoText: {
        fontSize: 38,
    },
    titulo: {
        fontSize: 22,
        fontWeight: 'bold',
        color: TEXTO_OSCURO,
        textAlign: 'center',
    },
    subtitulo: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
        textAlign: 'center',
    },
    card: {
        backgroundColor: BLANCO,
        borderRadius: 20,
        padding: 28,
        elevation: 4,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 10,
    },
    cardTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: TEXTO_OSCURO,
        marginBottom: 20,
        textAlign: 'center',
    },
    label: {
        fontSize: 13,
        fontWeight: '600',
        color: '#555',
        marginBottom: 6,
        marginTop: 12,
    },
    input: {
        backgroundColor: GRIS_INPUT,
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 15,
        paddingHorizontal: 16,
        paddingVertical: 13,
        fontSize: 15,
        color: TEXTO_OSCURO,
    },
    boton: {
        backgroundColor: BLANCO,
        borderRadius: 12,
        borderWidth: 2,
        borderColor: DORADO,
        paddingVertical: 14,
        alignItems: 'center',
        marginTop: 24,
        elevation: 2,
        shadowColor: DORADO,
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.25,
        shadowRadius: 6,
    },
    botonDeshabilitado: {
        opacity: 0.5,
    },
    botonTexto: {
        color: TEXTO_OSCURO,
        fontSize: 16,
        fontWeight: 'bold',
        letterSpacing: 0.5,
    },
    footer: {
        textAlign: 'center',
        color: '#999',
        fontSize: 12,
        marginTop: 24,
    },
});

import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { encuestasService } from '../services/encuestasService';

const AZUL = '#3a6073'; // Azul pizarra (apagado)
const VERDE = '#7d8c77'; // Verde musgo/sage (apagado)
const NARANJA = '#c4b897'; // Ocre/arena oscuro (apagado)
const MORADO = '#4A4A4A'; // Gris oscuro institucional

export default function SelectorEncuestasScreen({ navigation }) {
    const [encuestas, setEncuestas] = useState([]);
    const [cargando, setCargando] = useState(true);

    const cargarEncuestas = useCallback(async () => {
        try {
            setCargando(true);
            const data = await encuestasService.getEncuestasCreadas();
            setEncuestas(data);
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'No se pudieron cargar las encuestas personalizadas.');
        } finally {
            setCargando(false);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            cargarEncuestas();
        }, [cargarEncuestas])
    );

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            <View style={styles.header}>
                <Text style={styles.titulo}>Portal del Encuestador</Text>
                <Text style={styles.subtitulo}>Seleccione una opción de la lista para iniciar el levantamiento en campo.</Text>
            </View>

            {/* Sección 1: Acciones Rápidas */}
            <Text style={styles.sectionTitle}>Acciones Rápidas</Text>
            <View style={styles.grid}>
                {/* Opción Turistas */}
                <TouchableOpacity
                    style={[styles.card, { borderLeftColor: AZUL }]}
                    onPress={() => navigation.navigate('NuevaVisita')}
                >
                    <View style={[styles.iconCircle, { backgroundColor: AZUL + '22' }]}>
                        <Text style={styles.iconEmoji}>🗺️</Text>
                    </View>
                    <View style={styles.cardInfo}>
                        <Text style={styles.cardTitle}>Turista / Visitante</Text>
                        <Text style={styles.cardDesc}>Registro de flujo turístico y procedencia.</Text>
                    </View>
                    <Text style={styles.chevron}>›</Text>
                </TouchableOpacity>

                {/* Opción Residentes */}
                <TouchableOpacity
                    style={[styles.card, { borderLeftColor: VERDE }]}
                    onPress={() => navigation.navigate('EncuestaResidente')}
                >
                    <View style={[styles.iconCircle, { backgroundColor: VERDE + '22' }]}>
                        <Text style={styles.iconEmoji}>🏠</Text>
                    </View>
                    <View style={styles.cardInfo}>
                        <Text style={styles.cardTitle}>Residente Local</Text>
                        <Text style={styles.cardDesc}>Percepción de seguridad, tradiciones y ambiente.</Text>
                    </View>
                    <Text style={styles.chevron}>›</Text>
                </TouchableOpacity>

                {/* Opción Comercio */}
                <TouchableOpacity
                    style={[styles.card, { borderLeftColor: NARANJA }]}
                    onPress={() => navigation.navigate('EncuestaComercio')}
                >
                    <View style={[styles.iconCircle, { backgroundColor: NARANJA + '22' }]}>
                        <Text style={styles.iconEmoji}>🏪</Text>
                    </View>
                    <View style={styles.cardInfo}>
                        <Text style={styles.cardTitle}>Comercio / Taller</Text>
                        <Text style={styles.cardDesc}>Gobernanza y gestión del turismo local.</Text>
                    </View>
                    <Text style={styles.chevron}>›</Text>
                </TouchableOpacity>
            </View>

            {/* Sección 2: Encuestas Personalizadas */}
            <Text style={[styles.sectionTitle, { marginTop: 25 }]}>Encuestas Personalizadas</Text>
            {cargando ? (
                <ActivityIndicator size="large" color={MORADO} style={{ marginTop: 20 }} />
            ) : encuestas.length === 0 ? (
                <View style={styles.emptyContainer}>
                    <Text style={styles.emptyText}>No hay encuestas personalizadas activas en este momento.</Text>
                </View>
            ) : (
                <View style={styles.grid}>
                    {encuestas.map((encuesta) => (
                        <TouchableOpacity
                            key={encuesta.id}
                            style={[styles.card, { borderLeftColor: MORADO }]}
                            onPress={() => navigation.navigate('CompletarEncuesta', { encuesta })}
                        >
                            <View style={[styles.iconCircle, { backgroundColor: MORADO + '22' }]}>
                                <Text style={styles.iconEmoji}>📋</Text>
                            </View>
                            <View style={styles.cardInfo}>
                                <Text style={styles.cardTitle}>{encuesta.titulo}</Text>
                                <Text style={styles.cardDesc} numberOfLines={2}>
                                    {encuesta.descripcion || 'Sin descripción disponible.'}
                                </Text>
                            </View>
                            <Text style={styles.chevron}>›</Text>
                        </TouchableOpacity>
                    ))}
                </View>
            )}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#EDEBE3' },
    content: { padding: 20, paddingBottom: 40 },
    header: { marginBottom: 25, marginTop: 10 },
    titulo: { fontSize: 24, fontWeight: 'bold', color: '#2c3e50', marginBottom: 8 },
    subtitulo: { fontSize: 14, color: '#7f8c8d', lineHeight: 20 },
    grid: { gap: 15 },
    card: {
        backgroundColor: '#fff',
        borderRadius: 15,
        padding: 16,
        flexDirection: 'row',
        alignItems: 'center',
        elevation: 3,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        borderLeftWidth: 5,
    },
    iconCircle: {
        width: 60,
        height: 60,
        borderRadius: 30,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 15,
    },
    iconEmoji: { fontSize: 28 },
    cardInfo: { flex: 1 },
    cardTitle: { fontSize: 17, fontWeight: 'bold', color: '#2c3e50', marginBottom: 4 },
    cardDesc: { fontSize: 13, color: '#95a5a6' },
    chevron: { fontSize: 28, color: '#ccc', fontWeight: '300' },
    sectionTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#7f8c8d',
        marginBottom: 12,
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    emptyContainer: {
        padding: 30,
        backgroundColor: '#fff',
        borderRadius: 15,
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 1,
        borderColor: '#dee2e6',
        borderStyle: 'dashed',
    },
    emptyText: {
        fontSize: 14,
        color: '#7f8c8d',
        textAlign: 'center',
        lineHeight: 20,
    },
});

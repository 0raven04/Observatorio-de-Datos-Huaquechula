/**
 * MisVisitasScreen.js — Lista de registros de visita del encuestador.
 */
import React, { useState, useCallback } from 'react';
import {
    View, Text, FlatList, StyleSheet, ActivityIndicator,
    TouchableOpacity, Alert, RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { visitasService } from '../services/visitasService';

const AZUL = '#1a7abf';

function RegistroItem({ item, onEliminar }) {
    return (
        <View style={styles.card}>
            <View style={styles.cardHeader}>
                <Text style={styles.cardId}>Registro #{item.id_registro}</Text>
                <Text style={styles.cardFecha}>{item.fecha}</Text>
            </View>
            <View style={styles.cardBody}>
                <Text style={styles.cardDato}>📍 {item.procedencia || 'Sin procedencia'}</Text>
                <Text style={styles.cardDato}>👥 {item.tamanio_grupo} persona(s)</Text>
                <Text style={styles.cardDato}>🚗 {item.tipo_transporte || '—'}</Text>
                <Text style={styles.cardDato}>🎯 {item.motivo_visita || '—'}</Text>
                {item.es_extranjero && (
                    <Text style={styles.cardDatoDestacado}>🌍 Extranjero: {item.pais_origen}</Text>
                )}
            </View>
            <TouchableOpacity
                style={styles.eliminarBtn}
                onPress={() => onEliminar(item.id_registro)}
            >
                <Text style={styles.eliminarTexto}>Eliminar</Text>
            </TouchableOpacity>
        </View>
    );
}

export default function MisVisitasScreen() {
    const [visitas, setVisitas] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [refrescando, setRefrescando] = useState(false);

    const cargarVisitas = async () => {
        try {
            const data = await visitasService.getVisitas();
            setVisitas(data);
        } catch (e) {
            Alert.alert('Error', 'No se pudieron cargar los registros.');
        } finally {
            setCargando(false);
            setRefrescando(false);
        }
    };

    // Recarga al volver a esta pantalla
    useFocusEffect(
        useCallback(() => {
            setCargando(true);
            cargarVisitas();
        }, [])
    );

    const eliminar = (id) => {
        Alert.alert(
            'Confirmar eliminación',
            `¿Deseas eliminar el registro #${id}?`,
            [
                { text: 'Cancelar', style: 'cancel' },
                {
                    text: 'Eliminar',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await visitasService.eliminarVisita(id);
                            setVisitas((prev) => prev.filter((v) => v.id_registro !== id));
                        } catch {
                            Alert.alert('Error', 'No se pudo eliminar el registro.');
                        }
                    },
                },
            ]
        );
    };

    if (cargando) {
        return (
            <View style={styles.centrado}>
                <ActivityIndicator size="large" color={AZUL} />
                <Text style={styles.cargandoTexto}>Cargando registros…</Text>
            </View>
        );
    }

    return (
        <FlatList
            style={styles.container}
            contentContainerStyle={visitas.length === 0 ? styles.vacio : { padding: 16 }}
            data={visitas}
            keyExtractor={(item) => String(item.id_registro)}
            renderItem={({ item }) => <RegistroItem item={item} onEliminar={eliminar} />}
            refreshControl={
                <RefreshControl
                    refreshing={refrescando}
                    onRefresh={() => { setRefrescando(true); cargarVisitas(); }}
                    tintColor={AZUL}
                />
            }
            ListEmptyComponent={
                <View style={styles.centrado}>
                    <Text style={styles.vacioPrimario}>Sin registros</Text>
                    <Text style={styles.vacioSecundario}>Aún no has registrado ninguna visita.</Text>
                </View>
            }
        />
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f0f4f8' },
    centrado: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
    cargandoTexto: { color: '#888', marginTop: 10 },
    vacio: { flex: 1 },
    vacioPrimario: { fontSize: 18, fontWeight: 'bold', color: '#888', marginTop: 12 },
    vacioSecundario: { color: '#aaa', textAlign: 'center', marginTop: 6 },
    card: {
        backgroundColor: '#fff', borderRadius: 14, marginBottom: 12,
        elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.08, shadowRadius: 4, overflow: 'hidden',
    },
    cardHeader: {
        flexDirection: 'row', justifyContent: 'space-between',
        backgroundColor: AZUL, paddingHorizontal: 14, paddingVertical: 10,
    },
    cardId: { color: '#fff', fontWeight: 'bold', fontSize: 14 },
    cardFecha: { color: '#cce', fontSize: 13 },
    cardBody: { padding: 14, gap: 4 },
    cardDato: { fontSize: 14, color: '#333', lineHeight: 22 },
    cardDatoDestacado: { fontSize: 14, color: AZUL, fontWeight: '600' },
    eliminarBtn: {
        padding: 10, alignItems: 'center',
        borderTopWidth: 1, borderTopColor: '#eee',
    },
    eliminarTexto: { color: '#e74c3c', fontSize: 13, fontWeight: '600' },
});

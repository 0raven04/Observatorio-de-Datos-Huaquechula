/**
 * MisEncuestasScreen.js — Pantalla para visualizar las encuestas realizadas por el usuario actual.
 * Muestra tipo, hora y fecha, resumen y estado de sincronización (Cargado en BD del proyecto).
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
    View, Text, StyleSheet, FlatList, RefreshControl,
    ActivityIndicator, TouchableOpacity, Alert
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { encuestasService } from '../services/encuestasService';
import offlineQueue from '../services/offlineQueue';

const COLOR_TEXTO = '#4A4A4A';
const FONDO = '#EDEBE3';
const BLANCO = '#ffffff';
const VERDE_EXITO = '#28a745';
const AZUL_ACCENTO = '#3a6073';
const NARANJA_ALERTA = '#d97706';

export default function MisEncuestasScreen() {
    const [encuestas, setEncuestas] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [refrescando, setRefrescando] = useState(false);
    const [sincronizando, setSincronizando] = useState(false);

    const cargarMisEncuestas = useCallback(async () => {
        try {
            const data = await encuestasService.getMisEncuestas();
            setEncuestas(data);
        } catch (error) {
            console.error('Error al cargar encuestas:', error);
        } finally {
            setCargando(false);
            setRefrescando(false);
        }
    }, []);

    // Se ejecuta cada vez que el encuestador entra o regresa a esta pestaña
    useFocusEffect(
        useCallback(() => {
            cargarMisEncuestas();
        }, [cargarMisEncuestas])
    );

    // Escuchar eventos de la cola offline para actualización reactiva instantánea
    useEffect(() => {
        const unsubscribe = offlineQueue.subscribe(() => {
            cargarMisEncuestas();
        });
        return () => {
            if (typeof unsubscribe === 'function') unsubscribe();
        };
    }, [cargarMisEncuestas]);

    const onRefresh = () => {
        setRefrescando(true);
        cargarMisEncuestas();
    };

    const sincronizarOffline = async () => {
        setSincronizando(true);
        try {
            const res = await encuestasService.sincronizarColaOffline();
            await cargarMisEncuestas();
            if (res.synced > 0) {
                Alert.alert(
                    '✅ Sincronización Exitosa',
                    `Se sincronizaron ${res.synced} encuesta(s) con la base de datos central.`
                );
            } else if (res.remaining > 0) {
                Alert.alert(
                    '📡 Sin Conexión Aún',
                    'No se pudo conectar al servidor central. Las encuestas siguen resguardadas localmente.'
                );
            } else {
                Alert.alert('Al día', 'Todas las encuestas ya están en la base de datos.');
            }
        } catch (e) {
            Alert.alert('Aviso', 'Error al sincronizar. Revisa la cobertura o señal celular.');
        } finally {
            setSincronizando(false);
        }
    };

    const formatearFechaHora = (isoStr) => {
        try {
            const fecha = new Date(isoStr);
            return fecha.toLocaleString('es-MX', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true,
            });
        } catch (e) {
            return isoStr;
        }
    };

    const renderItem = ({ item }) => {
        const esBDOk = item.cargado_bd !== false;

        return (
            <View style={[styles.card, !esBDOk && styles.cardOffline]}>
                <View style={styles.cardHeader}>
                    <Text style={styles.cardIcon}>{item.icono || '📋'}</Text>
                    <View style={styles.cardHeaderTitle}>
                        <Text style={styles.tipoTexto}>{item.tipo}</Text>
                        <Text style={styles.fechaTexto}>🕒 {formatearFechaHora(item.fecha)}</Text>
                    </View>
                </View>

                {item.resumen ? (
                    <Text style={styles.resumenTexto}>{item.resumen}</Text>
                ) : null}

                <View style={styles.cardFooter}>
                    <View style={[styles.badge, esBDOk ? styles.badgeVerde : styles.badgeAmarillo]}>
                        <Text style={[styles.badgeText, esBDOk ? styles.badgeTextVerde : styles.badgeTextAmarillo]}>
                            {esBDOk ? '🟢 Cargado en BD del Proyecto' : '🟡 Guardado Localmente (Pendiente)'}
                        </Text>
                    </View>
                </View>
            </View>
        );
    };

    const totalEnBD = encuestas.filter(e => e.cargado_bd !== false).length;
    const totalPendientes = encuestas.length - totalEnBD;

    return (
        <View style={styles.container}>
            <View style={styles.banner}>
                <View style={styles.statBox}>
                    <Text style={styles.statNumber}>{encuestas.length}</Text>
                    <Text style={styles.statLabel}>Total Levantadas</Text>
                </View>
                <View style={styles.statBox}>
                    <Text style={[styles.statNumber, { color: VERDE_EXITO }]}>
                        {totalEnBD}
                    </Text>
                    <Text style={styles.statLabel}>En Base de Datos</Text>
                </View>
                {totalPendientes > 0 && (
                    <View style={styles.statBox}>
                        <Text style={[styles.statNumber, { color: NARANJA_ALERTA }]}>
                            {totalPendientes}
                        </Text>
                        <Text style={styles.statLabel}>Pendientes</Text>
                    </View>
                )}
            </View>

            {/* Banner de Sincronización si hay encuestas pendientes */}
            {totalPendientes > 0 && (
                <View style={styles.offlineActionBanner}>
                    <View style={{ flex: 1 }}>
                        <Text style={styles.offlineActionTitle}>📦 {totalPendientes} encuesta{totalPendientes > 1 ? 's' : ''} sin sincronizar</Text>
                        <Text style={styles.offlineActionSub}>Guardadas en el teléfono. Toca para enviar a la base de datos.</Text>
                    </View>
                    <TouchableOpacity
                        style={[styles.btnSync, sincronizando && { opacity: 0.6 }]}
                        onPress={sincronizarOffline}
                        disabled={sincronizando}
                    >
                        {sincronizando ? (
                            <ActivityIndicator size="small" color="#fff" />
                        ) : (
                            <Text style={styles.btnSyncText}>Sincronizar ⚡</Text>
                        )}
                    </TouchableOpacity>
                </View>
            )}

            {cargando ? (
                <View style={styles.centerContainer}>
                    <ActivityIndicator size="large" color={AZUL_ACCENTO} />
                    <Text style={styles.cargandoTexto}>Cargando historial de encuestas...</Text>
                </View>
            ) : encuestas.length === 0 ? (
                <View style={styles.centerContainer}>
                    <Text style={styles.emptyIcon}>📋</Text>
                    <Text style={styles.emptyTitulo}>No se han registrado encuestas</Text>
                    <Text style={styles.emptySub}>
                        Las encuestas que completes aparecerán aquí con su fecha, hora y estado en la base de datos.
                    </Text>
                    <TouchableOpacity style={styles.btnActualizar} onPress={onRefresh}>
                        <Text style={styles.btnActualizarTexto}>🔄 Actualizar</Text>
                    </TouchableOpacity>
                </View>
            ) : (
                <FlatList
                    data={encuestas}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={renderItem}
                    contentContainerStyle={styles.listContent}
                    refreshControl={
                        <RefreshControl refreshing={refrescando} onRefresh={onRefresh} colors={[AZUL_ACCENTO]} />
                    }
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: FONDO },
    banner: {
        flexDirection: 'row',
        backgroundColor: BLANCO,
        padding: 16,
        marginHorizontal: 16,
        marginTop: 16,
        marginBottom: 10,
        borderRadius: 12,
        elevation: 2,
        gap: 12,
    },
    statBox: { flex: 1, alignItems: 'center' },
    statNumber: { fontSize: 22, fontWeight: 'bold', color: COLOR_TEXTO },
    statLabel: { fontSize: 12, color: '#666', marginTop: 2 },
    listContent: { padding: 16, paddingTop: 4, paddingBottom: 40 },
    card: {
        backgroundColor: BLANCO,
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        elevation: 2,
        borderLeftWidth: 4,
        borderLeftColor: AZUL_ACCENTO,
    },
    cardOffline: {
        borderLeftColor: NARANJA_ALERTA,
        backgroundColor: '#fffdfa',
    },
    cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
    cardIcon: { fontSize: 24, marginRight: 12 },
    cardHeaderTitle: { flex: 1 },
    tipoTexto: { fontSize: 15, fontWeight: 'bold', color: COLOR_TEXTO },
    fechaTexto: { fontSize: 12, color: '#666', marginTop: 2 },
    resumenTexto: { fontSize: 13, color: '#555', backgroundColor: '#f9f9f9', padding: 8, borderRadius: 6, marginBottom: 8 },
    cardFooter: { flexDirection: 'row', justifyContent: 'flex-end', alignItems: 'center' },
    badge: { paddingVertical: 4, paddingHorizontal: 10, borderRadius: 20 },
    badgeVerde: { backgroundColor: '#e6f4ea' },
    badgeAmarillo: { backgroundColor: '#fff8e1' },
    badgeText: { fontSize: 12, fontWeight: 'bold' },
    badgeTextVerde: { color: VERDE_EXITO },
    badgeTextAmarillo: { color: '#f39c12' },
    offlineActionBanner: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fff3cd',
        borderWidth: 1,
        borderColor: '#ffeeba',
        borderRadius: 12,
        padding: 14,
        marginHorizontal: 16,
        marginBottom: 12,
        gap: 12,
    },
    offlineActionTitle: { fontSize: 14, fontWeight: 'bold', color: '#856404' },
    offlineActionSub: { fontSize: 11, color: '#856404', marginTop: 2 },
    btnSync: {
        backgroundColor: AZUL_ACCENTO,
        paddingVertical: 8,
        paddingHorizontal: 14,
        borderRadius: 8,
        justifyContent: 'center',
        alignItems: 'center',
    },
    btnSyncText: { color: BLANCO, fontWeight: 'bold', fontSize: 13 },
    centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
    cargandoTexto: { marginTop: 12, color: '#666', fontSize: 14 },
    emptyIcon: { fontSize: 48, marginBottom: 12 },
    emptyTitulo: { fontSize: 18, fontWeight: 'bold', color: COLOR_TEXTO, textAlign: 'center' },
    emptySub: { fontSize: 13, color: '#666', textAlign: 'center', marginTop: 6, marginBottom: 16 },
    btnActualizar: { backgroundColor: AZUL_ACCENTO, paddingVertical: 10, paddingHorizontal: 20, borderRadius: 20 },
    btnActualizarTexto: { color: BLANCO, fontWeight: 'bold', fontSize: 14 },
});

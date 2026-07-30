/**
 * MisEncuestasScreen.js — Pantalla para visualizar las encuestas realizadas por el usuario actual.
 * Muestra tipo, hora y fecha, resumen y estado de sincronización (Cargado en BD del proyecto).
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
    View, Text, StyleSheet, FlatList, RefreshControl,
    ActivityIndicator, TouchableOpacity,
} from 'react-native';
import { encuestasService } from '../services/encuestasService';

const COLOR_TEXTO = '#4A4A4A';
const FONDO = '#EDEBE3';
const BLANCO = '#ffffff';
const VERDE_EXITO = '#28a745';
const AZUL_ACCENTO = '#007bff';

export default function MisEncuestasScreen() {
    const [encuestas, setEncuestas] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [refrescando, setRefrescando] = useState(false);

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

    useEffect(() => {
        cargarMisEncuestas();
    }, [cargarMisEncuestas]);

    const onRefresh = () => {
        setRefrescando(true);
        cargarMisEncuestas();
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
            <View style={styles.card}>
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
                            {esBDOk ? '🟢 Cargado en BD del Proyecto' : '🟡 Guardado Localmente'}
                        </Text>
                    </View>
                </View>
            </View>
        );
    };

    return (
        <View style={styles.container}>
            <View style={styles.banner}>
                <View style={styles.statBox}>
                    <Text style={styles.statNumber}>{encuestas.length}</Text>
                    <Text style={styles.statLabel}>Encuestas Realizadas</Text>
                </View>
                <View style={styles.statBox}>
                    <Text style={[styles.statNumber, { color: VERDE_EXITO }]}>
                        {encuestas.filter(e => e.cargado_bd !== false).length}
                    </Text>
                    <Text style={styles.statLabel}>En Base de Datos</Text>
                </View>
            </View>

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
                        <RefreshControl refrescando={refrescando} onRefresh={onRefresh} colors={[AZUL_ACCENTO]} />
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
    centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
    cargandoTexto: { marginTop: 12, color: '#666', fontSize: 14 },
    emptyIcon: { fontSize: 48, marginBottom: 12 },
    emptyTitulo: { fontSize: 18, fontWeight: 'bold', color: COLOR_TEXTO, textAlign: 'center' },
    emptySub: { fontSize: 13, color: '#666', textAlign: 'center', marginTop: 6, marginBottom: 16 },
    btnActualizar: { backgroundColor: AZUL_ACCENTO, paddingVertical: 10, paddingHorizontal: 20, borderRadius: 20 },
    btnActualizarTexto: { color: BLANCO, fontWeight: 'bold', fontSize: 14 },
});

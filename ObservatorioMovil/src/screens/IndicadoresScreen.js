/**
 * IndicadoresScreen.js — Vista completa de todos los indicadores con historial de mediciones.
 * Para admin y propietarios del Observatorio.
 */
import React, { useState, useCallback } from 'react';
import {
    View, Text, ScrollView, StyleSheet, ActivityIndicator,
    Alert, TouchableOpacity, RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { indicadoresService } from '../services/indicadoresService';

const COLORES_EJE = ['#1a7abf', '#2a9d8f', '#e76f51', '#f4a261', '#8338ec'];

function MedicionBarra({ valor, max }) {
    const pct = max > 0 ? Math.min((parseFloat(valor) / max) * 100, 100) : 0;
    return (
        <View style={styles.barraContainer}>
            <View style={[styles.barraFill, { width: `${pct}%` }]} />
        </View>
    );
}

function IndicadorDetalle({ indicador, color }) {
    const [expandido, setExpandido] = useState(false);
    const mediciones = indicador.mediciones || [];
    const maxValor = Math.max(...mediciones.map((m) => parseFloat(m.valor)), 0);

    return (
        <TouchableOpacity
            style={styles.indicadorCard}
            onPress={() => setExpandido((e) => !e)}
            activeOpacity={0.85}
        >
            <View style={styles.indicadorHeader}>
                <View style={{ flex: 1 }}>
                    <Text style={styles.indicadorNombre}>{indicador.nombre}</Text>
                    {indicador.unidad_medida ? (
                        <Text style={styles.indicadorUnidad}>Unidad: {indicador.unidad_medida}</Text>
                    ) : null}
                </View>
                <Text style={styles.expandirIcon}>{expandido ? '▲' : '▼'}</Text>
            </View>

            {expandido && (
                <View style={styles.medicionesContainer}>
                    {mediciones.length === 0 ? (
                        <Text style={styles.sinDatos}>Sin mediciones registradas</Text>
                    ) : (
                        mediciones.map((m) => (
                            <View key={m.id} style={styles.medicionRow}>
                                <Text style={styles.medicionPeriodo}>{m.periodo}</Text>
                                <View style={{ flex: 1, marginHorizontal: 8 }}>
                                    <MedicionBarra valor={m.valor} max={maxValor} />
                                </View>
                                <Text style={[styles.medicionValor, { color }]}>{m.valor}</Text>
                            </View>
                        ))
                    )}
                </View>
            )}
        </TouchableOpacity>
    );
}

export default function IndicadoresScreen() {
    const [ejes, setEjes] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [refrescando, setRefrescando] = useState(false);

    const cargar = async () => {
        try {
            const data = await indicadoresService.getIndicadores();
            setEjes(data);
        } catch (e) {
            Alert.alert('Error', 'No se pudieron cargar los indicadores.');
        } finally {
            setCargando(false);
            setRefrescando(false);
        }
    };

    useFocusEffect(useCallback(() => { setCargando(true); cargar(); }, []));

    if (cargando) {
        return (
            <View style={styles.centrado}>
                <ActivityIndicator size="large" color="#2a9d8f" />
                <Text style={styles.cargandoTexto}>Cargando indicadores…</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            contentContainerStyle={styles.content}
            refreshControl={
                <RefreshControl refreshing={refrescando} onRefresh={() => { setRefrescando(true); cargar(); }} tintColor="#2a9d8f" />
            }
        >
            <Text style={styles.titulo}>Indicadores del Observatorio</Text>
            <Text style={styles.instruccion}>Toca un indicador para ver el historial de mediciones</Text>

            {ejes.map((eje, ejeIdx) => {
                const color = COLORES_EJE[ejeIdx % COLORES_EJE.length];
                return (
                    <View key={eje.id} style={styles.ejeSection}>
                        <View style={[styles.ejeHeader, { backgroundColor: color }]}>
                            <Text style={styles.ejeNombre}>{eje.nombre}</Text>
                            {eje.descripcion ? <Text style={styles.ejeDesc}>{eje.descripcion}</Text> : null}
                        </View>
                        {eje.categorias.map((cat) => (
                            <View key={cat.id} style={styles.categoriaSection}>
                                <Text style={[styles.categoriaNombre, { color }]}>{cat.nombre}</Text>
                                {cat.indicadores.map((ind) => (
                                    <IndicadorDetalle key={ind.id} indicador={ind} color={color} />
                                ))}
                            </View>
                        ))}
                    </View>
                );
            })}

            {ejes.length === 0 && (
                <View style={styles.centrado}>
                    <Text style={styles.vacio}>No hay indicadores registrados.</Text>
                </View>
            )}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f0f4f8' },
    content: { padding: 16, paddingBottom: 32 },
    centrado: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
    cargandoTexto: { color: '#888', marginTop: 10 },
    vacio: { color: '#999', fontSize: 16 },
    titulo: { fontSize: 20, fontWeight: 'bold', color: '#1a2e4a', marginBottom: 4 },
    instruccion: { fontSize: 13, color: '#888', marginBottom: 16 },
    ejeSection: {
        marginBottom: 16, borderRadius: 14, overflow: 'hidden',
        backgroundColor: '#fff', elevation: 2,
        shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.07, shadowRadius: 4,
    },
    ejeHeader: { padding: 14 },
    ejeNombre: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
    ejeDesc: { color: 'rgba(255,255,255,0.8)', fontSize: 12, marginTop: 3 },
    categoriaSection: { padding: 12 },
    categoriaNombre: { fontSize: 13, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 8 },
    indicadorCard: {
        backgroundColor: '#f7f9fc', borderRadius: 10, padding: 12, marginBottom: 8,
        borderWidth: 1, borderColor: '#e8edf3',
    },
    indicadorHeader: { flexDirection: 'row', alignItems: 'flex-start' },
    indicadorNombre: { fontSize: 14, fontWeight: '600', color: '#2d3748', lineHeight: 20 },
    indicadorUnidad: { fontSize: 12, color: '#888', marginTop: 2 },
    expandirIcon: { fontSize: 12, color: '#aaa', marginLeft: 8, marginTop: 2 },
    medicionesContainer: { marginTop: 10, borderTopWidth: 1, borderTopColor: '#eee', paddingTop: 10 },
    medicionRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
    medicionPeriodo: { width: 60, fontSize: 12, color: '#666' },
    barraContainer: { height: 8, backgroundColor: '#e8edf3', borderRadius: 4, overflow: 'hidden' },
    barraFill: { height: 8, backgroundColor: '#2a9d8f', borderRadius: 4 },
    medicionValor: { width: 60, fontSize: 13, fontWeight: 'bold', textAlign: 'right' },
    sinDatos: { fontSize: 13, color: '#bbb', fontStyle: 'italic' },
});

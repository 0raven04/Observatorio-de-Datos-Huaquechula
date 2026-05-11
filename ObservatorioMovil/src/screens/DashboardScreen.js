/**
 * DashboardScreen.js — Vista de resumen de indicadores para admin/propietario.
 * Muestra el último valor de cada indicador organizado por Eje temático.
 */
import React, { useState, useCallback } from 'react';
import {
    View, Text, ScrollView, StyleSheet,
    ActivityIndicator, Alert, TouchableOpacity, RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { indicadoresService } from '../services/indicadoresService';
import { useAuth } from '../context/AuthContext';

const VERDE = '#2a9d8f';
const COLORES_EJE = ['#1a7abf', '#2a9d8f', '#e76f51', '#f4a261', '#8338ec'];

export default function DashboardScreen() {
    const { usuario, logout } = useAuth();
    const [ejes, setEjes] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [refrescando, setRefrescando] = useState(false);

    const cargar = async () => {
        try {
            const data = await indicadoresService.getDashboard();
            setEjes(data);
        } catch (e) {
            Alert.alert('Error', 'No se pudieron cargar los indicadores del dashboard.');
        } finally {
            setCargando(false);
            setRefrescando(false);
        }
    };

    useFocusEffect(useCallback(() => { setCargando(true); cargar(); }, []));

    if (cargando) {
        return (
            <View style={styles.centrado}>
                <ActivityIndicator size="large" color={VERDE} />
                <Text style={styles.cargandoTexto}>Cargando dashboard…</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            contentContainerStyle={styles.content}
            refreshControl={
                <RefreshControl refreshing={refrescando} onRefresh={() => { setRefrescando(true); cargar(); }} tintColor={VERDE} />
            }
        >
            {/* Banner usuario */}
            <View style={[styles.banner, { backgroundColor: VERDE }]}>
                <View>
                    <Text style={styles.bannerSaludo}>Bienvenido/a,</Text>
                    <Text style={styles.bannerNombre}>{usuario?.nombre} {usuario?.ap}</Text>
                    <Text style={styles.bannerRol}>{usuario?.tipo}</Text>
                </View>
                <TouchableOpacity onPress={logout} style={styles.logoutBtn}>
                    <Text style={styles.logoutTexto}>Salir</Text>
                </TouchableOpacity>
            </View>

            <Text style={styles.titulo}>Dashboard de Indicadores</Text>
            <Text style={styles.subtitulo}>Huaquechula, Puebla — Último valor registrado</Text>

            {ejes.length === 0 ? (
                <View style={styles.centrado}>
                    <Text style={styles.vacio}>No hay indicadores disponibles.</Text>
                </View>
            ) : (
                ejes.map((eje, ejeIdx) => (
                    <View key={eje.id} style={styles.ejeSection}>
                        <View style={[styles.ejeHeader, { backgroundColor: COLORES_EJE[ejeIdx % COLORES_EJE.length] }]}>
                            <Text style={styles.ejeNombre}>{eje.nombre}</Text>
                        </View>
                        {eje.categorias.map((cat) => (
                            <View key={cat.id} style={styles.categoriaSection}>
                                <Text style={styles.categoriaNombre}>{cat.nombre}</Text>
                                <View style={styles.indicadoresGrid}>
                                    {cat.indicadores.map((ind) => (
                                        <View key={ind.id} style={styles.indicadorCard}>
                                            <Text style={styles.indicadorNombre} numberOfLines={2}>{ind.nombre}</Text>
                                            {ind.ultima_medicion ? (
                                                <>
                                                    <Text style={[styles.indicadorValor, { color: COLORES_EJE[ejeIdx % COLORES_EJE.length] }]}>
                                                        {ind.ultima_medicion.valor}
                                                    </Text>
                                                    <Text style={styles.indicadorUnidad}>{ind.unidad_medida}</Text>
                                                    <Text style={styles.indicadorPeriodo}>{ind.ultima_medicion.periodo}</Text>
                                                </>
                                            ) : (
                                                <Text style={styles.sinDatos}>Sin datos</Text>
                                            )}
                                        </View>
                                    ))}
                                </View>
                            </View>
                        ))}
                    </View>
                ))
            )}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f0f4f8' },
    content: { paddingBottom: 32 },
    centrado: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
    cargandoTexto: { color: '#888', marginTop: 10 },
    vacio: { color: '#999', fontSize: 16 },
    banner: {
        flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
        padding: 20, marginBottom: 0,
    },
    bannerSaludo: { color: 'rgba(255,255,255,0.8)', fontSize: 13 },
    bannerNombre: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
    bannerRol: { color: 'rgba(255,255,255,0.7)', fontSize: 12, textTransform: 'capitalize', marginTop: 2 },
    logoutBtn: { backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 6 },
    logoutTexto: { color: '#fff', fontSize: 13 },
    titulo: { fontSize: 20, fontWeight: 'bold', color: '#1a2e4a', marginHorizontal: 16, marginTop: 20, marginBottom: 4 },
    subtitulo: { fontSize: 13, color: '#888', marginHorizontal: 16, marginBottom: 16 },
    ejeSection: { marginHorizontal: 16, marginBottom: 16, borderRadius: 14, overflow: 'hidden', elevation: 2, backgroundColor: '#fff' },
    ejeHeader: { padding: 12 },
    ejeNombre: { color: '#fff', fontWeight: 'bold', fontSize: 15 },
    categoriaSection: { padding: 12 },
    categoriaNombre: { fontSize: 13, fontWeight: '600', color: '#555', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 },
    indicadoresGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
    indicadorCard: {
        backgroundColor: '#f7f9fc', borderRadius: 10, padding: 12,
        width: '47%', borderWidth: 1, borderColor: '#e8edf3',
    },
    indicadorNombre: { fontSize: 12, color: '#555', marginBottom: 6, lineHeight: 16 },
    indicadorValor: { fontSize: 22, fontWeight: 'bold' },
    indicadorUnidad: { fontSize: 11, color: '#888', marginTop: 2 },
    indicadorPeriodo: { fontSize: 11, color: '#aaa', marginTop: 4 },
    sinDatos: { fontSize: 13, color: '#bbb', fontStyle: 'italic' },
});

import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { encuestasService } from '../services/encuestasService';
import { useAuth } from '../context/AuthContext';

const AZUL = '#3a6073'; // Azul pizarra (apagado)
const VERDE = '#7d8c77'; // Verde musgo/sage (apagado)
const NARANJA = '#c4b897'; // Ocre/arena oscuro (apagado)
const MORADO = '#4A4A4A'; // Gris oscuro institucional

export default function SelectorEncuestasScreen({ navigation }) {
    const { usuario } = useAuth();
    const [encuestas, setEncuestas] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [pendientesOffline, setPendientesOffline] = useState(0);
    const [sincronizando, setSincronizando] = useState(false);

    const verificarColaOffline = useCallback(async () => {
        try {
            const count = await encuestasService.obtenerPendientesOffline();
            setPendientesOffline(count);
            // Si hay encuestas pendientes, intentar sincronizarlas silenciosamente
            if (count > 0 && !sincronizando) {
                encuestasService.sincronizarColaOffline().then(async (res) => {
                    if (res && res.synced > 0) {
                        const rest = await encuestasService.obtenerPendientesOffline();
                        setPendientesOffline(rest);
                    }
                }).catch(() => {});
            }
        } catch (e) {
            console.log('Error verificando cola offline:', e);
        }
    }, [sincronizando]);

    const ejecutarSincronizacionManual = async () => {
        setSincronizando(true);
        try {
            const res = await encuestasService.sincronizarColaOffline();
            const rest = await encuestasService.obtenerPendientesOffline();
            setPendientesOffline(rest);

            if (res.synced > 0) {
                Alert.alert(
                    '✅ Sincronización Exitosa',
                    `Se enviaron ${res.synced} encuesta(s) guardadas sin conexión al servidor del Observatorio.`
                );
            } else if (res.remaining > 0) {
                Alert.alert(
                    '📡 Sin Conexión Aún',
                    'No fue posible contactar al servidor central. Las encuestas continúan guardadas de forma segura en el dispositivo.'
                );
            } else {
                Alert.alert('Al día', 'No hay encuestas pendientes de sincronizar.');
            }
        } catch (e) {
            Alert.alert('Aviso', 'No se pudo completar la sincronización. Revisa tu cobertura celular.');
        } finally {
            setSincronizando(false);
        }
    };

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
            verificarColaOffline();
        }, [cargarEncuestas, verificarColaOffline])
    );

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            {/* Barra informativa del encuestador */}
            <View style={styles.userCard}>
                <View style={styles.userCardLeft}>
                    <View style={styles.userAvatar}>
                        <Text style={{ fontSize: 18 }}>👤</Text>
                    </View>
                    <View>
                        <Text style={styles.userCardName}>
                            {usuario?.nombre ? `${usuario.nombre} ${usuario.ap || ''}` : usuario?.nombre_usuario || 'Encuestador'}
                        </Text>
                        <Text style={styles.userCardSub}>
                            Usuario: @{usuario?.nombre_usuario || 'encuestador'}
                        </Text>
                    </View>
                </View>
            </View>

            {/* Banner de Sincronización Offline Resiliente */}
            {pendientesOffline > 0 && (
                <View style={styles.offlineBanner}>
                    <View style={{ flex: 1 }}>
                        <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 2 }}>
                            <Text style={{ fontSize: 16, marginRight: 6 }}>📦</Text>
                            <Text style={styles.offlineBannerTitle}>
                                {pendientesOffline} encuesta{pendientesOffline > 1 ? 's' : ''} pendiente{pendientesOffline > 1 ? 's' : ''}
                            </Text>
                        </View>
                        <Text style={styles.offlineBannerDesc}>
                            Guardada{pendientesOffline > 1 ? 's' : ''} localmente por sombra de red en Huaquechula.
                        </Text>
                    </View>
                    <TouchableOpacity
                        style={[styles.btnSyncOffline, sincronizando && { opacity: 0.6 }]}
                        onPress={ejecutarSincronizacionManual}
                        disabled={sincronizando}
                    >
                        {sincronizando ? (
                            <ActivityIndicator size="small" color="#fff" />
                        ) : (
                            <Text style={styles.btnSyncOfflineText}>Sincronizar ⚡</Text>
                        )}
                    </TouchableOpacity>
                </View>
            )}

            <View style={styles.header}>
                <Text style={styles.titulo}>Portal del Encuestador</Text>
                <Text style={styles.subtitulo}>Seleccione una opción de la lista para iniciar el levantamiento en campo.</Text>
            </View>

            {/* Sección 1: Encuestas Oficiales del Observatorio */}
            <Text style={styles.sectionTitle}>Encuestas Oficiales</Text>
            <View style={styles.grid}>
                {/* Opción Visitantes */}
                <TouchableOpacity
                    style={[styles.card, { borderLeftColor: AZUL }]}
                    onPress={() => navigation.navigate('EncuestaVisitante')}
                >
                    <View style={[styles.iconCircle, { backgroundColor: AZUL + '22' }]}>
                        <Text style={styles.iconEmoji}>🗺️</Text>
                    </View>
                    <View style={styles.cardInfo}>
                        <Text style={styles.cardTitle}>Encuesta: Perfil del Visitante</Text>
                        <Text style={styles.cardDesc}>Origen, actividades, zonas visitadas y nivel de satisfacción.</Text>
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
                        <Text style={styles.cardTitle}>Encuesta: Residente Local</Text>
                        <Text style={styles.cardDesc}>Eje de tradición, servicios públicos y turismo comunitario (TBC).</Text>
                    </View>
                    <Text style={styles.chevron}>›</Text>
                </TouchableOpacity>

                {/* Opción Institucional */}
                <TouchableOpacity
                    style={[styles.card, { borderLeftColor: NARANJA }]}
                    onPress={() => navigation.navigate('EncuestaInstitucional')}
                >
                    <View style={[styles.iconCircle, { backgroundColor: NARANJA + '22' }]}>
                        <Text style={styles.iconEmoji}>🏛️</Text>
                    </View>
                    <View style={styles.cardInfo}>
                        <Text style={styles.cardTitle}>Encuesta: Institucional</Text>
                        <Text style={styles.cardDesc}>Gobernanza municipal, salvaguardia del PCI y regulación.</Text>
                    </View>
                    <Text style={styles.chevron}>›</Text>
                </TouchableOpacity>
            </View>

            {/* Sección 2: Encuestas Promovidas en Campo */}
            <Text style={[styles.sectionTitle, { marginTop: 25 }]}>Encuestas Promovidas en Campo</Text>
            {cargando ? (
                <ActivityIndicator size="large" color={MORADO} style={{ marginTop: 20 }} />
            ) : encuestas.length === 0 ? (
                <View style={styles.emptyContainer}>
                    <Text style={styles.emptyText}>No hay encuestas adicionales habilitadas para móvil actualmente.</Text>
                </View>
            ) : (
                <View style={styles.grid}>
                    {encuestas.map((encuesta, idx) => {
                        const PALETA = [AZUL, VERDE, NARANJA, MORADO, '#5c6bc0'];
                        const EMOJIS = ['📋', '📝', '📊', '🌾', '📍'];
                        const colorTema = PALETA[idx % PALETA.length];
                        const emojiTema = EMOJIS[idx % EMOJIS.length];
                        return (
                            <TouchableOpacity
                                key={encuesta.id}
                                style={[styles.card, { borderLeftColor: colorTema }]}
                                onPress={() => navigation.navigate('CompletarEncuesta', { encuesta })}
                            >
                                <View style={[styles.iconCircle, { backgroundColor: colorTema + '22' }]}>
                                    <Text style={styles.iconEmoji}>{emojiTema}</Text>
                                </View>
                                <View style={styles.cardInfo}>
                                    <Text style={styles.cardTitle}>{encuesta.titulo}</Text>
                                    <Text style={styles.cardDesc} numberOfLines={2}>
                                        {encuesta.descripcion || 'Sin descripción disponible.'}
                                    </Text>
                                </View>
                                <Text style={styles.chevron}>›</Text>
                            </TouchableOpacity>
                        );
                    })}
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
    userCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 12,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 15,
        borderWidth: 1,
        borderColor: '#e2e8f0',
        elevation: 1,
    },
    userCardLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    userAvatar: {
        width: 38,
        height: 38,
        borderRadius: 19,
        backgroundColor: '#edf2f7',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 10,
    },
    userCardName: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#2d3748',
    },
    userCardSub: {
        fontSize: 11,
        color: '#718096',
    },
    offlineBanner: {
        backgroundColor: '#fffbeb',
        borderWidth: 1.5,
        borderColor: '#f59e0b',
        borderRadius: 12,
        padding: 12,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 15,
        elevation: 2,
    },
    offlineBannerTitle: {
        fontSize: 13,
        fontWeight: 'bold',
        color: '#92400e',
    },
    offlineBannerDesc: {
        fontSize: 11,
        color: '#b45309',
        marginTop: 1,
    },
    btnSyncOffline: {
        backgroundColor: '#f59e0b',
        paddingHorizontal: 12,
        paddingVertical: 8,
        borderRadius: 8,
        justifyContent: 'center',
        alignItems: 'center',
        minWidth: 100,
    },
    btnSyncOfflineText: {
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 'bold',
    },
});

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';

const AZUL = '#1a7abf';
const VERDE = '#2ecc71';
const NARANJA = '#f39c12';

export default function SelectorEncuestasScreen({ navigation }) {
    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            <View style={styles.header}>
                <Text style={styles.titulo}>Portal del Encuestador</Text>
                <Text style={styles.subtitulo}>Seleccione el tipo de levantamiento para iniciar en campo.</Text>
            </View>

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
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f9fa' },
    content: { padding: 20 },
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
});

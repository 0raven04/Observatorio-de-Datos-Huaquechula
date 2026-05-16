import React, { useState } from 'react';
import {
    View, Text, TouchableOpacity, StyleSheet,
    ScrollView, Alert, ActivityIndicator,
} from 'react-native';
import { encuestasService } from '../services/encuestasService';

const DORADO = '#FFC300';
const NARANJA_OBS = '#f39c12';
const TEXTO_OSCURO = '#212529';
const FONDO = '#eef1f5';
const BLANCO = '#ffffff';
const GRIS_BORDE = '#dee2e6';

function SelectorEscala({ label, valor, onSeleccionar, max = 5 }) {
    const opciones = Array.from({ length: max }, (_, i) => i + 1);
    return (
        <View style={styles.escalaContainer}>
            <Text style={styles.label}>{label}</Text>
            <View style={styles.selectorRow}>
                {opciones.map((num) => (
                    <TouchableOpacity
                        key={num}
                        style={[styles.selectorBtn, valor === num && styles.selectorBtnActivo]}
                        onPress={() => onSeleccionar(num)}
                    >
                        <Text style={[styles.selectorBtnTexto, valor === num && styles.selectorBtnTextoActivo]}>
                            {num}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );
}

function SelectorBotones({ label, opciones, seleccionado, onSeleccionar }) {
    return (
        <View style={styles.escalaContainer}>
            <Text style={styles.label}>{label}</Text>
            <View style={styles.selectorRow}>
                {opciones.map((op) => (
                    <TouchableOpacity
                        key={op}
                        style={[styles.selectorBtn, seleccionado === op && styles.selectorBtnActivo]}
                        onPress={() => onSeleccionar(op)}
                    >
                        <Text style={[styles.selectorBtnTexto, seleccionado === op && styles.selectorBtnTextoActivo]}>
                            {op}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );
}

export default function EncuestaComercioScreen({ navigation }) {
    const [enviando, setEnviando] = useState(false);
    const [form, setForm] = useState({
        tipo_comercio: '',
        participacion_decisiones: null,
        capacitacion_turistica: null,
        integracion_turistica: null,
    });

    const enviarFormulario = async () => {
        if (!form.tipo_comercio) {
            Alert.alert('Campo incompleto', 'Por favor selecciona el tipo de comercio.');
            return;
        }

        setEnviando(true);
        try {
            await encuestasService.crearEncuestaComercio(form);
            Alert.alert('✅ Éxito', 'La encuesta de comercio ha sido guardada correctamente.');
            navigation.goBack();
        } catch (error) {
            Alert.alert('Error', 'No se pudo guardar la encuesta. Revisa tu conexión.');
        } finally {
            setEnviando(false);
        }
    };

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            <Text style={styles.titulo}>Encuesta a Comercio / Artesano</Text>
            
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Giro Comercial</Text>
                <SelectorBotones 
                    label="Tipo de Comercio"
                    opciones={['Hospedaje', 'Alimentos', 'Artesanía', 'Guía', 'Otro']}
                    seleccionado={form.tipo_comercio}
                    onSeleccionar={(v) => setForm({...form, tipo_comercio: v})}
                />
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Gobernanza y Gestión</Text>
                <SelectorEscala 
                    label="Nivel de participación en decisiones turísticas (1-4)"
                    max={4}
                    valor={form.participacion_decisiones}
                    onSeleccionar={(v) => setForm({...form, participacion_decisiones: v})}
                />
                <SelectorEscala 
                    label="Nivel de capacitación turística recibida (1-3)"
                    max={3}
                    valor={form.capacitacion_turistica}
                    onSeleccionar={(v) => setForm({...form, capacitacion_turistica: v})}
                />
                <SelectorEscala 
                    label="Nivel de integración con proyectos turísticos (1-3)"
                    max={3}
                    valor={form.integracion_turistica}
                    onSeleccionar={(v) => setForm({...form, integracion_turistica: v})}
                />
            </View>

            <TouchableOpacity
                style={[styles.boton, enviando && styles.botonDeshabilitado]}
                onPress={enviarFormulario}
                disabled={enviando}
            >
                {enviando ? (
                    <ActivityIndicator color="#fff" />
                ) : (
                    <Text style={styles.botonTexto}>Guardar Registro</Text>
                )}
            </TouchableOpacity>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: FONDO },
    content: { padding: 20, paddingBottom: 50 },
    titulo: { fontSize: 22, fontWeight: 'bold', color: TEXTO_OSCURO, marginBottom: 20 },
    section: { backgroundColor: BLANCO, borderRadius: 15, padding: 16, marginBottom: 15, elevation: 2 },
    sectionTitle: { fontSize: 16, fontWeight: 'bold', color: NARANJA_OBS, marginBottom: 12 },
    label: { fontSize: 13, fontWeight: '600', color: '#555', marginTop: 10, marginBottom: 6 },
    escalaContainer: { marginTop: 10 },
    selectorRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
    selectorBtn: {
        paddingHorizontal: 12, paddingVertical: 8, borderRadius: 10,
        borderWidth: 2, borderColor: GRIS_BORDE, backgroundColor: BLANCO, minWidth: 40, alignItems: 'center'
    },
    selectorBtnActivo: { borderColor: DORADO },
    selectorBtnTexto: { fontSize: 13, color: '#555' },
    selectorBtnTextoActivo: { color: TEXTO_OSCURO, fontWeight: '700' },
    boton: {
        backgroundColor: BLANCO, borderRadius: 12, borderWidth: 2, borderColor: DORADO,
        paddingVertical: 15, alignItems: 'center', marginTop: 10, elevation: 2
    },
    botonDeshabilitado: { opacity: 0.5 },
    botonTexto: { color: TEXTO_OSCURO, fontSize: 16, fontWeight: 'bold' },
});

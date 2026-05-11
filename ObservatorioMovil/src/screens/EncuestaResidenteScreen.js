import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    ScrollView, Alert, ActivityIndicator,
} from 'react-native';
import { encuestasService } from '../services/encuestasService';

const DORADO = '#FFC300';
const VERDE_OBS = '#2ecc71';
const TEXTO_OSCURO = '#212529';
const FONDO = '#eef1f5';
const BLANCO = '#ffffff';
const GRIS_INPUT = '#f5f5f5';
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

export default function EncuestaResidenteScreen({ navigation }) {
    const [enviando, setEnviando] = useState(false);
    const [form, setForm] = useState({
        edad: '',
        genero: '',
        barrio_colonia: '',
        confianza_policia: null,
        percepcion_inseguridad: null,
        tension_festividades: null,
        acceso_servicios_festividades: null,
        perdida_tradicion: null,
        calidad_aire: null,
        gestion_residuos: null,
    });

    const enviarFormulario = async () => {
        // Validar campos básicos
        if (!form.edad || !form.genero || !form.barrio_colonia) {
            Alert.alert('Campos incompletos', 'Por favor llena los datos demográficos.');
            return;
        }

        setEnviando(true);
        try {
            const payload = {
                ...form,
                edad: parseInt(form.edad),
            };
            await encuestasService.crearEncuestaResidente(payload);
            Alert.alert('✅ Éxito', 'La encuesta ha sido guardada correctamente.');
            navigation.goBack();
        } catch (error) {
            Alert.alert('Error', 'No se pudo guardar la encuesta. Revisa tu conexión.');
        } finally {
            setEnviando(false);
        }
    };

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            <Text style={styles.titulo}>Encuesta a Residente</Text>
            
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Datos Demográficos</Text>
                <Text style={styles.label}>Edad</Text>
                <TextInput
                    style={styles.input}
                    keyboardType="numeric"
                    value={form.edad}
                    onChangeText={(v) => setForm({...form, edad: v})}
                    placeholder="Ej: 25"
                />
                <SelectorBotones 
                    label="Género"
                    opciones={['Hombre', 'Mujer', 'Otro']}
                    seleccionado={form.genero}
                    onSeleccionar={(v) => setForm({...form, genero: v})}
                />
                <Text style={styles.label}>Barrio o Colonia</Text>
                <TextInput
                    style={styles.input}
                    value={form.barrio_colonia}
                    onChangeText={(v) => setForm({...form, barrio_colonia: v})}
                    placeholder="Ej: Centro"
                />
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Seguridad Ciudadana</Text>
                <SelectorEscala 
                    label="Nivel de confianza en la policía municipal (1-5)"
                    valor={form.confianza_policia}
                    onSeleccionar={(v) => setForm({...form, confianza_policia: v})}
                />
                <SelectorEscala 
                    label="¿Qué tan inseguro se siente en su localidad? (1-5)"
                    valor={form.percepcion_inseguridad}
                    onSeleccionar={(v) => setForm({...form, percepcion_inseguridad: v})}
                />
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Tradiciones y Turismo</Text>
                <SelectorEscala 
                    label="Tensión por saturación de turistas en festividades (1-5)"
                    valor={form.tension_festividades}
                    onSeleccionar={(v) => setForm({...form, tension_festividades: v})}
                />
                <SelectorEscala 
                    label="Dificultad de acceso a servicios en festividades (1-4)"
                    max={4}
                    valor={form.acceso_servicios_festividades}
                    onSeleccionar={(v) => setForm({...form, acceso_servicios_festividades: v})}
                />
                <SelectorEscala 
                    label="Percepción de pérdida de tradiciones (1-5)"
                    valor={form.perdida_tradicion}
                    onSeleccionar={(v) => setForm({...form, perdida_tradicion: v})}
                />
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Medio Ambiente</Text>
                <SelectorEscala 
                    label="Calidad del aire en su zona (1-3)"
                    max={3}
                    valor={form.calidad_aire}
                    onSeleccionar={(v) => setForm({...form, calidad_aire: v})}
                />
                <SelectorEscala 
                    label="Eficiencia en la gestión de residuos (1-3)"
                    max={3}
                    valor={form.gestion_residuos}
                    onSeleccionar={(v) => setForm({...form, gestion_residuos: v})}
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
                    <Text style={styles.botonTexto}>Guardar Encuesta</Text>
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
    sectionTitle: { fontSize: 16, fontWeight: 'bold', color: VERDE_OBS, marginBottom: 12 },
    label: { fontSize: 13, fontWeight: '600', color: '#555', marginTop: 10, marginBottom: 6 },
    input: {
        backgroundColor: GRIS_INPUT, borderWidth: 1, borderColor: GRIS_BORDE,
        borderRadius: 12, paddingHorizontal: 15, paddingVertical: 10, fontSize: 15,
    },
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

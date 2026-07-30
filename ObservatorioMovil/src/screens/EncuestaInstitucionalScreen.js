/**
 * EncuestaInstitucionalScreen.js — Formulario digital para la Encuesta: Institucional.
 * Réplica idéntica en bloques, preguntas y opciones del formulario web del Observatorio.
 */
import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    ScrollView, Alert, ActivityIndicator,
} from 'react-native';
import { encuestasService } from '../services/encuestasService';

const DORADO = '#D6CEAA';
const AZUL_INSTITUCIONAL = '#34495e';
const TEXTO_OSCURO = '#4A4A4A';
const FONDO = '#EDEBE3';
const BLANCO = '#ffffff';
const GRIS_BORDE = '#B3B3B3';

const CANALES_DIFUSION_OPCIONES = [
    'Campañas digitales y uso de redes sociales institucionales',
    'Vinculación con agencias de viaje o secretarías de turismo estatal/federal',
    'Publicaciones académicas, folletería impresa y guías locales',
    'Eventos, ferias de turismo o intercambios culturales exteriores',
    'Ninguno',
];

function SelectorRadio({ opciones, seleccionado, onSeleccionar }) {
    return (
        <View style={styles.radioGroup}>
            {opciones.map((op) => {
                const val = typeof op === 'object' ? op.val : op;
                const txt = typeof op === 'object' ? op.label : String(op);
                const marcado = seleccionado === val;
                return (
                    <TouchableOpacity
                        key={String(val)}
                        style={[styles.radioCard, marcado && styles.radioCardMarcado]}
                        onPress={() => onSeleccionar(val)}
                    >
                        <Text style={styles.radioDot}>{marcado ? '🔘' : '⚪'}</Text>
                        <Text style={[styles.radioText, marcado && styles.radioTextMarcado]}>{txt}</Text>
                    </TouchableOpacity>
                );
            })}
        </View>
    );
}

function MultiSelectCheckboxes({ opciones, seleccionados, onToggle }) {
    return (
        <View style={styles.multiGrid}>
            {opciones.map((op) => {
                const marcado = seleccionados.includes(op);
                return (
                    <TouchableOpacity
                        key={op}
                        style={[styles.checkCard, marcado && styles.checkCardMarcado]}
                        onPress={() => onToggle(op)}
                    >
                        <Text style={styles.checkIcon}>{marcado ? '☑️' : '⏹️'}</Text>
                        <Text style={[styles.checkLabel, marcado && styles.checkLabelMarcado]}>{op}</Text>
                    </TouchableOpacity>
                );
            })}
        </View>
    );
}

export default function EncuestaInstitucionalScreen({ navigation }) {
    const [enviando, setEnviando] = useState(false);
    const [form, setForm] = useState({
        seguimiento_salvaguardia: 'si',
        canales_difusion: [],
        visitantes_festividades: '',
        regulacion: 'reglamento',
        gestion_tecnica: 'si',
        integracion_territorial: 'entre_25_50',
        visitantes_anual: '',
    });

    const toggleCanal = (canal) => {
        setForm((prev) => {
            const arr = prev.canales_difusion.includes(canal)
                ? prev.canales_difusion.filter((c) => c !== canal)
                : [...prev.canales_difusion, canal];
            return { ...prev, canales_difusion: arr };
        });
    };

    const enviarFormulario = async () => {
        if (!form.visitantes_festividades || !form.visitantes_anual) {
            Alert.alert('Campos requeridos', 'Por favor completa las estimaciones de visitantes.');
            return;
        }

        setEnviando(true);
        try {
            const payload = {
                seguimiento_salvaguardia: form.seguimiento_salvaguardia,
                canales_difusion: form.canales_difusion.join(', '),
                visitantes_festividades: parseInt(form.visitantes_festividades) || 0,
                regulacion: form.regulacion,
                gestion_tecnica: form.gestion_tecnica,
                integracion_territorial: form.integracion_territorial,
                visitantes_anual: parseInt(form.visitantes_anual) || 0,
            };

            await encuestasService.crearEncuestaInstitucional(payload);
            Alert.alert('✅ Encuesta Guardada', 'La Encuesta Institucional fue registrada con éxito.');
            navigation.goBack();
        } catch (error) {
            const msg = error.response?.data ? JSON.stringify(error.response.data) : error.message;
            Alert.alert('Error al guardar', msg);
        } finally {
            setEnviando(false);
        }
    };

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            <View style={styles.banner}>
                <Text style={styles.bannerIcon}>🏛️</Text>
                <View style={{ flex: 1 }}>
                    <Text style={styles.bannerTitulo}>Nueva Encuesta: Institucional</Text>
                    <Text style={styles.bannerDesc}>
                        Dirigido a: Autoridades municipales (Turismo, Cultura, Servicios Públicos, Planeación).
                    </Text>
                </View>
            </View>

            {/* Bloque A: Eje de Tradición y Patrimonio */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>🏛️ Bloque A: Eje de Tradición y Patrimonio</Text>

                <Text style={styles.label}>
                    1. ¿Cuenta la administración municipal actual con registros o indicadores formales para dar seguimiento al estado de conservación del PCI?
                </Text>
                <SelectorRadio
                    opciones={[
                        { val: 'si', label: 'Sí, contamos con herramientas de monitoreo e inventarios' },
                        { val: 'eventual', label: 'Registros eventuales (fotografías/bitácoras), sin sistema formal' },
                        { val: 'no', label: 'No se cuenta con herramientas institucionales' }
                    ]}
                    seleccionado={form.seguimiento_salvaguardia}
                    onSeleccionar={(v) => setForm({ ...form, seguimiento_salvaguardia: v })}
                />

                <Text style={[styles.label, { marginTop: 14 }]}>
                    2. ¿Cuáles son los canales oficiales y mecanismos institucionales implementados para la difusión del PCI?
                </Text>
                <MultiSelectCheckboxes
                    opciones={CANALES_DIFUSION_OPCIONES}
                    seleccionados={form.canales_difusion}
                    onToggle={toggleCanal}
                />

                <Text style={[styles.label, { marginTop: 14 }]}>
                    3. Número de visitantes registrados al municipio durante la tradición (festividades):
                </Text>
                <TextInput
                    style={styles.input}
                    placeholder="Ej. 5000"
                    placeholderTextColor="#aaa"
                    keyboardType="numeric"
                    value={form.visitantes_festividades}
                    onChangeText={(v) => setForm({ ...form, visitantes_festividades: v })}
                />
            </View>

            {/* Bloque B: Eje de Turismo de Base Comunitaria */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>👥 Bloque B: Eje de Turismo de Base Comunitaria (TBC)</Text>

                <Text style={styles.label}>
                    4. ¿Qué mecanismos normativos o reglamentos locales posee el ayuntamiento para regular el flujo turístico?
                </Text>
                <SelectorRadio
                    opciones={[
                        { val: 'reglamento', label: 'Reglamento de turismo vigente con normativas comunitarias' },
                        { val: 'normas_basicas', label: 'Normas básicas de comercio sin reglamento específico' },
                        { val: 'no', label: 'No existen herramientas de regulación turística' }
                    ]}
                    seleccionado={form.regulacion}
                    onSeleccionar={(v) => setForm({ ...form, regulacion: v })}
                />

                <Text style={[styles.label, { marginTop: 14 }]}>
                    5. ¿Dispone el municipio de un Plan de Desarrollo Turístico Municipal u otras herramientas de gestión técnica?
                </Text>
                <SelectorRadio
                    opciones={[
                        { val: 'si', label: 'Sí, Plan Sectorial alineado a la gestión comunitaria' },
                        { val: 'general', label: 'Plan general sin enfoque específico en turismo comunitario' },
                        { val: 'no', label: 'No se cuenta con herramientas de planeación técnica' }
                    ]}
                    seleccionado={form.gestion_tecnica}
                    onSeleccionar={(v) => setForm({ ...form, gestion_tecnica: v })}
                />

                <Text style={[styles.label, { marginTop: 14 }]}>
                    6. ¿Qué porcentaje de las comunidades rurales con vocación turística están integradas en los corredores oficiales?
                </Text>
                <SelectorRadio
                    opciones={[
                        { val: 'menos_25', label: 'Menos del 25% de las localidades' },
                        { val: 'entre_25_50', label: 'Entre el 25% y el 50% de las localidades' },
                        { val: 'mas_50', label: 'Más del 50% de las localidades rurales' }
                    ]}
                    seleccionado={form.integracion_territorial}
                    onSeleccionar={(v) => setForm({ ...form, integracion_territorial: v })}
                />

                <Text style={[styles.label, { marginTop: 14 }]}>
                    7. Número de visitantes registrados al municipio durante el año:
                </Text>
                <TextInput
                    style={styles.input}
                    placeholder="Ej. 25000"
                    placeholderTextColor="#aaa"
                    keyboardType="numeric"
                    value={form.visitantes_anual}
                    onChangeText={(v) => setForm({ ...form, visitantes_anual: v })}
                />
            </View>

            <TouchableOpacity
                style={[styles.btnEnviar, enviando && styles.btnDeshabilitado]}
                onPress={enviarFormulario}
                disabled={enviando}
            >
                {enviando ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnTexto}>Guardar Encuesta</Text>}
            </TouchableOpacity>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: FONDO },
    content: { padding: 16, paddingBottom: 40 },
    banner: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: BLANCO,
        padding: 16,
        borderRadius: 12,
        marginBottom: 16,
        borderLeftWidth: 5,
        borderLeftColor: AZUL_INSTITUCIONAL,
        elevation: 2,
    },
    bannerIcon: { fontSize: 28, marginRight: 12 },
    bannerTitulo: { fontSize: 18, fontWeight: 'bold', color: AZUL_INSTITUCIONAL },
    bannerDesc: { fontSize: 12, color: '#666', marginTop: 2 },
    block: {
        backgroundColor: BLANCO,
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        elevation: 2,
    },
    blockTitle: {
        fontSize: 15,
        fontWeight: 'bold',
        color: TEXTO_OSCURO,
        marginBottom: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
        paddingBottom: 6,
    },
    label: { fontSize: 13, fontWeight: '600', color: TEXTO_OSCURO, marginBottom: 8 },
    input: {
        backgroundColor: '#f9f9f9',
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 8,
        padding: 10,
        fontSize: 14,
        color: '#333',
        marginTop: 4,
    },
    radioGroup: { gap: 8, marginTop: 4 },
    radioCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#f9f9f9',
        padding: 10,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#eee',
    },
    radioCardMarcado: { backgroundColor: '#f0f4f8', borderColor: AZUL_INSTITUCIONAL },
    radioDot: { fontSize: 14, marginRight: 8 },
    radioText: { fontSize: 12, color: '#444', flex: 1 },
    radioTextMarcado: { color: AZUL_INSTITUCIONAL, fontWeight: 'bold' },
    multiGrid: { gap: 8, marginTop: 4 },
    checkCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#f9f9f9',
        padding: 10,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#eee',
    },
    checkCardMarcado: { backgroundColor: '#f0f4f8', borderColor: AZUL_INSTITUCIONAL },
    checkIcon: { fontSize: 16, marginRight: 8 },
    checkLabel: { fontSize: 12, color: '#444', flex: 1 },
    checkLabelMarcado: { color: AZUL_INSTITUCIONAL, fontWeight: 'bold' },
    btnEnviar: {
        backgroundColor: AZUL_INSTITUCIONAL,
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
        marginTop: 10,
        elevation: 3,
    },
    btnDeshabilitado: { opacity: 0.6 },
    btnTexto: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});

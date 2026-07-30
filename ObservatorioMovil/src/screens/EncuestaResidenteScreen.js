/**
 * EncuestaResidenteScreen.js — Formulario digital para la Encuesta: Residente Local.
 * Réplica idéntica en bloques, preguntas y opciones del formulario web del Observatorio.
 */
import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    ScrollView, Alert, ActivityIndicator,
} from 'react-native';
import { encuestasService } from '../services/encuestasService';

const DORADO = '#D6CEAA';
const VERDE_OBS = '#28a745';
const TEXTO_OSCURO = '#4A4A4A';
const FONDO = '#EDEBE3';
const BLANCO = '#ffffff';
const GRIS_BORDE = '#B3B3B3';

function SelectorSelect({ label, opciones, seleccionado, onSeleccionar }) {
    return (
        <View style={styles.fieldWrap}>
            <Text style={styles.label}>{label}</Text>
            <View style={styles.chipRow}>
                {opciones.map((op) => {
                    const val = typeof op === 'object' ? op.val : op;
                    const txt = typeof op === 'object' ? op.label : String(op);
                    const activo = seleccionado === val;
                    return (
                        <TouchableOpacity
                            key={String(val)}
                            style={[styles.chipBtn, activo && styles.chipBtnActivo]}
                            onPress={() => onSeleccionar(val)}
                        >
                            <Text style={[styles.chipTexto, activo && styles.chipTextoActivo]}>{txt}</Text>
                        </TouchableOpacity>
                    );
                })}
            </View>
        </View>
    );
}

export default function EncuestaResidenteScreen({ navigation }) {
    const [enviando, setEnviando] = useState(false);
    const [form, setForm] = useState({
        edad: '35',
        genero: 'Femenino',
        barrio_colonia: 'Centro',
        confianza_policia: 3,
        percepcion_inseguridad: 2,
        tension_festividades: '2',
        acceso_servicios_festividades: '3',
        perdida_tradicion: '2',
        participacion_preservacion: 'si',
        participacion_decisiones: 'no',
        capacitacion_turistica: 'no',
        beneficio_economico: 'indirecto',
        interes_jovenes: 'medio',
    });

    const enviarFormulario = async () => {
        setEnviando(true);
        try {
            const payload = {
                ...form,
                edad: parseInt(form.edad) || 30,
                confianza_policia: parseInt(form.confianza_policia) || 3,
                percepcion_inseguridad: parseInt(form.percepcion_inseguridad) || 2,
            };
            await encuestasService.crearEncuestaResidente(payload);
            Alert.alert('✅ Encuesta Guardada', 'La Encuesta de Residente Local fue registrada exitosamente.');
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
                <Text style={styles.bannerIcon}>🏠</Text>
                <View style={{ flex: 1 }}>
                    <Text style={styles.bannerTitulo}>Encuesta: Residente Local</Text>
                    <Text style={styles.bannerDesc}>
                        Dirigido a: Residentes de la cabecera municipal y localidades de Huaquechula.
                    </Text>
                </View>
            </View>

            {/* Datos Generales */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>Datos Demográficos</Text>
                <Text style={styles.label}>Edad</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Ej. 35"
                    placeholderTextColor="#aaa"
                    keyboardType="numeric"
                    value={form.edad}
                    onChangeText={(v) => setForm({ ...form, edad: v })}
                />
                <Text style={styles.label}>Género</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Femenino / Masculino / Otro"
                    placeholderTextColor="#aaa"
                    value={form.genero}
                    onChangeText={(v) => setForm({ ...form, genero: v })}
                />
                <Text style={styles.label}>Barrio / Colonia / Localidad</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Ej. Centro"
                    placeholderTextColor="#aaa"
                    value={form.barrio_colonia}
                    onChangeText={(v) => setForm({ ...form, barrio_colonia: v })}
                />
            </View>

            {/* Bloque A: Eje de Tradición y Patrimonio */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>🏛️ Bloque A: Eje de Tradición y Patrimonio</Text>
                <Text style={styles.subtext}>
                    Mide las tensiones y esfuerzos de preservación de festividades (Altares Monumentales, Santa Cruz, etc.).
                </Text>

                <SelectorSelect
                    label="1. ¿Durante las festividades, qué tanto considera que la afluencia de visitantes altera negativamente su rutina diaria?"
                    opciones={[
                        { val: '1', label: '1 - Nada / Muy poco' },
                        { val: '2', label: '2 - Moderado' },
                        { val: '3', label: '3 - Bastante' },
                        { val: '4', label: '4 - Mucho / Severo' }
                    ]}
                    seleccionado={form.tension_festividades}
                    onSeleccionar={(v) => setForm({ ...form, tension_festividades: v })}
                />

                <SelectorSelect
                    label="2. Durante las temporadas festivas, ¿cómo califica el acceso y disponibilidad de servicios públicos (agua, basura, seguridad)?"
                    opciones={[
                        { val: '1', label: '1 - Muy deficiente' },
                        { val: '2', label: '2 - Regular' },
                        { val: '3', label: '3 - Bueno' },
                        { val: '4', label: '4 - Excelente' }
                    ]}
                    seleccionado={form.acceso_servicios_festividades}
                    onSeleccionar={(v) => setForm({ ...form, acceso_servicios_festividades: v })}
                />

                <SelectorSelect
                    label="3. ¿Considera que la llegada del turismo ha provocado cambios que desvirtúan el significado original de nuestras tradiciones?"
                    opciones={[
                        { val: '1', label: '1 - Sin alteración' },
                        { val: '2', label: '2 - Poco impacto' },
                        { val: '3', label: '3 - Alteración moderada' },
                        { val: '4', label: '4 - Alta desvirtuación' }
                    ]}
                    seleccionado={form.perdida_tradicion}
                    onSeleccionar={(v) => setForm({ ...form, perdida_tradicion: v })}
                />

                <SelectorSelect
                    label="4. ¿Participa de forma activa en actividades comunitarias de preservación (altares, artesanías, cocina tradicional)?"
                    opciones={[
                        { val: 'si', label: 'Sí, activamente' },
                        { val: 'eventual', label: 'Eventualmente' },
                        { val: 'no', label: 'No participo' }
                    ]}
                    seleccionado={form.participacion_preservacion}
                    onSeleccionar={(v) => setForm({ ...form, participacion_preservacion: v })}
                />
            </View>

            {/* Bloque B: Eje de Turismo de Base Comunitaria */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>👥 Bloque B: Eje de Turismo de Base Comunitaria (TBC)</Text>
                <Text style={styles.subtext}>
                    Evalúa la participación y protagonismo de la comunidad en la gestión y beneficios del turismo.
                </Text>

                <SelectorSelect
                    label="5. ¿Ha participado o ha sido convocado a reuniones comunitarias para decidir cómo gestionar el turismo?"
                    opciones={[
                        { val: 'si', label: 'Sí, he participado' },
                        { val: 'interesado', label: 'Interesado, pero no convocado' },
                        { val: 'no', label: 'No me interesa / No participo' }
                    ]}
                    seleccionado={form.participacion_decisiones}
                    onSeleccionar={(v) => setForm({ ...form, participacion_decisiones: v })}
                />

                <SelectorSelect
                    label="6. ¿Ha recibido capacitación o información clara sobre cómo atender al turismo de manera responsable?"
                    opciones={[
                        { val: 'si', label: 'Sí, útil y suficiente' },
                        { val: 'proceso', label: 'En proceso / Insuficiente' },
                        { val: 'no', label: 'No he recibido' }
                    ]}
                    seleccionado={form.capacitacion_turistica}
                    onSeleccionar={(v) => setForm({ ...form, capacitacion_turistica: v })}
                />

                <SelectorSelect
                    label="7. ¿Su hogar percibe un beneficio económico o social directo derivado de proyectos turísticos locales?"
                    opciones={[
                        { val: 'si', label: 'Sí, directo' },
                        { val: 'indirecto', label: 'Beneficio indirecto' },
                        { val: 'no', label: 'Sin beneficio' }
                    ]}
                    seleccionado={form.beneficio_economico}
                    onSeleccionar={(v) => setForm({ ...form, beneficio_economico: v })}
                />

                <SelectorSelect
                    label="8. En su hogar, ¿las generaciones más jóvenes muestran interés y aprenden los saberes de nuestras tradiciones?"
                    opciones={[
                        { val: 'alto', label: 'Alto interés' },
                        { val: 'medio', label: 'Interés moderado' },
                        { val: 'bajo', label: 'Bajo / Nulo interés' }
                    ]}
                    seleccionado={form.interes_jovenes}
                    onSeleccionar={(v) => setForm({ ...form, interes_jovenes: v })}
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
        borderLeftColor: VERDE_OBS,
        elevation: 2,
    },
    bannerIcon: { fontSize: 28, marginRight: 12 },
    bannerTitulo: { fontSize: 18, fontWeight: 'bold', color: VERDE_OBS },
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
        marginBottom: 6,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
        paddingBottom: 6,
    },
    subtext: { fontSize: 12, color: '#666', marginBottom: 12, fontStyle: 'italic' },
    fieldWrap: { marginBottom: 14 },
    label: { fontSize: 13, fontWeight: '600', color: TEXTO_OSCURO, marginBottom: 6 },
    input: {
        backgroundColor: '#f9f9f9',
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 8,
        padding: 10,
        fontSize: 14,
        color: '#333',
        marginBottom: 10,
    },
    chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
    chipBtn: {
        backgroundColor: '#f5f5f5',
        paddingVertical: 8,
        paddingHorizontal: 12,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#ddd',
        marginBottom: 4,
    },
    chipBtnActivo: { backgroundColor: VERDE_OBS, borderColor: VERDE_OBS },
    chipTexto: { fontSize: 12, color: '#444' },
    chipTextoActivo: { color: '#fff', fontWeight: 'bold' },
    btnEnviar: {
        backgroundColor: VERDE_OBS,
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
        marginTop: 10,
        elevation: 3,
    },
    btnDeshabilitado: { opacity: 0.6 },
    btnTexto: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});

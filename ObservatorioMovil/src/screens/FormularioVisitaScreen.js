/**
 * FormularioVisitaScreen.js — Formulario digital para que los encuestadores
 * registren visitas turísticas en campo, enviando datos al API Django.
 */
import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    ScrollView, Alert, ActivityIndicator, Switch,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { visitasService } from '../services/visitasService';

// Paleta del Observatorio (alineada con el sitio web)
const DORADO = '#FFC300';
const DORADO_OSCURO = '#D4A200';
const TEXTO_OSCURO = '#212529';
const FONDO = '#eef1f5';
const BLANCO = '#ffffff';
const GRIS_INPUT = '#f5f5f5';
const GRIS_BORDE = '#dee2e6';
const AZUL_ENCABEZADO = '#1a7abf'; // se mantiene para el banner de usuario

const OPCIONES_TRANSPORTE = ['Automovil', 'Autobus', 'Avion', 'Otro'];
const OPCIONES_MOTIVO = ['Turismo', 'Trabajo', 'Estudios', 'Evento', 'Otro'];
const OPCIONES_SEXO = ['Hombre', 'Mujer', 'Otro'];

function SelectorBotones({ opciones, seleccionado, onSeleccionar, estilo }) {
    return (
        <View style={[styles.selectorRow, estilo]}>
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
    );
}

/* Sub-formulario por persona */
function PersonaForm({ index, persona, onChange }) {
    return (
        <View style={styles.personaCard}>
            <Text style={styles.personaTitle}>Persona {index + 1}</Text>
            <Text style={styles.label}>Edad</Text>
            <TextInput
                style={styles.input}
                placeholder="Edad"
                placeholderTextColor="#aaa"
                keyboardType="numeric"
                value={persona.edad}
                onChangeText={(v) => onChange(index, 'edad', v)}
            />
            <Text style={styles.label}>Género</Text>
            <SelectorBotones
                opciones={OPCIONES_SEXO}
                seleccionado={persona.sexo}
                onSeleccionar={(v) => onChange(index, 'sexo', v)}
            />
        </View>
    );
}

export default function FormularioVisitaScreen() {
    const { usuario, logout } = useAuth();
    const [enviando, setEnviando] = useState(false);

    const [form, setForm] = useState({
        tamanio_grupo: '1',
        es_extranjero: false,
        pais_origen: '',
        procedencia: '',
        tipo_transporte: '',
        motivo_visita: '',
        estancia_dias: '1',
        numero_visitas: '1',
    });

    const [personas, setPersonas] = useState([{ edad: '', sexo: '' }]);

    const actualizarGrupo = (n) => {
        const num = Math.max(1, parseInt(n) || 1);
        setForm((f) => ({ ...f, tamanio_grupo: String(num) }));
        setPersonas((prev) => {
            const arr = [...prev];
            while (arr.length < num) arr.push({ edad: '', sexo: '' });
            return arr.slice(0, num);
        });
    };

    const actualizarPersona = (idx, campo, valor) => {
        setPersonas((prev) => {
            const arr = [...prev];
            arr[idx] = { ...arr[idx], [campo]: valor };
            return arr;
        });
    };

    const enviarFormulario = async () => {
        if (!form.tipo_transporte || !form.motivo_visita || !form.procedencia) {
            Alert.alert('Campos requeridos', 'Por favor completa procedencia, transporte y motivo.');
            return;
        }
        setEnviando(true);
        try {
            const personasValidas = personas.filter(
                (p) => p.edad && parseInt(p.edad) > 0 && p.sexo
            );
            const payload = {
                tamanio_grupo: parseInt(form.tamanio_grupo),
                es_extranjero: form.es_extranjero,
                pais_origen: form.es_extranjero ? form.pais_origen : '',
                procedencia: form.procedencia,
                tipo_transporte: form.tipo_transporte,
                motivo_visita: form.motivo_visita,
                estancia_dias: parseInt(form.estancia_dias) || 1,
                numero_visitas: parseInt(form.numero_visitas) || 1,
                personas_input: personasValidas.map((p) => ({
                    edad: parseInt(p.edad),
                    sexo: p.sexo,
                })),
            };

            await visitasService.crearVisita(payload);
            Alert.alert('✅ Registro guardado', 'La visita fue registrada correctamente.');
            // Resetear formulario
            setForm({
                tamanio_grupo: '1', es_extranjero: false, pais_origen: '',
                procedencia: '', tipo_transporte: '', motivo_visita: '',
                estancia_dias: '1', numero_visitas: '1',
            });
            setPersonas([{ edad: '', sexo: '' }]);
        } catch (error) {
            const msg = error.response?.data ? JSON.stringify(error.response.data) : error.message;
            Alert.alert('Error al guardar', msg);
        } finally {
            setEnviando(false);
        }
    };

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            {/* Cabecera con info del encuestador */}
            <View style={styles.encuestadorBanner}>
                <Text style={styles.encuestadorTexto}>
                    👤 {usuario?.nombre} {usuario?.ap}
                </Text>
                <TouchableOpacity onPress={logout}>
                    <Text style={styles.cerrarSesionTexto}>Cerrar sesión</Text>
                </TouchableOpacity>
            </View>

            <Text style={styles.titulo}>Nueva Visita</Text>

            {/* Tamaño del grupo */}
            <Text style={styles.label}>Número de personas en el grupo</Text>
            <TextInput
                style={styles.input}
                keyboardType="numeric"
                value={form.tamanio_grupo}
                onChangeText={actualizarGrupo}
                placeholder="1"
                placeholderTextColor="#aaa"
            />

            {/* ¿Es extranjero? */}
            <View style={styles.switchRow}>
                <Text style={styles.label}>¿Visitante extranjero?</Text>
                <Switch
                    value={form.es_extranjero}
                    onValueChange={(v) => setForm((f) => ({ ...f, es_extranjero: v }))}
                    trackColor={{ false: '#ccc', true: AZUL_ENCABEZADO }}
                    thumbColor="#fff"
                />
            </View>

            {form.es_extranjero && (
                <>
                    <Text style={styles.label}>País de origen</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="Ej: Estados Unidos"
                        placeholderTextColor="#aaa"
                        value={form.pais_origen}
                        onChangeText={(v) => setForm((f) => ({ ...f, pais_origen: v }))}
                    />
                </>
            )}

            {/* Procedencia */}
            <Text style={styles.label}>Procedencia (ciudad)</Text>
            <TextInput
                style={styles.input}
                placeholder="Ej: Ciudad de México"
                placeholderTextColor="#aaa"
                value={form.procedencia}
                onChangeText={(v) => setForm((f) => ({ ...f, procedencia: v }))}
            />

            {/* Transporte */}
            <Text style={styles.label}>Tipo de transporte</Text>
            <SelectorBotones
                opciones={OPCIONES_TRANSPORTE}
                seleccionado={form.tipo_transporte}
                onSeleccionar={(v) => setForm((f) => ({ ...f, tipo_transporte: v }))}
            />

            {/* Motivo */}
            <Text style={styles.label}>Motivo de visita</Text>
            <SelectorBotones
                opciones={OPCIONES_MOTIVO}
                seleccionado={form.motivo_visita}
                onSeleccionar={(v) => setForm((f) => ({ ...f, motivo_visita: v }))}
            />

            {/* Estadía */}
            <Text style={styles.label}>Días de estancia</Text>
            <TextInput
                style={styles.input}
                keyboardType="numeric"
                value={form.estancia_dias}
                onChangeText={(v) => setForm((f) => ({ ...f, estancia_dias: v }))}
                placeholder="1"
                placeholderTextColor="#aaa"
            />

            {/* Número de visitas previas */}
            <Text style={styles.label}>¿Cuántas veces ha visitado Huaquechula?</Text>
            <TextInput
                style={styles.input}
                keyboardType="numeric"
                value={form.numero_visitas}
                onChangeText={(v) => setForm((f) => ({ ...f, numero_visitas: v }))}
                placeholder="1"
                placeholderTextColor="#aaa"
            />

            {/* Personas del grupo */}
            <Text style={[styles.label, styles.seccionTitle]}>Datos por persona</Text>
            {personas.map((p, i) => (
                <PersonaForm
                    key={i}
                    index={i}
                    persona={p}
                    onChange={actualizarPersona}
                />
            ))}

            {/* Botón enviar */}
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

    // Banner encuestador — mantiene azul institucional
    encuestadorBanner: {
        flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
        backgroundColor: AZUL_ENCABEZADO, borderRadius: 12, padding: 14, marginBottom: 20,
        elevation: 3, shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.15, shadowRadius: 4,
    },
    encuestadorTexto: { color: BLANCO, fontWeight: '700', fontSize: 14 },
    cerrarSesionTexto: { color: DORADO, fontSize: 13, textDecorationLine: 'underline', fontWeight: '600' },

    // Títulos
    titulo: { fontSize: 24, fontWeight: 'bold', color: TEXTO_OSCURO, marginBottom: 20 },
    label: { fontSize: 13, fontWeight: '600', color: '#555', marginTop: 14, marginBottom: 6 },
    seccionTitle: { fontSize: 16, color: AZUL_ENCABEZADO, marginTop: 24, fontWeight: '700' },

    // Inputs — estilo web: fondo gris claro, borde sutil, radio generoso
    input: {
        backgroundColor: GRIS_INPUT,
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 15,
        paddingHorizontal: 16,
        paddingVertical: 13,
        fontSize: 15,
        color: TEXTO_OSCURO,
    },

    // Switch row
    switchRow: {
        flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
        marginTop: 14, backgroundColor: BLANCO, borderRadius: 12, padding: 14,
        borderWidth: 1, borderColor: GRIS_BORDE,
        elevation: 1, shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.06, shadowRadius: 3,
    },

    // Botones selector — estilo web: borde dorado cuando activo
    selectorRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
    selectorBtn: {
        paddingHorizontal: 14, paddingVertical: 9, borderRadius: 10,
        borderWidth: 2, borderColor: GRIS_BORDE, backgroundColor: BLANCO,
    },
    selectorBtnActivo: { backgroundColor: BLANCO, borderColor: DORADO },
    selectorBtnTexto: { fontSize: 13, color: '#555' },
    selectorBtnTextoActivo: { color: TEXTO_OSCURO, fontWeight: '700' },

    // Tarjeta por persona
    personaCard: {
        backgroundColor: BLANCO, borderRadius: 15, padding: 16,
        marginTop: 12, borderWidth: 1, borderColor: GRIS_BORDE,
        elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.08, shadowRadius: 6,
    },
    personaTitle: { fontWeight: 'bold', color: AZUL_ENCABEZADO, marginBottom: 6, fontSize: 14 },

    // Botón principal — estilo web: fondo blanco con borde dorado y texto oscuro
    boton: {
        backgroundColor: BLANCO,
        borderRadius: 12,
        borderWidth: 2,
        borderColor: DORADO,
        paddingVertical: 15,
        alignItems: 'center',
        marginTop: 28,
        elevation: 2,
        shadowColor: DORADO,
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.25,
        shadowRadius: 6,
    },
    botonDeshabilitado: { opacity: 0.5 },
    botonTexto: { color: TEXTO_OSCURO, fontSize: 16, fontWeight: 'bold', letterSpacing: 0.3 },
});

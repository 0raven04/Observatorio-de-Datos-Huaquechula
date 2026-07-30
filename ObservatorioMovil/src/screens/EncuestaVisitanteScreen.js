/**
 * EncuestaVisitanteScreen.js — Formulario digital para la Encuesta: Perfil del Visitante.
 * Réplica idéntica en secciones, campos y opciones del formulario web del Observatorio.
 */
import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    ScrollView, Alert, ActivityIndicator,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { encuestasService } from '../services/encuestasService';

const DORADO = '#D6CEAA';
const TEXTO_OSCURO = '#4A4A4A';
const FONDO = '#EDEBE3';
const BLANCO = '#ffffff';
const GRIS_BORDE = '#B3B3B3';
const AZUL_ENCABEZADO = '#007bff';

const OPCIONES_GENERO = ['Femenino', 'Masculino', 'No binario / Otro', 'Prefiero no decirlo'];
const OPCIONES_VIAJA_CON = [
    'Solo / Sola',
    'En pareja',
    'En familia (con niños)',
    'Con amigos / familiares (adultos)',
    'Grupo organizado / Excursión'
];

const ZONAS_OPCIONES = [
    { id: 'Centro', label: '📍 Centro' },
    { id: 'Altares monumentales', label: '🛕 Altares monumentales' },
    { id: 'Ex Convento Franciscano', label: '🏛️ Ex Convento Franciscano' },
    { id: 'Páramo de los Duendes', label: '🌲 Páramo de los Duendes' },
    { id: 'Acueducto de Matlala', label: '🌊 Acueducto de Matlala' },
    { id: 'Piedras Arqueológicas/Naturales', label: '🗿 Piedras Arqueológicas/Naturales' },
];

const ACTIVIDADES_OPCIONES = [
    'Probar la gastronomía local / ir a restaurantes',
    'Visitar museos, iglesias o sitios históricos',
    'Comprar artesanías o productos locales',
    'Actividades de naturaleza / senderismo / aventura',
    'Asistir a un evento, fiesta patronal o festival tradicional',
    'Turismo de negocios / congresos',
    'Descanso / Relajación',
];

function SelectorChips({ opciones, seleccionado, onSeleccionar }) {
    return (
        <View style={styles.chipGrid}>
            {opciones.map((op) => {
                const esObj = typeof op === 'object';
                const val = esObj ? op.id : op;
                const label = esObj ? op.label : op;
                const activo = seleccionado === val;
                return (
                    <TouchableOpacity
                        key={val}
                        style={[styles.chipBtn, activo && styles.chipBtnActivo]}
                        onPress={() => onSeleccionar(val)}
                    >
                        <Text style={[styles.chipTexto, activo && styles.chipTextoActivo]}>{label}</Text>
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
                const esObj = typeof op === 'object';
                const val = esObj ? op.id : op;
                const label = esObj ? op.label : op;
                const marcado = seleccionados.includes(val);
                return (
                    <TouchableOpacity
                        key={val}
                        style={[styles.checkCard, marcado && styles.checkCardMarcado]}
                        onPress={() => onToggle(val)}
                    >
                        <Text style={styles.checkIcon}>{marcado ? '☑️' : '⏹️'}</Text>
                        <Text style={[styles.checkLabel, marcado && styles.checkLabelMarcado]}>{label}</Text>
                    </TouchableOpacity>
                );
            })}
        </View>
    );
}

export default function EncuestaVisitanteScreen({ navigation }) {
    const { usuario } = useAuth();
    const [enviando, setEnviando] = useState(false);

    const [form, setForm] = useState({
        genero: 'Femenino',
        edad: '',
        viaja_con: 'Solo / Sola',
        residencia_ciudad: '',
        residencia_estado: '',
        residencia_pais: 'México',
        zonas_visitadas: [],
        actividades: [],
        satisfaccion: 5,
        lo_que_mas_gusto: '',
    });

    const toggleZona = (zona) => {
        setForm((prev) => {
            const arr = prev.zonas_visitadas.includes(zona)
                ? prev.zonas_visitadas.filter((z) => z !== zona)
                : [...prev.zonas_visitadas, zona];
            return { ...prev, zonas_visitadas: arr };
        });
    };

    const toggleActividad = (act) => {
        setForm((prev) => {
            const arr = prev.actividades.includes(act)
                ? prev.actividades.filter((a) => a !== act)
                : [...prev.actividades, act];
            return { ...prev, actividades: arr };
        });
    };

    const enviarEncuesta = async () => {
        if (!form.edad || parseInt(form.edad) <= 0) {
            Alert.alert('Campo requerido', 'Por favor ingresa tu edad.');
            return;
        }
        if (!form.residencia_ciudad || !form.residencia_estado) {
            Alert.alert('Campo requerido', 'Por favor completa tu ciudad y estado de residencia.');
            return;
        }

        setEnviando(true);
        try {
            const payload = {
                genero: form.genero,
                edad: parseInt(form.edad),
                viaja_con: form.viaja_con,
                residencia_ciudad: form.residencia_ciudad,
                residencia_estado: form.residencia_estado,
                residencia_pais: form.residencia_pais || 'México',
                zonas_visitadas: form.zonas_visitadas.join(', '),
                actividades: form.actividades.join(', '),
                satisfaccion: form.satisfaccion,
                lo_que_mas_gusto: form.lo_que_mas_gusto,
            };

            await encuestasService.crearEncuestaVisitante(payload);
            Alert.alert('✅ Encuesta Guardada', 'La Encuesta de Perfil del Visitante fue registrada con éxito.');
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
                <Text style={styles.bannerIcon}>👤</Text>
                <Text style={styles.bannerTitulo}>Encuesta: Perfil del Visitante</Text>
            </View>

            {/* I. Perfil del Visitante */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>I. Perfil del Visitante</Text>
                
                <Text style={styles.label}>1. ¿Con qué género te identificas?</Text>
                <SelectorChips
                    opciones={OPCIONES_GENERO}
                    seleccionado={form.genero}
                    onSeleccionar={(v) => setForm({ ...form, genero: v })}
                />

                <Text style={styles.label}>2. ¿Cuál es tu edad?</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Ej. 28"
                    placeholderTextColor="#aaa"
                    keyboardType="numeric"
                    value={form.edad}
                    onChangeText={(v) => setForm({ ...form, edad: v })}
                />

                <Text style={styles.label}>3. ¿Con quién viajas en este viaje?</Text>
                <SelectorChips
                    opciones={OPCIONES_VIAJA_CON}
                    seleccionado={form.viaja_con}
                    onSeleccionar={(v) => setForm({ ...form, viaja_con: v })}
                />
            </View>

            {/* II. Origen y Conectividad */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>II. Origen y Conectividad</Text>
                <Text style={styles.sublabel}>4. ¿Cuál es tu lugar de residencia habitual?</Text>

                <Text style={styles.label}>Ciudad</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Ciudad"
                    placeholderTextColor="#aaa"
                    value={form.residencia_ciudad}
                    onChangeText={(v) => setForm({ ...form, residencia_ciudad: v })}
                />

                <Text style={styles.label}>Estado / Provincia</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Estado"
                    placeholderTextColor="#aaa"
                    value={form.residencia_estado}
                    onChangeText={(v) => setForm({ ...form, residencia_estado: v })}
                />

                <Text style={styles.label}>País</Text>
                <TextInput
                    style={styles.input}
                    placeholder="País"
                    placeholderTextColor="#aaa"
                    value={form.residencia_pais}
                    onChangeText={(v) => setForm({ ...form, residencia_pais: v })}
                />

                <Text style={[styles.label, { marginTop: 14 }]}>
                    5. De las siguientes zonas de nuestro municipio, ¿cuáles visitaste o piensas visitar?
                </Text>
                <MultiSelectCheckboxes
                    opciones={ZONAS_OPCIONES}
                    seleccionados={form.zonas_visitadas}
                    onToggle={toggleZona}
                />
            </View>

            {/* III. Comportamiento y Actividades */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>III. Comportamiento y Actividades</Text>
                <Text style={styles.label}>6. ¿Qué actividades realizaste durante tu estancia?</Text>
                <MultiSelectCheckboxes
                    opciones={ACTIVIDADES_OPCIONES}
                    seleccionados={form.actividades}
                    onToggle={toggleActividad}
                />
            </View>

            {/* IV. Satisfacción y Reseñas */}
            <View style={styles.block}>
                <Text style={styles.blockTitle}>IV. Satisfacción y Reseñas</Text>
                
                <Text style={styles.label}>7. En general, ¿cómo calificarías tu experiencia en nuestro municipio?</Text>
                <View style={styles.starRow}>
                    {[1, 2, 3, 4, 5].map((star) => (
                        <TouchableOpacity
                            key={star}
                            onPress={() => setForm({ ...form, satisfaccion: star })}
                            style={styles.starBtn}
                        >
                            <Text style={styles.starText}>{star <= form.satisfaccion ? '⭐' : '☆'}</Text>
                        </TouchableOpacity>
                    ))}
                </View>

                <Text style={styles.label}>8. Cuéntanos brevemente, ¿qué fue lo que más te gustó de tu visita?</Text>
                <TextInput
                    style={[styles.input, styles.textarea]}
                    placeholder="Cuéntanos qué fue lo que más te gustó..."
                    placeholderTextColor="#aaa"
                    multiline
                    numberOfLines={4}
                    value={form.lo_que_mas_gusto}
                    onChangeText={(v) => setForm({ ...form, lo_que_mas_gusto: v })}
                />
            </View>

            {/* Botón Guardar */}
            <TouchableOpacity
                style={[styles.btnEnviar, enviando && styles.btnDeshabilitado]}
                onPress={enviarEncuesta}
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
        borderLeftColor: AZUL_ENCABEZADO,
        elevation: 2,
    },
    bannerIcon: { fontSize: 24, marginRight: 10 },
    bannerTitulo: { fontSize: 18, fontWeight: 'bold', color: AZUL_ENCABEZADO },
    block: {
        backgroundColor: BLANCO,
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        elevation: 2,
    },
    blockTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: TEXTO_OSCURO,
        marginBottom: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
        paddingBottom: 6,
    },
    label: { fontSize: 14, fontWeight: '600', color: TEXTO_OSCURO, marginTop: 10, marginBottom: 6 },
    sublabel: { fontSize: 13, color: '#666', marginBottom: 6 },
    input: {
        backgroundColor: '#f9f9f9',
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 8,
        padding: 10,
        fontSize: 14,
        color: '#333',
    },
    textarea: { height: 90, textAlignVertical: 'top' },
    chipGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
    chipBtn: {
        backgroundColor: '#f0f0f0',
        paddingVertical: 8,
        paddingHorizontal: 12,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: '#ddd',
    },
    chipBtnActivo: { backgroundColor: AZUL_ENCABEZADO, borderColor: AZUL_ENCABEZADO },
    chipTexto: { fontSize: 13, color: '#555' },
    chipTextoActivo: { color: '#fff', fontWeight: 'bold' },
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
    checkCardMarcado: { backgroundColor: '#eef6ff', borderColor: AZUL_ENCABEZADO },
    checkIcon: { fontSize: 16, marginRight: 8 },
    checkLabel: { fontSize: 13, color: '#444', flex: 1 },
    checkLabelMarcado: { color: AZUL_ENCABEZADO, fontWeight: '600' },
    starRow: { flexDirection: 'row', gap: 12, marginVertical: 8 },
    starBtn: { padding: 4 },
    starText: { fontSize: 28 },
    btnEnviar: {
        backgroundColor: AZUL_ENCABEZADO,
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
        marginTop: 10,
        elevation: 3,
    },
    btnDeshabilitado: { opacity: 0.6 },
    btnTexto: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});

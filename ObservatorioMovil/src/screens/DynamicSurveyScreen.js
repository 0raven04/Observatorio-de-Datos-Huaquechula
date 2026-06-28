import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    ScrollView, Alert, ActivityIndicator,
} from 'react-native';
import { encuestasService } from '../services/encuestasService';

const DORADO = '#D6CEAA';
const VERDE = '#2ecc71';
const MORADO = '#4A4A4A';
const ROJO = '#e74c3c';
const TEXTO_OSCURO = '#4A4A4A';
const FONDO = '#EDEBE3';
const BLANCO = '#ffffff';
const GRIS_INPUT = '#f9f9f9';
const GRIS_BORDE = '#B3B3B3';

export default function DynamicSurveyScreen({ route, navigation }) {
    const { encuesta } = route.params;
    const [respuestas, setRespuestas] = useState({});
    const [enviando, setEnviando] = useState(false);
    const [errores, setErrores] = useState({});

    // Manejar el cambio de valor para una pregunta
    const handleValueChange = (preguntaId, valor) => {
        setRespuestas((prev) => ({
            ...prev,
            [preguntaId]: valor,
        }));
        // Limpiar error de esta pregunta si es que se ha respondido
        if (errores[preguntaId]) {
            setErrores((prev) => {
                const newErr = { ...prev };
                delete newErr[preguntaId];
                return newErr;
            });
        }
    };

    // Manejar selección múltiple (CASILLAS)
    const handleCheckboxToggle = (preguntaId, opcionTexto) => {
        const seleccionActual = respuestas[preguntaId] || [];
        let nuevaSeleccion;
        if (seleccionActual.includes(opcionTexto)) {
            nuevaSeleccion = seleccionActual.filter((item) => item !== opcionTexto);
        } else {
            nuevaSeleccion = [...seleccionActual, opcionTexto];
        }
        handleValueChange(preguntaId, nuevaSeleccion);
    };

    const enviarFormulario = async () => {
        // Validación local de campos requeridos
        const nuevosErrores = {};
        encuesta.preguntas.forEach((p) => {
            const val = respuestas[p.id];
            if (p.requerida) {
                if (val === undefined || val === null || val === '' || (Array.isArray(val) && val.length === 0)) {
                    nuevosErrores[p.id] = 'Esta pregunta es obligatoria.';
                }
            }
        });

        if (Object.keys(nuevosErrores).length > 0) {
            setErrores(nuevosErrores);
            Alert.alert('Campos requeridos', 'Por favor contesta todas las preguntas obligatorias antes de enviar.');
            return;
        }

        setEnviando(true);
        try {
            // Formatear payload de respuestas para la API
            const payload = Object.keys(respuestas).map((pregId) => ({
                pregunta_id: parseInt(pregId),
                valor: respuestas[pregId],
            }));

            await encuestasService.responderEncuestaCreada(encuesta.id, payload);
            Alert.alert('✅ Éxito', 'La encuesta ha sido guardada y sincronizada correctamente.');
            navigation.goBack();
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'No se pudo guardar la encuesta. Revisa tu conexión de red.');
        } finally {
            setEnviando(false);
        }
    };

    const renderCampoPregunta = (p) => {
        const valor = respuestas[p.id];
        const error = errores[p.id];

        switch (p.tipo_pregunta) {
            case 'TEXTO':
                return (
                    <TextInput
                        style={[styles.input, error && styles.inputError]}
                        value={valor || ''}
                        onChangeText={(text) => handleValueChange(p.id, text)}
                        placeholder="Escribe tu respuesta corta..."
                        placeholderTextColor="#aaa"
                    />
                );

            case 'PARRAFO':
                return (
                    <TextInput
                        style={[styles.input, styles.inputMultiline, error && styles.inputError]}
                        value={valor || ''}
                        onChangeText={(text) => handleValueChange(p.id, text)}
                        placeholder="Escribe tu respuesta detallada..."
                        placeholderTextColor="#aaa"
                        multiline
                        numberOfLines={4}
                    />
                );

            case 'OPCION_MULTIPLE':
            case 'DESPLEGABLE':
                // Mostramos opciones como botones grandes, modernos y accesibles
                return (
                    <View style={styles.opcionesContainer}>
                        {p.opciones.map((op) => {
                            const seleccionado = valor === op.texto;
                            return (
                                <TouchableOpacity
                                    key={op.id}
                                    style={[
                                        styles.opcionBtn,
                                        seleccionado && styles.opcionBtnActivo,
                                        error && styles.opcionBtnError
                                    ]}
                                    onPress={() => handleValueChange(p.id, op.texto)}
                                >
                                    <View style={[styles.radioCircle, seleccionado && styles.radioCircleActivo]}>
                                        {seleccionado && <View style={styles.radioInner} />}
                                    </View>
                                    <Text style={[styles.opcionTexto, seleccionado && styles.opcionTextoActivo]}>
                                        {op.texto}
                                    </Text>
                                </TouchableOpacity>
                            );
                        })}
                    </View>
                );

            case 'CASILLAS':
                return (
                    <View style={styles.opcionesContainer}>
                        {p.opciones.map((op) => {
                            const seleccionados = valor || [];
                            const seleccionado = seleccionados.includes(op.texto);
                            return (
                                <TouchableOpacity
                                    key={op.id}
                                    style={[
                                        styles.opcionBtn,
                                        seleccionado && styles.opcionBtnActivo,
                                        error && styles.opcionBtnError
                                    ]}
                                    onPress={() => handleCheckboxToggle(p.id, op.texto)}
                                >
                                    <View style={[styles.checkboxSquare, seleccionado && styles.checkboxSquareActivo]}>
                                        {seleccionado && <Text style={styles.checkboxCheck}>✓</Text>}
                                    </View>
                                    <Text style={[styles.opcionTexto, seleccionado && styles.opcionTextoActivo]}>
                                        {op.texto}
                                    </Text>
                                </TouchableOpacity>
                            );
                        })}
                    </View>
                );

            default:
                return null;
        }
    };

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            {/* Cabecera de la Encuesta */}
            <View style={styles.headerCard}>
                <Text style={styles.surveyTitle}>{encuesta.titulo}</Text>
                {encuesta.descripcion ? (
                    <Text style={styles.surveyDesc}>{encuesta.descripcion}</Text>
                ) : null}
                <View style={styles.infoBadgeRow}>
                    {encuesta.anonima ? (
                        <View style={[styles.infoBadge, { backgroundColor: '#e8f4fd' }]}>
                            <Text style={[styles.infoBadgeText, { color: '#1a7abf' }]}>🔒 Anónima</Text>
                        </View>
                    ) : (
                        <View style={[styles.infoBadge, { backgroundColor: '#fdf3e8' }]}>
                            <Text style={[styles.infoBadgeText, { color: '#f39c12' }]}>👤 Identificable</Text>
                        </View>
                    )}
                    <View style={[styles.infoBadge, { backgroundColor: '#eafaf1' }]}>
                        <Text style={[styles.infoBadgeText, { color: VERDE }]}>✓ Activa</Text>
                    </View>
                </View>
            </View>

            {/* Listado de Preguntas */}
            {encuesta.preguntas.map((p, index) => {
                const error = errores[p.id];
                return (
                    <View key={p.id} style={styles.preguntaCard}>
                        <Text style={styles.preguntaTexto}>
                            {index + 1}. {p.texto}{' '}
                            {p.requerida ? <Text style={styles.requerido}>*</Text> : null}
                        </Text>
                        {renderCampoPregunta(p)}
                        {error ? <Text style={styles.errorTexto}>{error}</Text> : null}
                    </View>
                );
            })}

            {/* Botón de envío */}
            <TouchableOpacity
                style={[styles.botonEnviar, enviando && styles.botonDeshabilitado]}
                onPress={enviarFormulario}
                disabled={enviando}
            >
                {enviando ? (
                    <ActivityIndicator color="#fff" />
                ) : (
                    <Text style={styles.botonEnviarTexto}>Guardar Respuestas</Text>
                )}
            </TouchableOpacity>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: FONDO },
    content: { padding: 20, paddingBottom: 50 },
    headerCard: {
        backgroundColor: BLANCO,
        borderRadius: 15,
        padding: 20,
        marginBottom: 20,
        elevation: 3,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    surveyTitle: { fontSize: 20, fontWeight: 'bold', color: TEXTO_OSCURO, marginBottom: 8 },
    surveyDesc: { fontSize: 14, color: '#666', lineHeight: 20, marginBottom: 12 },
    infoBadgeRow: { flexDirection: 'row', gap: 10, flexWrap: 'wrap' },
    infoBadge: {
        paddingVertical: 4,
        paddingHorizontal: 10,
        borderRadius: 8,
    },
    infoBadgeText: { fontSize: 11, fontWeight: '600' },
    preguntaCard: {
        backgroundColor: BLANCO,
        borderRadius: 15,
        padding: 18,
        marginBottom: 15,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 3,
    },
    preguntaTexto: {
        fontSize: 15,
        fontWeight: 'bold',
        color: '#2c3e50',
        marginBottom: 12,
        lineHeight: 22,
    },
    requerido: { color: ROJO },
    input: {
        backgroundColor: GRIS_INPUT,
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 12,
        paddingHorizontal: 15,
        paddingVertical: 12,
        fontSize: 15,
        color: TEXTO_OSCURO,
    },
    inputMultiline: {
        height: 100,
        textAlignVertical: 'top',
    },
    inputError: {
        borderColor: ROJO,
        backgroundColor: '#fdf2f2',
    },
    errorTexto: {
        color: ROJO,
        fontSize: 12,
        marginTop: 6,
        fontWeight: '600',
    },
    opcionesContainer: {
        gap: 10,
    },
    opcionBtn: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: GRIS_INPUT,
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 12,
        paddingVertical: 12,
        paddingHorizontal: 15,
    },
    opcionBtnActivo: {
        borderColor: MORADO,
        backgroundColor: MORADO + '11',
    },
    opcionBtnError: {
        borderColor: ROJO,
    },
    opcionTexto: {
        fontSize: 14,
        color: '#555',
        marginLeft: 10,
        flex: 1,
    },
    opcionTextoActivo: {
        color: TEXTO_OSCURO,
        fontWeight: 'bold',
    },
    radioCircle: {
        width: 20,
        height: 20,
        borderRadius: 10,
        borderWidth: 2,
        borderColor: '#bbb',
        alignItems: 'center',
        justifyContent: 'center',
    },
    radioCircleActivo: {
        borderColor: MORADO,
    },
    radioInner: {
        width: 10,
        height: 10,
        borderRadius: 5,
        backgroundColor: MORADO,
    },
    checkboxSquare: {
        width: 20,
        height: 20,
        borderRadius: 4,
        borderWidth: 2,
        borderColor: '#bbb',
        alignItems: 'center',
        justifyContent: 'center',
    },
    checkboxSquareActivo: {
        borderColor: MORADO,
        backgroundColor: MORADO,
    },
    checkboxCheck: {
        color: BLANCO,
        fontWeight: 'bold',
        fontSize: 12,
        lineHeight: 14,
    },
    botonEnviar: {
        backgroundColor: BLANCO,
        borderRadius: 15,
        borderWidth: 2,
        borderColor: MORADO,
        paddingVertical: 16,
        alignItems: 'center',
        marginTop: 15,
        elevation: 3,
        shadowColor: MORADO,
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.2,
        shadowRadius: 6,
    },
    botonDeshabilitado: {
        opacity: 0.5,
    },
    botonEnviarTexto: {
        color: MORADO,
        fontSize: 16,
        fontWeight: 'bold',
    },
});

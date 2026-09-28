/**
 * SelectorProcedencia.js — Componente de selección geográfica en cascada para la app móvil
 * Cascada: País -> Estado -> Ciudad/Municipio (con fallback a texto libre para extranjero u otro)
 * Observatorio de Datos Huaquechula
 */

import React, { useState, useEffect } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    Modal, FlatList, SafeAreaView
} from 'react-native';
import { PAISES_COMUNES, DATOS_MEXICO } from '../constants/geoData';

const DORADO = '#D6CEAA';
const TEXTO_OSCURO = '#4A4A4A';
const FONDO = '#EDEBE3';
const BLANCO = '#ffffff';
const GRIS_BORDE = '#B3B3B3';
const AZUL_ACCENTO = '#007bff';

function ModalListPicker({ visible, title, items, onSelect, onClose }) {
    const [busqueda, setBusqueda] = useState('');

    useEffect(() => {
        if (visible) setBusqueda('');
    }, [visible]);

    const filtrados = items.filter(it => 
        it.toLowerCase().includes(busqueda.toLowerCase())
    );

    return (
        <Modal visible={visible} animationType="slide" transparent={true} onRequestClose={onClose}>
            <View style={modalStyles.overlay}>
                <SafeAreaView style={modalStyles.safeArea}>
                    <View style={modalStyles.container}>
                        <View style={modalStyles.header}>
                            <Text style={modalStyles.title}>{title}</Text>
                            <TouchableOpacity onPress={onClose} style={modalStyles.closeBtn}>
                                <Text style={modalStyles.closeBtnText}>✕</Text>
                            </TouchableOpacity>
                        </View>

                        <TextInput
                            style={modalStyles.searchInput}
                            placeholder="🔍 Buscar..."
                            placeholderTextColor="#999"
                            value={busqueda}
                            onChangeText={setBusqueda}
                            autoCorrect={false}
                        />

                        <FlatList
                            data={filtrados}
                            keyExtractor={(item) => item}
                            renderItem={({ item }) => (
                                <TouchableOpacity
                                    style={modalStyles.itemRow}
                                    onPress={() => {
                                        onSelect(item);
                                        onClose();
                                    }}
                                >
                                    <Text style={modalStyles.itemText}>{item}</Text>
                                    <Text style={modalStyles.chevron}>›</Text>
                                </TouchableOpacity>
                            )}
                            ListEmptyComponent={
                                <View style={modalStyles.emptyBox}>
                                    <Text style={modalStyles.emptyText}>No se encontraron coincidencias.</Text>
                                </View>
                            }
                        />
                    </View>
                </SafeAreaView>
            </View>
        </Modal>
    );
}

export default function SelectorProcedencia({
    initialPais = 'México',
    initialEstado = 'Puebla',
    initialCiudad = 'Huaquechula',
    onChange
}) {
    const [pais, setPais] = useState(initialPais);
    const [estado, setEstado] = useState(initialEstado);
    const [ciudad, setCiudad] = useState(initialCiudad);
    const [ciudadOtro, setCiudadOtro] = useState('');

    // Estados de modales
    const [modalPais, setModalPais] = useState(false);
    const [modalEstado, setModalEstado] = useState(false);
    const [modalCiudad, setModalCiudad] = useState(false);

    const isMexico = pais === 'México' || pais === 'Mexico';
    const isOtroMunicipio = ciudad.startsWith('Otro ') || ciudad.startsWith('Otra ');

    // Notificar al componente padre
    useEffect(() => {
        let textoConsolidado = '';
        const esExtranjero = !isMexico;

        if (isMexico) {
            const cdFinal = (isOtroMunicipio && ciudadOtro.trim()) ? ciudadOtro.trim() : ciudad;
            if (cdFinal && estado) {
                textoConsolidado = `${cdFinal}, ${estado}`;
            } else {
                textoConsolidado = cdFinal || estado || 'México';
            }
        } else {
            textoConsolidado = ciudad.trim() ? `${ciudad.trim()}, ${pais}` : pais;
        }

        if (onChange) {
            onChange({
                pais,
                estado: isMexico ? estado : 'Extranjero',
                ciudad: (isMexico && isOtroMunicipio && ciudadOtro.trim()) ? ciudadOtro.trim() : ciudad,
                textoConsolidado,
                esExtranjero
            });
        }
    }, [pais, estado, ciudad, ciudadOtro]);

    const handleSelectPais = (p) => {
        setPais(p);
        if (p === 'México' || p === 'Mexico') {
            setEstado('Puebla');
            setCiudad('Huaquechula');
            setCiudadOtro('');
        } else {
            setEstado('Extranjero');
            setCiudad('');
            setCiudadOtro('');
        }
    };

    const handleSelectEstado = (est) => {
        setEstado(est);
        const listaCiudades = DATOS_MEXICO[est] || [];
        setCiudad(listaCiudades[0] || '');
        setCiudadOtro('');
    };

    const estadosList = Object.keys(DATOS_MEXICO);
    const ciudadesList = isMexico ? (DATOS_MEXICO[estado] || ['Otro municipio']) : [];

    return (
        <View style={styles.container}>
            {/* 1. Selector de País */}
            <Text style={styles.fieldLabel}>País</Text>
            <TouchableOpacity style={styles.selectBtn} onPress={() => setModalPais(true)}>
                <Text style={styles.selectBtnText}>{pais || 'Seleccione un país...'}</Text>
                <Text style={styles.selectBtnArrow}>▾</Text>
            </TouchableOpacity>

            {/* 2. Selector de Estado (Solo México) */}
            {isMexico && (
                <>
                    <Text style={styles.fieldLabel}>Estado</Text>
                    <TouchableOpacity style={styles.selectBtn} onPress={() => setModalEstado(true)}>
                        <Text style={styles.selectBtnText}>{estado || 'Seleccione un estado...'}</Text>
                        <Text style={styles.selectBtnArrow}>▾</Text>
                    </TouchableOpacity>
                </>
            )}

            {/* 3. Selector / Input de Ciudad */}
            <Text style={styles.fieldLabel}>Ciudad / Municipio</Text>
            {isMexico ? (
                <>
                    <TouchableOpacity style={styles.selectBtn} onPress={() => setModalCiudad(true)}>
                        <Text style={styles.selectBtnText}>{ciudad || 'Seleccione una ciudad/municipio...'}</Text>
                        <Text style={styles.selectBtnArrow}>▾</Text>
                    </TouchableOpacity>

                    {isOtroMunicipio && (
                        <View style={styles.otroContainer}>
                            <Text style={styles.otroLabel}>Especifique el municipio o localidad:</Text>
                            <TextInput
                                style={styles.input}
                                placeholder="Ej. San Jerónimo Coyula..."
                                placeholderTextColor="#aaa"
                                value={ciudadOtro}
                                onChangeText={setCiudadOtro}
                            />
                        </View>
                    )}
                </>
            ) : (
                <TextInput
                    style={styles.input}
                    placeholder="Escriba la ciudad de residencia..."
                    placeholderTextColor="#aaa"
                    value={ciudad}
                    onChangeText={setCiudad}
                />
            )}

            {/* Badge y Previsualización */}
            <View style={styles.previewBox}>
                <Text style={styles.previewText}>
                    📍 <Text style={styles.previewBold}>
                        {isMexico
                            ? `${(isOtroMunicipio && ciudadOtro.trim()) ? ciudadOtro.trim() : ciudad}, ${estado}`
                            : (ciudad ? `${ciudad}, ${pais}` : pais)}
                    </Text>
                </Text>
                <View style={[styles.badge, isMexico ? styles.badgeNacional : styles.badgeExtranjero]}>
                    <Text style={[styles.badgeText, isMexico ? styles.badgeTextNac : styles.badgeTextExt]}>
                        {isMexico ? 'Nacional' : `Extranjero (${pais})`}
                    </Text>
                </View>
            </View>

            {/* Modales */}
            <ModalListPicker
                visible={modalPais}
                title="Selecciona el País"
                items={PAISES_COMUNES}
                onSelect={handleSelectPais}
                onClose={() => setModalPais(false)}
            />

            <ModalListPicker
                visible={modalEstado}
                title="Selecciona el Estado"
                items={estadosList}
                onSelect={handleSelectEstado}
                onClose={() => setModalEstado(false)}
            />

            <ModalListPicker
                visible={modalCiudad}
                title={`Ciudades en ${estado}`}
                items={ciudadesList}
                onSelect={(cd) => setCiudad(cd)}
                onClose={() => setModalCiudad(false)}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#fbfbfb',
        borderRadius: 12,
        padding: 14,
        borderWidth: 1,
        borderColor: '#e8e8e8',
        marginVertical: 8,
    },
    fieldLabel: {
        fontSize: 13,
        fontWeight: '700',
        color: TEXTO_OSCURO,
        marginTop: 10,
        marginBottom: 4,
    },
    selectBtn: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: BLANCO,
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 8,
        paddingHorizontal: 12,
        paddingVertical: 12,
        marginBottom: 4,
    },
    selectBtnText: {
        fontSize: 14,
        color: TEXTO_OSCURO,
        fontWeight: '500',
    },
    selectBtnArrow: {
        fontSize: 16,
        color: '#888',
    },
    input: {
        backgroundColor: BLANCO,
        borderWidth: 1,
        borderColor: GRIS_BORDE,
        borderRadius: 8,
        paddingHorizontal: 12,
        paddingVertical: 10,
        fontSize: 14,
        color: TEXTO_OSCURO,
    },
    otroContainer: {
        marginTop: 6,
    },
    otroLabel: {
        fontSize: 12,
        color: '#666',
        marginBottom: 4,
        fontStyle: 'italic',
    },
    previewBox: {
        marginTop: 14,
        paddingTop: 10,
        borderTopWidth: 1,
        borderTopColor: '#eee',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 6,
    },
    previewText: {
        fontSize: 12,
        color: '#555',
        flex: 1,
    },
    previewBold: {
        fontWeight: 'bold',
        color: TEXTO_OSCURO,
    },
    badge: {
        paddingHorizontal: 8,
        paddingVertical: 3,
        borderRadius: 12,
    },
    badgeNacional: {
        backgroundColor: '#e6f4ea',
    },
    badgeExtranjero: {
        backgroundColor: '#fff3cd',
    },
    badgeText: {
        fontSize: 11,
        fontWeight: 'bold',
    },
    badgeTextNac: {
        color: '#28a745',
    },
    badgeTextExt: {
        color: '#856404',
    },
});

const modalStyles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'flex-end',
    },
    safeArea: {
        flex: 1,
        justifyContent: 'flex-end',
    },
    container: {
        backgroundColor: BLANCO,
        borderTopLeftRadius: 20,
        borderTopRightRadius: 20,
        maxHeight: '80%',
        paddingBottom: 20,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    title: {
        fontSize: 17,
        fontWeight: 'bold',
        color: TEXTO_OSCURO,
    },
    closeBtn: {
        padding: 6,
    },
    closeBtnText: {
        fontSize: 18,
        color: '#999',
        fontWeight: 'bold',
    },
    searchInput: {
        backgroundColor: '#f5f5f5',
        marginHorizontal: 16,
        marginVertical: 10,
        borderRadius: 8,
        paddingHorizontal: 12,
        paddingVertical: 9,
        fontSize: 14,
        color: TEXTO_OSCURO,
    },
    itemRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 14,
        paddingHorizontal: 18,
        borderBottomWidth: 1,
        borderBottomColor: '#f3f3f3',
    },
    itemText: {
        fontSize: 15,
        color: TEXTO_OSCURO,
    },
    chevron: {
        fontSize: 18,
        color: '#bbb',
    },
    emptyBox: {
        padding: 24,
        alignItems: 'center',
    },
    emptyText: {
        color: '#999',
        fontSize: 14,
    },
});

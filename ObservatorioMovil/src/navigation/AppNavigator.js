/**
 * AppNavigator.js — Configuración de navegación de la app del Observatorio.
 *
 * Lógica de flujo:
 *   - Sin sesión → LoginScreen
 *   - Con sesión → Tab: Encuestas (Portal Encuestador) + Mis Visitas (Historial)
 */
import React from 'react';
import { ActivityIndicator, View, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import { useAuth } from '../context/AuthContext';

// Pantallas
import LoginScreen from '../screens/LoginScreen';
import SelectorEncuestasScreen from '../screens/SelectorEncuestasScreen';
import FormularioVisitaScreen from '../screens/FormularioVisitaScreen';
import EncuestaVisitanteScreen from '../screens/EncuestaVisitanteScreen';
import EncuestaResidenteScreen from '../screens/EncuestaResidenteScreen';
import EncuestaInstitucionalScreen from '../screens/EncuestaInstitucionalScreen';
import EncuestaComercioScreen from '../screens/EncuestaComercioScreen';
import MisEncuestasScreen from '../screens/MisEncuestasScreen';
import DynamicSurveyScreen from '../screens/DynamicSurveyScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Paleta compartida
const COLOR_INSTITUCIONAL = '#4A4A4A';

// ── Stack para el flujo de Encuestas ──────────────────────────────────────────
function EncuestasStack() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerStyle: { backgroundColor: COLOR_INSTITUCIONAL },
                headerTintColor: '#fff',
                headerTitleStyle: { fontWeight: 'bold' },
            }}
        >
            <Stack.Screen
                name="SelectorEncuestas"
                component={SelectorEncuestasScreen}
                options={{ title: 'Portal del Encuestador' }}
            />
            <Stack.Screen
                name="EncuestaVisitante"
                component={EncuestaVisitanteScreen}
                options={{ title: 'Encuesta: Perfil del Visitante' }}
            />
            <Stack.Screen
                name="EncuestaResidente"
                component={EncuestaResidenteScreen}
                options={{ title: 'Encuesta: Residente Local' }}
            />
            <Stack.Screen
                name="EncuestaInstitucional"
                component={EncuestaInstitucionalScreen}
                options={{ title: 'Encuesta: Institucional' }}
            />
            <Stack.Screen
                name="NuevaVisita"
                component={FormularioVisitaScreen}
                options={{ title: 'Registro Conteo de Visita' }}
            />
            <Stack.Screen
                name="EncuestaComercio"
                component={EncuestaComercioScreen}
                options={{ title: 'Encuesta Comercio' }}
            />
            <Stack.Screen
                name="CompletarEncuesta"
                component={DynamicSurveyScreen}
                options={{ title: 'Completar Encuesta' }}
            />
        </Stack.Navigator>
    );
}

// ── Tabs para Encuestador / Usuarios Autenticados ─────────────────────────────
function EncuestadorTabs() {
    return (
        <Tab.Navigator
            screenOptions={{
                tabBarActiveTintColor: COLOR_INSTITUCIONAL,
                tabBarInactiveTintColor: '#999',
                headerShown: false,
            }}
        >
            <Tab.Screen
                name="EncuestasFlow"
                component={EncuestasStack}
                options={{
                    title: 'Encuestas',
                    tabBarLabel: 'Encuestas',
                    tabBarIcon: ({ color, size }) => (
                        <TabIcon emoji="📋" color={color} size={size} />
                    ),
                }}
            />
            <Tab.Screen
                name="MisEncuestas"
                component={MisEncuestasScreen}
                options={{
                    headerShown: true,
                    title: 'Mis Encuestas Realizadas',
                    tabBarLabel: 'Mis encuestas',
                    headerStyle: { backgroundColor: COLOR_INSTITUCIONAL },
                    headerTintColor: '#fff',
                    tabBarIcon: ({ color, size }) => (
                        <TabIcon emoji="🗂️" color={color} size={size} />
                    ),
                }}
            />
        </Tab.Navigator>
    );
}

// ── Ícono de tab con emoji ────────────────────────────────────────────────────
function TabIcon({ emoji }) {
    return (
        <Text style={{ fontSize: 20, lineHeight: 24 }}>{emoji}</Text>
    );
}

// ── Navigator principal ───────────────────────────────────────────────────────
export default function AppNavigator() {
    const { usuario, cargando } = useAuth();

    if (cargando) {
        return (
            <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#EDEBE3' }}>
                <ActivityIndicator size="large" color="#4A4A4A" />
            </View>
        );
    }

    return (
        <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false }}>
                {!usuario ? (
                    <Stack.Screen name="Login" component={LoginScreen} />
                ) : (
                    <Stack.Screen name="EncuestadorApp" component={EncuestadorTabs} />
                )}
            </Stack.Navigator>
        </NavigationContainer>
    );
}

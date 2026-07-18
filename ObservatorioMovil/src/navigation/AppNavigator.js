/**
 * AppNavigator.js — Configuración de navegación de la app del Observatorio.
 *
 * Lógica de flujo:
 *   - Sin sesión           → LoginScreen
 *   - Encuestador          → Tab: Encuestas + Mis Visitas
 *   - Admin / Propietario  → Tab: Encuestas + Mis Visitas + Dashboard + Indicadores
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
import EncuestaResidenteScreen from '../screens/EncuestaResidenteScreen';
import EncuestaComercioScreen from '../screens/EncuestaComercioScreen';
import MisVisitasScreen from '../screens/MisVisitasScreen';
import DashboardScreen from '../screens/DashboardScreen';
import IndicadoresScreen from '../screens/IndicadoresScreen';
import DynamicSurveyScreen from '../screens/DynamicSurveyScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Paleta compartida
const COLOR_INSTITUCIONAL = '#4A4A4A';
const COLOR_ADMIN = '#2a9d8f';

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
                options={{ title: 'Control de Encuestas' }}
            />
            <Stack.Screen
                name="NuevaVisita"
                component={FormularioVisitaScreen}
                options={{ title: 'Registro de Visita' }}
            />
            <Stack.Screen
                name="EncuestaResidente"
                component={EncuestaResidenteScreen}
                options={{ title: 'Encuesta Residente' }}
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

// ── Tabs para Encuestador ─────────────────────────────────────────────────────
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
                name="MisVisitas"
                component={MisVisitasScreen}
                options={{
                    headerShown: true,
                    title: 'Mis Registros',
                    tabBarLabel: 'Mis Visitas',
                    headerStyle: { backgroundColor: COLOR_INSTITUCIONAL },
                    headerTintColor: '#fff',
                    tabBarIcon: ({ color, size }) => (
                        <TabIcon emoji="📁" color={color} size={size} />
                    ),
                }}
            />
        </Tab.Navigator>
    );
}

// ── Tabs para Admin / Propietario (Portal Encuestador + Dashboard) ─────────────
function AdminTabs() {
    return (
        <Tab.Navigator
            screenOptions={{
                tabBarActiveTintColor: COLOR_ADMIN,
                tabBarInactiveTintColor: '#999',
                headerShown: false,
            }}
        >
            {/* Admin también puede usar el portal encuestador */}
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
                name="MisVisitas"
                component={MisVisitasScreen}
                options={{
                    headerShown: true,
                    title: 'Mis Registros',
                    tabBarLabel: 'Mis Visitas',
                    headerStyle: { backgroundColor: COLOR_ADMIN },
                    headerTintColor: '#fff',
                    tabBarIcon: ({ color, size }) => (
                        <TabIcon emoji="📁" color={color} size={size} />
                    ),
                }}
            />
            <Tab.Screen
                name="Dashboard"
                component={DashboardScreen}
                options={{
                    headerShown: true,
                    title: 'Dashboard',
                    tabBarLabel: 'Dashboard',
                    headerStyle: { backgroundColor: COLOR_ADMIN },
                    headerTintColor: '#fff',
                    tabBarIcon: ({ color, size }) => (
                        <TabIcon emoji="📊" color={color} size={size} />
                    ),
                }}
            />
            <Tab.Screen
                name="Indicadores"
                component={IndicadoresScreen}
                options={{
                    headerShown: true,
                    title: 'Indicadores',
                    tabBarLabel: 'Indicadores',
                    headerStyle: { backgroundColor: COLOR_ADMIN },
                    headerTintColor: '#fff',
                    tabBarIcon: ({ color, size }) => (
                        <TabIcon emoji="📈" color={color} size={size} />
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

    // Determinar qué tabs mostrar según el tipo de usuario
    const esAdmin = usuario?.tipo === 'admin' || usuario?.tipo === 'propietario';

    return (
        <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false }}>
                {!usuario ? (
                    <Stack.Screen name="Login" component={LoginScreen} />
                ) : esAdmin ? (
                    <Stack.Screen name="AdminApp" component={AdminTabs} />
                ) : (
                    <Stack.Screen name="EncuestadorApp" component={EncuestadorTabs} />
                )}
            </Stack.Navigator>
        </NavigationContainer>
    );
}

/**
 * AppNavigator.js — Configuración de navegación de la app del Observatorio.
 *
 * Lógica de flujo:
 *   - Sin sesión → LoginScreen
 *   - Encuestador → Tab: Formulario + Mis Visitas
 *   - Admin / Propietario → Tab: Dashboard + Indicadores
 */
import React from 'react';
import { ActivityIndicator, View } from 'react-native';
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

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// ── Stack para el flujo de Encuestas ──────────────────────────────────────────
function EncuestasStack() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerStyle: { backgroundColor: '#1a7abf' },
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
        </Stack.Navigator>
    );
}

// ── Tabs para Encuestador ─────────────────────────────────────────────────────
function EncuestadorTabs() {
    return (
        <Tab.Navigator
            screenOptions={{
                tabBarActiveTintColor: '#1a7abf',
                tabBarInactiveTintColor: '#999',
                headerShown: false, // El header lo maneja el Stack interno
            }}
        >
            <Tab.Screen
                name="EncuestasFlow"
                component={EncuestasStack}
                options={{ title: 'Encuestas', tabBarLabel: 'Encuestas' }}
            />
            <Tab.Screen
                name="MisVisitas"
                component={MisVisitasScreen}
                options={{ 
                    headerShown: true,
                    title: 'Mis Registros', 
                    tabBarLabel: 'Mis Visitas',
                    headerStyle: { backgroundColor: '#1a7abf' },
                    headerTintColor: '#fff',
                }}
            />
        </Tab.Navigator>
    );
}

// ── Tabs para Admin / Propietario ─────────────────────────────────────────────
function AdminTabs() {
    return (
        <Tab.Navigator
            screenOptions={{
                tabBarActiveTintColor: '#2a9d8f',
                tabBarInactiveTintColor: '#999',
                headerStyle: { backgroundColor: '#2a9d8f' },
                headerTintColor: '#fff',
                headerTitleStyle: { fontWeight: 'bold' },
            }}
        >
            <Tab.Screen
                name="Dashboard"
                component={DashboardScreen}
                options={{ title: 'Dashboard', tabBarLabel: 'Dashboard' }}
            />
            <Tab.Screen
                name="Indicadores"
                component={IndicadoresScreen}
                options={{ title: 'Indicadores', tabBarLabel: 'Indicadores' }}
            />
        </Tab.Navigator>
    );
}

// ── Navigator principal ───────────────────────────────────────────────────────
export default function AppNavigator() {
    const { usuario, cargando } = useAuth();

    if (cargando) {
        return (
            <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f0f4f8' }}>
                <ActivityIndicator size="large" color="#1a7abf" />
            </View>
        );
    }

    return (
        <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false }}>
                {!usuario ? (
                    <Stack.Screen name="Login" component={LoginScreen} />
                ) : usuario.tipo === 'encuestador' || usuario.tipo === 'admin' ? (
                    // Permitimos que el admin vea también las pestañas de encuestador si lo desea,
                    // pero aquí seguimos la lógica original separada.
                    usuario.tipo === 'encuestador' ? (
                        <Stack.Screen name="EncuestadorApp" component={EncuestadorTabs} />
                    ) : (
                        <Stack.Screen name="AdminApp" component={AdminTabs} />
                    )
                ) : (
                    <Stack.Screen name="AdminApp" component={AdminTabs} />
                )}
            </Stack.Navigator>
        </NavigationContainer>
    );
}

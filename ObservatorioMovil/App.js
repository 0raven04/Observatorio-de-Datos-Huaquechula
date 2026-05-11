/**
 * App.js — Entry point de la App Móvil del Observatorio de Datos Huaquechula.
 * Envuelve toda la app con el AuthProvider para el manejo global de sesión.
 */
import { StatusBar } from 'expo-status-bar';
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <AuthProvider>
      <StatusBar style="auto" />
      <AppNavigator />
    </AuthProvider>
  );
}

/**
 * storage.js — Almacenamiento universal para web y móvil.
 * - En web (navegador): usa localStorage (disponible en todos los browsers)
 * - En móvil (Android/iOS): usa expo-secure-store (almacenamiento cifrado)
 */
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const storage = {
  async setItem(key, value) {
    if (Platform.OS === 'web') {
      localStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  },

  async getItem(key) {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    } else {
      return await SecureStore.getItemAsync(key);
    }
  },

  async deleteItem(key) {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
    } else {
      await SecureStore.deleteItemAsync(key);
    }
  },
};

export default storage;

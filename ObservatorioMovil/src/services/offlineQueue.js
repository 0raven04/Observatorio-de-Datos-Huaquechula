import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api';

const QUEUE_STORAGE_KEY = '@observatorio_offline_queue_v1';

export const offlineQueue = {
    /**
     * Obtiene todos los elementos pendientes en la cola offline.
     */
    async getQueue() {
        try {
            const raw = await AsyncStorage.getItem(QUEUE_STORAGE_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            console.error('Error al leer cola offline:', e);
            return [];
        }
    },

    /**
     * Obtiene la cantidad de encuestas pendientes de sincronización.
     */
    async getQueueCount() {
        const queue = await this.getQueue();
        return queue.length;
    },

    /**
     * Agrega una encuesta a la cola offline.
     * Preserva la fecha y hora local exacta del momento de captura en campo.
     */
    async enqueue(item) {
        try {
            const queue = await this.getQueue();
            const newItem = {
                id: item.id || `local_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
                endpoint: item.endpoint,
                tipo: item.tipo || 'encuesta',
                payload: {
                    ...item.payload,
                    fecha_captura_local: item.payload?.fecha_captura_local || new Date().toISOString(),
                },
                fecha_guardado_local: new Date().toISOString(),
            };
            queue.push(newItem);
            await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
            return newItem;
        } catch (e) {
            console.error('Error al encolar encuesta offline:', e);
            throw e;
        }
    },

    /**
     * Intenta sincronizar todos los elementos pendientes con el servidor.
     * onProgress: callback opcional (actual, total)
     */
    async syncQueue(onProgress = null) {
        const queue = await this.getQueue();
        if (queue.length === 0) {
            return { total: 0, synced: 0, failed: 0, remaining: 0 };
        }

        const remainingQueue = [];
        let syncedCount = 0;
        let failedCount = 0;

        for (let i = 0; i < queue.length; i++) {
            const item = queue[i];
            if (onProgress) {
                onProgress(i + 1, queue.length);
            }

            try {
                // Enviar la petición al backend central
                await api.post(item.endpoint, item.payload);
                syncedCount++;
            } catch (err) {
                // Si es un error de validación 400 permanente, registrar y descartar para no bloquear
                if (err.response && err.response.status === 400) {
                    console.warn(`[SyncQueue] Encuesta ${item.id} descartada por validación 400:`, err.response.data);
                    failedCount++;
                } else {
                    // Si es un error de red o servidor no disponible (5xx), conservar y pausar
                    console.log(`[SyncQueue] Conexión interrumpida en elemento ${item.id}, pausando sync:`, err.message);
                    remainingQueue.push(item);
                    for (let j = i + 1; j < queue.length; j++) {
                        remainingQueue.push(queue[j]);
                    }
                    break;
                }
            }
        }

        await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(remainingQueue));
        return {
            total: queue.length,
            synced: syncedCount,
            failed: failedCount,
            remaining: remainingQueue.length,
        };
    },

    /**
     * Limpia la cola offline manualmente si es necesario.
     */
    async clearQueue() {
        await AsyncStorage.removeItem(QUEUE_STORAGE_KEY);
    }
};

export default offlineQueue;

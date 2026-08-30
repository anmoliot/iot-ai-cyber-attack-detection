import { useEffect, useState, useRef } from 'react';
import type { Alert } from './api';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/alerts';

type ConnectionState = 'connecting' | 'connected' | 'reconnecting' | 'offline';

export function useAlertStream(initialAlerts: Alert[] = []) {
  const [alerts, setAlerts] = useState<Alert[]>(initialAlerts);
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 10;

  useEffect(() => {
    // If initialAlerts changes (e.g. from a fresh fetch on reconnect), update our state
    setAlerts(initialAlerts);
  }, [initialAlerts]);

  useEffect(() => {
    let reconnectTimeout: ReturnType<typeof setTimeout>;

    const connect = () => {
      setConnectionState(reconnectAttempts.current > 0 ? 'reconnecting' : 'connecting');

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnectionState('connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const newAlert: Alert = JSON.parse(event.data);
          setAlerts((prev: Alert[]) => {
            const next = [newAlert, ...prev];
            return next.slice(0, 200); // Keep max 200 alerts
          });
        } catch (e) {
          console.error("Failed to parse alert", e);
        }
      };

      ws.onclose = () => {
        if (reconnectAttempts.current < maxReconnectAttempts) {
          setConnectionState('reconnecting');
          const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts.current), 10000);
          reconnectAttempts.current += 1;
          reconnectTimeout = setTimeout(connect, delay);
        } else {
          setConnectionState('offline');
        }
      };

      ws.onerror = () => {
        // ws.onclose will handle the reconnect
        ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.onclose = null; // Prevent reconnect loop on unmount
        wsRef.current.close();
      }
    };
  }, []);

  return { alerts, connectionState };
}

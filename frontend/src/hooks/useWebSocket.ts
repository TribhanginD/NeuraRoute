import { useState, useEffect, useRef } from 'react';

type JsonValue = Record<string, unknown> | null;

const getDefaultWebSocketUrl = (): string | undefined => {
  if (typeof window === 'undefined') return undefined;
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const host = window.location.hostname;
  const port = process.env.REACT_APP_WS_PORT || '8000';
  const path = process.env.REACT_APP_WS_PATH || '/ws/agent-actions';
  return `${protocol}://${host}:${port}${path}`;
};

export function useWebSocket(url?: string) {
  const resolvedUrl = url || process.env.REACT_APP_WS_URL || getDefaultWebSocketUrl();
  const [data, setData] = useState<JsonValue>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Event | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 1000; // Start with 1 second

  useEffect(() => {
    if (!resolvedUrl) return;

    const connect = () => {
      try {
        const ws = new WebSocket(resolvedUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          setError(null);
          reconnectAttemptsRef.current = 0;
          console.log('WebSocket connected');
        };

        ws.onmessage = (event: MessageEvent) => {
          try {
            const parsedData = JSON.parse(event.data);
            setData(parsedData);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
          }
        };

        ws.onclose = (event) => {
          setIsConnected(false);
          console.log('WebSocket disconnected:', event.code, event.reason);
          
          // Attempt to reconnect if not a normal closure
          if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
            const delay = reconnectDelay * Math.pow(2, reconnectAttemptsRef.current);
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttemptsRef.current += 1;
              connect();
            }, delay);
          }
        };

        ws.onerror = (socketError) => {
          setError(socketError);
          console.error('WebSocket error:', socketError);
        };

      } catch (err) {
        setError(err);
        console.error('Failed to create WebSocket connection:', err);
      }
    };

    connect();

    // Cleanup function
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [resolvedUrl]);

  const sendMessage = (message: JsonValue) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return {
    data,
    isConnected,
    error,
    sendMessage,
  };
} 

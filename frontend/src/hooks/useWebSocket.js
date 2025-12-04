import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for WebSocket connection with auto-reconnect
 * 
 * @param {string} url - WebSocket server URL
 * @returns {Object} - { connected, lastMessage, reconnectAttempt }
 */
function useWebSocket(url) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  
  // Exponential backoff sequence: 1s, 2s, 4s, 8s, 16s, max 30s
  const backoffSequence = [1000, 2000, 4000, 8000, 16000];
  const maxBackoff = 30000;
  
  const connect = useCallback(() => {
    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
        // Reset reconnect attempts on successful connection
        reconnectAttemptsRef.current = 0;
        setReconnectAttempt(0);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        wsRef.current = null;
        
        // Schedule reconnection with exponential backoff
        scheduleReconnect();
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnected(false);
      scheduleReconnect();
    }
  }, [url]);
  
  const scheduleReconnect = useCallback(() => {
    // Clear any existing reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    // Calculate delay with exponential backoff
    const delay = reconnectAttemptsRef.current < backoffSequence.length
      ? backoffSequence[reconnectAttemptsRef.current]
      : maxBackoff;
    
    console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttemptsRef.current + 1})`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectAttemptsRef.current++;
      setReconnectAttempt(reconnectAttemptsRef.current);
      connect();
    }, delay);
  }, [connect, backoffSequence, maxBackoff]);
  
  // Initial connection on mount
  useEffect(() => {
    connect();
    
    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);
  
  return {
    connected,
    lastMessage,
    reconnectAttempt
  };
}

export default useWebSocket;

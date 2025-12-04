"""
WebSocket Manager for Crystal Ball CI/CD System

Manages WebSocket connections and broadcasts predictions to connected clients.
"""

from typing import List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts messages to all connected clients.
    
    Responsibilities:
    - Accept and register new WebSocket connections
    - Remove disconnected clients
    - Broadcast predictions to all active connections
    - Handle connection failures gracefully during broadcast
    """
    
    def __init__(self):
        """Initialize with empty connection list"""
        self.active_connections: List[WebSocket] = []
        logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from the active list.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict) -> None:
        """
        Send a message to all connected WebSocket clients.
        
        Handles connection failures gracefully by removing failed connections
        and continuing to broadcast to remaining clients.
        
        Args:
            message: Dictionary to send as JSON to all clients
        """
        if not self.active_connections:
            logger.info("No active WebSocket connections to broadcast to")
            return
        
        logger.info(f"Broadcasting message to {len(self.active_connections)} clients")
        
        # Track failed connections to remove after broadcast attempt
        failed_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to WebSocket client: {e}")
                failed_connections.append(connection)
        
        # Remove failed connections
        for failed_connection in failed_connections:
            await self.disconnect(failed_connection)
        
        if failed_connections:
            logger.info(f"Removed {len(failed_connections)} failed connections")
    
    def get_connection_count(self) -> int:
        """
        Get the number of active WebSocket connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)

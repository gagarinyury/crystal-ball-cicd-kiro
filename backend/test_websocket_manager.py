"""
Unit tests for WebSocket Manager
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_websocket_manager_initialization():
    """Test that WebSocketManager initializes with empty connections list"""
    manager = WebSocketManager()
    assert manager.active_connections == []
    assert manager.get_connection_count() == 0


@pytest.mark.asyncio
async def test_connect_accepts_and_registers_connection():
    """Test that connect method accepts and registers a WebSocket connection"""
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    
    await manager.connect(mock_websocket)
    
    # Verify websocket.accept() was called
    mock_websocket.accept.assert_called_once()
    
    # Verify connection was added to active_connections
    assert mock_websocket in manager.active_connections
    assert manager.get_connection_count() == 1


@pytest.mark.asyncio
async def test_connect_multiple_connections():
    """Test that multiple connections can be registered"""
    manager = WebSocketManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()
    
    await manager.connect(mock_ws1)
    await manager.connect(mock_ws2)
    await manager.connect(mock_ws3)
    
    assert manager.get_connection_count() == 3
    assert mock_ws1 in manager.active_connections
    assert mock_ws2 in manager.active_connections
    assert mock_ws3 in manager.active_connections


@pytest.mark.asyncio
async def test_disconnect_removes_connection():
    """Test that disconnect method removes a connection from active list"""
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    
    await manager.connect(mock_websocket)
    assert manager.get_connection_count() == 1
    
    await manager.disconnect(mock_websocket)
    
    # Verify connection was removed
    assert mock_websocket not in manager.active_connections
    assert manager.get_connection_count() == 0


@pytest.mark.asyncio
async def test_disconnect_nonexistent_connection():
    """Test that disconnecting a non-existent connection doesn't cause errors"""
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    
    # Should not raise an error
    await manager.disconnect(mock_websocket)
    assert manager.get_connection_count() == 0


@pytest.mark.asyncio
async def test_broadcast_sends_to_all_connections():
    """Test that broadcast sends message to all active connections"""
    manager = WebSocketManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()
    
    await manager.connect(mock_ws1)
    await manager.connect(mock_ws2)
    await manager.connect(mock_ws3)
    
    test_message = {
        'prediction_score': 85,
        'mystical_message': 'The stars align favorably'
    }
    
    await manager.broadcast(test_message)
    
    # Verify all connections received the message
    mock_ws1.send_json.assert_called_once_with(test_message)
    mock_ws2.send_json.assert_called_once_with(test_message)
    mock_ws3.send_json.assert_called_once_with(test_message)


@pytest.mark.asyncio
async def test_broadcast_with_no_connections():
    """Test that broadcast handles empty connection list gracefully"""
    manager = WebSocketManager()
    
    test_message = {'prediction_score': 85}
    
    # Should not raise an error
    await manager.broadcast(test_message)


@pytest.mark.asyncio
async def test_broadcast_removes_failed_connections():
    """Test that broadcast removes connections that fail during send"""
    manager = WebSocketManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()
    
    # Make ws2 fail during send
    mock_ws2.send_json.side_effect = Exception("Connection lost")
    
    await manager.connect(mock_ws1)
    await manager.connect(mock_ws2)
    await manager.connect(mock_ws3)
    
    assert manager.get_connection_count() == 3
    
    test_message = {'prediction_score': 85}
    await manager.broadcast(test_message)
    
    # Verify ws1 and ws3 received the message
    mock_ws1.send_json.assert_called_once_with(test_message)
    mock_ws3.send_json.assert_called_once_with(test_message)
    
    # Verify ws2 was removed from active connections
    assert mock_ws2 not in manager.active_connections
    assert manager.get_connection_count() == 2
    assert mock_ws1 in manager.active_connections
    assert mock_ws3 in manager.active_connections


@pytest.mark.asyncio
async def test_broadcast_continues_after_failure():
    """Test that broadcast continues to other connections after one fails"""
    manager = WebSocketManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()
    
    # Make ws1 fail
    mock_ws1.send_json.side_effect = Exception("Connection error")
    
    await manager.connect(mock_ws1)
    await manager.connect(mock_ws2)
    await manager.connect(mock_ws3)
    
    test_message = {'prediction_score': 85}
    await manager.broadcast(test_message)
    
    # Verify ws2 and ws3 still received the message despite ws1 failing
    mock_ws2.send_json.assert_called_once_with(test_message)
    mock_ws3.send_json.assert_called_once_with(test_message)
    
    # Verify only ws1 was removed
    assert mock_ws1 not in manager.active_connections
    assert mock_ws2 in manager.active_connections
    assert mock_ws3 in manager.active_connections
    assert manager.get_connection_count() == 2


@pytest.mark.asyncio
async def test_broadcast_removes_multiple_failed_connections():
    """Test that broadcast removes all failed connections"""
    manager = WebSocketManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()
    mock_ws4 = AsyncMock()
    
    # Make ws1 and ws3 fail
    mock_ws1.send_json.side_effect = Exception("Connection error 1")
    mock_ws3.send_json.side_effect = Exception("Connection error 2")
    
    await manager.connect(mock_ws1)
    await manager.connect(mock_ws2)
    await manager.connect(mock_ws3)
    await manager.connect(mock_ws4)
    
    test_message = {'prediction_score': 85}
    await manager.broadcast(test_message)
    
    # Verify only ws2 and ws4 remain
    assert manager.get_connection_count() == 2
    assert mock_ws1 not in manager.active_connections
    assert mock_ws2 in manager.active_connections
    assert mock_ws3 not in manager.active_connections
    assert mock_ws4 in manager.active_connections

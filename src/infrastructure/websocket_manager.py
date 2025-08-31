import asyncio
import json
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from src.common.loggers import app_logger


class WebSocketManager:
    """
    Manages WebSocket connections for different clubs.
    Allows sending messages to specific clubs or broadcasting to all connected clients.
    """
    
    def __init__(self):
        # Dictionary mapping club_id to set of connected websockets for that club
        self._connections: Dict[str, Set[WebSocket]] = {}
        # Dictionary mapping websocket to club_id for cleanup purposes
        self._websocket_to_club: Dict[WebSocket, str] = {}
        self._lock = asyncio.Lock()
    
    async def register_connection(self, websocket: WebSocket, club_id: str):
        """
        Register a new WebSocket connection for a specific club.
        
        Args:
            websocket: The WebSocket connection
            club_id: The club identifier
        """
        async with self._lock:
            if club_id not in self._connections:
                self._connections[club_id] = set()
            
            self._connections[club_id].add(websocket)
            self._websocket_to_club[websocket] = club_id
            
            app_logger.info(f"Registered WebSocket connection for club {club_id}. "
                           f"Total connections for club: {len(self._connections[club_id])}")
    
    async def unregister_connection(self, websocket: WebSocket):
        """
        Unregister a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection to unregister
        """
        app_logger.debug(f"Unregistering WebSocket connection")
        async with self._lock:
            if websocket in self._websocket_to_club:
                club_id = self._websocket_to_club[websocket]
                
                # Remove from connections
                if club_id in self._connections:
                    self._connections[club_id].discard(websocket)
                    app_logger.debug(f"Unregistered WebSocket connection for club {club_id}. Total connections for club: {len(self._connections[club_id])}, {self._connections[club_id]}")
                    # Clean up empty club entries
                    if not self._connections[club_id]:
                        del self._connections[club_id]
                
                # Remove from websocket mapping
                del self._websocket_to_club[websocket]
                
                app_logger.info(f"Unregistered WebSocket connection for club {club_id}")
    
    async def send_message(self, club_id: str, message: Any):
        """
        Send a message to all connected WebSocket clients for a specific club.
        
        Args:
            club_id: The club identifier
            message: The message to send (dict or string - strings will be wrapped in {"message": message})
        """
        if club_id not in self._connections:
            #app_logger.warning(f"No WebSocket connections found for club {club_id}")
            return
        
        # Handle message formatting
        if isinstance(message, str):
            message_dict = {"message": message}
        elif isinstance(message, dict):
            message_dict = message
        else:
            app_logger.error(f"Message must be a string or dict, got {type(message)}")
            return
        
        # Serialize message to JSON
        try:
            message_json = json.dumps(message_dict)
        except (TypeError, ValueError) as e:
            app_logger.error(f"Failed to serialize message for club {club_id}: {e}")
            return
        
        # Get a copy of connections to avoid modifying during iteration
        async with self._lock:
            connections = self._connections[club_id].copy()
        
        if not connections:
            #app_logger.warning(f"No active connections for club {club_id}")
            return
        
        # Send message to all connections for this club
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_text(message_json)
                #app_logger.debug(f"Sent message to club {club_id}")
            except WebSocketDisconnect:
                app_logger.info(f"WebSocket connection closed for club {club_id}")
                disconnected.append(websocket)
            except Exception as e:
                app_logger.error(f"Error sending message to club {club_id}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            await self.unregister_connection(websocket)
    
    async def send_json(self, club_id: str, data: Any):
        """
        Send JSON data to all connected WebSocket clients for a specific club.
        
        Args:
            club_id: The club identifier
            data: The data to send as JSON
        """
        if club_id not in self._connections:
            app_logger.warning(f"No WebSocket connections found for club {club_id}")
            return
        
        # Get a copy of connections to avoid modifying during iteration
        async with self._lock:
            connections = self._connections[club_id].copy()
        
        if not connections:
            app_logger.warning(f"No active connections for club {club_id}")
            return
        
        # Send JSON to all connections for this club
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_json(data)
                app_logger.debug(f"Sent JSON message to club {club_id}")
            except WebSocketDisconnect:
                app_logger.info(f"WebSocket connection closed for club {club_id}")
                disconnected.append(websocket)
            except Exception as e:
                app_logger.error(f"Error sending JSON message to club {club_id}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            await self.unregister_connection(websocket)
    
    async def broadcast_message(self, message: Any, exclude_club_ids: Optional[Set[str]] = None):
        """
        Broadcast a message to all connected WebSocket clients across all clubs.
        
        Args:
            message: The message to broadcast
            exclude_club_ids: Optional set of club IDs to exclude from broadcast
        """
        if exclude_club_ids is None:
            exclude_club_ids = set()
        
        async with self._lock:
            club_ids = list(self._connections.keys())
        
        for club_id in club_ids:
            if club_id not in exclude_club_ids:
                await self.send_message(club_id, message)
    
    async def broadcast_json(self, data: Any, exclude_club_ids: Optional[Set[str]] = None):
        """
        Broadcast JSON data to all connected WebSocket clients across all clubs.
        
        Args:
            data: The data to broadcast as JSON
            exclude_club_ids: Optional set of club IDs to exclude from broadcast
        """
        if exclude_club_ids is None:
            exclude_club_ids = set()
        
        async with self._lock:
            club_ids = list(self._connections.keys())
        
        for club_id in club_ids:
            if club_id not in exclude_club_ids:
                await self.send_json(club_id, data)
    
    def get_connection_count(self, club_id: Optional[str] = None) -> int:
        """
        Get the number of active connections.
        
        Args:
            club_id: If provided, returns count for specific club. Otherwise, returns total count.
            
        Returns:
            Number of active connections
        """
        if club_id:
            return len(self._connections.get(club_id, set()))
        
        return sum(len(connections) for connections in self._connections.values())
    
    def get_connected_clubs(self) -> Set[str]:
        """
        Get a set of all club IDs that have active connections.
        
        Returns:
            Set of club IDs with active connections
        """
        return set(self._connections.keys())


# Global instance
websocket_manager = WebSocketManager()

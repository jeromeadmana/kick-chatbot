# app/websocket_manager.py
from typing import Dict, List
from fastapi import WebSocket
import asyncio

class ConnectionManager:
    """
    Simple WebSocket connection manager.
    - Keeps connections per session_id.
    - Broadcasts messages to all connections in a session.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.setdefault(session_id, []).append(websocket)

    async def disconnect(self, session_id: str, websocket: WebSocket):
        async with self._lock:
            conns = self.active_connections.get(session_id, [])
            if websocket in conns:
                conns.remove(websocket)
            if not conns:
                self.active_connections.pop(session_id, None)

    async def broadcast(self, session_id: str, message: str):
        conns = list(self.active_connections.get(session_id, []))
        for ws in conns:
            try:
                await ws.send_json({"type": "assistant", "content": message})
            except Exception:
                # best-effort: ignore broken sockets
                pass

ws_manager = ConnectionManager()

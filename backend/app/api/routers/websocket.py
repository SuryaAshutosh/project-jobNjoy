"""
WebSocket router for real-time job updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from app.core.auth import get_current_active_user
from app.models.db_models import User

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/jobs")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time job updates
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            data = await websocket.receive_text()
            # Echo the message back (can be customized for specific functionality)
            await manager.send_personal_message(f"You sent: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client has disconnected")

@router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for user notifications
    """
    await manager.connect(websocket)
    try:
        while True:
            # In a real implementation, this would send notifications
            # For now, we'll just keep the connection alive
            await asyncio.sleep(30)  # Send a ping every 30 seconds
            await manager.send_personal_message(json.dumps({"type": "ping", "timestamp": asyncio.get_event_loop().time()}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
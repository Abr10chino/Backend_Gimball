import asyncio
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        asyncio.create_task(self._ping_client(websocket))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

    async def _ping_client(self, websocket: WebSocket):
        while websocket in self.active_connections:
            await asyncio.sleep(20)
            try:
                await websocket.send_json({"topic": "ping", "data": "keepalive"})
            except Exception:
                self.disconnect(websocket)
                break

manager = ConnectionManager()
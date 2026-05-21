import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from app.mqtt import startMQTT, stopMQTT
from app.websocket import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    startMQTT(loop)
    yield
    stopMQTT()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "Backend del Gimbal corriendo perfectamente"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(3600)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
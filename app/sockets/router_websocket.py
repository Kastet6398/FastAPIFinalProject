from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from app.auth import dependencies


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

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



router = APIRouter(
    prefix='/ws',
)


@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket):
    # await websocket.accept()
    # while True:
    #     text = await websocket.receive_text()
    #     await websocket.send_text(f'Your text: {text}')
    #     # await websocket.send_json(json.dumps({'count': 5}))

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # print(data)
            await manager.broadcast(f" says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
"""Server for WebSocket chat application using FastAPI."""
import json
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse

from DSA.sign_utils import generate_params

app = FastAPI()
connected_users: Dict[str, tuple[WebSocket, str]] = {}

p, q, g = generate_params()

with open("DSA_params.txt", "w", encoding="utf-8") as f:
    f.write(f"p: {p}\n")
    f.write(f"q: {q}\n")
    f.write(f"g: {g}\n")

async def broadcast_users():
    """Broadcast the list of connected users to all clients."""
    user_list = list(connected_users.keys())
    for user_ws, public_key in connected_users.values():
        await user_ws.send_text(f"__USERS__:{','.join(user_list)}")

@app.websocket("/ws/get_key_{username}")
async def websocket_get_key(websocket: WebSocket, username: str):
    await websocket.accept()
    await websocket.send_text(str(connected_users[username][1]))
    await websocket.close()

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """WebSocket endpoint for chat application.
    Handles incoming messages and broadcasts them to the appropriate recipient.
    """
    if username in connected_users:
        await websocket.accept()
        await websocket.send_text("__ERROR__:Username already taken")
        await websocket.close()
        return

    await websocket.accept()
    public_key = await websocket.receive_text()
    connected_users[username] = (websocket, public_key)
    print(f"{username} підключився ✅")

    # Повідомляємо всіх про новий список юзерів
    await broadcast_users()

    try:
        while True:
            data = await websocket.receive_json()
            try:
                sender, recipient, message, iv, signature, y = data
            except ValueError:
                await websocket.send_text("❌ Некоректний формат повідомлення.")
                continue

            if recipient in connected_users:
                await connected_users[recipient][0].send_json(data)
                await websocket.send_text(f"✅ Повідомлення надіслано {recipient}")
            else:
                await websocket.send_text(f"❌ Користувача {recipient} не знайдено.")
    except WebSocketDisconnect:
        print(f"{username} відключився ❌")
        del connected_users[username]
        await broadcast_users()

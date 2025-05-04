"""Server for WebSocket chat application using FastAPI."""

from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from DSA.sign_utils import generate_params

app = FastAPI()
connected_users: Dict[str, WebSocket] = {}

p, q, g = generate_params()

with open("DSA_params.txt", "w", encoding="utf-8") as f:
    f.write(f"p: {p}\n")
    f.write(f"q: {q}\n")
    f.write(f"g: {g}\n")

async def broadcast_users():
    """Broadcast the list of connected users to all clients."""
    user_list = list(connected_users.keys())
    for user_ws in connected_users.values():
        await user_ws.send_text(f"__USERS__:{','.join(user_list)}")

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """WebSocket endpoint for chat application.
    Handles incoming messages and broadcasts them to the appropriate recipient.
    """
    await websocket.accept()
    connected_users[username] = websocket
    print(f"{username} підключився ✅")

    # Повідомляємо всіх про новий список юзерів
    await broadcast_users()

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Отримано від {username}: {data}")

            # Очікуємо формат: "recipient||message"
            try:
                recipient, message, signature, y = data.split("||")
            except ValueError:
                await websocket.send_text("❌ Некоректний формат повідомлення.")
                continue

            if recipient in connected_users:
                await connected_users[recipient].send_text(f"{username}||{message}||{signature}||{y}")
                await websocket.send_text(f"✅ Повідомлення надіслано {recipient}")
            else:
                await websocket.send_text(f"❌ Користувача {recipient} не знайдено.")
    except WebSocketDisconnect:
        print(f"{username} відключився ❌")
        del connected_users[username]
        await broadcast_users()

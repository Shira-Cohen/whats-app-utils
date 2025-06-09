from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import logging

from whats_app_utils.custem_logger import logger

# שמירת חיבורים פתוחים לפי user_id
connected_users: Dict[str, WebSocket] = {}


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    logger.info(f"user {user_id} שלום ")
    await websocket.accept()
    connected_users[user_id] = websocket
    logger.info(f"user {user_id} connected via WebSocket dict = {connected_users}")
    try:
        while True:
            await websocket.receive_text()  # שומר את החיבור פתוח, גם אם אין הודעות
    except WebSocketDisconnect:
        connected_users.pop(user_id, None)
        logger.info(f"user {user_id} disconnected")


async def send_message_to_user(user_id: str, message: str):
    logger.info(f"send message to user {user_id}")
    websocket = connected_users.get(user_id)
    logger.info(f"send message to user {user_id} websocket = {websocket}  dict = {connected_users}")
    if websocket:
        await websocket.send_text(message)

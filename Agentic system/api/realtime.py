"""WebSocket endpoints.

/ws   the duplex voice conversation (dialogue_orchestrator/dialogue_voice.py)
/ws2  the safety module: pushes crisis_alert and a heartbeat while it waits"""

import asyncio
import json
import logging
import time

from fastapi import APIRouter, WebSocket

from api.dependencies import storage
from dialogue_orchestrator.dialogue_voice import voice_endpoint
from safety.crisis_watcher import crisis_watch_loop

logger = logging.getLogger("realtime")
router = APIRouter()

@router.websocket("/ws")
async def ws_voice(ws: WebSocket):
    await voice_endpoint(ws, storage)

@router.websocket("/ws2")
async def ws_crisis(ws: WebSocket):
    await ws.accept()
    watcher = None
    try:
        init = json.loads(await ws.receive_text())
        if init.get("type") != "init" or not init.get("session_id"):
            await ws.close(code=4001)
            return
        watcher = asyncio.create_task(crisis_watch_loop(ws, storage, init["session_id"]))
        while True:
            message = await ws.receive()
            if message.get("type") == "websocket.disconnect":
                break
            if "text" not in message:
                continue
            try:
                payload = json.loads(message["text"])
            except ValueError:
                continue
            if payload.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong", "ts": time.time()}))
    except Exception as exc:
        logger.info("ws2 closed: %s", exc)
    finally:
        if watcher:
            watcher.cancel()

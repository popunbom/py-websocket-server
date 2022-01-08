#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
from os import getenv
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect

ENV = {
    "HOST": getenv("APP_HOST", "127.0.0.1"),
    "PORT": int(getenv("APP_PORT", "8080")),
    "LOG_LEVEL": getenv("LOG_LEVEL", "info")
}

logger = logging.getLogger("uvicorn.error")
subscribers: Dict[int, WebSocket] = {}
app = FastAPI()


class Message(BaseModel):
    body: str
    timestamp: Optional[datetime]


@app.websocket("/ws")
async def handle_subscriber(ws: WebSocket):
    await ws.accept()
    # Add to subscribers
    subscribers[id(ws)] = ws
    logger.debug("Add subscriber")
    # Handling subscriber's message
    try:
        while True:
            message = await ws.receive_json()
            await publish(Message(**message))
    except WebSocketDisconnect:
        pass
    except Exception:
        await ws.close()
    finally:
        del subscribers[id(ws)]


@app.post("/publish")
async def publish(message: Message):
    message.timestamp = datetime.now()

    message = message.json()
    n_subscribers = len(subscribers)
    for subscriber in subscribers.values():
        await subscriber.send_text(message)
    logger.debug("Publish message to {} subscribers".format(n_subscribers))

    return {"message": message, "n_publishers": n_subscribers}

if __name__ == '__main__':
    uvicorn.run("__main__:app",
                host=ENV["HOST"],
                port=ENV["PORT"],
                log_level=ENV["LOG_LEVEL"])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
バックエンドサーバ
- WebSocket サーバー
- Google の Speech-to−Text API へリクエストを行い
  音声データの文字起こしを行う
"""


from datetime import datetime
import logging
from os import getenv, path
from typing import Dict

import uvicorn
from fastapi import FastAPI
from google.cloud.speech import RecognitionConfig
from starlette.websockets import WebSocket, WebSocketDisconnect

from lib.message import DataURL, Message, MessageBody, MessageType
from lib.stream_transcriber import Language, StreamTranscriber, TranscribeConfig


ENV = {
    "HOST": getenv("APP_HOST", "127.0.0.1"),
    "PORT": int(getenv("APP_PORT", "8080")),
    "LOG_LEVEL": getenv("LOG_LEVEL", "info"),
    "GAPI_CREDENTIAL_FILE": getenv(
        "GAPI_CREDENTIAL_FILE",
        path.join(path.dirname(__file__),
                  "./credentials/service_account_key.json")
    ),
}

logger = logging.getLogger("uvicorn.error")

app = FastAPI()
transcriber = StreamTranscriber(
    credential_filename=ENV["GAPI_CREDENTIAL_FILE"],
    config=TranscribeConfig(
        audio_codec=RecognitionConfig.AudioEncoding.LINEAR16,  # audio/wav
        sampling_rate_hz=16000,  # 16 kHz
        language=Language.JAPANESE
    )
)

subscribers: Dict[int, WebSocket] = {}


@app.websocket("/ws")
async def handle_subscriber(ws: WebSocket):
    """
    `/ws`

    WebSocket の subscribe リクエストを受け取る

    Parameters
    ----------
    ws : WebSocket
        WebSocket リクエスト
    """
    await ws.accept()
    # Add to subscribers
    subscribers[id(ws)] = ws
    logger.debug("Add subscriber")
    # Handling subscriber's message
    try:
        while True:
            message = await ws.receive_json()
            await publish(Message(**message))
    except WebSocketDisconnect as e:
        logger.error(e)
        pass
    except Exception as e:
        logger.error(e)
        await ws.close()
    finally:
        del subscribers[id(ws)]


@app.post("/publish")
async def publish(message: Message):
    """
    POST /publish

    WebSocket メッセージを publish する

    Parameters
    ----------
    message : Message
        メッセージ
    """
    message.timestamp = datetime.now()
    if message.body.type == MessageType.VOICE:
        # Transcribe audio using Google Cloud Speech-to-Text API
        data_url: DataURL = message.body.content
        result = transcriber.transcribe_stream(data_url.as_bytes())
        message = Message(
            body=MessageBody(
                type=MessageType.TEXT,
                content=result.text
            ),
            timestamp=message.timestamp
        )
    n_subscribers = len(subscribers)
    for subscriber in subscribers.values():
        await subscriber.send_text(message.json())
    logger.debug("Publish message to {} subscribers".format(n_subscribers))

    return {"message": message, "n_publishers": n_subscribers}


if __name__ == '__main__':
    uvicorn.run("__main__:app",
                host=ENV["HOST"],
                port=ENV["PORT"],
                log_level=ENV["LOG_LEVEL"])

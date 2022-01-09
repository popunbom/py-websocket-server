#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base64 import b64decode
from enum import Enum
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


class MessageType(Enum):
    TEXT = "text"
    VOICE = "voice"


class DataURLEncoding(Enum):
    PLAIN = "plain"
    BASE64 = "base64"


class DataURL(BaseModel):
    """ JavaScript の Data URL """
    media_type: str
    encoding: DataURLEncoding
    data: str

    def as_bytes(self) -> bytes:
        if self.encoding == DataURLEncoding.PLAIN:
            return self.data.encode("utf-8")
        elif self.encoding == DataURLEncoding.BASE64:
            return b64decode(self.data)
        return b""


class MessageBody(BaseModel):
    """ メッセージ本体  """
    type: MessageType
    content: Union[DataURL, str]  # Plain text (TEXT) | Data URL (VOICE)


class Message(BaseModel):
    """ WebSocket メッセージ """
    body: MessageBody
    timestamp: Optional[datetime]

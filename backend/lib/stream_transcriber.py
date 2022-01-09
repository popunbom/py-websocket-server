#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from enum import Enum
from typing import Iterable

from pydantic import BaseModel

from google.cloud import speech
from google.protobuf import json_format
from google.oauth2.service_account import Credentials
from google.api_core.grpc_helpers import _StreamingResponseIterator


logger = logging.getLogger("uvicorn.error")


class Language(Enum):
    """ 解析対象の言語 """
    ENGLISH = "en-US"
    JAPANESE = "ja-JP"


class TranscribeConfig(BaseModel):
    """ 解析設定 """
    audio_codec: speech.RecognitionConfig.AudioEncoding
    sampling_rate_hz: int
    language: Language


class TranscribeResult(BaseModel):
    """ API による解析結果 """
    text: str


class StreamTranscriber:
    """
    Google Clound Speech-to-Text API を利用して
    音声ストリーミングを文字起こしする
    """
    client: speech.SpeechClient
    config: speech.RecognitionConfig

    def __init__(self, credential_filename: str, config: TranscribeConfig) -> None:
        print("StreamTranscriber: __init__")
        self.client = speech.SpeechClient(
            credentials=Credentials.from_service_account_file(
                filename=credential_filename
            )
        )
        self.config = speech.RecognitionConfig(
            encoding=config.audio_codec,
            sample_rate_hertz=config.sampling_rate_hz,
            language_code=config.language.value
        )
        print("config: {}".format(self.config))

    def transcribe_stream(self, stream: bytes) -> TranscribeResult:
        """
        音声ストリームデータを文字起こしする

        Parameters
        ----------
        stream : bytes
            音声データのバイナリ

        Returns
        -------
        TranscribeResult
            解析結果
        """

        logger.info("[Speech-to-Text] stream data: {}, {:,} bytes".format(
            stream[:6],
            len(stream) / 1000)
        )
        responses: _StreamingResponseIterator = self.client.streaming_recognize(
            config=speech.StreamingRecognitionConfig(config=self.config),
            requests=[speech.StreamingRecognizeRequest(
                audio_content=stream
            )]
        )

        transcribe_result = TranscribeResult(text="")
        for response in responses:
            response: speech.StreamingRecognizeResponse = response
            logger.info("[Speech-to-Text] response: {}".format(
                json.dumps(
                    speech.StreamingRecognizeResponse.to_dict(response),
                    ensure_ascii=False,
                    indent=2
                )
            ))
            for result in response.results:
                result: speech.StreamingRecognitionResult = result
                # 最も確度が高い結果のみを採用する
                alternative: speech.SpeechRecognitionAlternative = result.alternatives[0]
                transcribe_result.text += alternative.transcript
        else:
            logger.info("[Speech-to-Text] no response returned")

        return transcribe_result

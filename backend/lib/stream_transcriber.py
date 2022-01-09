#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from enum import Enum
from typing import Iterable

from pydantic import BaseModel

from google.cloud import speech
from google.protobuf import json_format
from google.oauth2.service_account import Credentials


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

        responses: Iterable[speech.StreamingRecognizeResponse] = self.client.streaming_recognize(
            config=speech.StreamingRecognitionConfig(config=self.config),
            requests=[speech.StreamingRecognizeRequest(
                audio_content=stream
            )]
        )

        logger.info("[Speech-to-Text] responses: {}".format(
            json_format.MessageToJson(responses)
        ))
        transcribe_result = TranscribeResult(text="")
        for response in responses:
            for result in response.results:
                result: speech.StreamingRecognitionResult = result
                # 最も確度が高い結果のみを採用する
                alternative: speech.SpeechRecognitionAlternative = result.alternatives[0]
                logger.info("transcript: {}".format(alternative.transcript))
                transcribe_result.text += alternative.transcript

        return transcribe_result

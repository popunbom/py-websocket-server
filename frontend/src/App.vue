<template>
<h1>websocket-client</h1>
<hr>
<div class="send-message">
  <input type="text" v-model="inputText" @keydown.enter="handleSendText">
  <button @click="handleSendText">send</button>
</div>
<hr>
<AudioRecorder @ready-audio="handleReadyAudio"/>
<hr>
<div class="messages">
  <div class="message" v-for="(message, i) in messages" :key="i">
    {{ message.timestampToString() }} : {{ message.text() }}
  </div>
</div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { Message, isMessage } from "./entities/Message";
import AudioRecorder from "./components/AudioRecorder.vue";

const messages = ref<Message[]>([])
const inputText = ref<string>("")

// WebSocket コネクションの作成
const ws = new WebSocket(`ws://localhost:${import.meta.env.VITE_WS_PORT}/ws`)
ws.addEventListener("open", () => console.log("WebSocket: connect open"))
ws.addEventListener("message", (e) => {
  const message = JSON.parse(e.data)
  if (isMessage(message)) {
    messages.value = [
      new Message(message.body, message.timestamp), 
      ...messages.value
    ]
  } else {
    console.error("invalid message type")
    console.error(message)
  }
})

// テキストベースでメッセージ送信
const handleSendText = () => {
  const message = JSON.stringify(Message.fromPlainText(inputText.value))
  console.log(`message: ${message}`)
  ws.send(message)
}

// 音声ベースでメッセージ送信
const handleReadyAudio = (dataUrl: string) => {
  console.log(`dataUrl: ${dataUrl}`)
  
  const message = JSON.stringify(Message.fromVoiceDataURL(dataUrl))
  console.log(`message: ${message}`)
  ws.send(message)
}

</script>

<style>
.message {
  margin: 4px;
  padding: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
}
.send-message > * {
  margin: 4px;
}
</style>

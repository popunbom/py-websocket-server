<template>
<h1>websocket-client</h1>
<hr>
<div class="send-message">
  <input type="text" v-model="inputText" @keydown.enter="handleClickSend">
  <button @click="handleClickSend">send</button>
</div>
<hr>
<div class="messages">
  <div class="message" v-for="(message, i) in messages" :key="i">
    {{timestampToString(message.timestamp)}} : {{message.body}}
  </div>
</div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { Message, isMessage } from "./entities/Message";

const messages = ref<Message[]>([])

const inputText = ref<string>("")

const timestampToString = (timestamp: string): string => {
  const d = (new Date(Date.parse(timestamp)))
  d.setHours(d.getHours())
  return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`
}

const ws = new WebSocket(`ws://localhost:${import.meta.env.VITE_WS_PORT}/ws`)
ws.addEventListener("open", () => console.log("WebSocket: connect open"))
ws.addEventListener("message", (e) => {
  const message = JSON.parse(e.data)
  if (isMessage(message)) {
    messages.value.push(message)
  } else {
    console.error("invalid message type")
    console.error(message)
  }
})

const handleClickSend = () => ws.send(
  JSON.stringify({
    body: inputText.value,
    timestamp: (new Date()).toISOString(),
  })
)


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

<template>
  <h3>audio-recorder</h3>
  <div class="toolbar">
    <button @click="handleClick">
      {{ (isRecording) ? "stop" : "start" }}
    </button>
    <span class="status">{{ recordingState }}</span>
  </div>
</template>
<script setup lang="ts">
import RecordRTC, { StereoAudioRecorder } from "recordrtc";
import { computed, ref } from "vue";

let recorder: RecordRTC

const TIME_SLICE_MS = 5000 // 5 sec

const blobToDataURL = (blob: Blob): Promise<string> => {
  return new Promise<string>(
    (resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target?.result as string)
      reader.onerror = (e) => reject(e)
      reader.onabort = (e) => reject(e)
      reader.readAsDataURL(blob)
    }
  )
}

const emit = defineEmits<{
  (e: "readyAudio", dataUrl: string): void,
}>()

const recordingState = ref<string>("undefined")

// MediaDevice を取得
navigator.mediaDevices.getUserMedia({video: false, audio: true})
  .then(stream => {
    recorder = new RecordRTC(stream,
      {
        type: "audio",
        recorderType: StereoAudioRecorder,
        // WAV / mono / 16 kHz / 64 kbps
        mimeType: "audio/wav",
        bitsPerSecond: 64000, // 64 kbps (not working on WAV)
        desiredSampRate: 16000, // 16 kHz
        numberOfAudioChannels: 1, // mono
        timeSlice: TIME_SLICE_MS,
        // event handlers
        ondataavailable: (blob) => 
          blobToDataURL(blob)
          .then((dataUrl: string) => emit("readyAudio", dataUrl))
      }
    )
  })
  .catch(e => console.error(e))

const isRecording = computed<boolean>(() => recordingState.value === "recording")
const handleClick = () => {
  if (isRecording.value) {
    recorder.stopRecording()
  } else {
    if (recordingState.value !== "undefined") {
      recorder.destroy()
    }
    recorder.startRecording()
  }
  recordingState.value = recorder.getState()
}

</script>
<style scoped>
.toolbar > * {
  margin: 4px;
}
</style>

<template>
  <h3>audio-recorder</h3>
  <div class="toolbar">
    <span>
      Status: 
      <span v-bind:class="{status: true, speaking: isSpeaking}">
        {{ isSpeaking ? "SPEAKING" : "SILENT" }}
      </span>
    </span>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from "vue";

import hark from "hark";
import RecordRTC, { StereoAudioRecorder } from "recordrtc";


const TIME_SLICE_MS = 100 // 100 ms
const PRESERVED_BUFFER = 5
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

let recorder: RecordRTC
let speechEvent: hark.Harker

let recordingData: Blob[] = []

const emit = defineEmits<{
  (e: "readyAudio", dataUrl: string): void,
}>()
const isSpeaking = ref<boolean>(false)

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
        ondataavailable: (blob) => {
          if (!isSpeaking.value && recordingData.length >= PRESERVED_BUFFER) {
            recordingData.splice(0)
          }
          recordingData.push(blob)
          console.log(`recordingData(length=${recordingData.length})`)
        }
      }
    )
    
    speechEvent = hark(stream, {
      interval: 10, // 10 ms
      threshold: -60, // -60 dB
    })
    speechEvent.on("speaking", () => {
      console.log("speechEvent: speaking")
      isSpeaking.value = true
    })
    speechEvent.on("stopped_speaking", () => {
      console.log("speechEvent: stopped_speaking")
      isSpeaking.value = false
      blobToDataURL(
        recordingData.reduce(
          (concat, blob) => concat = new Blob([concat, blob]),
          new Blob()
        )
      ).then(
        (dataUrl: string) => emit("readyAudio", dataUrl)
      )
    })

    recorder.startRecording()
  })
  .catch(e => console.error(e))

</script>
<style scoped>
.toolbar > * {
  margin: 4px;
}
.status {
  padding: 4px 8px;
  
  background-color: blue;
  color: white;
}
.status.speaking {
  background-color: crimson;
  color: white;
  font-weight: bold;
}
</style>

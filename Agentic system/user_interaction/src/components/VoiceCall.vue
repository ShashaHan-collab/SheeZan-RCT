<script setup>
import { onBeforeUnmount, ref } from "vue";
import { toast } from "../utils/ui.js";

const props = defineProps({
  userId: { type: String, required: true },
  sessionId: { type: String, required: true },
});
const emit = defineEmits(["exit"]);

const VAD_RMS = 0.02;
const VAD_SILENCE_MS = 1000;

const state = ref("Calling…");
const caption = ref("");
const speaking = ref(false);

let ws = null;
let audioCtx = null;
let processor = null;
let micStream = null;
let micSpeaking = false;
let silenceSince = null;
let playing = false;
let audioQueue = [];
let nextStart = 0;
let currentSource = null;
let liveText = "";
let stopped = false;

const send = (data) => { if (ws && ws.readyState === 1) ws.send(data); };
const sendJson = (obj) => send(JSON.stringify(obj));

function playNext() {
  if (playing || !audioQueue.length) return;
  const buffer = audioQueue.shift();
  const src = audioCtx.createBufferSource();
  src.buffer = buffer;
  src.connect(audioCtx.destination);
  const startAt = Math.max(audioCtx.currentTime + 0.02, nextStart);
  src.start(startAt);
  nextStart = startAt + buffer.duration;
  currentSource = src;
  playing = true;
  src.onended = () => { playing = false; if (audioQueue.length) playNext(); };
}

function queueAudio(arrayBuffer) {
  if (!audioCtx) return;
  const int16 = new Int16Array(arrayBuffer);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;
  const buffer = audioCtx.createBuffer(1, float32.length, 24000);
  buffer.copyToChannel(float32, 0);
  audioQueue.push(buffer);
  playNext();
}

function stopAudio() {
  if (currentSource) { try { currentSource.stop(); } catch { /* done */ } }
  currentSource = null;
  audioQueue = [];
  playing = false;
}

function downsampleAndSend(input, rate) {
  const ratio = rate / 16000;
  const len = Math.max(1, Math.round(input.length / ratio));
  const out = new Int16Array(len);
  let offset = 0;
  for (let i = 0; i < len; i++) {
    const end = Math.min(Math.round((i + 1) * ratio), input.length);
    let sum = 0, count = 0;
    for (let j = offset; j < end; j++) { sum += input[j]; count++; }
    offset = end;
    const s = Math.max(-1, Math.min(1, count ? sum / count : 0));
    out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  send(out.buffer);
}

function handleVAD(chunk) {
  let sum = 0;
  for (let i = 0; i < chunk.length; i++) sum += chunk[i] * chunk[i];
  const rms = Math.sqrt(sum / chunk.length);
  if (rms > VAD_RMS) {
    if (!micSpeaking) {
      micSpeaking = true;
      sendJson({ type: "vad_start" });
      state.value = "I'm listening…";
      if (playing) interrupt();
    }
    silenceSince = null;
  } else if (micSpeaking) {
    if (!silenceSince) silenceSince = Date.now();
    if (Date.now() - silenceSince > VAD_SILENCE_MS) {
      micSpeaking = false;
      silenceSince = null;
      sendJson({ type: "vad_end" });
      state.value = "Answering…";
    }
  }
}

async function initAudio() {
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const source = audioCtx.createMediaStreamSource(micStream);
  processor = audioCtx.createScriptProcessor(4096, 1, 1);
  source.connect(processor);
  processor.connect(audioCtx.destination);
  processor.onaudioprocess = (e) => {
    if (stopped || !ws || ws.readyState !== 1) return;
    const chunk = e.inputBuffer.getChannelData(0);
    handleVAD(chunk);
    downsampleAndSend(chunk, audioCtx.sampleRate);
  };
  await audioCtx.resume();
}

function interrupt() {
  stopAudio();
  liveText = "";
  sendJson({ type: "interrupt" });
}

function onMessage(event) {
  if (typeof event.data !== "string") { queueAudio(event.data); return; }
  const msg = JSON.parse(event.data);
  if (msg.type === "asr_partial") { liveText = msg.text; caption.value = `You: ${liveText}`; }
  else if (msg.type === "asr_final") { liveText = msg.text; caption.value = `You said: ${liveText}`; }
  else if (msg.type === "llm_delta" || msg.type === "llm_done") {
    state.value = "Speaking…";
    speaking.value = true;
  } else if (msg.type === "audio_interrupt") { stopAudio(); }
  else if (msg.type === "voice_mode_exit") {
    caption.value = "This step needs text — back to the chat!";
    setTimeout(hangUp, 900);
    toast("Let's continue this step in text mode");
  }
}

function hangUp() {
  if (stopped) return;
  stopped = true;
  try { ws && ws.close(); } catch { /* ignore */ }
  try { processor && processor.disconnect(); } catch { /* ignore */ }
  try { micStream && micStream.getTracks().forEach((t) => t.stop()); } catch { /* ignore */ }
  try { audioCtx && audioCtx.close(); } catch { /* ignore */ }
  stopAudio();
  emit("exit");
}

ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
ws.binaryType = "arraybuffer";
ws.onopen = async () => {
  sendJson({ type: "init", user_id: props.userId, session_id: props.sessionId });
  state.value = "Connected — wait a moment";
  try { await initAudio(); } catch (err) {
    toast("Microphone unavailable: " + err.message, true);
    hangUp();
  }
};
ws.onmessage = onMessage;
ws.onclose = () => { if (!stopped) hangUp(); };
ws.onerror = () => { if (!stopped) toast("Voice connection lost", true); };

onBeforeUnmount(hangUp);
</script>

<template>
  <div class="voice-overlay">
    <div class="vo-ring inner"></div>
    <div class="vo-ring glow" :class="{ quiet: !speaking }"></div>
    <div class="vo-avatar"><img src="/companion.svg" alt="Companion"></div>
    <div class="vo-state">{{ state }}</div>
    <div class="vo-caption">{{ caption }}</div>
    <div class="vo-actions">
      <button class="vo-btn solid" @click="interrupt">Interrupt</button>
      <button class="vo-btn ghost" @click="hangUp">Leave</button>
    </div>
  </div>
</template>

<style scoped>
.voice-overlay {
  position: fixed; inset: 0; z-index: 100;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 16px; padding: 30px; text-align: center;
  background: linear-gradient(120deg, rgba(90,120,255,.25), rgba(180,90,255,.25), rgba(90,220,200,.25));
  background-size: 200% 200%;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  animation: bgFlow 12s ease-in-out infinite;
  color: #fff;
}
@keyframes bgFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
</style>

<script setup>
import { onBeforeUnmount, ref } from "vue";
import { confirmDialog } from "../utils/ui.js";

const props = defineProps({
  userId: { type: String, required: true },
  sessionId: { type: String, required: true },
  enabled: { type: Boolean, default: true },
});

const alertShown = ref(false);

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

let ws = null;
let stopped = false;
let reconnectTimer = null;

function connect() {
  if (stopped || !props.enabled) return;
  ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws2`);
  ws.onopen = () => ws.send(JSON.stringify({ type: "init", user_id: props.userId, session_id: props.sessionId }));
  ws.onmessage = (event) => {
    let data;
    try { data = JSON.parse(event.data); } catch { return; }
    if (data.type === "crisis_alert" && !alertShown.value) {
      alertShown.value = true;
      const body = escapeHtml(data.body || "").replace(/\n\s*/g, "<br>");
      confirmDialog({
        title: escapeHtml(data.title || "Safety first"),
        html: `<div class="crisis-box">${body}</div>`,
        actions: [{ label: "I understand", value: true, primary: true }],
      });
    }
  };
  ws.onclose = () => {
    ws = null;
    if (!stopped) reconnectTimer = setTimeout(connect, 3000);
  };
}

function stop() {
  stopped = true;
  clearTimeout(reconnectTimer);
  if (ws) ws.close();
}

connect();
onBeforeUnmount(stop);
</script>

<template>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import ChatMessage from "../components/ChatMessage.vue";
import VoiceCall from "../components/VoiceCall.vue";
import CrisisWatcher from "../components/CrisisWatcher.vue";
import { post, ssePost, SIGNAL } from "../utils/api.js";
import { getIdentity } from "../utils/store.js";
import { toast, confirmDialog } from "../utils/ui.js";

const router = useRouter();
// Matches the trainer's fixed 1-10 rating question (backend RATING_SCALE).
const RATING_RE = /(?:^|\D)1\s+2\s+3\s+4\s+5\s+6\s+7\s+8\s+9\s+10(?:\D|$)/;

const messages = ref([]);
const sessionId = ref(null);
const userId = getIdentity().user_id;
const busy = ref(false);
const finished = ref(false);
const text = ref("");
const scrollBox = ref(null);
const voiceOpen = ref(false);
const ratingVisible = ref(false);
const ratingValue = ref(5);
const taRef = ref(null);
const finishLabel = ref("Finish for today");

function push(m) { messages.value.push(m); }
function scrollDown() {
  nextTick(() => {
    const el = scrollBox.value;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  });
}

async function openSession() {
  try {
    const res = await post("/api/create_session", { user_id: userId });
    sessionId.value = res.session_id;
    if (res.messages) {
      for (const m of res.messages) push({ ...m, streaming: false });
    } else if (res.prologue) {
      push({ role: "assistant", content: res.prologue, events: [], streaming: false });
    }
    finished.value = messages.value.some((m) => (m.events || []).includes(SIGNAL.waitForCheckin));
    maybeShowRating();
  } catch (err) {
    toast(err.message, true);
    router.push("/home");
  }
}

async function refreshFromServer() {
  try {
    const { messages: list } = await post("/api/get_session", { session_id: sessionId.value });
    messages.value = list.map((m) => ({ ...m, streaming: false }));
    finished.value = list.some((m) => (m.events || []).includes(SIGNAL.waitForCheckin));
    ratingVisible.value = false;
    maybeShowRating();
    scrollDown();
  } catch { /* keep current view */ }
}

function sendMsg(raw, command, module) {
  const query = String(raw).trim();
  if (!query || busy.value || finished.value) return;
  busy.value = true;
  retireWidgets();
  push({ role: "user", content: query, events: [], streaming: false });
  push({ role: "assistant", content: "", events: [], streaming: true });
  scrollDown();

  const body = { session_id: sessionId.value, query };
  if (command) body.command = command;
  if (module) body.module = module;
  let full = "";
  ssePost("/api/chat", body, (soFar) => {
    full = soFar;
    const last = messages.value[messages.value.length - 1];
    if (last && last.streaming) last.content = full;
    scrollDown();
  })
    .then(async () => {
      messages.value[messages.value.length - 1].streaming = false;
      await refreshFromServer();   // stored copy carries the structured events
      const last = messages.value[messages.value.length - 1];
      const evs = (last && last.events) || [];
      if (evs.includes(SIGNAL.getSnapshot) || evs.includes(SIGNAL.getAdvice)) {
        await runFlow(evs.includes(SIGNAL.getSnapshot) ? "snapshot" : "advice");
      } else {
        maybeShowRating();
      }
      scrollDown();
    })
    .catch(async (err) => {
      messages.value.pop();
      toast(`${err.message} — please send your message again`, true);
      await refreshFromServer();
    })
    .finally(() => { busy.value = false; });
}

function retireWidgets() {
  messages.value.forEach((m) => { if (m.events?.length) m.widgetDone = true; });
}

function onWidgetSend({ text, command, module }) { sendMsg(text, command, module); }

async function runFlow(kind) {
  busy.value = true;
  try {
    await ssePost(`/api/get_${kind}`, { session_id: sessionId.value, query: "" }, () => {});
    await refreshFromServer();
  } catch (err) {
    toast(err.message, true);
  } finally {
    busy.value = false;
  }
}

function maybeShowRating(content) {
  const c = content ?? messages.value[messages.value.length - 1]?.content ?? "";
  ratingVisible.value = !finished.value && !busy.value && RATING_RE.test(c);
}

function sendRating() {
  ratingVisible.value = false;
  sendMsg(String(ratingValue.value));
}

async function finalize() {
  const answer = await confirmDialog({
    title: "Before we close…",
    paragraphs: ["Do you think you will try one of the small steps from our plan?"],
    actions: [
      { label: "Yes, I'll try", value: "yes", primary: true },
      { label: "Not for now", value: "no" },
    ],
  });
  if (!answer) return;
  finishLabel.value = "Saving your memory…";
  try {
    const res = await post("/api/finish", { session_id: sessionId.value, query: answer });
    push({ role: "assistant", content: res.epilogue, events: [], streaming: false });
    scrollDown();
    finishLabel.value = "Back to my home";
    finishAction.value = () => router.push("/home");
  } catch (err) {
    toast(err.message, true);
    finishLabel.value = "Finish for today";
  }
}
const finishAction = ref(() => finalize());
function onFinishClick() { finishAction.value(); }

function openVoice() {
  if (finished.value) return;
  const pending = messages.value.some((m) => !m.widgetDone && m.events?.length);
  if (pending) { toast("Please finish the current step in text mode first"); return; }
  voiceOpen.value = true;
}
async function onVoiceExit() {
  voiceOpen.value = false;
  await refreshFromServer();
}

function submit() {
  const t = text.value.trim();
  if (!t) return;
  text.value = "";
  sendMsg(t);
}

function grow() {
  const el = taRef.value;
  if (!el) return;
  el.style.height = "auto";
  el.style.height = `${Math.min(el.scrollHeight, 96)}px`;
}

onMounted(() => {
  document.body.style.overflow = "hidden";
  openSession();
});
onBeforeUnmount(() => {
  document.body.style.overflow = "";
  voiceOpen.value = false;
});
</script>

<template>
  <div class="chat-shell">
    <header class="topbar">
      <button class="icon-btn" title="Back to home" @click="router.push('/home')">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1>Companion</h1>
    </header>

    <main ref="scrollBox" id="messages">
      <ChatMessage v-for="(m, i) in messages" :key="i" :message="m" @send="onWidgetSend" />
    </main>

    <div v-if="ratingVisible" class="rating-wrap">
      <div class="rating-caption">
        <span>1  at ease</span><span>10  the worst</span>
      </div>
      <input v-model.number="ratingValue" class="rating-range" type="range" min="1" max="10" step="1">
      <button class="rating-ok" @click="sendRating">Confirm</button>
    </div>

    <div v-if="!finished" id="chatInputBar">
      <button class="voice-btn" title="Voice call" @click="openVoice">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="9" y="3" width="6" height="11" rx="3"/>
          <path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>
        </svg>
      </button>
      <textarea ref="taRef" v-model="text" rows="1" placeholder="Say something…"
                @input="grow" @keydown.enter.exact.prevent="submit"></textarea>
      <button class="send" @click="submit">Send</button>
    </div>
    <div v-if="!finished" class="privacy-note">
      Private — only you and this demo server can read your conversation.
    </div>

    <div v-if="finished" class="checkin-wrapper">
      <button class="checkin-btn" @click="onFinishClick">{{ finishLabel }}</button>
    </div>

    <VoiceCall v-if="voiceOpen" :user-id="userId" :session-id="sessionId" @exit="onVoiceExit" />
    <CrisisWatcher v-if="sessionId && !finished" :user-id="userId" :session-id="sessionId" />
  </div>
</template>

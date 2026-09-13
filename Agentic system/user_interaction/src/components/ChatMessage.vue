<script setup>
import { ref, watch } from "vue";
import { renderMarkdown } from "../utils/markdown.js";

const props = defineProps({
  message: { type: Object, required: true },
});
const emit = defineEmits(["send"]);

const DOMAINS = ["School", "Family", "Friends", "Self"];
// Module keys must match TRAINING_MODULES in the backend.
const MODULES = {
  Cognitive_Restructuring: "Cognitive Restructuring — untangle a stuck thought",
  Episodic_Future_Thinking: "Episodic Future Thinking — find your reasons to change",
};
const REFLECTION = {
  choices: [
    "A. Realising I have thoughts I didn't choose",
    "B. Finding out those thoughts can be questioned",
    "C. Learning how to rebalance one myself",
  ],
};

const html = () => renderMarkdown(props.message.content);
const isUser = () => props.message.role === "user";
const events = () => props.message.events || [];
const hasEvent = (type) => events().some((e) => e.type === type);
const eventPayload = (type, key) => {
  const e = events().find((x) => x.type === type);
  return e ? e[key] : "";
};
const isTyping = () => props.message.streaming && !props.message.content;

const answered = ref(false);
const picked = ref([]);
watch(() => props.message.widgetDone, (done) => { if (done) answered.value = true; });

function toggle(d) {
  const i = picked.value.indexOf(d);
  i >= 0 ? picked.value.splice(i, 1) : picked.value.push(d);
}

function send(text, command, module) {
  answered.value = true;
  emit("send", { text, command, module });
}
</script>

<template>
  <div class="bubble-wrap" :class="isUser() ? 'me' : 'ai'">
    <div class="bubble-line">
      <div v-if="isUser()" class="avatar placeholder">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="8" r="4"/><path d="M4 20c1.8-3.8 4.6-5.5 8-5.5s6.2 1.7 8 5.5"/>
        </svg>
      </div>
      <img v-else class="avatar" src="/companion.svg" alt="Companion">
      <div class="bubble-col">
        <div class="bubble" v-html="html()"></div>
        <div v-if="isTyping()" class="typing"><i></i><i></i><i></i></div>
      </div>
    </div>

    <div v-if="!isUser()" class="widgets">
      <template v-if="hasEvent('snapshot') && !answered">
        <div class="note">
          Want to understand any of these areas a bit more? Pick one or more —
          or keep talking about anything.
        </div>
        <button v-for="d in DOMAINS" :key="d" class="option"
                :class="{ sel: picked.includes(d) }"
                @click="toggle(d)">{{ d }}</button>
        <button class="primary" :disabled="!picked.length"
                @click="send(picked.join(', '), 'get_analysis')">
          Explain this area
        </button>
      </template>

      <template v-else-if="hasEvent('advice') && !answered">
        <div class="note">Beyond talking, I prepared small practical steps for you.</div>
        <button class="option" @click="send('Let\'s start a training session', 'offer_train')">
          Start a training session
        </button>
        <button class="mini-btn" @click="send('Not today — wrap up here', 'skip_train')">
          Not today — wrap up here
        </button>
      </template>

      <template v-else-if="hasEvent('ask_train') && !answered">
        <div class="note">
          I recommend the {{ eventPayload('ask_train', 'module').replace(/_/g, ' ') }}
          training today. You can also pick the other one.
        </div>
        <button v-for="(label, key) in MODULES" :key="key" class="option"
                @click="send(`Let's go with ${key.replace(/_/g, ' ')}`, 'start_train', key)">
          <span>{{ label }}</span>
          <span v-if="key === eventPayload('ask_train', 'module')" class="sub rec">
            Recommended for today
          </span>
        </button>
        <button class="mini-btn" @click="answered = true">Not now — I'll just keep talking</button>
      </template>

      <template v-else-if="hasEvent('cognitive_select') && !answered">
        <button v-for="c in REFLECTION.choices" :key="c" class="option"
                @click="send(c)">{{ c }}</button>
      </template>
    </div>
  </div>
</template>

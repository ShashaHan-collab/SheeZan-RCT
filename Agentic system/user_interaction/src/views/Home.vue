<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { post } from "../utils/api.js";
import { getIdentity, clearIdentity } from "../utils/store.js";
import { toast, fmtDate } from "../utils/ui.js";

const router = useRouter();
const overview = ref(null);
const busy = ref(true);

onMounted(async () => {
  try {
    overview.value = await post("/api/overview", { user_id: getIdentity().user_id });
  } catch (err) {
    clearIdentity();
    router.push("/");
    toast(err.message, true);
  } finally {
    busy.value = false;
  }
});

const hasActive = () =>
  overview.value?.active_session && !overview.value.active_session.finished;

function goChat() {
  router.push("/chat");
}

function signOut() {
  clearIdentity();
  router.push("/");
}
</script>

<template>
  <div class="page page-home">
    <div class="home-pad" v-if="overview">
      <div class="home-title">
        <h2>Well-being companion</h2>
        <p>A private space to check in</p>
      </div>

      <div class="home-card">
        <h3>Hi again</h3>
        <div class="sub">
          <template v-if="hasActive()">
            You have an open conversation — pick it up where we left off.
          </template>
          <template v-else-if="overview.sessions.length">
            We have talked {{ overview.sessions.length }}
            {{ overview.sessions.length === 1 ? "time" : "times" }} — I remember
            you. Ready for a new conversation?
          </template>
          <template v-else>
            This is your first visit here — shall we have a chat?
          </template>
        </div>
      </div>

      <button class="primary big-cta" @click="goChat">
        {{ hasActive() ? "Continue today's conversation" : "Start a new conversation" }}
      </button>

      <template v-if="overview.sessions.length">
        <div class="section-title">
          <span>Memories</span>
        </div>
        <p class="small muted" style="margin-bottom:10px">
          What your companion remembers from earlier conversations — it reads this
          when you start a new one.
        </p>

        <div class="session-list">
          <div v-for="s in overview.sessions" :key="s.session_id" class="session-item">
            <div class="head">
              <span class="small muted">{{ fmtDate(s.finished_at) }}</span>
              <span v-if="s.module" class="tag">{{ s.module.replace(/_/g, " ") }}</span>
              <span class="spacer"></span>
            </div>
            <p v-if="s.preview">{{ s.preview }}</p>

            <template v-if="s.digest && (s.digest.current_state || s.digest.concerns?.length || s.digest.agreed_plan || s.digest.strengths)">
              <details class="accordion">
                <summary>Show memory</summary>
                <div class="accordion-body">
                  <div v-if="s.digest.current_state" class="kv">
                    <b>How they were</b><span>{{ s.digest.current_state }}</span>
                  </div>
                  <div v-if="s.digest.concerns?.length" class="kv">
                    <b>Concerns</b><span>{{ s.digest.concerns.join("  ·  ") }}</span>
                  </div>
                  <div v-if="s.digest.agreed_plan" class="kv">
                    <b>Agreed plan</b><span>{{ s.digest.agreed_plan }}</span>
                  </div>
                  <div v-if="s.digest.strengths" class="kv">
                    <b>Strengths</b><span>{{ s.digest.strengths }}</span>
                  </div>
                </div>
              </details>
            </template>
          </div>
        </div>
      </template>

      <div class="home-card account-line">
        <span>Your unlock code: <b>{{ overview.code }}</b></span>
        <button class="mini-btn" @click="signOut">Forget this device and sign out</button>
      </div>
    </div>

    <div v-else-if="busy" class="home-pad muted">Loading…</div>
  </div>
</template>

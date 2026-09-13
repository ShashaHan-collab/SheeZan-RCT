<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import contactIcon from "../assets/icon-contact.svg?raw";
import { post } from "../utils/api.js";
import { setIdentity } from "../utils/store.js";
import { toast } from "../utils/ui.js";

const router = useRouter();
const code = ref("");
const busy = ref(false);

function onInput() {
  code.value = code.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 5);
}

async function signIn() {
  if (code.value.length !== 5) { toast("The code has 5 letters or digits", true); return; }
  busy.value = true;
  try {
    const res = await post("/api/login", { code: code.value });
    setIdentity(res.user_id, res.code);
    router.push("/home");
  } catch (err) {
    toast(err.message, true);
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="page page-login">
    <div class="login-hero">
      <img src="/companion.svg" alt="" width="80" height="80">
      <h2>Welcome back</h2>
      <p>Type the unlock code you received when you created your profile.</p>
    </div>

    <div class="cream-actions">
      <div class="login-field">
        <span class="field-icon" v-html="contactIcon"></span>
        <input v-model="code" @input="onInput" type="text" maxlength="5"
               autocomplete="off" placeholder="Your unlock code">
      </div>
      <button class="primary big-cta" :disabled="busy" @click="signIn">Sign in</button>
      <router-link class="ghost big-cta" to="/">Back</router-link>
    </div>
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
import { toastState, dialogState, closeDialog } from "./utils/ui.js";
</script>

<template>
  <div class="viewport">
    <RouterView />

    <div class="toast" :class="{ show: toastState.visible, bad: toastState.bad }">
      {{ toastState.message }}
    </div>

    <div class="modal-back" :class="{ show: dialogState.visible }"
         @click.self="closeDialog()">
      <div class="modal" role="dialog" aria-modal="true">
        <h3>{{ dialogState.title }}</h3>
        <div class="modal-body">
          <p v-for="(p, i) in dialogState.paragraphs" :key="i"
             :class="{ 'no-top': i > 0 }">{{ p }}</p>
          <div v-if="dialogState.html" v-html="dialogState.html"></div>
        </div>
        <div class="actions">
          <button v-for="a in dialogState.actions" :key="a.label"
                  :class="a.primary ? 'primary' : 'ghost'"
                  @click="closeDialog(a.value)">{{ a.label }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { confirmDialog } from "../utils/ui.js";

const aboutSections = [
  {
    title: "What happens here?",
    items: [
      "A friendly, private conversation — typed, or spoken on a voice call.",
      "After a few talks, a gentle mood snapshot with four areas you can open one by one (school, family, friends, self).",
      "Two short guided training sessions to build healthier thinking and habits.",
      "It remembers you across conversations and follows up on the small steps you agreed on.",
    ],
  },
  {
    title: "Privacy",
    items: [
      "Everything lives in local JSON files on the demo server (data/). Nothing is shared and there is no advertising.",
      "The unlock code you receive is the only key to your conversations — keep it safe.",
    ],
  },
  {
    title: "Safety",
    items: [
      "This is a research demonstration, not a medical service and never a substitute for real-world support.",
      "If you are struggling, please reach a trusted adult or a professional — when a conversation shows strong signs of distress, it will show you how.",
    ],
  },
];

async function showAbout() {
  const html = aboutSections
    .map((s) => `
      <div class="tips-card" style="margin-bottom:10px">
        <div class="tips-title">${s.title}</div>
        ${s.items.map((t) => `<p>${t}</p>`).join("")}
      </div>`)
    .join("");
  await confirmDialog({ title: "About this app", html, actions: [{ label: "Got it", value: true, primary: true }] });
}
</script>

<template>
  <div class="page page-welcome">
    <div class="login-hero">
      <img src="/companion.svg" alt="" width="80" height="80">
      <h2>Well-being companion</h2>
      <p>An empathic AI companion for teens — a place to figure out how
        you've been feeling, one conversation at a time.</p>
    </div>

    <div class="sheets">
      <div class="tips-card">
        <div class="tips-title">What happens here?</div>
        <ul>
          <li>A friendly, private conversation (typed, or spoken on a voice call).</li>
          <li>After a few talks, a gentle mood snapshot with four areas to explore.</li>
          <li>Two short guided training sessions for healthier thinking and habits.</li>
          <li>It remembers you across conversations and follows up.</li>
        </ul>
      </div>
      <div class="notice-amber">
        Research demonstration — not a medical service. If you are struggling,
        please reach a trusted adult or professional.
      </div>
    </div>

    <div class="cream-actions">
      <router-link class="primary big-cta" to="/register">Start — create my profile</router-link>
      <router-link class="ghost big-cta" to="/login">I already have an unlock code</router-link>
      <button class="link" @click="showAbout">About, privacy and safety</button>
    </div>
  </div>
</template>

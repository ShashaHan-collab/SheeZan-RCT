<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { post } from "../utils/api.js";
import { setIdentity } from "../utils/store.js";
import { toast, confirmDialog } from "../utils/ui.js";

const router = useRouter();

const profile = reactive({
  age: null,
  gender: "",
  education: "",
  background: "",
  live: "",
  live_with: "",
  use_phone_time: "",
  social_behavior: "",
  interests: [],
});

const labels = {
  gender: "Gender",
  education: "What grade or stage are you in?",
  background: "Where do you live?",
  live: "How do you attend school?",
  live_with: "Who do you live with most of the time?",
  use_phone_time: "Daily phone time in the last week?",
  social_behavior: "Your social-media habits lately?",
};

const selectFields = {
  education: ["Primary school", "Junior high", "Senior high / vocational", "College / university"],
  background: ["Village / town", "County seat", "Smaller city", "Mid-size city", "Big city"],
  live: [
    "Day student — home every day",
    "Boarding school — home weekly",
    "Boarding school — home monthly",
    "Boarding school — home each term",
  ],
  live_with: [
    "Parents (and other family living with them)",
    "Grandparents (parents not around)",
    "Other relatives",
    "Someone else — I'll say in the chat",
  ],
  use_phone_time: ["Under 2 hours", "2-4 hours", "4-6 hours", "6-8 hours", "Over 8 hours"],
};

const chipFields = {
  gender: ["Female", "Male", "Prefer not to say"],
  social_behavior: [
    "Mostly passive — I scroll and watch more than I post or chat",
    "Mostly active — I post, chat and reply a lot",
    "About half passive, half active",
    "I almost never open social apps",
  ],
};

const interests = ["Reading", "Sports", "Music", "Movies", "Games", "Drawing", "Photography",
  "Cooking", "Dancing", "Crafting", "Pets", "Nature", "Science", "Tech",
  "Fashion", "Fitness", "Biking", "Coffee", "Writing", "Collecting"];

function toggle(list, item) {
  const i = list.indexOf(item);
  i >= 0 ? list.splice(i, 1) : list.push(item);
}

async function submit() {
  const required = ["gender", "education", "background", "live", "live_with",
    "use_phone_time", "social_behavior"];
  if (profile.age == null || profile.age < 10 || profile.age > 19) {
    toast("Please enter an age between 10 and 19", true);
    return;
  }
  if (required.some((k) => !profile[k])) {
    toast("Please answer all the questions", true);
    return;
  }
  try {
    const res = await post("/api/register", { profile });
    setIdentity(res.user_id, res.code);
    await confirmDialog({
      title: "You're in!",
      paragraphs: [
        "This is your personal unlock code. Write it down or keep it somewhere safe — you will use it to open your conversations on this or any other device.",
      ],
      html: `<div class="code-chip">${res.code}</div>`,
      actions: [{ label: "Start chatting", value: true, primary: true }],
    });
    router.push("/chat");
  } catch (err) {
    toast(err.message, true);
  }
}
</script>

<template>
  <div class="page page-register">
    <div class="register-head">
      <h2>Nice to meet you!</h2>
      <p>A few quick questions so your companion can help in the right way.</p>
    </div>

    <div class="register-card">
      <div class="field">
        <label for="age">Your age</label>
        <input id="age" v-model.number="profile.age" type="number" min="10" max="19"
               inputmode="numeric" placeholder="Between 10 and 19">
      </div>

      <div v-for="(opts, key) in selectFields" :key="key" class="field">
        <label :for="key">{{ labels[key] }}</label>
        <select :id="key" v-model="profile[key]">
          <option value="" disabled>Please choose…</option>
          <option v-for="opt in opts" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </div>

      <div v-for="(opts, key) in chipFields" :key="key" class="field">
        <label>{{ labels[key] }}</label>
        <div class="seg">
          <button v-for="opt in opts" :key="opt" :class="{ sel: profile[key] === opt }"
                  @click="profile[key] = opt">{{ opt }}</button>
        </div>
      </div>

      <div class="field">
        <label>Pick your hobbies (optional)</label>
        <div class="chips">
          <button v-for="h in interests" :key="h"
                  :class="{ sel: profile.interests.includes(h) }"
                  @click="toggle(profile.interests, h)">{{ h }}</button>
        </div>
      </div>
    </div>

    <button class="primary big-cta" @click="submit">Create my profile</button>
    <router-link class="ghost big-cta" to="/">Back</router-link>
  </div>
</template>

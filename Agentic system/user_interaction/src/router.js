
import { createRouter, createWebHashHistory } from "vue-router";
import { getIdentity } from "./utils/store.js";

const routes = [
  { path: "/", component: () => import("./views/Welcome.vue") },
  { path: "/login", component: () => import("./views/Login.vue") },
  { path: "/register", component: () => import("./views/Register.vue") },
  { path: "/home", component: () => import("./views/Home.vue"), meta: { requiresUser: true } },
  { path: "/chat", component: () => import("./views/Chat.vue"), meta: { requiresUser: true } },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.requiresUser && !getIdentity().user_id) return "/";
  return true;
});

export default router;


const USER_KEY = "demo_user_id";
const CODE_KEY = "demo_code";

export function getIdentity() {
  return { user_id: localStorage.getItem(USER_KEY), code: localStorage.getItem(CODE_KEY) };
}

export function setIdentity(user_id, code) {
  localStorage.setItem(USER_KEY, user_id);
  localStorage.setItem(CODE_KEY, code || "");
}

export function clearIdentity() {
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(CODE_KEY);
}

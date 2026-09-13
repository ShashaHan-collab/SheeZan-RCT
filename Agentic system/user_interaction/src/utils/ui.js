
import { reactive } from "vue";

export const toastState = reactive({ visible: false, message: "", bad: false });
let toastTimer = null;

export function toast(message, bad = false) {
  toastState.message = message;
  toastState.bad = bad;
  toastState.visible = true;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastState.visible = false; }, 2600);
}

export const dialogState = reactive({
  visible: false,
  title: "",
  paragraphs: [],
  html: "",
  actions: [],
  resolve: null,
});

export function confirmDialog({ title, paragraphs = [], html = "", actions = [] }) {
  return new Promise((resolve) => {
    dialogState.title = title;
    dialogState.paragraphs = paragraphs;
    dialogState.html = html;
    dialogState.actions = actions;
    dialogState.resolve = resolve;
    dialogState.visible = true;
  });
}

export function closeDialog(value) {
  dialogState.visible = false;
  if (dialogState.resolve) dialogState.resolve(value ?? null);
  dialogState.resolve = null;
}

export function fmtDate(ts) {
  if (!ts) return "—";
  return new Date(ts * 1000).toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}


export async function post(path, body = {}) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try { detail = (await res.json()).detail || detail; } catch { /* keep default */ }
    throw new Error(detail);
  }
  return res.json();
}

export function ssePost(path, body, onChunk, signal) {
  return fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  }).then(async (res) => {
    if (!res.ok) {
      let detail = `Request failed (${res.status})`;
      try { detail = (await res.json()).detail || detail; } catch { /* ignore */ }
      throw new Error(detail);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let full = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buffer.indexOf("\n\n")) >= 0) {
        const frame = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        // SSE frames end with a blank line; only the `data:` line carries a payload.
        const line = frame.split("\n").find((l) => l.startsWith("data:"));
        if (!line) continue;
        const event = JSON.parse(line.slice(5).trim());
        if (event.error) throw new Error(event.content || "Server error");
        if (event.content) full += event.content;
        if (onChunk) onChunk(full, event);
        if (event.done) return full;
      }
    }
    return full;
  });
}

export const SIGNAL = {
  getSnapshot: "get_snapshot",
  snapshot: "snapshot",
  getAdvice: "get_advice",
  advice: "advice",
  askTrain: "ask_train",
  cognitiveSelect: "cognitive_select",
  waitForCheckin: "wait_for_checkin",
};

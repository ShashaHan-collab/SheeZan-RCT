
function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inline(text) {
  return esc(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

export function renderMarkdown(md) {
  const lines = String(md ?? "").replace(/\r/g, "").split("\n");
  let out = "";
  let list = null;
  let para = "";

  const closePara = () => {
    if (para.trim()) out += `<p>${inline(para.trim())}</p>`;
    para = "";
  };
  const closeList = () => {
    if (list) out += `</${list}>`;
    list = null;
  };

  for (const raw of lines) {
    const line = raw.trimEnd();

    const h = line.match(/^(#{1,4})\s+(.*)/);
    if (h) { closeList(); closePara(); out += `<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`; continue; }

    if (/^---+$/.test(line.trim())) { closeList(); closePara(); out += "<hr>"; continue; }

    const ul = line.match(/^\s*[-*]\s+(.*)/);
    if (ul) {
      closePara();
      if (list !== "ul") { closeList(); out += "<ul>"; list = "ul"; }
      out += `<li>${inline(ul[1])}</li>`;
      continue;
    }

    const ol = line.match(/^\s*(\d+)[.)]\s+(.*)/);
    if (ol) {
      closePara();
      if (list !== "ol") { closeList(); out += "<ol>"; list = "ol"; }
      out += `<li>${inline(ol[2])}</li>`;
      continue;
    }

    if (!line.trim()) { closeList(); closePara(); continue; }

    closeList();
    para += (para ? " " : "") + line;
  }
  closeList();
  closePara();
  return out;
}

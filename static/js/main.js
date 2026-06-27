// main.js — AI LeetCode Helper Agent frontend logic

const ACCENTS = {
  explain: "--c-explain",
  approach: "--c-approach",
  complexity: "--c-complexity",
  hints: "--c-hints",
  review: "--c-review",
  dryrun: "--c-dryrun",
};

let currentAction = "explain";
let currentQuestionId = null;

const $ = (id) => document.getElementById(id);

const outputBody = $("outputBody");
const statusText = $("statusText");
const runBtn = $("runBtn");

// ---------- Tiny markdown -> HTML renderer (no external deps) ----------
function renderMarkdown(md) {
  if (!md) return "";
  let html = md
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) => {
    return `<pre><code>${code}</code></pre>`;
  });

  // headings
  html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
  html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
  html = html.replace(/^# (.*$)/gim, "<h1>$1</h1>");

  // bold / italic / inline code
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // simple tables (markdown pipe tables)
  html = html.replace(/((?:^\|.*\|\n?)+)/gim, (block) => {
    const lines = block.trim().split("\n").filter(Boolean);
    if (lines.length < 2) return block;
    const rows = lines.filter((l) => !/^\|[\s:|-]+\|$/.test(l));
    let out = "<table>";
    rows.forEach((row, i) => {
      const cells = row.split("|").slice(1, -1).map((c) => c.trim());
      const tag = i === 0 ? "th" : "td";
      out += "<tr>" + cells.map((c) => `<${tag}>${c}</${tag}>`).join("") + "</tr>";
    });
    out += "</table>";
    return out;
  });

  // lists
  html = html.replace(/^\s*[-*] (.*$)/gim, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`);

  // numbered lists
  html = html.replace(/^\d+\.\s+(.*$)/gim, "<li>$1</li>");

  // paragraphs (lines not already wrapped)
  html = html
    .split("\n")
    .map((line) => {
      const trimmed = line.trim();
      if (!trimmed) return "";
      if (/^<(h1|h2|h3|ul|li|pre|table|tr)/.test(trimmed)) return line;
      return `<p>${line}</p>`;
    })
    .join("\n");

  return html;
}

function setAccent(action) {
  const varName = ACCENTS[action];
  if (varName) {
    document.documentElement.style.setProperty(
      "--accent",
      getComputedStyle(document.documentElement).getPropertyValue(varName)
    );
  }
}

function setActiveTab(action) {
  document.querySelectorAll(".tab").forEach((t) => {
    t.classList.toggle("active", t.dataset.action === action);
  });
  setAccent(action);
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    currentAction = tab.dataset.action;
    setActiveTab(currentAction);
  });
});

function showLoading() {
  outputBody.innerHTML = `<div class="empty-state"><p>Running AI agent...</p></div>`;
  statusText.textContent = "Calling Gemini...";
  runBtn.disabled = true;
}

function showError(msg) {
  outputBody.innerHTML = `<div class="empty-state"><p style="color:#e0605c;">⚠ ${msg}</p></div>`;
  statusText.textContent = "Error";
  runBtn.disabled = false;
}

function showResult(html) {
  outputBody.innerHTML = renderMarkdown(html);
  statusText.textContent = "Done";
  runBtn.disabled = false;
}

async function callApi(endpoint, payload) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

runBtn.addEventListener("click", async () => {
  const questionText = $("questionText").value.trim();
  const questionName = $("questionName").value.trim();
  const userCode = $("userCode").value.trim();
  const language = $("language").value;
  const sampleInput = $("sampleInput").value.trim();
  const tamil = $("tamilToggle").checked;

  if (!questionText) {
    showError("Please paste the problem statement first.");
    return;
  }

  showLoading();

  try {
    let data;
    switch (currentAction) {
      case "explain":
        data = await callApi("/api/explain", { question_text: questionText, question_name: questionName, tamil });
        currentQuestionId = data.question_id;
        break;
      case "approach":
        data = await callApi("/api/approach", { question_text: questionText });
        break;
      case "complexity":
        data = await callApi("/api/complexity", { question_text: questionText, code: userCode });
        break;
      case "hints":
        data = await callApi("/api/hints", { question_text: questionText });
        break;
      case "review":
        if (!userCode) { showError("Paste your code in the left panel for review."); return; }
        data = await callApi("/api/review", {
          question_text: questionText, user_code: userCode, language, question_id: currentQuestionId,
        });
        currentQuestionId = data.question_id;
        break;
      case "dryrun":
        if (!userCode) { showError("Paste your code in the left panel for a dry run."); return; }
        data = await callApi("/api/dryrun", {
          question_text: questionText, user_code: userCode, sample_input: sampleInput, language,
        });
        break;
    }
    showResult(data.result);
  } catch (err) {
    showError(err.message);
  }
});

// ---------- History / Favorites Drawer ----------
const drawer = $("drawer");
const drawerOverlay = $("drawerOverlay");
const drawerBody = $("drawerBody");
const drawerTitle = $("drawerTitle");

function openDrawer() { drawer.classList.add("open"); drawerOverlay.classList.add("open"); }
function closeDrawer() { drawer.classList.remove("open"); drawerOverlay.classList.remove("open"); }

$("drawerClose").addEventListener("click", closeDrawer);
drawerOverlay.addEventListener("click", closeDrawer);

function renderHistoryList(items, isFav) {
  if (!items.length) {
    drawerBody.innerHTML = `<p style="color:var(--muted); font-size:12px;">Nothing here yet.</p>`;
    return;
  }
  drawerBody.innerHTML = items.map((q) => `
    <div class="history-item" data-id="${q.id}">
      <div class="h-name">${q.question_name}</div>
      <div class="h-date">${new Date(q.date).toLocaleString()}</div>
      <div class="h-actions">
        <button data-act="load" data-id="${q.id}">Load</button>
        <button data-act="fav" data-id="${q.id}">${q.is_favorite ? "★ Unfavorite" : "☆ Favorite"}</button>
        <button data-act="del" data-id="${q.id}">Delete</button>
      </div>
    </div>
  `).join("");

  drawerBody.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const id = btn.dataset.id;
      const act = btn.dataset.act;
      if (act === "load") {
        const res = await fetch(`/api/question/${id}`);
        const q = await res.json();
        $("questionName").value = q.question_name;
        $("questionText").value = q.question_text;
        currentQuestionId = q.id;
        if (q.ai_response) showResult(q.ai_response);
        closeDrawer();
      } else if (act === "fav") {
        await fetch(`/api/favorite/${id}`, { method: "POST" });
        loadDrawer(isFav ? "favorites" : "history");
      } else if (act === "del") {
        await fetch(`/api/question/${id}`, { method: "DELETE" });
        loadDrawer(isFav ? "favorites" : "history");
      }
    });
  });
}

async function loadDrawer(type) {
  drawerTitle.textContent = type === "favorites" ? "★ Favorites" : "History";
  const endpoint = type === "favorites" ? "/api/favorites" : "/api/history";
  const res = await fetch(endpoint);
  const data = await res.json();
  renderHistoryList(type === "favorites" ? data.favorites : data.history, type === "favorites");
  openDrawer();
}

$("historyBtn").addEventListener("click", () => loadDrawer("history"));
$("favBtn").addEventListener("click", () => loadDrawer("favorites"));

// init accent
setAccent("explain");

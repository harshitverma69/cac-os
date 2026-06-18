import { initPipeline } from "./pipeline.js";

const LEVEL_COLORS = { B: "Basic", I: "Intermediate", A: "Advanced", D: "Infra" };

let catalog = null;
let pipeline = null;
let activeLevel = null;
let query = "";
let activeView = "agents";
let pollTimer = null;

const els = {
  grid: document.getElementById("skill-grid"),
  search: document.getElementById("search"),
  levelFilters: document.getElementById("level-filters"),
  setupSteps: document.getElementById("setup-steps"),
  setupNote: document.getElementById("setup-note"),
  copySetup: document.getElementById("copy-setup"),
  clearFilters: document.getElementById("clear-filters"),
  statVisible: document.getElementById("stat-visible"),
  statTotal: document.getElementById("stat-total"),
  dialog: document.getElementById("detail-dialog"),
  toast: document.getElementById("toast"),
  agentsPanel: document.getElementById("agents-panel"),
  livePanel: document.getElementById("live-panel"),
  liveEmpty: document.getElementById("live-empty"),
  liveContent: document.getElementById("live-content"),
  liveBadge: document.getElementById("live-badge"),
  liveStatus: document.getElementById("live-status"),
  liveTitle: document.getElementById("live-title"),
  liveHeadline: document.getElementById("live-headline"),
  liveMetrics: document.getElementById("live-metrics"),
  liveReport: document.getElementById("live-report"),
  liveHistory: document.getElementById("live-history"),
  livePoll: document.getElementById("live-poll"),
  agentIndex: document.getElementById("agent-index"),
  copyAllCommands: document.getElementById("copy-all-commands"),
  levelLegend: document.getElementById("level-legend"),
  catalogBody: document.getElementById("agent-catalog-body"),
  catalogCount: document.getElementById("catalog-count"),
  agentCatalog: document.getElementById("agent-catalog"),
  pipelinePanel: document.getElementById("pipeline-panel"),
  pipelineEmpty: document.getElementById("pipeline-empty"),
  pipelineActive: document.getElementById("pipeline-active"),
  pipelineRunId: document.getElementById("pipeline-run-id"),
  pipelineFolder: document.getElementById("pipeline-folder"),
  pipelineStepBadge: document.getElementById("pipeline-step-badge"),
  pipelineStepTitle: document.getElementById("pipeline-step-title"),
  pipelineStepCommand: document.getElementById("pipeline-step-command"),
  pipelineFinishHint: document.getElementById("pipeline-finish-hint"),
  pipelineNext: document.getElementById("pipeline-next"),
  pipelineCopy: document.getElementById("pipeline-copy"),
  pipelineOpenDetail: document.getElementById("pipeline-open-detail"),
  pipelineReset: document.getElementById("pipeline-reset"),
  pipelineSteps: document.getElementById("pipeline-steps"),
  pipelineDialog: document.getElementById("pipeline-dialog"),
  pipelineForm: document.getElementById("pipeline-form"),
  pipelinePathInput: document.getElementById("pipeline-path-input"),
  pipelineStartBtn: document.getElementById("pipeline-start-btn"),
  pipelineError: document.getElementById("pipeline-error"),
  pipelineCancelBtn: document.getElementById("pipeline-cancel-btn"),
  pipelineEmptyStart: document.getElementById("pipeline-empty-start"),
  runAllBtn: document.getElementById("run-all-btn"),
  pipelineWaitingHint: document.getElementById("pipeline-waiting-hint"),
};

async function loadCatalog() {
  const res = await fetch("data/skills.json");
  if (!res.ok) throw new Error("Could not load data/skills.json — run: make build-frontend");
  catalog = await res.json();
}

function showToast(msg = "Copied") {
  els.toast.textContent = msg;
  els.toast.hidden = false;
  setTimeout(() => {
    els.toast.hidden = true;
  }, 1600);
}

async function copyText(text) {
  await navigator.clipboard.writeText(text);
  showToast();
}

function filteredSkills() {
  return catalog.skills.filter((s) => {
    if (activeLevel && s.level_code !== activeLevel) return false;
    if (!query) return true;
    const hay = `${s.task_id} ${s.name} ${s.description} ${s.slash_command}`.toLowerCase();
    return hay.includes(query);
  });
}

function skillsByLevel(skills) {
  const groups = {};
  for (const lv of catalog.levels) {
    groups[lv.code] = skills.filter((s) => s.level_code === lv.code);
  }
  return groups;
}

function skillCardHtml(s) {
  return `
    <article class="skill-card" data-id="${s.task_id}" tabindex="0">
      <div class="id badge badge-${s.level_code}">${s.task_id} · ${s.level}</div>
      <h3>${s.name}</h3>
      <p>${s.description}</p>
      <div class="meta">
        ${s.depends_on.length ? `Depends: ${s.depends_on.join(", ")}` : "No dependencies"}
        · <code>${s.slash_command}</code>
      </div>
    </article>`;
}

function bindSkillCards(root) {
  root.querySelectorAll(".skill-card").forEach((card) => {
    const open = () => openDetail(card.dataset.id);
    card.addEventListener("click", open);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        open();
      }
    });
  });
}

function renderLevelLegend() {
  if (!els.levelLegend) return;
  els.levelLegend.innerHTML = catalog.levels
    .map((lv) => {
      const count = catalog.skills.filter((s) => s.level_code === lv.code).length;
      const names = catalog.skills
        .filter((s) => s.level_code === lv.code)
        .map((s) => s.task_id)
        .join(", ");
      return `
        <div class="legend-item">
          <span class="badge badge-${lv.code}">${lv.code} · ${lv.label}</span>
          <span class="muted">${count} agents: ${names}</span>
        </div>`;
    })
    .join("");
}

function renderAgentIndex() {
  if (!els.agentIndex) return;
  const groups = skillsByLevel(catalog.skills);
  els.agentIndex.innerHTML = catalog.levels
    .map((lv) => {
      const items = groups[lv.code] || [];
      return `
        <div class="agent-index-group">
          <div class="agent-index-heading badge badge-${lv.code}">${lv.code} · ${lv.label}</div>
          <ul>
            ${items
              .map(
                (s) => `
              <li>
                <button type="button" class="agent-index-btn" data-id="${s.task_id}" title="${s.slash_command}">
                  <strong>${s.task_id}</strong>
                  <span>${s.name}</span>
                </button>
              </li>`
              )
              .join("")}
          </ul>
        </div>`;
    })
    .join("");

  els.agentIndex.querySelectorAll(".agent-index-btn").forEach((btn) => {
    btn.addEventListener("click", () => openDetail(btn.dataset.id));
  });
}

function renderAgentCatalog() {
  if (!els.catalogBody) return;
  const items = filteredSkills();
  els.catalogBody.innerHTML = items
    .map(
      (s) => `
    <tr class="catalog-row" data-id="${s.task_id}" tabindex="0">
      <td><span class="badge badge-${s.level_code}">${s.task_id}</span></td>
      <td><strong>${s.name}</strong><br><span class="muted catalog-desc">${s.description}</span></td>
      <td>${s.level}</td>
      <td><code>${s.slash_command}</code></td>
      <td>${s.depends_on.length ? s.depends_on.join(", ") : "—"}</td>
    </tr>`
    )
    .join("");

  if (els.catalogCount) {
    els.catalogCount.textContent =
      items.length === catalog.skill_count
        ? `${catalog.skill_count} agents`
        : `${items.length} of ${catalog.skill_count} agents`;
  }

  els.catalogBody.querySelectorAll(".catalog-row").forEach((row) => {
    const open = () => openDetail(row.dataset.id);
    row.addEventListener("click", open);
    row.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        open();
      }
    });
  });
}

function renderSetup() {
  const steps = catalog.setup?.steps || [];
  els.setupSteps.innerHTML = steps.map((step) => `<li><code>${step}</code></li>`).join("");
  if (els.setupNote) {
    els.setupNote.textContent = catalog.setup?.note || "";
    els.setupNote.hidden = !catalog.setup?.note;
  }
  els.copySetup.onclick = () => copyText(steps.join("\n"));
}

function renderLevelFilters() {
  els.levelFilters.innerHTML = catalog.levels
    .map(
      (lv) =>
        `<button type="button" class="chip level-${lv.code}" data-level="${lv.code}">${lv.code} · ${lv.label}</button>`
    )
    .join("");

  els.levelFilters.querySelectorAll("[data-level]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const code = btn.dataset.level;
      activeLevel = activeLevel === code ? null : code;
      els.levelFilters.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      if (activeLevel) btn.classList.add("active");
      renderGrid();
    });
  });

  els.clearFilters.onclick = () => {
    activeLevel = null;
    query = "";
    els.search.value = "";
    els.levelFilters.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
    renderGrid();
  };
}

function renderGrid() {
  const items = filteredSkills();
  els.statVisible.textContent = String(items.length);
  els.statTotal.textContent = String(catalog.skill_count);

  const groups = skillsByLevel(items);
  if (!items.length) {
    els.grid.innerHTML = `<div class="panel muted">No agents match your search or filter.</div>`;
    renderAgentCatalog();
    return;
  }

  els.grid.innerHTML = catalog.levels
    .map((lv) => {
      const skills = groups[lv.code] || [];
      if (!skills.length) return "";
      const ids = skills.map((s) => s.task_id).join(", ");
      return `
        <section class="level-section" id="level-${lv.code}">
          <div class="level-section-header">
            <h2><span class="badge badge-${lv.code}">${lv.code}</span> ${lv.label}</h2>
            <span class="muted">${skills.length} agent${skills.length === 1 ? "" : "s"}: ${ids}</span>
          </div>
          <div class="skill-grid">
            ${skills.map((s) => skillCardHtml(s)).join("")}
          </div>
        </section>`;
    })
    .join("");

  bindSkillCards(els.grid);
  renderAgentCatalog();
}

function openDetail(taskId) {
  const s = catalog.skills.find((x) => x.task_id === taskId);
  if (!s) return;

  document.getElementById("detail-badge").className = `badge badge-${s.level_code}`;
  document.getElementById("detail-badge").textContent = `${s.task_id} · ${s.level}`;
  document.getElementById("detail-title").textContent = s.name;
  document.getElementById("detail-desc").textContent = s.description;

  const depsEl = document.getElementById("detail-deps");
  if (s.depends_on.length) {
    depsEl.innerHTML = s.depends_on
      .map((d) => `<button type="button" class="chip" data-goto="${d}">${d}</button>`)
      .join("");
    depsEl.querySelectorAll("[data-goto]").forEach((btn) => {
      btn.addEventListener("click", () => openDetail(btn.dataset.goto));
    });
  } else {
    depsEl.innerHTML = '<span class="muted">None — can run standalone</span>';
  }

  document.getElementById("detail-slash").textContent = s.slash_command;
  document.getElementById("detail-finish").textContent = s.finish_command;
  document.getElementById("detail-make").textContent = s.make_run;

  document.getElementById("detail-files").innerHTML = [
    ["Agent spec", s.agent_spec],
    ["Skill spec", s.skill_spec],
    ["Blueprint", s.blueprint],
    ["Output JSON", s.output_json],
    ["Golden reference", s.golden_json],
  ]
    .map(([label, path]) => `<li><strong>${label}:</strong> <code>${path}</code></li>`)
    .join("");

  document.getElementById("detail-steps").innerHTML = s.run_steps
    .map(
      (step) =>
        `<li><strong>${step.title}</strong><span>${step.body.replace(/`([^`]+)`/g, "<code>$1</code>")}</span></li>`
    )
    .join("");

  els.dialog.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.onclick = () => {
      const id = btn.dataset.copy;
      copyText(document.getElementById(id).textContent);
    };
  });

  els.dialog.showModal();
}

function setView(view) {
  activeView = view;
  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === view);
  });
  els.agentsPanel.classList.toggle("hidden", view !== "agents");
  els.livePanel.classList.toggle("hidden", view !== "live");
  els.pipelinePanel.classList.toggle("hidden", view !== "pipeline");
  els.search.classList.toggle("hidden", view !== "agents");
  if (view === "live") {
    refreshLive();
  }
  if (view === "pipeline") {
    pipeline?.render();
  }
}

function simpleMarkdown(md) {
  const mermaidBlocks = [];
  const withPlaceholders = md.replace(/```mermaid\s*\n([\s\S]*?)```/gi, (_, code) => {
    const idx = mermaidBlocks.length;
    mermaidBlocks.push(code.trim());
    return `@@MERMAID_${idx}@@`;
  });

  let html = withPlaceholders
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");
  html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");
  html = html.replace(/^\|(.+)\|$/gm, (line) => {
    if (/^\|[\s\-:|]+\|$/.test(line)) return "";
    const cells = line.split("|").slice(1, -1).map((c) => c.trim());
    return `<tr>${cells.map((c) => `<td>${c}</td>`).join("")}</tr>`;
  });
  html = html.replace(/((?:<tr>[\s\S]*?<\/tr>\s*)+)/g, "<table>$1</table>");
  html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
  html = html.replace(/((?:<li>[\s\S]*?<\/li>\s*)+)/g, "<ul>$1</ul>");
  html = html.replace(/\n\n/g, "<br><br>");

  mermaidBlocks.forEach((_, idx) => {
    html = html.replace(
      `@@MERMAID_${idx}@@`,
      `<div class="mermaid-diagram"><div class="mermaid" data-mermaid-idx="${idx}"></div></div>`
    );
  });

  return { html, mermaidBlocks };
}

let mermaidInitialized = false;

function initMermaid() {
  if (mermaidInitialized || !window.mermaid) return;
  window.mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    themeVariables: {
      primaryColor: "#e0f2fe",
      primaryTextColor: "#1e3a5f",
      primaryBorderColor: "#7dd3fc",
      lineColor: "#64748b",
      secondaryColor: "#fef3c7",
      tertiaryColor: "#dcfce7",
    },
    securityLevel: "loose",
    er: { useMaxWidth: true },
  });
  mermaidInitialized = true;
}

async function renderMermaidBlocks(container, blocks) {
  if (!blocks.length || !window.mermaid) return;
  initMermaid();
  const nodes = container.querySelectorAll(".mermaid");
  nodes.forEach((node, idx) => {
    node.textContent = blocks[idx] || "";
  });
  try {
    await window.mermaid.run({ nodes: [...nodes] });
  } catch (err) {
    console.warn("Mermaid render failed:", err);
    nodes.forEach((node, idx) => {
      if (!blocks[idx]) return;
      node.outerHTML = `<pre class="mermaid-fallback"><code>${blocks[idx]}</code></pre>`;
    });
  }
}

async function renderLiveEntry(entry) {
  if (!entry) {
    els.liveEmpty.classList.remove("hidden");
    els.liveContent.classList.add("hidden");
    return;
  }

  els.liveEmpty.classList.add("hidden");
  els.liveContent.classList.remove("hidden");

  const levelCode = entry.skill_id?.[0] || "B";
  els.liveBadge.className = `badge badge-${levelCode}`;
  els.liveBadge.textContent = `${entry.skill_id} · ${entry.level || LEVEL_COLORS[levelCode] || ""}`;
  els.liveStatus.textContent = entry.status_label || "DONE";
  els.liveStatus.className = `status-pill ${entry.status_tone || "neutral"}`;
  els.liveTitle.textContent = `${entry.skill_name} — run ${entry.run_id}`;
  els.liveHeadline.textContent = entry.headline || "";

  els.liveMetrics.innerHTML = (entry.metrics || [])
    .map((m) => `<div><dt>${m.label}</dt><dd>${m.value}</dd></div>`)
    .join("");

  try {
    const res = await fetch(`${entry.markdown_url}?t=${Date.now()}`);
    if (res.ok) {
      const md = await res.text();
      const { html, mermaidBlocks } = simpleMarkdown(md);
      els.liveReport.innerHTML = html;
      await renderMermaidBlocks(els.liveReport, mermaidBlocks);
    } else {
      els.liveReport.textContent = "Report markdown not found.";
    }
  } catch {
    els.liveReport.textContent = "Could not load report.";
  }
}

function renderHistory(history, selected) {
  if (!history?.length) {
    els.liveHistory.innerHTML = '<li class="muted">No history yet.</li>';
    return;
  }
  els.liveHistory.innerHTML = history
    .map(
      (item) => `
    <li>
      <button type="button" data-run="${item.run_id}" data-skill="${item.skill_id}">
        <strong>${item.skill_id}</strong> ${item.skill_name}
        <span class="muted"> · ${item.run_id} · ${item.status_label}</span>
      </button>
    </li>`
    )
    .join("");

  els.liveHistory.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const run = btn.dataset.run;
      const skill = btn.dataset.skill;
      const match = history.find((h) => h.run_id === run && h.skill_id === skill);
      if (match) await renderLiveEntry(match);
      window.history.replaceState({}, "", `?run=${run}&skill=${skill}&live=1`);
    });
  });
}

async function refreshLive() {
  try {
    const res = await fetch(`data/live.json?t=${Date.now()}`);
    if (!res.ok) {
      els.livePoll.textContent = "Waiting for first skill run…";
      return;
    }
    const live = await res.json();
    const params = new URLSearchParams(window.location.search);
    const run = params.get("run");
    const skill = params.get("skill");
    let entry = live.latest;
    if (run && skill) {
      entry =
        live.history?.find((h) => h.run_id === run && h.skill_id === skill) || entry;
    }
    await renderLiveEntry(entry);
    renderHistory(live.history, entry);
    pipeline?.onLiveUpdate(live);
    els.livePoll.textContent = entry
      ? `Updated ${entry.published_at || entry.updated_at}`
      : "Polling…";
  } catch {
    els.livePoll.textContent = "Could not load live.json";
  }
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => {
    if (activeView === "live" || activeView === "pipeline") refreshLive();
  }, 2500);
}

els.search.addEventListener("input", (e) => {
  query = e.target.value.trim().toLowerCase();
  renderGrid();
});

document.querySelectorAll(".nav-tab").forEach((tab) => {
  tab.addEventListener("click", () => setView(tab.dataset.view));
});

async function init() {
  try {
    await loadCatalog();
    renderSetup();
    renderLevelFilters();
    renderLevelLegend();
    renderAgentIndex();
    renderGrid();
    startPolling();

    pipeline = initPipeline({
      els,
      copyText,
      showToast,
      setView,
      openDetail,
    });

    if (els.copyAllCommands) {
      els.copyAllCommands.onclick = () => {
        const cmds = catalog.skills.map((s) => `${s.task_id} ${s.name}: ${s.slash_command}`).join("\n");
        copyText(cmds);
      };
    }

    const params = new URLSearchParams(window.location.search);
    if (params.get("live") === "1" || params.get("run")) {
      setView("live");
      await refreshLive();
    } else {
      setView("agents");
    }
  } catch (err) {
    els.grid.innerHTML = `<div class="panel"><strong>Error:</strong> ${err.message}</div>`;
  }
}

init();

const STORAGE_KEY = "repo-analyser-pipeline";
const API_TIMEOUT_MS = 15000;

export function initPipeline(deps) {
  const {
    els,
    copyText,
    showToast,
    setView,
    openDetail,
  } = deps;

  let state = loadState();

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (
        !parsed?.execution_order?.length ||
        !Array.isArray(parsed.skills) ||
        !parsed.repository_path
      ) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return parsed;
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  }

  function saveState() {
    if (state) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
    render();
  }

  function currentSkill() {
    if (!state?.execution_order) return null;
    const id = state.execution_order[state.current_index];
    return state.skills?.find((s) => s.task_id === id) || null;
  }

  function cursorPrompt(skill) {
    if (!skill || !state?.repository_path) return "";
    return `${skill.slash_command} @${state.repository_path}`;
  }

  function markCompleted(skillId) {
    if (!state) return;
    if (!state.completed.includes(skillId)) {
      state.completed.push(skillId);
    }
  }

  function checkLiveCompletion(live) {
    if (!state || !live?.history?.length) return;
    const pending = state.execution_order.slice(state.current_index);
    for (const skillId of pending) {
      const hit = live.history.find(
        (h) => h.run_id === state.run_id && h.skill_id === skillId
      );
      if (hit) {
        markCompleted(skillId);
        while (
          state.current_index < state.execution_order.length &&
          state.completed.includes(state.execution_order[state.current_index])
        ) {
          state.current_index += 1;
        }
      }
    }
    saveState();
  }

  async function startPipeline(repositoryPath) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

    try {
      const res = await fetch("/api/pipeline/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repository_path: repositoryPath }),
        signal: controller.signal,
      });

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        throw new Error(
          "Pipeline API not available. Start the UI with: make serve-frontend (do not open index.html directly)."
        );
      }

      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || "Could not create pipeline plan");
      }

      state = {
        run_id: data.run_id,
        repository_path: data.repository_path,
        execution_order: data.execution_order,
        skills: data.skills,
        total: data.total,
        current_index: 0,
        completed: [],
        started_at: new Date().toISOString(),
      };
      saveState();
      els.pipelineDialog?.close();
      setView("pipeline");
      showToast("Pipeline started — copy the command and run it in Cursor");
    } catch (err) {
      if (err.name === "AbortError") {
        throw new Error(
          "Server timed out. Run: cd Repo-Analyser && make serve-frontend"
        );
      }
      if (err instanceof TypeError) {
        throw new Error(
          "Cannot reach http://127.0.0.1:8765. Run: cd Repo-Analyser && make serve-frontend"
        );
      }
      throw err;
    } finally {
      clearTimeout(timeout);
    }
  }

  function render() {
    if (!els.pipelinePanel) return;

    if (!state) {
      els.pipelineEmpty?.classList.remove("hidden");
      els.pipelineActive?.classList.add("hidden");
      return;
    }

    els.pipelineEmpty?.classList.add("hidden");
    els.pipelineActive?.classList.remove("hidden");

    const skill = currentSkill();
    const total = state.total || state.execution_order.length;
    if (els.pipelineRunId) {
      els.pipelineRunId.textContent = state.run_id;
    }
    if (els.pipelineFolder) {
      els.pipelineFolder.textContent = state.repository_path;
    }
    if (els.pipelineStepBadge && skill) {
      els.pipelineStepBadge.className = `badge badge-${skill.level_code}`;
      els.pipelineStepBadge.textContent = `${skill.task_id} · ${skill.level || skill.level_code}`;
    }
    if (els.pipelineStepTitle) {
      els.pipelineStepTitle.textContent = skill ? skill.name : "All agents finished";
    }
    if (els.pipelineWaitingHint) {
      if (skill) {
        els.pipelineWaitingHint.textContent =
          "This does not run automatically — copy the command below, run it in Cursor, then click Mark done & next.";
        els.pipelineWaitingHint.classList.remove("hidden");
      } else {
        els.pipelineWaitingHint.classList.add("hidden");
      }
    }
    if (els.pipelineStepCommand) {
      els.pipelineStepCommand.textContent = skill ? cursorPrompt(skill) : "";
    }
    if (els.pipelineFinishHint) {
      els.pipelineFinishHint.textContent = skill
        ? `When done in Cursor, run: python3 -m runtime.skill_finish write --run-id ${state.run_id} --skill ${skill.task_id} --payload-file payload.json`
        : "";
    }

    if (els.pipelineNext) {
      els.pipelineNext.disabled = !skill;
      els.pipelineNext.textContent = skill
        ? state.current_index === total - 1
          ? "Mark done & finish"
          : "Mark done & next"
        : "Finished";
    }
    if (els.pipelineCopy) {
      els.pipelineCopy.disabled = !skill;
    }

    if (els.pipelineSteps) {
      els.pipelineSteps.innerHTML = state.execution_order
        .map((id, idx) => {
          const meta = state.skills.find((s) => s.task_id === id);
          let status = "pending";
          if (state.completed.includes(id)) status = "done";
          else if (idx === state.current_index) status = "current";
          return `
            <li class="pipeline-step pipeline-step-${status}" data-id="${id}">
              <span class="pipeline-step-num">${idx + 1}</span>
              <span class="pipeline-step-id">${id}</span>
              <span class="pipeline-step-name">${meta?.name || id}</span>
              <span class="pipeline-step-status">${status === "done" ? "✓" : status === "current" ? "→" : "·"}</span>
            </li>`;
        })
        .join("");

      els.pipelineSteps.querySelectorAll(".pipeline-step").forEach((row) => {
        row.addEventListener("click", () => {
          const id = row.dataset.id;
          const idx = state.execution_order.indexOf(id);
          if (idx >= 0) {
            state.current_index = idx;
            saveState();
          }
        });
      });
    }
  }

  function openFolderDialog() {
    const done = state?.completed?.length || 0;
    const total = state?.total || state?.execution_order?.length || 0;
    const inProgress = state && done < total;

    if (inProgress) {
      setView("pipeline");
      showToast("Pipeline in progress — run the current agent in Cursor");
      return;
    }

    if (els.pipelinePathInput) {
      els.pipelinePathInput.value = state?.repository_path || "";
    }
    if (els.pipelineError) {
      els.pipelineError.textContent = "";
      els.pipelineError.classList.add("hidden");
    }
    if (els.pipelineStartBtn) {
      els.pipelineStartBtn.disabled = false;
      els.pipelineStartBtn.textContent = "Start pipeline";
    }
    els.pipelineDialog?.showModal();
  }

  function bindEvents() {
    els.runAllBtn?.addEventListener("click", openFolderDialog);
    els.pipelineEmptyStart?.addEventListener("click", openFolderDialog);

    els.pipelineCancelBtn?.addEventListener("click", () => {
      els.pipelineDialog?.close();
    });

    els.pipelineForm?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const path = els.pipelinePathInput?.value?.trim();
      if (!path) return;
      try {
        els.pipelineStartBtn.disabled = true;
        els.pipelineStartBtn.textContent = "Validating…";
        if (els.pipelineError) {
          els.pipelineError.textContent = "";
          els.pipelineError.classList.add("hidden");
        }
        await startPipeline(path);
      } catch (err) {
        showToast(err.message || "Failed to start");
        if (els.pipelineError) {
          els.pipelineError.textContent = err.message || "Failed to start pipeline";
          els.pipelineError.classList.remove("hidden");
        }
      } finally {
        els.pipelineStartBtn.disabled = false;
        els.pipelineStartBtn.textContent = "Start pipeline";
      }
    });

    els.pipelineCopy?.addEventListener("click", () => {
      const skill = currentSkill();
      if (skill) copyText(cursorPrompt(skill));
    });

    els.pipelineOpenDetail?.addEventListener("click", () => {
      const skill = currentSkill();
      if (skill) openDetail(skill.task_id);
    });

    els.pipelineNext?.addEventListener("click", () => {
      const skill = currentSkill();
      if (!skill) return;
      markCompleted(skill.task_id);
      if (state.current_index < state.execution_order.length - 1) {
        state.current_index += 1;
      } else {
        state.current_index = state.execution_order.length;
      }
      saveState();
    });

    els.pipelineReset?.addEventListener("click", () => {
      if (confirm("Clear pipeline progress and pick a new folder?")) {
        state = null;
        saveState();
      }
    });
  }

  function onLiveUpdate(live) {
    checkLiveCompletion(live);
  }

  bindEvents();
  render();

  return { onLiveUpdate, render, getState: () => state };
}

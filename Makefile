.PHONY: validate list route validate-run build-skills run-skill run-pipeline test validate-dag validate-pipeline test-determinism harden install-cursor-skills export-md view-run skill-done clean-runs repolens-eval expand-agent-specs build-frontend serve-frontend help

PYTHON ?= python3
SCRIPT := scripts/repo_analyser.py
export PYTHONPATH := .

help:
	@echo "Repo-Analyser Makefile"
	@echo ""
	@echo "  make validate              Validate registry, specs, blueprints, golden examples, DAG"
	@echo "  make list                  List all 24 tasks"
	@echo "  make route INTENT=...      Compute execution plan (see task_router.md for intents)"
	@echo "  make route TASKS=B1,B2     Compute plan for specific tasks"
	@echo "  make validate-run RUN_DIR=generated_projects/my-run"
	@echo "  make export-md RUN_DIR=generated_projects/my-run  Export Markdown reports"
	@echo "  make skill-done RUN_ID=my-run SKILL=B1           Print CLI report after skill (auto)"
	@echo "  make view-run                                     Interactive run browser (manual)"
	@echo "  make clean-runs                                   Remove ephemeral run outputs"
	@echo "  make repolens-eval         Run all 24 agents against ../repolens (RepoLens bridge)"
	@echo "  make build-skills          Compile agents → .skill.md + registry + HOW_TO_RUN.md"
	@echo "  make expand-agent-specs    Expand agent specs to full procedural detail"
	@echo "  make install-cursor-skills Install all 24 skills into Cursor / menu"
	@echo "  make build-frontend        Build local agent guide UI (frontend/data/skills.json)"
	@echo "  make serve-frontend        Open local UI at http://127.0.0.1:8765 (no deploy)"
	@echo "  make run-skill SKILL=B1    Execute one skill deterministically"
	@echo "  make run-pipeline          Execute all 24 skills in DAG order"
	@echo "  make validate-dag          Validate skill dependency DAG"
	@echo "  make validate-pipeline     Validate pipeline run (RUN_ID=final_test)"
	@echo "  make test-determinism      Prove run-to-run identical skill outputs"
	@echo "  make harden                Full production check (tests + determinism)"
	@echo "  make test                  Run runtime tests with coverage"
	@echo ""
	@echo "Intents: discover, map_apis, find_tests, build_fastapi, build_node, build_rust,"
	@echo "         er_diagram, trace_flow, safe_change, polyglot_pair, dockerize, fix_bug,"
	@echo "         worktree_plan, worktree_execute, fraud_system, modernize, review_pr,"
	@echo "         perf_improve, terraform, compose_stack, ci_pipeline, kubernetes,"
	@echo "         bootstrap, observability, full_eval"

validate:
	$(PYTHON) $(SCRIPT) validate-registry

list:
	$(PYTHON) $(SCRIPT) list

route:
ifndef INTENT
ifndef TASKS
	$(error Set INTENT=... or TASKS=B1,B2,...)
endif
endif
ifdef TASKS
	$(PYTHON) $(SCRIPT) route --tasks "$(TASKS)" $(if $(RUN_ID),--run-id $(RUN_ID),)
else
	$(PYTHON) $(SCRIPT) route --intent "$(INTENT)" $(if $(RUN_ID),--run-id $(RUN_ID),)
endif

validate-run:
ifndef RUN_DIR
	$(error Set RUN_DIR=generated_projects/your-run)
endif
	$(PYTHON) $(SCRIPT) validate-run "$(RUN_DIR)"

export-md:
ifndef RUN_DIR
	$(error Set RUN_DIR=generated_projects/your-run)
endif
	$(PYTHON) $(SCRIPT) export-md "$(RUN_DIR)"

view-run:
	$(PYTHON) -m runtime.report_cli interactive

skill-done:
ifndef RUN_ID
	$(error Set RUN_ID=your-run and SKILL=B1)
endif
ifndef SKILL
	$(error Set RUN_ID=your-run and SKILL=B1)
endif
	$(PYTHON) -m runtime.skill_finish --run-id "$(RUN_ID)" --skill "$(SKILL)"

clean-runs:
	$(PYTHON) $(SCRIPT) clean-runs

skills: build-skills

build-skills:
	$(PYTHON) runtime/skill_registry_builder.py

expand-agent-specs:
	$(PYTHON) tools/expand_agent_specs.py

run-skill:
ifndef SKILL
	$(error Set SKILL=B1)
endif
	$(PYTHON) -m runtime --skill "$(SKILL)" --run-id $(or $(RUN_ID),skill-run)

run-pipeline:
	$(PYTHON) -m runtime --full-pipeline --run-id $(or $(RUN_ID),pipeline-run)

test:
	$(PYTHON) -m pytest tests/ -v --cov=runtime --cov-report=term-missing

validate-dag:
	$(PYTHON) -m runtime.skill_orchestrator --validate-dag

validate-pipeline:
ifndef RUN_ID
	$(error Set RUN_ID=final_test)
endif
	$(PYTHON) -m runtime.validate_pipeline --run-id "$(RUN_ID)" $(if $(COMPARE_RUN_ID),--compare-run-id "$(COMPARE_RUN_ID)",)

test-determinism:
	$(PYTHON) -m runtime --full-pipeline --run-id final_test
	$(PYTHON) -m runtime --full-pipeline --run-id final_test_2
	@for skill in B1 B2 B3 B4 B5 B6 I1 I2 I3 I4 I5 I6 A1 A2 A3 A4 A5 A6 D1 D2 D3 D4 D5 D6; do \
		diff -q generated_projects/final_test/$$skill/output.json generated_projects/final_test_2/$$skill/output.json || exit 1; \
	done
	@echo "OK: all 24 skill outputs are byte-identical across runs"

harden:
	rm -rf generated_projects/run-* generated_projects/final_test generated_projects/final_test_2
	$(MAKE) build-skills
	$(MAKE) validate-dag
	$(MAKE) run-pipeline RUN_ID=final_test
	$(MAKE) run-pipeline RUN_ID=final_test_2
	$(MAKE) test-determinism
	$(MAKE) validate-pipeline RUN_ID=final_test COMPARE_RUN_ID=final_test_2
	$(MAKE) test

install-cursor-skills:
	$(PYTHON) tools/install_cursor_skills.py --clean

build-frontend:
	$(PYTHON) tools/build_frontend.py

serve-frontend: build-frontend
	$(PYTHON) tools/serve_frontend.py $(if $(PORT),--port $(PORT),) $(if $(NO_OPEN),--no-open,)

REPOLENS_REPO ?= ../repolens
repolens-eval:
	PYTHONPATH=$(REPOLENS_REPO)/backend $(PYTHON) tools/repolens_eval_runner.py \
		--repo $(REPOLENS_REPO) --run-id repolens-eval

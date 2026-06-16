.PHONY: validate list route validate-run skills build-skills run-skill run-pipeline test help

PYTHON ?= python3
SCRIPT := scripts/cac_os.py
export PYTHONPATH := .

help:
	@echo "CAC-OS Makefile"
	@echo ""
	@echo "  make validate              Validate registry, specs, blueprints, golden examples, DAG"
	@echo "  make list                  List all 24 tasks"
	@echo "  make route INTENT=...      Compute execution plan (see task_router.md for intents)"
	@echo "  make route TASKS=B1,B2     Compute plan for specific tasks"
	@echo "  make validate-run RUN_DIR=generated_projects/my-run"
	@echo "  make skills                Regenerate skills/skill_registry.{json,md} (Cursor menu)"
	@echo "  make build-skills          Compile agents → .skill.md + core/skill_registry.json"
	@echo "  make run-skill SKILL=B1    Execute one skill deterministically"
	@echo "  make run-pipeline          Execute all 24 skills in DAG order"
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

skills:
	$(PYTHON) tools/build_skill_registry.py

build-skills:
	$(PYTHON) runtime/skill_registry_builder.py

run-skill:
ifndef SKILL
	$(error Set SKILL=B1)
endif
	$(PYTHON) -m runtime --skill "$(SKILL)" --run-id $(or $(RUN_ID),skill-run)

run-pipeline:
	$(PYTHON) -m runtime --full-pipeline --run-id $(or $(RUN_ID),pipeline-run)

test:
	$(PYTHON) -m pytest tests/ -v --cov=runtime --cov-report=term-missing

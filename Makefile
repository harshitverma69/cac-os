.PHONY: validate list route validate-run skills build-skills run-skill run-pipeline test validate-dag validate-pipeline test-determinism harden help

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
	@echo "  make validate-dag          Validate skill dependency DAG"
	@echo "  make validate-pipeline     Validate pipeline run (RUN_ID=final_test)"
	@echo "  make test-determinism      Prove run-to-run identical skill outputs"
	@echo "  make harden                Full production hardening sequence"
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

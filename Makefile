.SHELLFLAGS += -e

MODERN_LINT_CONFIG=$(PWD)/lint-configs/pyproject.toml
APP_FOLDER=APP_FOLDER_UNSPECIFIED

SEMGREP_RULES=semgrep/rules
SEMGREP_CONFIGS= --config=$(SEMGREP_RULES)
SEMGREP_EXCLUDES=--exclude='*json' --exclude='.html' --exclude='.svg' --exclude='wheels/'

.PHONY: install lint lint-fix semgrep

install:
	python3 -m pip install -r dev-requirements.txt
	pre-commit install

lint:
	cd $(APP_FOLDER) && python3 -m ruff check . --config $(MODERN_LINT_CONFIG)
	cd $(APP_FOLDER) && python3 -m ruff format --check --diff --config $(MODERN_LINT_CONFIG) .

lint-fix:
	cd $(APP_FOLDER) && python3 -m ruff check --fix . --config $(MODERN_LINT_CONFIG)
	cd $(APP_FOLDER) && python3 -m ruff format . --config $(MODERN_LINT_CONFIG)

semgrep-run:
	semgrep $(SEMGREP_CONFIGS) $(APP_FOLDER) $(SEMGREP_EXCLUDES)

semgrep-test:
	semgrep --test $(SEMGREP_RULES)

semgrep-upload:
	./semgrep/upload_private_rules.sh

.SHELLFLAGS += -e

LINT_CONFIG=$(PWD)/lint-configs/tox.ini
MODERN_LINT_CONFIG=$(PWD)/lint-configs/pyproject.toml
APP_FOLDER=APP_FOLDER_UNSPECIFIED

SEMGREP_RULES=semgrep/rules
SEMGREP_CONFIGS= --config=$(SEMGREP_RULES)
SEMGREP_EXCLUDES=--exclude='*json' --exclude='.html' --exclude='.svg' --exclude='wheels/'

.PHONY: install flake8-check isort-check isort-fix autopep8-fix autopep8-fix-aggressive lint lint-fix lint-fix-aggressive semgrep black-check

install:
	python3 -m pip install -r dev-requirements.txt

flake8-check:
	cd $(APP_FOLDER) && python3 -m flake8 . --config $(LINT_CONFIG)

black-check:
	cd $(APP_FOLDER) && python3 -m black --check --diff --config $(MODERN_LINT_CONFIG) .

isort-check:
	cd $(APP_FOLDER) && python3 -m isort . --src . --settings-path $(MODERN_LINT_CONFIG) --check-only --diff

isort-fix:
	cd $(APP_FOLDER) && python3 -m isort . --src . --settings-path $(MODERN_LINT_CONFIG)

autopep8-fix:
	cd $(APP_FOLDER) && python3 -m autopep8 . --recursive --in-place --global-config $(LINT_CONFIG)

autopep8-fix-aggressive:
	cd $(APP_FOLDER) && python3 -m autopep8 . --aggressive --recursive --in-place --global-config $(LINT_CONFIG)

lint: flake8-check isort-check black-check

lint-fix: autopep8-fix isort-fix

lint-fix-aggressive: autopep8-fix-aggressive isort-fix

semgrep-run:
	semgrep $(SEMGREP_CONFIGS) $(APP_FOLDER) $(SEMGREP_EXCLUDES)

semgrep-test:
	semgrep --test $(SEMGREP_RULES)

semgrep-upload:
	./semgrep/upload_private_rules.sh

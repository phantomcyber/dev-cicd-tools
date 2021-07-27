LINT_CONFIG=lint-configs

.PHONY: install lint lint-fix

install:
	python3 -m pip install -r dev-requirements.txt

lint:
	python3 -m flake8 . --config $(LINT_CONFIG)
	python3 -m isort . --check-only --settings-path $(LINT_CONFIG)

lint-fix:
	python3 -m autopep8 --global-config $(LINT_CONFIG)
	python3 -m isort . --settings-path $(LINT_CONFIG)

prepare:
	python3 splunkbase-migration/migrate-app-portal.py --prepare --app-data $(APP_DATA_FILE)


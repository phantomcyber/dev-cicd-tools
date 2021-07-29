.SHELLFLAGS += -e

LINT_CONFIG=$(PWD)/lint-configs/tox.ini
APP_FOLDER=APP_FOLDER_UNSPECIFIED

.PHONY: install flake8-check isort-check isort-fix autopep8-fix autopep8-fix-aggressive lint lint-fix lint-fix-aggressive

install:
	python3 -m pip install -r dev-requirements.txt

flake8-check:
	cd $(APP_FOLDER) && python3 -m flake8 . --config $(LINT_CONFIG)

isort-check:
	cd $(APP_FOLDER) && python3 -m isort . --check-only --settings-path $(LINT_CONFIG)

isort-fix:
	cd $(APP_FOLDER) && python3 -m isort . --settings-path $(LINT_CONFIG)

autopep8-fix:
	cd $(APP_FOLDER) && python3 -m autopep8 . --recursive --in-place --global-config $(LINT_CONFIG)

autopep8-fix-aggressive:
	cd $(APP_FOLDER) && python3 -m autopep8 . --aggressive --recursive --in-place --global-config $(LINT_CONFIG)

lint: flake8-check isort-check
	
lint-fix: autopep8-fix isort-fix
		
lint-fix-aggressive: autopep8-fix-aggressive isort-fix

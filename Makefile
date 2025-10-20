PYTHON ?= uv run -q python3
PROJECT_ROOT := $(shell pwd)
export PYTHONPATH := $(PROJECT_ROOT)/src:$(PYTHONPATH)

.PHONY: i18n-register i18n-stubs i18n-extract i18n-update i18n-compile i18n-verify i18n-refresh

i18n-register:
	$(PYTHON) scripts/i18n_register.py

i18n-stubs: i18n-register
	$(PYTHON) scripts/gen_i18n_stubs.py

i18n-extract:
	$(PYTHON) -m babel.messages.frontend extract -F babel.cfg -o src/infra/i18n/locales/messages.pot .

i18n-update:
	$(PYTHON) -m babel.messages.frontend update -i src/infra/i18n/locales/messages.pot -d src/infra/i18n/locales

i18n-compile:
	$(PYTHON) -m babel.messages.frontend compile -d src/infra/i18n/locales

i18n-verify:
	$(PYTHON) scripts/i18n_verify.py

i18n-refresh: i18n-stubs i18n-extract i18n-update i18n-compile i18n-verify
	@echo "i18n refresh done"



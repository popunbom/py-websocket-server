VENV_DIR = .venv
ifneq ($(shell test -f /.dockerenv; echo $$?), 0)
	PYTHON = $(VENV_DIR)/bin/python3
	PIP = $(VENV_DIR)/bin/pip3
else
	PYTHON = $(shell which python3)
	PIP = $(shell which pip3)
endif


.PHONY: all
all: init run

.PHONY: init
init:
ifneq ($(shell test -f /.dockerenv; echo $$?), 0)
	python3 -m venv $(VENV_DIR)
endif
	$(PIP) install -r requirements.txt

.PHONY: run
run:
	$(PYTHON) server.py

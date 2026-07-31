NAME = src/fly_in.py
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

run: install
	$(PYTHON) ${NAME}

clean:
	rm -rf .mypy_cache
	rm -rf __pycache__
	rm -rf venv

install: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	rm -rf maps
	rm -f maps.tar.gz
	$(PYTHON) -m wget https://cdn.intra.42.fr/document/document/55008/maps.tar.gz
	tar -xvf maps.tar.gz
	rm -rf maps.tar.gz


debug: install
	$(PYTHON) -m pdb ${NAME}

lint:
	flake8 --exclude=./venv .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	flake8 --exclude=./venv .
	mypy . --strict

.PHONY: run install clean lint lint-strict debug

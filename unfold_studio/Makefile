PYTHON = ../.venv/bin/python
MANAGE = $(PYTHON) manage.py
NPM = npm

.PHONY: dev build test lint docs

dev:
	$(MANAGE) runserver & npm run dev

build:
	npm run build
	$(MANAGE) collectstatic --noinput

test:
	$(PYTHON) -m pytest
	npm run test

lint:
	$(PYTHON) -m ruff check .
	npm run lint

docs:
	cd ../docs && ../.venv/bin/sphinx-build -b html . _build/html

PYTHON = .venv/bin/python
MANAGE = $(PYTHON) unfold_studio/manage.py
SPHINX = .venv/bin/sphinx-build

.PHONY: dev build test lint docs

dev:
	trap 'kill 0' INT; $(MANAGE) runserver & npm --prefix unfold_studio run dev & wait

build:
	npm --prefix unfold_studio run build
	$(MANAGE) collectstatic --noinput

test:
	$(PYTHON) -m pytest unfold_studio
	npm --prefix unfold_studio run test

lint:
	$(PYTHON) -m ruff check unfold_studio
	npm --prefix unfold_studio run lint

docs:
	uv sync --group docs
	$(SPHINX) -b html docs docs/_build/html

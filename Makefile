PYTHON = .venv/bin/python
MANAGE = $(PYTHON) unfold_studio/manage.py
SPHINX = .venv/bin/sphinx-build
BUMP = .venv/bin/bump-my-version

.PHONY: dev build test lint docs install-hooks bump-major bump-minor bump-patch

dev:
	bash scripts/dev.sh

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

install-hooks:
	cp scripts/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

bump-major:
	$(BUMP) bump major

bump-minor:
	$(BUMP) bump minor

bump-patch:
	$(BUMP) bump patch --no-tag

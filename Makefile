PYTHON = .venv/bin/python
SPHINX = .venv/bin/sphinx-build

.PHONY: docs

docs:
	uv sync --group docs
	$(SPHINX) -b html docs docs/_build/html

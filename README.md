# Unfold Studio

[Unfold Studio](https://unfoldstudio.net) is a free, open-source platform for writing
and playing interactive stories using [Ink](https://www.inklestudios.com/ink/), a
scripting language designed for branching narratives. It is used in schools, writing
clubs, and by individual authors. Stories can incorporate AI-generated text and respond
to free-text input from readers.

**If you want to write or read stories, go to [unfoldstudio.net](https://unfoldstudio.net).**

---

## For developers and contributors

This repository contains the source code for the Unfold Studio web application.
Technical documentation (architecture, development setup, deployment) lives in
`docs/` and can be built with:

```
make docs
open docs/_build/html/index.html
```

Quick orientation:

- `unfold_studio/` — Django project (Python backend + Vue/TypeScript frontend)
- `docs/` — Sphinx documentation source

See `docs/introduction.rst` for a developer overview, or `docs/dev-setup.rst`
to get a local instance running.

Introduction for New Developers
================================

Welcome to the Unfold Studio codebase. This page is aimed at developers joining
the project for the first time — if you have taken a web development or software
engineering course, you should be able to get oriented here.

What is Unfold Studio?
----------------------

Unfold Studio is a collaborative storytelling platform. Users write interactive stories
in `Ink <https://www.inklestudios.com/ink/>`_, a scripting language designed for
branching narratives. The app compiles those stories and lets readers play through
them in a browser — making choices, entering text, and triggering AI-generated passages.

The platform has two sides:

* **Writing** — a browser-based code editor with syntax highlighting, live
  compilation feedback, and version history.
* **Playing** — a reader-facing player that runs the compiled story, handles choices,
  and calls out to an LLM when the story requests generated text or needs to
  interpret free-text input.

It also has classroom and research features: literacy groups (classes/cohorts),
assignment prompts, reading event logs, and a research data API.

Before diving into the code, spend some time using the app as a writer and reader
at `unfoldstudio.net <https://unfoldstudio.net>`_. The user-facing documentation
there — including the Ink language guide — will give you a much clearer picture of
what the code is actually doing.

Tech Stack Overview
-------------------

You will need to be comfortable with the following technologies. Each section links
to a starting point if the technology is new to you.

**Python / Django**
   Django is the web framework that handles HTTP requests, the database, and server-side
   HTML rendering. It follows an MTV pattern (Model / Template / View) which is similar
   to MVC. Most of the backend logic lives here.

   - `Django tutorial <https://docs.djangoproject.com/en/stable/intro/tutorial01/>`_
   - We use **Django 5** with class-based views, the ORM, and the sites framework.

**PostgreSQL**
   The database. PostgreSQL is required — the app uses features not available in
   SQLite. See :doc:`dev-setup` for local setup options.

**Redis + Celery**
   Redis is an in-memory store used as a message broker. Celery is a task queue that
   runs jobs asynchronously — in our case, compiling large Ink stories without blocking
   the HTTP request. For local dev you can skip both by setting
   ``CELERY_TASK_ALWAYS_EAGER = True``, which runs tasks synchronously in-process.

**TypeScript / Vue 3**
   The browser-side code is written in TypeScript (typed JavaScript) and uses
   `Vue 3 <https://vuejs.org/guide/introduction.html>`_ for reactive UI components.
   Vue uses the Composition API with ``<script setup>`` — if you have only seen
   React or class-based components before, spend 30 minutes with the
   `Vue 3 quick start <https://vuejs.org/guide/quick-start.html>`_ before diving in.

**Vite**
   `Vite <https://vitejs.dev/>`_ compiles and bundles the TypeScript/Vue source files
   into browser-ready JavaScript. You do not need to understand Vite in depth —
   just know that ``make dev`` runs Vite in watch mode so your changes rebuild
   automatically.

**Ink / inkjs**
   `Ink <https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md>`_
   is a scripting language for interactive fiction made by Inkle Studios. We compile
   Ink source to JSON using `inklecate` (the official compiler), then run it in the
   browser using `inkjs <https://github.com/y-lohse/inkjs>`_ (a JavaScript port of
   the runtime).

**CodeMirror 6**
   The in-browser code editor is built with `CodeMirror 6 <https://codemirror.net/>`_.
   We have a custom Ink syntax highlighting mode. You rarely need to touch this unless
   you are working on the editor experience.

**LLM API (OpenAI or Anthropic)**
   The text generation features send requests to a configurable LLM provider.
   The ``text_generation`` app abstracts over multiple backends and caches responses
   so the same prompt is never called twice. You will need an API key for dev
   (see :doc:`dev-setup`).

How the Pieces Fit Together
---------------------------

Here is a simplified walk-through of what happens when a user plays a story:

1. The browser loads a Django-rendered HTML page (``show_story.html``). Django
   injects a ``window.__UNFOLD__`` JavaScript object containing the story ID,
   CSRF token, API URLs, and optionally the pre-fetched story JSON.

2. The Vite-compiled bundle (``main.ts``) mounts a Vue app on ``#main``.
   ``StoryPage.vue`` fetches the story JSON and hands it to ``InkPlayer``.

3. ``InkPlayer`` runs the story using the ``inkjs`` runtime, building DOM nodes for
   text paragraphs and choice buttons as the story progresses.

4. When the story hits a ``generate()`` external function call, the player POSTs
   to ``/generate/``. Django calls the configured LLM backend (or returns a cached
   response) and sends back the generated text.

5. When the author saves changes, the browser POSTs the new Ink source to
   ``/stories/<id>/compile/``. Django calls ``inklecate``, stores the compiled JSON,
   and returns errors if there are any.

Where Things Live
-----------------

**This repository powers** `app.unfoldstudio.net <https://app.unfoldstudio.net>`_ —
the web application where users write and play stories. The marketing and landing site
at `unfoldstudio.net <https://unfoldstudio.net>`_ is a separate static site in its own
repository; it is not part of this codebase.

The repository has two top-level directories:

``unfold_studio/``
   The Django project. All Python code, templates, and frontend source live here.
   This is where you will spend most of your time.

``docs/``
   These documentation files (Sphinx / RST format).

Inside ``unfold_studio/``, Django apps are laid out flat alongside the core
``unfold_studio`` package:

.. list-table::
   :header-rows: 1
   :widths: 25 55

   * - Directory
     - What it does
   * - ``unfold_studio/``
     - Core: URL routing, settings, template tags (``vite_asset``, etc.)
   * - ``stories/``
     - Story model, Ink compilation, CRUD views
   * - ``books/``
     - Curated story collections
   * - ``story_play/``
     - Play session tracking
   * - ``profiles/``
     - User profiles and follow relationships
   * - ``text_generation/``
     - LLM API calls, caching, generate/get-next-direction views
   * - ``literacy_groups/``
     - Classroom / cohort management
   * - ``research/``
     - API-key-protected research data export
   * - ``src/``
     - TypeScript/Vue frontend source (compiled by Vite)

See :doc:`architecture` for a deeper walk-through of the request lifecycle,
the Ink pipeline, and key design decisions.

Good Starting Points
--------------------

* Get the app running locally: :doc:`dev-setup`
* Understand the code structure: :doc:`architecture`
* Learn Ink: `Writing with Ink <https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md>`_
* Django ORM reference: `Django models <https://docs.djangoproject.com/en/stable/topics/db/models/>`_
* Vue 3 Composition API: `Vue docs <https://vuejs.org/guide/essentials/reactivity-fundamentals.html>`_

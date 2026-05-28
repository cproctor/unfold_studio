Architecture
============

App Layout
----------

The project is a Django monorepo with the main application at ``unfold_studio/``.
Django apps are co-located in the same directory:

.. list-table::
   :header-rows: 1
   :widths: 25 55

   * - App
     - Responsibility
   * - ``unfold_studio``
     - Core app: URL routing, base settings, template tags, management commands
   * - ``stories``
     - Story model, Ink preprocessing and compilation, CRUD views, versioning
   * - ``books``
     - Book model (curated collections of stories), CRUD views
   * - ``story_play``
     - ``StoryPlayInstance`` and ``StoryPlayRecord`` models; play tracking API
   * - ``profiles``
     - User profile model (bio, avatar, follow relationships, researcher flag)
   * - ``literacy_events``
     - Event log for literacy research (story read, choice made, etc.)
   * - ``literacy_groups``
     - Group model for classroom/cohort management
   * - ``comments``
     - Story comments
   * - ``prompts``
     - Prompt templates for text generation
   * - ``text_generation``
     - LLM backend abstraction, generate/get-next-direction views, caching
   * - ``generated_text_evaluator``
     - Quality evaluation pipeline for AI-generated story text
   * - ``research``
     - API endpoints for research data export (API-key protected)
   * - ``commons``
     - Shared utilities: ``SoftDeleteMixin``, ``SoftDeleteManager``

Request Lifecycle (Story Play)
------------------------------

A user plays a story with these request flows:

1. **Page load** — Django renders ``show_story.html``, injecting a
   ``window.__UNFOLD__`` config block with the story ID, CSRF token, API URLs,
   and optional pre-fetched JSON. The Vite bundle (``main.ts``) is loaded via
   the ``{% vite_asset %}`` template tag.

2. **Vue mount** — ``main.ts`` calls ``createApp(StoryPage).mount('#main')``.
   ``StoryPage.vue`` fetches story JSON (or uses the pre-fetched data), creates
   an ``InkPlayer``, and calls ``player.play(story)``.

3. **Play** — ``InkPlayer`` calls ``inkjs.Story.Continue()`` in a loop, building
   DOM nodes for text, choices, and input forms. External functions bound to
   the Ink runtime trigger AI generation and text input.

4. **AI generation** — When the story calls the ``generate()`` external function,
   ``InkPlayer`` POSTs to ``/generate/``. The ``GenerateTextView`` calls the
   configured LLM backend and returns generated text.

5. **Continue function** — When the story calls ``continue_function()``, the
   player shows a free-text input box. The user's input is sent to
   ``/get-next-direction/`` which uses an LLM to decide whether to pass the
   input directly to the story, request clarification, or generate a bridge
   passage.

Ink Pipeline
------------

Ink sources are preprocessed before compilation:

1. **Preprocessing** (``stories/models.py::preprocess_ink``) — Resolves
   ``INCLUDE`` directives, extracts ``VAR`` declarations, builds a knot map.
   Prevents circular includes and reports missing stories.

2. **Compilation** (subprocess call to ``inklecate``) — The preprocessed Ink
   source is compiled to JSON. Errors are parsed and stored as ``StoryError``
   records.

3. **Serving** — The compiled JSON is stored on the ``Story`` model and served
   via ``/stories/<id>/json/`` for the runtime.

Async compilation (``/stories/<id>/compile_async/``) queues a Celery task and
returns a task ID for polling. This prevents timeouts for large stories.

Text Generation
---------------

The ``text_generation`` app abstracts over multiple LLM providers:

* ``OpenAIBackend`` — wraps the OpenAI Python client
* ``AnthropicBackend`` — wraps the Anthropic Python client

Both backends implement ``TextGenerationBackendInterface``:

* ``generate(prompt, context_array, seed)`` — generate story text
* ``get_ai_response_by_system_and_user_prompt(system, user, seed)`` — structured
  JSON response for direction decisions

The active backend is selected by ``TEXT_GENERATION['backend']`` in settings.
Results are cached in ``TextGenerationRecord`` (keyed by prompt hash + backend
config hash + seed) to avoid redundant API calls.

Front-End Architecture
----------------------

The frontend is built with **Vite 6** + **Vue 3** + **TypeScript 5**:

* ``src/main.ts`` — entry point for the story editor/player page; mounts
  ``StoryPage.vue`` on ``#main``
* ``src/embed.ts`` — entry point for the embed player; mounts ``EmbedPlayer.vue``
  on ``#embed-app``
* ``src/StoryPage.vue`` — top-level component; composes toolbar, editor, player
* ``src/StoryEditor.vue`` — CodeMirror 6 editor with Ink syntax highlighting
* ``src/StoryToolbar.vue`` — save, fork, share, replay, show/hide code
* ``src/EmbedPlayer.vue`` — minimal embed player with logo header
* ``src/player.ts`` — ``InkPlayer`` class; imperative DOM-based story playback
* ``src/api.ts`` — ``StoryAPI`` class; fetch-based API calls to Django
* ``src/sanitize.ts`` — DOMPurify wrapper for safe innerHTML assignment
* ``src/types.ts`` — TypeScript interfaces (``StoryContent``, ``UnfoldConfig``)
* ``src/globals.d.ts`` — ambient declarations for ``inkjs`` global and
  ``window.__UNFOLD__``

The ``inkjs`` runtime is loaded as a ``<script>`` tag (not npm) because it is a
large UMD bundle designed for browser globals. TypeScript sees it via the ambient
``declare namespace inkjs`` declaration in ``globals.d.ts``.

The ``{% vite_asset 'src/main.ts' %}`` template tag reads
``static/dist/.vite/manifest.json`` at runtime to resolve hashed filenames.
In development, rebuild on file change with ``npm run dev`` (Vite watch mode).

Key Design Decisions
--------------------

**``window.__UNFOLD__`` config block** — Server-rendered JavaScript variables
replace the old RequireJS entry-point pattern. The config block injects story
ID, CSRF token, API URLs, and optional pre-fetched JSON. This decouples the
Django template from the frontend module system.

**inkjs as a global** — Loading inkjs via a ``<script>`` tag rather than npm
avoids bundling the large runtime with the Vite bundle. It is declared as an
ambient global in TypeScript.

**DOMPurify sanitization** — All story text is passed through DOMPurify before
being assigned to ``innerHTML``. The Ink runtime can include author-written HTML
for formatting; DOMPurify allows only a safe subset of tags.

**Soft deletes** — Stories, books, groups, and prompts use ``SoftDeleteMixin``
which adds a ``deleted_at`` timestamp. ``SoftDeleteManager`` excludes deleted
records by default. The ``purge_deleted_records`` management command physically
removes records older than a configurable threshold.

**API key auth for research endpoints** — Research data export endpoints use a
custom ``@require_api_key`` decorator rather than session authentication. API
keys are stored hashed in the ``APIKey`` model.

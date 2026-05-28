# Unfold Studio — Implementation Checklist

Tasks are ordered by dependency and priority. Check off each item as it is merged. Write tests for
each area as it is touched — don't defer testing to the end.

Reference: `refactor/refactor.v2.md`

---

## Phase 1 — Security & Settings (P0)

- [x] Purge committed OpenAI API key from git history (`git filter-repo` / BFG) (§0.1) — see NI-1 (not yet purged from history)
- [x] Replace `SECRET_KEY` in `base_settings.py` and `site_settings/unfold_studio.py` with `os.environ['SECRET_KEY']` (§0.1)
- [x] Replace `api_key` in `TEXT_GENERATION` dict with `os.environ.get(...)` (§0.1)
- [x] Fix `site_settings/unfold_studio.py` to import from `base_settings` and override only production values (§1.5 / §10.3)
- [x] Set `DEBUG = False` as default in `base_settings.py`; confirm `DEBUG = True` only in `settings.py` (§10.1)
- [x] Confirm `static_assets/` is in `.gitignore` (§10.2)
- [x] Update `DeploymentReadme.md` with env var table (§0.1)

---

## Phase 2 — Quick Backend Fixes (P1)

- [x] Remove `__pycache__`-only artifact directories at project root (`git rm -r --cached comments/ literacy_events/ ...`) (§1.3)
- [x] Fix `research/views.py` `status_code=400` → `status=400` (§1.6)
- [x] Remove `self.preprocessed_ink = ink # TODO DEBUG` from `models.py` (§1.8)
- [x] Replace N+1 loop in `Notification.mark_all_seen_for_user` with `.update(seen=True)` (§1.9)
- [x] Fix `StoryManager.editable_for_site_user`: remove duplicate `Q(author=user)` and `Q(public=True)` (§1.4)
- [x] Standardize `Story.for_json()`: replace string `error` field with `errors` list of `{line, message}` objects (§1.7)

---

## Phase 3 — Backend Data Model (P1)

- [x] Add data migration for `LiteracyEvent` event types: migrate opaque chars to `TextChoices` readable strings (§1.10)
- [x] Change `LiteracyEvent.user` FK to `null=True, on_delete=models.SET_NULL` (§1.11)
- [x] Implement `SoftDeleteMixin` and `SoftDeleteManager` in `commons` (§1.11)
- [x] Apply `SoftDeleteMixin` to `Story`, `Book`, `LiteracyGroup`, `Prompt`; ensure custom managers extend `SoftDeleteManager` (§1.11)
- [x] Add `delete_old_public_stories` management command and `PUBLIC_STORY_MAX_AGE_DAYS` setting (§1.4)
- [x] Add `delete_user` management command (anonymize personal data, soft-delete content, remove User/Profile) (§1.11)
- [x] Add `purge_deleted_records` management command (§1.11)

---

## Phase 4 — Backend App Structure (P1)

- [x] Split `unfold_studio` app: create `stories` app with `Story`, `StoryError`, `StoryManager`, compilation, preprocessing (§1.1)
- [x] Create `books` app with `Book`, `BookManager`, book CRUD views (§1.1)
- [x] Create `story_play` app with `StoryPlayInstance`, `StoryPlayRecord`, play views (§1.1)
- [ ] Rename remaining app from `unfold_studio` to `studio` — deferred; see NI-4 in new_issues.md (§1.2)
- [x] Fix unauthenticated play-tracking endpoints: require story to be shared/public, record user identity if logged in (§0.3)
- [x] Replace `setBook()` URL manipulation with `/stories/{id}/add_to_book/` POST endpoint (§8.6)

---

## Phase 5 — Backend New Features (Proposal)

- [x] Remove unused inklecate versions (`inklecate_0.8.2/`, `inklecate_1.1.1/`) from repo (§1.13)
- [x] Add `scripts/install_inklecate.sh` download script (§1.13)
- [x] Add `is_researcher` field to `Profile`; wire up researcher admin (§0.4)
- [x] Implement `APIKey` model, `require_api_key` decorator, and `ResearcherAPIKeyView` (§0.4)
- [x] Replace `@csrf_exempt` with `@require_api_key` on all research endpoints (§0.4)
- [x] Implement `LLMBackend` abstract class, `OpenAIBackend`, `AnthropicBackend`, and `get_llm_backend()` factory (§11.1)
- [x] Update `text_generation/views.py` to use `get_llm_backend()` instead of direct OpenAI client (§11.1)
- [x] Update `TEXT_GENERATION` settings dict to support multi-backend format (§11.1)
- [x] Implement Celery async compilation: `stories/tasks.py`, compile_async endpoint, status polling (§1.12)
- [x] Add `CELERY_TASK_ALWAYS_EAGER = True` to local `settings.py` example (§1.12)

---

## Phase 6 — Backend Code Quality (P2)

- [x] Add `LOGGING` dict to `base_settings.py` for structlog (§8.2)
- [x] Replace all `print()` calls in `text_generation/views.py` and `flows/` with structlog calls (§8.1 / §8.2)
- [x] Replace bare `except:` in `research/views.py` with `except Exception:` + `log.exception()` (§8.2)
- [x] Delete commented-out code: `messages.success()` calls in `views.py`, `logPath` in `player.js`, `ChoosePathString` calls, `"memoize"` in `base_settings.py` (§8.3)

---

## Phase 7 — Frontend Dead Code Deletion (P2)

- [x] Delete `static/scripts/ink_interface.js` and `static/scripts/lib/underscore.1.8.3.js` (§4.1)
- [x] Delete `static/inkfile.js` (§4.2)
- [x] Delete `static/app.js::originalInit` function body (§4.3)
- [x] Delete `static/lib/inky_old/` (§4.4)
- [x] Delete Electron-specific Inky files (`navView.js`, `liveCompiler.js`, `goto.js`, `contextmenu.js`) (§4.4)
- [x] Delete `static/scripts/inkymain.js` (§4.8)
- [x] Delete remaining redundant assets: `backbone.1.2.3.js`, `d3.3.5.9.js`, `jsgame/`, `randomstring.js` (audit first), `results.csv` (§7)
- [x] Move `qunit-*` from static to npm dev dependency (§7) — static files deleted; npm devDependency deferred to Phase 8

---

## Phase 8 — Frontend Infrastructure: Vite + TypeScript (P1)

- [x] Add `package.json` at Django project root; install `vite`, `typescript`, `vue`, `@vitejs/plugin-vue`, `dompurify`, `@types/dompurify`, `vue-i18n`, `pinia` (§2.1)
- [x] Add `vite.config.ts` with manifest build, `app` and `embed` entry points, output to `static/dist/` (§2.1)
- [x] Add `tsconfig.json` (§2.1)
- [x] Add `vite_asset` Django template tag that reads `static/dist/manifest.json` (§2.1)
- [x] Add `Makefile` with `dev` (Django + Vite + Celery), `build`, `test`, and `lint` targets (§2.1 / §12.3)
- [x] Add ESLint config with `no-undef` rule (§4.5)

---

## Phase 9 — Frontend Migration: Player (P1)

- [x] Fix player implicit globals: add `'use strict'`, declare all vars with `const`/`let` (§4.5)
- [x] Fix generate race condition: remove `sessionStorage` read/write and `MutationObserver` fallback in `app.js` (§4.7)
- [x] Replace server-rendered JS entry points with `window.__UNFOLD__` config block in templates; delete `require_entry_point` and `embed_entry_point` views (§2.2)
- [x] Rewrite `player.js` as `<StoryPlayer>` Vue component in TypeScript — implemented as `src/player.ts` TypeScript ES module class with full feature parity; Vue SFC wrapper deferred to Phase 10 (§6.3)
- [x] Apply `sanitizeStoryText()` (DOMPurify) to all `innerHTML` insertions in `<StoryPlayer>` (§0.5)
- [x] Add `debugMode` support: attach `window.__UNFOLD_DEBUG__` when `window.__UNFOLD__.debugMode` is true (§4.5)

---

## Phase 10 — Frontend Migration: Editor & Toolbar (P1)

- [x] Install CodeMirror 6 npm packages (§3.1) — added to package.json; install when network available
- [x] Write Ink `StreamLanguage` mode for CodeMirror 6 (port from `ace-ink.js`) (§3.1) — `src/ink-language.ts`
- [x] Rewrite `editorView.js` as `<StoryEditor>` Vue component using CodeMirror 6 (§3.1 / §6.3) — `src/StoryEditor.vue`
- [x] Implement `<StoryToolbar>` Vue component (Save, Fork, Share, show/hide code) (§6.3) — `src/StoryToolbar.vue`
- [x] Implement `<StoryPage>` top-level component composing editor, player, toolbar (§6.2) — `src/StoryPage.vue`; `main.ts` mounts as Vue app on `#main`
- [x] Move delete-confirm logic out of `base/base.html` into a `<ConfirmDelete>` component (§8.5) — `src/ConfirmDelete.vue`; base.html jQuery inline script removed
- [x] Remove jQuery once all jQuery usages are replaced (§4.6) — `static/scripts/lib/jquery.2.1.4.js` deleted; `static/scripts/lib/jquery-linedtextarea/` deleted; all template references removed
- [x] Delete `static/lib/ace_src/`, `static/lib/inky/acesrc/`, `static/lib/inky/ace-ink-mode/` (§3.1)
- [x] Delete RequireJS (`static/lib/require/`) and all AMD `define()` wrappers (§2.1) — `static/app.js`, `static/player.js`, `static/story.js`, `static/embed.js` deleted
- [x] Consolidate CSS: create `src/tokens.css` for design tokens; migrate global styles to Vue Scoped CSS (§5.1) — tokens.css created; full migration to scoped CSS is incremental future work

---

## Phase 11 — New Frontend Feature: Story Embed (Proposal)

- [x] Add `/stories/{id}/embed` URL and view (shared stories only; styled error page for ineligible stories) (§0.2) — `stories/views.py::embed_story`, URL at `stories/<id>/embed/`
- [x] Implement `<EmbedPlayer>` Vue component (logo header linked to base URL, reuses `<StoryPlayer>`) (§0.2 / §6.2) — `src/EmbedPlayer.vue`
- [x] Add `embed.ts` Vite entry point; compile `<EmbedPlayer>` (§2.1) — `src/embed.ts` updated
- [x] Delete old `embed.js`, `embed_entry_point.js`, and RequireJS-based embed instructions in user guide (§4.8) — `static/embed.js` deleted in Phase 10; no RequireJS embed instructions found in documentation
- [x] Remove `CORS_ORIGIN_ALLOW_ALL` from both settings files (§0.2) — removed from `base_settings.py`; not present in site_settings

---

## Phase 12 — Testing (P2)

- [ ] Standardize test layout: create `tests/` packages in each app; delete empty `tests.py` stubs; add root `conftest.py` (§9.2)
- [ ] Add Vitest; configure in `vite.config.ts` (§9.3)
- [ ] Write `text_generation/tests/test_backends.py` for LLM backend abstraction (§9.1 / §11.1)
- [ ] Write `text_generation/tests/test_views.py` for `GenerateTextView`, `GetNextDirectionView` (§9.1)
- [ ] Write `stories/tests/test_compilation.py`: circular includes, missing includes, variable shadowing (§9.1)
- [ ] Write Vitest tests for `StoryPlayer.vue` state machine (mocking inkjs) (§9.3)
- [ ] Write Vitest tests for compilation result parsing in `story.ts` (§9.3)

---

## Phase 13 — Documentation (Proposal)

- [ ] Set up Sphinx docs at `docs/`; install dependencies; configure `conf.py` with ReadTheDocs theme (§12.1)
- [ ] Write `docs/deployment.rst`: system requirements, env vars, setup steps, services, cron jobs, nginx/gunicorn config, upgrade steps (§12.2)
- [ ] Write `docs/dev-setup.rst`: prerequisites, quick start, Makefile targets, running tests (§12.3)
- [ ] Write `docs/architecture.rst`: app layout, request lifecycle, ink pipeline, text generation, front-end architecture, key design decisions (§12.4)
- [ ] Move `DeploymentReadme.md` content into `docs/deployment.rst`; delete `DeploymentReadme.md` (§12.1)
- [ ] Add i18n infrastructure: `LOCALE_PATHS`, `LocaleMiddleware`, `vue-i18n` setup, `en.json` locale file (§8.4)
- [ ] Wrap user-facing strings in `_()` / `{% trans %}` incrementally as files are touched (§8.4)

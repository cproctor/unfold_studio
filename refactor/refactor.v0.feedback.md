# Unfold Studio — Refactor Plan

This document identifies issues, redundancies, and improvement opportunities across the codebase,
grouped by area and prioritized. Issues are marked **P0** (fix now), **P1** (fix soon), **P2** (fix
when touching the area), or **Proposal** (worth doing but not required).

---

## 0 — Critical Security (P0)

These must be addressed before any other work.

### 0.1 Committed API key and secret key

`unfold_studio/unfold_studio/settings.py` (the local development settings file) has a live OpenAI
API key committed to git:

```
"api_key": "sk-svcacct-W5rZoPmuLvzpBIL9WcWeT3BlbkFJJvNteb6uYFuor69xu2au",
```

Assume this key is already compromised. Rotate it immediately, then remove it from the file and
from git history (`git filter-repo` or BFG).

> I have revoked the key at OpenAI. The remaining parts of this task are to remove the key from the 
> settings file and the git hitory. Assuming we are going to provide the API key via an env var in the 
> future, add instructions to the deployment docs for how to do this. 

`base_settings.py` and `site_settings/unfold_studio.py` both contain the same hardcoded
`SECRET_KEY`. This means all environments share one secret, and it is committed to the repository.
Replace with `os.environ['SECRET_KEY']` and provision the value separately for each deployment.

> Update deployment docs with instructions.

### 0.2 CORS wildcard

`CORS_ORIGIN_ALLOW_ALL = True` appears in both `base_settings.py` and
`site_settings/unfold_studio.py`. This allows any origin to make cross-origin requests. Replace
with an explicit `CORS_ALLOWED_ORIGINS` list restricted to the embed and documentation domains.

> I want to be able to embed Unfold Studio stories in iframes on other pages; proper functionality
> includes making requests which were failing prior to opening up CORS. I don't see a major security
> issue with `CORS_ORIGIN_ALLOW_ALL = True`, but if there is a more restrictive way to still display 
> stories on other pages, I'm open to that. We could also create a feature to allow embedding stories
> on other pages via a dedicated URL route and view (e.g. /stories/{id}/embed), which would show the story
> runtime/source code panes in read-only mode without the rest of the site UI (e.g. menus), and just open this view 
> to CORS. If this isn't too much and feels like the right way to go, propose this feature. 

### 0.3 Unauthenticated story-play tracking endpoints

`CreateStoryPlayInstanceView` and `CreateStoryPlayRecordView` (both in `unfold_studio/views.py`)
have no authentication check. Any anonymous user—or any script—can create arbitrary play records.
These should verify at minimum that the story being referenced is publicly playable.

### 0.4 CSRF-exempt research endpoint

`research/views.py` uses `@csrf_exempt` on `compile_story`. This endpoint lets callers compile
arbitrary ink by sending an HTTP POST without a CSRF token. If it is only for internal tooling,
require an API token or IP allowlist. If it is not in active use, remove it.

> This is for internal tools, so yes let's require an API key. I believe this will require a new 
> model, right? If so, propose this as a feature within the research app--all API access will be scoped
> to research-related features. Add a researcher role to the Profiles model, a Researcher menu item for
> researchers, and a view for creating and rotating API keys for researchers. 

### 0.5 XSS via innerHTML in player.js

`player.js` sets `innerHTML` from story text and LLM-generated text in six places (lines 101, 122,
444, 457, 474, 483, 526). Story text from the database is not sanitized before injection. A story
author whose work is shared could embed `<script>` tags or event handlers that run in any reader's
browser. Use `textContent` for plain narrative text; allow a narrow subset of HTML through a
sanitizer (e.g. DOMPurify) if rich formatting is needed.

---

## 1 — Backend: App Structure (P1)

### 1.1 The `unfold_studio` app is too large

The app that shares its name with the project (`unfold_studio/unfold_studio/`) contains:
- `Story`, `Book`, `StoryError`, `StoryPlayInstance`, `StoryPlayRecord` models
- Compilation logic (calling inklecate, preprocessing ink)
- All CRUD views for stories and books
- Story embedding and embedding entry-point views
- Signup

This is approximately 600 lines in `models.py` and 580 lines in `views.py`. Suggested splits:

| New app | What it contains |
|---|---|
| `stories` | `Story`, `StoryError`, `StoryManager`, compilation, preprocessing, version history views |
| `books` | `Book`, `BookManager`, book CRUD views |
| `story_play` | `StoryPlayInstance`, `StoryPlayRecord`, play instance/record creation views |

The `unfold_studio` app would then shrink to app config, settings, base URLs, and signup.

### 1.2 Confusing name collision

The Django project root and the main app share the name `unfold_studio`. Paths like
`unfold_studio/unfold_studio/models.py` and imports like `from unfold_studio.models import Story`
are ambiguous at a glance. Renaming the app to `studio` or `core` would clarify this without
changing user-visible behavior.

> I thought django projects by convention were expected to have an app of the same name, containing
> core functionality (e.g. wsgi). Is this not the case?

### 1.3 Duplicate app directories at project root

The directories `comments/`, `literacy_events/`, `literacy_groups/`, `profiles/`, and `prompts/`
exist both at the project root (`/Users/chrisp/Repos/unfold_studio/`) and inside the Django source
root (`unfold_studio/`). The project-root copies appear to be empty except for `__pycache__`
generated by Python path resolution. Confirm these are artifacts and remove them to avoid confusion.

> these are certainly artifacts of a git error; remove them. 

### 1.4 Bugs in `StoryManager.editable_for_site_user`

`models.py:80–83` has a duplicated `Q(author=user)` condition and includes `Q(public=True)` in the
editable queryset, allowing any logged-in user to "edit" public stories they don't own. Compare
with `for_site_user` to verify intended semantics and fix.

> The intended semantics are that stories can be:
> - private (owned and only visible to their authors, or to teachers of groups in which which the story was submitted to a prompt)
> - shared (owned and publicly visible)
> - public (created by an unauthenticated user; no owner/author; anyone can edit. These are ephemeral. There should be a management 
>   task to delete public stories older than a specified age.

### 1.5 Duplicate settings configuration

`base_settings.py` and `site_settings/unfold_studio.py` contain mostly the same content (separate
copies of `INSTALLED_APPS`, `MIDDLEWARE`, `AUTH_PASSWORD_VALIDATORS`, etc.). The `site_settings/`
file should import from `base_settings` and only override production values, which is what the
`settings.py` pattern does correctly. Consolidate these two files.

### 1.6 Research endpoint error

`research/views.py:21` uses `status_code=400` (wrong keyword argument). Django's `JsonResponse`
uses `status=`. The current code returns HTTP 200 on errors.

### 1.7 `Story.for_json()` is stale

`models.py:463–475` has a comment "Needs to be updated", commented-out fields, and mixes the old
single-string error format with a new list format in the same response. The field `error_line` is
returned as a list but `error` is returned as a newline-joined string. The client in `app.js`
parses these differently. Standardize on the list format used by the newer code.

### 1.8 Debug artifact in model

`models.py:169`: `self.preprocessed_ink = ink # TODO DEBUG`. This sets a non-field attribute on
the model object during compilation. Remove it.

### 1.9 N+1 query in `Notification.mark_all_seen_for_user`

`literacy_events/models.py:163–166` iterates unseen notifications and saves each one individually.
Replace with `self.filter(recipient=user, seen=False).update(seen=True)`.

### 1.10 `LiteracyEvent` event type constants

Event types are single-character strings (`'0'`, `'1'`, `'b'`, `'c'` …). This is opaque and
difficult to extend. Django's `TextChoices` would give named constants with readable values and
database-level validation.

> Agreed. Propose the names of constants or ask if you need help naming them.

### 1.11 Soft-delete pattern is inconsistent

`Story`, `Book`, `LiteracyGroup`, and `Prompt` all have a `deleted = BooleanField(default=False)`
field managed manually. There is no shared mixin, no signals, and no querysets that automatically
exclude deleted objects. Any queryset that forgets to filter `deleted=False` will silently return
deleted content. Introduce a `SoftDeleteMixin` or use a library like `django-safedelete`.

> All model records should use the soft delete pattern. Propose a consistent way of implementing this. 
> There should also be a management task to truly delete a user and all cascading records. 

### 1.12 `ink_to_json` writes files synchronously

`models.py:310–334` writes ink source to a temp file, shells out to inklecate, and reads the
result—all synchronously during a request. On a slow disk or high load, this blocks the request
worker. Move compilation to a background task (Celery or Django-Q). Provide the client a polling
or WebSocket mechanism for compile results.

> I recognize the value of this proposal, but I want to see more details. Spec out the implications 
> for deployment (including local deployment on dev computers. Additionally, devs can choose to use 
> the staging postgres bindings instead of standing up postgres on their own machines (and to have shared
> db state); would it make sense to also allow devs to use remote staging bindings for the task queue, 
> and presumably also the backend compilation via inklecate? 


### 1.13 Three vendored inklecate binaries

`inklecate_0.8.2/`, `inklecate_1.1.1/`, and `inklecate_1.2.0/` all live in the repository. Only
one is used (configured via `INK_VERSION`). Remove the unused binaries; store the active one as a
tracked dependency or download it in the deployment process.

> Propose what this would look like in the deployment process and in the docs. 

---

## 2 — Frontend: Module System and Bundling (P1)

### 2.1 RequireJS (AMD) is obsolete

The entire front end uses AMD `define([...], function(...) {...})` modules loaded by RequireJS.
RequireJS was the dominant browser module solution ~2012. It has been superseded by ES modules and
modern bundlers. The current setup has no build step, no tree-shaking, and no import resolution
for npm packages.

**Proposal:** Migrate to [Vite](https://vite.dev/) (or esbuild). Vite supports plain ES modules
with `import`/`export`, compiles for browsers with a single command, and integrates naturally with
Django's static files via `vite-plugin-django` or manual manifest wiring. This is a significant
migration but it unblocks all other JS improvements below.

> Agreed. I am ready for a full overhaul of the front-end, and agree with the migration to vite. 
> Should we also migrate to typescript for front-end code? Spec out what this change will entail. 

### 2.2 Entry point uses server-rendered JS

`require_entry_point.js` and `embed_entry_point.js` are Django views that render JavaScript
templates to inject `fetch_story` and `save_story` functions with server-generated URLs. This
tightly couples server-side template rendering to client-side module loading and makes the JS
untestable outside of a running Django server. Replace with data attributes on the HTML `<body>` or
a small `<script>` block that sets configuration variables, then import pure ES modules.

> Give more detail on how this will be implemented. 

---

## 3 — Frontend: Code Editor (P1)

### 3.1 ACE editor is vendored and outdated

The entire ACE source tree is checked into `static/lib/ace_src/` (16 MB, hundreds of files) and
`static/lib/inky/acesrc/` (duplicate). The ink syntax mode in
`static/lib/inky/ace-ink-mode/ace-ink.js` is custom. ACE is functional but has been largely
superseded by [CodeMirror 6](https://codemirror.net/), which:
- Has a leaner, tree-shaking-friendly API
- Performs better on mobile
- Has first-class TypeScript types
- Is actively maintained with a larger ecosystem

**Proposal:** Migrate the code editor to CodeMirror 6 with a custom ink language mode. The custom
ink mode in `ace-ink.js` can serve as a reference for syntax patterns. This simplifies the static
assets substantially and enables a build step that pulls CodeMirror from npm rather than vendoring.

> Agreed. Give more details on implementation.

---

## 4 — Frontend: Player Runtime (P2)

### 4.1 `ink_interface.js` is dead code

`static/scripts/ink_interface.js` (448 lines) is an old hand-written ink interpreter (`InkInterface`,
`InkNode`, `InkProcess`). It pre-dates inkjs and depends on Lodash (`_.each`, `_.any`, etc.). The
production player uses inkjs from `scripts/ink.js`. Confirm `ink_interface.js` is not referenced
anywhere, then delete it along with the Lodash dependency in `static/scripts/lib/`.

### 4.2 `inkfile.js` is broken dead code

`static/inkfile.js` defines `InkFile.prototype = {...}` but never defines `InkFile` as a
constructor. The file is not imported by any active module. Delete it.

### 4.3 `app.js` has a large dead code block

`static/app.js:148–198` is a function named `originalInit` that is never called. It references
`LiveCompiler`, `NavView`, `remote.getCurrentWindow()` (an Electron API), and other objects that
don't exist in the browser context. This appears to be original Inky desktop app code left in
during the web adaptation. Delete it.

### 4.4 Vendored Inky components

`static/lib/inky/` (13 MB) is a copy of the [Inky](https://github.com/inkle/inky) desktop app's
UI source. Many files are unused in the web context:
- `navView.js` — calls Electron's `remote.getCurrentWindow()`
- `liveCompiler.js` — references Electron filesystem APIs
- `goto.js`, `contextmenu.js` — Electron-specific

Review each file and delete those that are not actually imported by the active `app.js` or
`editorView.js` paths.

`static/lib/inky_old/` — confirm this is entirely superseded and delete.

### 4.5 Player has implicit globals

In `player.js`, several variable assignments are missing `const`/`let`/`var`, creating accidental
globals: `response = await this.api...` (line 218), `chosen_choice = ...` (line 493),
`formContainer = this.createInputForm(...)` (lines 235, 253), `content = ...` (line 143), and
others. Use strict mode (`'use strict'`) to catch these, or ESLint with a linter rule.

> Agreed. But I want a debug mode where some globals will be exposed (most important, the story object, 
> but also other objects useful for debugging.) 

### 4.6 jQuery is loaded twice at different versions

`base/base.html` loads `scripts/lib/jquery.2.1.4.js`, and `lib/inky/` includes
`jquery-2.2.3.min.js`. These are both old (current is 3.x). Consolidate to one version and update.
Consider whether jQuery is still needed at all given that the modern `player.js` already uses
`fetch`, `document.createElement`, etc. directly.

> I am open to removing jquery. Provide implementation details.

### 4.7 Player race condition is documented but unresolved

`player.js:60–63` documents a race condition where a generate API call could return before the DOM
element is created. The comment says "in all likelihood this will always work fine" — this is not
a reliable basis for production code. The current approach of storing in `sessionStorage` and using
a MutationObserver as a fallback (in `app.js:121–145`) is a workaround, not a fix. Resolve by
waiting for the DOM element to exist before updating it.

> Agreed. Session storage feels like a messy implementation.

### 4.8 `inkymain.js` — unclear status

`static/scripts/inkymain.js` appears to be a standalone ink story renderer (used externally for
embedding?). Clarify its purpose and whether it overlaps with `embed.js`.

> Investigate this more. What is embed.js for? If we can get rid of these I'm for it. 

---

## 5 — Frontend: Styling (P2)

### 5.1 Multiple disconnected CSS files

The following stylesheets are loaded independently with no shared design system:
- `base/base_style.css` — global styles
- `style/inkystyle.css` — story view
- `style/sms.css` — SMS-format story display
- `lib/inky/main.css` — editor layout (from Inky)
- `lib/inky/inkTheme.css` — ACE editor theme

There are no CSS variables, no component hierarchy, and no documentation of which selectors belong
to which context.

**Proposal:** Consolidate into a single design system using CSS custom properties for colors,
spacing, and typography. If a JS framework is adopted (see §6), a component-scoped styling
approach (CSS modules or Tailwind) would reduce specificity conflicts.

> Agreed. Once the §6 JS framework/build tool proposal is adopted, also propose whether we should
> move to scss, css modules, or tailwind. I'm open to a full style migration to a modern approach, 
> but I'd like to see a principled argument for it. 

---

## 6 — Proposal: JavaScript Framework

The story view (`show_story.html`) has significant UI logic spread across:
- `app.js` (initialization and event wiring)
- `player.js` (ink runtime and DOM rendering)
- `editorView.js` (ACE wrapper)
- inline `<script>` blocks in templates
- jQuery event handlers

This makes the UI hard to reason about and hard to test. A lightweight JS framework would provide
component encapsulation, reactive state, and a cleaner separation between data and presentation.

**Recommendation:** [Alpine.js](https://alpinejs.dev/) for incremental adoption with no build
step, or [Vue 3](https://vuejs.org/) if a build step is introduced (which it should be — see §2.1).
React is also viable but has a steeper migration cost for a project of this size. Svelte is a good
option if the team is comfortable with a compile step and wants minimal runtime overhead.

The player logic in `player.js` is the most complex piece and the best candidate for a first
component: it manages state (running, story point, current choices), renders DOM, and calls APIs.
A reactive component model would make the play session state explicit and testable.

> I want to migrate to vue. Give more details on the implementation here.

---

## 7 — Redundant and Obsolete Assets

| Path | Status | Action |
|---|---|---|
| `static/scripts/ink_interface.js` | Superseded by inkjs | Delete |
| `static/inkfile.js` | Broken, unreferenced | Delete |
| `static/lib/inky_old/` | Superseded by `lib/inky/` | Delete |
| `static/lib/ace_src/` | Vendored source; if ACE is kept, use compiled build only | Delete source, keep build |
| `static/lib/inky/acesrc/` | Second copy of ACE source | Delete |
| `static/lib/inky/jquery-2.2.3.min.js` | Duplicate jQuery | Delete |
| `static/scripts/lib/underscore.1.8.3.js` | Dependency of `ink_interface.js` (dead) | Delete |
| `static/scripts/lib/backbone.1.2.3.js` | Unused | Delete |
| `static/scripts/lib/d3.3.5.9.js` | Unused | Delete |
| `static/scripts/lib/jsgame/` | Unused game library | Delete |
| `static/scripts/lib/qunit-*` | Test runner vendored in static | Move to dev tooling |
| `static/scripts/randomstring.js` | Check if referenced | Audit and delete if not |
| `static/scripts/inkymain.js` | Role unclear | Clarify or delete |
| `inklecate_0.8.2/` | Old version | Delete |
| `inklecate_1.1.1/` | Old version | Delete |
| `results.csv` | Data file at project root | Relocate or delete |
| `app.js:originalInit` | Dead code block | Delete |

---

## 8 — Code Quality (P2)

### 8.1 `print()` in production views

`text_generation/views.py` has 7 active `print()` calls and 4 commented-out `#print()` calls.
These bypass the structlog setup that the rest of the app uses. Replace with `log.debug()` or
`log.info()` and delete commented-out prints. The project already imports `structlog` at the top
of the file.

`text_generation/flows/story_evaluation_flow.py` has `print("hi")` — this is development
scaffolding.

### 8.2 Bare `except` and wide exception swallowing

`text_generation/views.py:196`: `except Exception as e: print(str(e))` swallows all exceptions and
returns a 500. The exception detail is printed but not logged through structlog, so it won't appear
in structured logs.

`research/views.py:18`: `except:` (bare, no exception type) swallows everything including
`SystemExit` and `KeyboardInterrupt`.

Use specific exception types and log with `log.exception()` which captures the full traceback.

> Yes. Additionally, I'd like to migrate to structlog across the board, and generally adopt modern logging. 
> Update this proposal with implementation details.

### 8.3 Commented-out code blocks

Several files contain significant commented-out code rather than using version control to recover
old logic:
- `views.py:192, 273, 309, 334` — commented `messages.success(...)` calls
- `player.js:187–203` — `logPath` function body commented out
- `player.js` — multiple commented-out `ChoosePathString` calls
- `base_settings.py:164` — `"memoize": False` with reference to commented config

Remove commented code; version control provides the history.

### 8.4 Typos in production strings

`text_generation/views.py:94`: `"Unexpected error occured"` (misspelled: "occurred")
`text_generation/views.py:143`: `"Exception occoured"` (doubly misspelled)

> Yes, but more systematically, I want to adopt internationalization. Propose what this will entail.

### 8.5 Inline JavaScript in base template

`base/base.html:31–37` contains jQuery-based delete-confirm logic that runs globally on every
page. This assumes `#delete`, `#delete_prompt`, and `#delete_confirm` elements may or may not
exist on any given page. Move this logic to the specific template that uses it.

### 8.6 `setBook()` is a global JS function in a template

`show_story.html:76–81` defines `setBook` as a global function in an inline `<script>`. Globals
pollute `window` and are fragile. Move this to a module or data-attribute pattern.

> What is this function doing? I suspect it should not exist. Investigate and update. 

---

## 9 — Testing Gaps

The test coverage is sparse. Notable gaps:

- `unfold_studio/tests/test_story_compilation.py` — exists but check that preprocessing edge
  cases are covered (circular includes, missing includes, variable shadowing)
- No tests for `text_generation/views.py` (`GenerateTextView`, `GetNextDirectionView`)
- `generated_text_evaluator/tests.py` exists but may be empty (file listed alongside a `tests/`
  directory — confirm which is authoritative)
- No front-end tests. Once the module system is modernized, add Vitest or Jest for player logic.
- Integration tests in `integration_tests/` are Selenium-based and require a live server.
  Good to have, but they should be supplemented by unit tests that don't require a browser.

---

## 10 — Infrastructure and Settings

### 10.1 `DEBUG=True` is the default

`base_settings.py:25`: `DEBUG = True`. Any deployment that fails to override this will run in
debug mode, which exposes stack traces. The default should be `DEBUG = False`; explicitly set
`DEBUG = True` only in development.

### 10.2 `static_assets/` should be in `.gitignore`

`static_assets/` is the `STATIC_ROOT` target for `collectstatic`. Generated files should not be
committed. Confirm it is in `.gitignore`.

### 10.3 Settings duplication: `base_settings.py` vs `site_settings/unfold_studio.py`

These two files are mostly parallel copies. The intent seems to be:
- `base_settings.py` → shared defaults
- `site_settings/unfold_studio.py` → production overrides for unfold.studio
- `settings.py` → local dev overrides

But `site_settings/unfold_studio.py` duplicates nearly everything from `base_settings.py` rather
than importing from it. Consolidate: `site_settings/unfold_studio.py` should be:
```python
from unfold_studio.base_settings import *
# then only production overrides
```
> I believe this duplicates an issue noted above. If so, merge them. If not, explain why they are different. 


### 10.4 `conftest.py` is misplaced

`unfold_studio/conftest.py` is at the Django project root but pytest is run from there, so it
works. However, there are also app-level test files (`comments/tests.py`, etc.) that are empty
stubs. Establish a consistent test layout.

> Agreed. Propose more details here.

# Unfold Studio — Refactor Plan v1

Issues are marked **P0** (fix now), **P1** (fix soon), **P2** (fix when touching the area), or
**Proposal** (worthwhile but not required). Blockquoted sections are open questions for the next
review round.

---

## 0 — Critical Security (P0)

### 0.1 Committed API key and secret key

The OpenAI API key that was in `settings.py` has been revoked. Remaining work:

1. Remove the key from `settings.py` and purge it from git history using `git filter-repo` or BFG
   Repo Cleaner.
2. Replace `SECRET_KEY` in `base_settings.py` and `site_settings/unfold_studio.py` with
   `os.environ['SECRET_KEY']`.
3. Replace the `api_key` field in the `TEXT_GENERATION` settings dict with
   `os.environ['OPENAI_API_KEY']`.
4. Update `DeploymentReadme.md` to document all required environment variables with a table like:

   | Variable | Description | Where to get it |
   |---|---|---|
   | `SECRET_KEY` | Django secret key | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
   | `OPENAI_API_KEY` | OpenAI API key | OpenAI dashboard |
   | `DATABASE_URL` | Postgres connection string | Hosting provider |

### 0.2 CORS and story embedding

`CORS_ORIGIN_ALLOW_ALL = True` was set to make story embedding on external pages work. The right
fix is to replace the current embed mechanism with a dedicated embed route that eliminates the need
for wide-open CORS.

**Proposed feature: `/stories/{id}/embed`**

Create a new route and view that renders the story player without the site menu, footer, or
editor—just the play pane. External sites embed this with a standard `<iframe>`:

```html
<iframe src="https://unfold.studio/stories/9215/embed"
        width="600" height="500" frameborder="0">
</iframe>
```

Because the player page and all its API calls (`/stories/{id}/json/`, `/generate`, etc.) are
served from the same origin (`unfold.studio`), no CORS headers are needed at all—the browser sees
everything as same-origin within the iframe. This is cleaner and more secure than the current
RequireJS-based embed.

The embed view should:
- Require the story to be shared or public (same visibility rules as regular viewing)
- Render only the player pane with minimal chrome (perhaps a small "Powered by Unfold Studio"
  footer with a link)
- Be read-only (no Save, Fork, or Share controls)

`CORS_ORIGIN_ALLOW_ALL` can then be removed from both settings files. The current embed system
(RequireJS + `embed_entry_point.js`) is documented as "a bit messy" in the user guide and will be
deprecated as part of the front-end rewrite (§2).

### 0.3 Unauthenticated story-play tracking endpoints

`CreateStoryPlayInstanceView` and `CreateStoryPlayRecordView` have no authentication check. Any
script can create arbitrary play records against any story. Add a check: the story referenced must
be publicly playable (shared or public), and if the user is authenticated, record their identity;
if anonymous, allow the record but mark it accordingly. A more hardened approach would require a
session-scoped token, but that is out of scope for the initial fix.

### 0.4 CSRF-exempt research endpoint

The `research/views.py` compile endpoint uses `@csrf_exempt`. The fix is to require an API key
on all research endpoints.

**Proposed feature: Researcher role and API key management**

1. **Researcher role on Profile.** Add `is_researcher = BooleanField(default=False)` to
   `profiles/models.py` (parallel to `is_teacher`). Researchers are managed by admins via the
   Django admin panel.

2. **`APIKey` model in the `research` app.** Fields: `key` (random 40-char hex, generated on
   creation), `owner` (FK to User), `created_at`, `last_used_at`, `revoked` (BooleanField).
   Keys are sent in an `Authorization: Bearer <key>` header.

3. **API key views.** A `ResearcherAPIKeyView` (login required + researcher required) shows the
   researcher's current key and offers a "Rotate key" button (which revokes the old key and
   generates a new one). Accessible from a "Researcher" menu item visible only to researchers.

4. **Authentication decorator.** A `require_api_key` decorator checks the `Authorization` header,
   looks up the key, verifies `revoked=False`, and updates `last_used_at`. Replace `@csrf_exempt`
   with `@require_api_key` on all research endpoints.

5. **Update `DeploymentReadme.md`** with instructions for granting researcher status via the admin
   panel.

### 0.5 XSS via innerHTML in player.js

`player.js` sets `innerHTML` from story text and LLM-generated text at six insertion points (lines
101, 122, 444, 457, 474, 483, 526). A shared story could include `<script>` tags or event handlers
that run in any reader's browser.

Fix: Use `textContent` for all narrative text output. For LLM-generated text (which may
legitimately contain simple formatting), pass content through
[DOMPurify](https://github.com/cure53/DOMPurify) before insertion. DOMPurify strips dangerous
tags and event handlers while preserving safe HTML like `<em>`, `<strong>`, and `<a>`. Add it as
an npm dependency once the Vite build is in place (§2.1).

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

### 1.2 App name collision with project

Django does not require an app to share the project name. The `wsgi.py`, `urls/base.py`, and
`base_settings.py` are part of the *project package* (the Python package at
`unfold_studio/unfold_studio/`), not a Django app. The `AppConfig` in `apps.py` does make it a
registered Django app too, but that is not necessary.

Renaming the app from `unfold_studio` to `studio` or `core` would make imports like
`from studio.models import Story` unambiguous, and paths like `studio/models.py` readable at a
glance. The project package (settings, wsgi, root URLs) keeps the name `unfold_studio`.

This is a low-risk rename (no database table names change if `app_label` is set explicitly) but
it touches many import statements. Tag it as part of the 1.1 app split to do in one pass.

### 1.3 Artifact directories at project root

The directories `comments/`, `literacy_events/`, `literacy_groups/`, `profiles/`, and `prompts/`
at the project root are `__pycache__`-only artifacts from a git error. Remove them:

```
git rm -r --cached comments/ literacy_events/ literacy_groups/ profiles/ prompts/
```

Confirm `.gitignore` includes `__pycache__/` and `*.pyc`.

### 1.4 Bug in `StoryManager.editable_for_site_user` and story visibility semantics

The intended visibility/editability model:

| Story type | How created | Who can view | Who can edit |
|---|---|---|---|
| Private | Logged-in user, not shared | Author; group leaders of prompts story is submitted to | Author only |
| Shared | Logged-in user, marked shared | Everyone | Author only |
| Public | Anonymous user (no author) | Everyone | No one — public stories are ephemeral |

The current `editable_for_site_user` has two bugs:
- `Q(author=user)` appears twice (one is redundant)
- `Q(public=True)` allows any logged-in user to edit public stories, which are authorless

Fix: remove the duplicate condition and remove `Q(public=True)` from
`editable_for_site_user`. Public (anonymous) stories are not editable by logged-in users; readers
who want to keep a public story should fork it.

**Also add:** a management command `delete_old_public_stories` that hard-deletes public stories
older than a configurable age (default 30 days). Add a `PUBLIC_STORY_MAX_AGE_DAYS = 30` setting.

### 1.5 Duplicate settings configuration (P1) ← merged from §10.3

`base_settings.py` and `site_settings/unfold_studio.py` are nearly full duplicates. There are
three settings contexts:

- `base_settings.py` → shared defaults (development-safe)
- `site_settings/unfold_studio.py` → production overrides for unfold.studio
- `settings.py` → local dev overrides

The fix: `site_settings/unfold_studio.py` should begin with
`from unfold_studio.base_settings import *` and then only override production-specific values
(`DEBUG = False`, `ALLOWED_HOSTS`, `DATABASES`, `STATIC_ROOT`, etc.). Currently it redeclares the
full `INSTALLED_APPS`, `MIDDLEWARE`, `AUTH_PASSWORD_VALIDATORS`, and many other lists from scratch.

### 1.6 Research endpoint bug

`research/views.py:21` uses `status_code=400` (wrong keyword). Django's `JsonResponse` uses
`status=`. The current code silently returns HTTP 200 on malformed requests. Fix to `status=400`.

### 1.7 `Story.for_json()` is stale

`models.py:463–475` has a comment "Needs to be updated", commented-out fields, and mixes formats:
`error` is a newline-joined string but `error_line` is a list. Standardize: remove the
single-string `error` field, expose `errors` as a list of `{line, message}` objects, and update
`app.js` / `player.js` to consume the new format.

### 1.8 Debug artifact in model

`models.py:169`: `self.preprocessed_ink = ink # TODO DEBUG` sets a transient non-field attribute
during compilation. Remove it.

### 1.9 N+1 query in `Notification.mark_all_seen_for_user`

`literacy_events/models.py:163–166` iterates and saves each unseen notification individually.
Replace with:
```python
self.filter(recipient=user, seen=False).update(seen=True)
```

### 1.10 `LiteracyEvent` event type constants

Event types are opaque single-character strings. Migrate to `TextChoices` with readable values.
Proposed mapping:

| Current value | Proposed TextChoices name | Proposed db value |
|---|---|---|
| '0' | `LOVED_STORY` | `'loved_story'` |
| '1' | `COMMENTED` | `'commented'` |
| '2' | `FORKED` | `'forked'` |
| '3' | `PUBLISHED_STORY` | `'published_story'` |
| 'b' | `UNPUBLISHED_STORY` | `'unpublished_story'` |
| '4' | `PUBLISHED_BOOK` | `'published_book'` |
| '5' | `ADDED_TO_BOOK` | `'added_to_book'` |
| '9' | `REMOVED_FROM_BOOK` | `'removed_from_book'` |
| '6' | `FOLLOWED` | `'followed'` |
| 'a' | `UNFOLLOWED` | `'unfollowed'` |
| '8' | `SIGNED_UP` | `'signed_up'` |
| 'c' | `CREATED_PROMPT` | `'created_prompt'` |
| 'd' | `SUBMITTED_TO_PROMPT` | `'submitted_to_prompt'` |
| 'e' | `REMOVED_FROM_PROMPT` | `'removed_from_prompt'` |
| 'f' | `READ_STORY` | `'read_story'` |
| 'g' | `PUBLISHED_PROMPT_AS_BOOK` | `'published_as_book'` |
| 'h' | `UNPUBLISHED_PROMPT_BOOK` | `'unpublished_book'` |
| 'i' | `TAGGED_VERSION` | `'tagged_version'` |
| 'j' | `JOINED_GROUP` | `'joined_group'` |
| 'k' | `LEFT_GROUP` | `'left_group'` |

This requires a data migration to update existing rows.

### 1.11 Soft-delete pattern (Proposal)

`Story`, `Book`, `LiteracyGroup`, and `Prompt` all use `deleted = BooleanField(default=False)`
managed manually with no shared enforcement.

**Proposed `SoftDeleteMixin`:**

```python
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)

class SoftDeleteMixin(models.Model):
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # bypasses soft-delete filter

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True
```

All models with `deleted` fields inherit from `SoftDeleteMixin`. The `all_objects` manager is used
only in admin views and management commands where deleted records need to be visible.

**Also add:** a management command `purge_deleted_records` that permanently removes records that
have been soft-deleted for longer than a configurable threshold (default 90 days). This command
also handles cascade-purging all related records (stories, literacy events, notifications, etc.)
for a given user.

**User deletion:** A separate `delete_user` management command:
1. Anonymizes or deletes the user's personal data (email, bio)
2. Soft-deletes all stories, book memberships, group memberships, and prompt submissions
3. Removes the user's `Profile` and `User` records
4. Preserves literacy events as anonymous historical records (for research integrity)

> Should deleted records be kept indefinitely until explicitly purged, or should the soft-delete
> retention period be automatic (e.g. always purge after 90 days)? The `purge_deleted_records`
> command above can be run on a schedule, but it may be simpler to auto-purge in the
> `delete()` method itself via a background task.

### 1.12 Synchronous ink compilation (Proposal)

`models.py:310–334` writes ink to a temp file, shells out to inklecate, and reads the
result—all synchronously inside a request. This blocks a request worker for the duration of
compilation (typically ~1–2 seconds).

**Option A — Async with Celery (recommended for production scale)**

Add [Celery](https://docs.celeryq.dev/) with a Redis or RabbitMQ broker. Compilation becomes a
background task; the client polls or uses a WebSocket to receive results.

*Local development:* Run `celery -A unfold_studio worker` alongside `manage.py runserver`.
Developers who prefer not to run Redis locally can set `CELERY_TASK_ALWAYS_EAGER = True` in
`settings.py`, which executes tasks synchronously in the same process (preserving current
behavior). Devs using the staging database can also point at a shared staging Celery worker by
setting `CELERY_BROKER_URL` to the staging Redis, though this is only advisable for one developer
at a time.

*Client side:* When the user saves, the editor posts ink to `/stories/{id}/compile/`, which
immediately returns `{"status": "compiling", "task_id": "..."}`. The client polls
`/stories/{id}/compile/{task_id}/status/` until it receives `{"status": "ok", ...}` or
`{"status": "error", ...}`. A 2-second polling interval is sufficient.

*Deployment additions:* A Celery worker process alongside the Django web process. Document in
`DeploymentReadme.md`.

**Option B — Async threads without Celery (simpler, lower scale)**

Use `concurrent.futures.ThreadPoolExecutor` with a bounded pool to run inklecate off the request
thread. Return a task ID; the client polls a lightweight status endpoint. No additional
infrastructure. Suitable for low-to-moderate load but not robust (workers restart with the process,
tasks are lost on deploy).

**Option C — Keep synchronous, add timeout and better error handling (minimal change)**

Keep compilation synchronous but wrap `subprocess.check_output` with a timeout (e.g., 10 seconds)
and add appropriate error handling. Document this as a known limitation. Appropriate if scale is
not currently a concern.

> Which option is right depends on expected load and infrastructure appetite. Option C requires
> minimal work. Option A gives the best production behavior but adds Redis as a dependency.
> Which do you prefer?

### 1.13 Vendored inklecate binaries

Three inklecate versions live in the repo; only one is used. Remove the unused two
(`inklecate_0.8.2/`, `inklecate_1.1.1/`) immediately. For the active binary:

**Proposed deployment approach:** Download the binary at deploy time rather than committing it.

Add a `scripts/install_inklecate.sh`:
```bash
#!/usr/bin/env bash
VERSION=${INK_VERSION:-1.2.0}
OS=$(uname -s)
if [ "$OS" = "Darwin" ]; then PLATFORM="mac"; else PLATFORM="linux"; fi
curl -L "https://github.com/inkle/ink/releases/download/v${VERSION}/inklecate_${PLATFORM}.zip" \
  -o /tmp/inklecate.zip
unzip -o /tmp/inklecate.zip -d "inklecate_${VERSION}/"
chmod +x "inklecate_${VERSION}/inklecate"
```

Add this script to the deployment runbook and to CI. Local dev instructions: run
`./scripts/install_inklecate.sh` once after cloning. `DeploymentReadme.md` should document this
as a setup step.

---

## 2 — Frontend: Module System and Bundling (P1)

### 2.1 Migrate from RequireJS to Vite with TypeScript

The entire front end uses AMD `define([...], function(...) {...})` modules loaded by RequireJS
(circa 2012). Migrate to [Vite](https://vite.dev/) with TypeScript.

**Why TypeScript?** The player, story, and API modules manage complex stateful interactions. Type
annotations will catch the class of bugs currently present (implicit globals, wrong argument
types, missing null checks). The migration can be incremental: TypeScript accepts plain `.js`
files, so files can be converted one at a time.

**Migration plan:**

1. Add a `package.json` at `unfold_studio/` (the Django project root). Install:
   `vite`, `typescript`, `vue`, `@vitejs/plugin-vue`, `dompurify`, `@types/dompurify`.

2. Create `vite.config.ts` with Django integration. Vite will build to
   `unfold_studio/static/dist/` with a manifest. During development, Vite's dev server proxies
   asset requests; in production, `collectstatic` copies the built `dist/` into `STATIC_ROOT`.

   ```ts
   // vite.config.ts
   import { defineConfig } from 'vite'
   import vue from '@vitejs/plugin-vue'

   export default defineConfig({
     plugins: [vue()],
     build: {
       manifest: true,
       outDir: 'static/dist',
       rollupOptions: {
         input: {
           app: 'src/main.ts',          // story editor/player
           embed: 'src/embed.ts',       // embed player (§0.2)
         }
       }
     }
   })
   ```

3. A Django template tag reads `static/dist/manifest.json` to resolve hashed asset filenames:
   ```html
   {% vite_asset 'src/main.ts' %}
   ```
   This is a simple custom tag (~20 lines); no third-party package required.

4. During development, run `vite build --watch` (or `vite` dev server) alongside
   `manage.py runserver`. Add both commands to a `Makefile` or `Procfile`.

5. Convert files in order of complexity (low to high): `story.js` → `player.js` → new Vue
   components. Completed files get the `.ts` extension; AMD `define()` wrappers are replaced with
   ES `import`/`export`.

**What goes away:** RequireJS (`static/lib/require/`), all AMD `define()` wrappers, the
`require_entry_point.js` and `embed_entry_point.js` Django views (see §2.2).

### 2.2 Replace server-rendered JS entry points

Currently `require_entry_point.js` and `embed_entry_point.js` are Django views that render
JavaScript templates—injecting server-generated URLs and defining AMD modules. This couples Django
URL resolution to client-side module loading and makes the JS untestable outside of a running
server.

**Replacement:** Pass configuration to the client via a `<script>` block in the Django template,
then load a pure ES module.

```html
{# show_story.html #}
<script>
  window.__UNFOLD__ = {
    storyId: {{ story.id }},
    csrfToken: "{{ csrf_token }}",
    editable: {{ editable|lower }},
    urls: {
      json:            "{% url 'show_json' story.id %}",
      compile:         "{% url 'compile_story' story.id %}",
      generate:        "{% url 'generate' %}",
      getNextDir:      "{% url 'get_next_direction' %}",
      playInstance:    "{% url 'new_story_play_instance' %}",
      playRecord:      "{% url 'new_story_play_record' %}",
    }
  };
</script>
{% vite_asset 'src/main.ts' %}
```

The TypeScript modules import nothing from Django; they read `window.__UNFOLD__` for runtime
values and use `fetch()` directly. The Django URL names are resolved once at page render, not
hard-coded in JS.

The two Django views (`require_entry_point`, `embed_entry_point`) and their URL entries are
deleted. The templates `require_entry_point.js` and `embed_entry_point.js` are deleted.

---

## 3 — Frontend: Code Editor (P1)

### 3.1 Migrate from ACE to CodeMirror 6

The ACE source tree is vendored in `static/lib/ace_src/` (16 MB) with a duplicate in
`static/lib/inky/acesrc/`. ACE is functional but superseded by
[CodeMirror 6](https://codemirror.net/), which has a leaner tree-shakeable API, TypeScript types,
and active maintenance.

**Implementation:**

1. Install via npm: `@codemirror/state`, `@codemirror/view`, `@codemirror/basic-setup`,
   `@codemirror/language`, `@codemirror/commands`, `@codemirror/theme-one-dark` (or similar).

2. Write a custom Ink language mode using CodeMirror's `StreamLanguage` adapter. The existing
   `static/lib/inky/ace-ink-mode/ace-ink.js` defines the token set and can be ported directly.
   Key token types to preserve:
   - Keywords: `VAR`, `CONST`, `LIST`, `EXTERNAL`, `INCLUDE`, `->`, `<->`
   - Knot headers: `=== name ===`
   - Stitch headers: `= name`
   - Choice markers: `+`, `*`
   - Fallback choices: `-`
   - Comments: `//`, `/* */`
   - String literals, tags (`# tag`)

3. Replace the `EditorView` class in `static/lib/inky/editorView.js` with a Vue component
   (`<StoryEditor>`). The component exposes the editor content via `v-model` and emits compile
   events (§6).

4. Delete `static/lib/ace_src/`, `static/lib/inky/acesrc/`, and the Inky ACE mode
   (`static/lib/inky/ace-ink-mode/`).

---

## 4 — Frontend: Player Runtime (P2)

### 4.1 Delete `ink_interface.js`

`static/scripts/ink_interface.js` (448 lines) is an old hand-written ink interpreter that predates
inkjs. It is not imported by any active module. Confirm with `grep -r "ink_interface"`, then
delete along with its Lodash dependency (`static/scripts/lib/underscore.1.8.3.js`).

### 4.2 Delete `inkfile.js`

`static/inkfile.js` sets `InkFile.prototype` on an undefined constructor and is not imported
anywhere. Delete it.

### 4.3 Delete `app.js::originalInit`

`static/app.js:148–198` is an unreachable function referencing Electron APIs (`remote`,
`LiveCompiler`, `NavView`). Delete the `originalInit` property and its body.

### 4.4 Audit and trim vendored Inky components

`static/lib/inky/` (13 MB) is a copy of the Inky desktop app's UI source. Files that reference
Electron APIs are dead code in the browser context:
- `navView.js` — calls `remote.getCurrentWindow()`
- `liveCompiler.js` — references Electron filesystem
- `goto.js`, `contextmenu.js` — Electron-specific menus

Delete `static/lib/inky_old/` entirely. For `static/lib/inky/`, delete each file not reachable
from the active `app.js` import graph. After the Vue migration (§6), the surviving Inky files
(primarily `editorView.js`, `split.js`) will be replaced by Vue components and can be deleted.

### 4.5 Player implicit globals and debug mode

`player.js` has multiple implicit global assignments (`response`, `chosen_choice`, `formContainer`,
`content`, etc.). Fix by adding `'use strict'` at the top of each file and declaring all
variables with `const`/`let`. ESLint with `no-undef` will catch remaining issues as part of the
Vite migration.

**Debug mode:** Add a `debugMode` option to the player that, when true, attaches key objects to
`window` for browser console inspection:
```js
if (config.debugMode) {
  window.__UNFOLD_DEBUG__ = { player: this, story: this.story };
}
```
`debugMode` is set from `window.__UNFOLD__.debugMode`, which Django templates can enable when
`settings.DEBUG` is true.

### 4.6 Remove jQuery

jQuery is used for `$.ajax()`, `$(selector).hide()`, and a few DOM utilities. With the Vue/Vite
migration, all of these have modern replacements:

| jQuery pattern | Replacement |
|---|---|
| `$.ajax(url, opts)` | `fetch(url, opts)` |
| `$(el).html('')` | `el.innerHTML = ''` |
| `$(el).scrollTop()` | `el.scrollTop` |
| `$(el).height()` | `el.offsetHeight` |
| `$(el).hide()` / `.show()` | Vue `v-show` or `el.style.display` |
| `$(function() {...})` | `DOMContentLoaded` or Vue `mounted()` |

jQuery removal is a natural byproduct of the Vue migration (§6) rather than a separate step.
Both jQuery files (`static/scripts/lib/jquery.2.1.4.js`,
`static/lib/inky/jquery-2.2.3.min.js`) are deleted once the migration is complete.

### 4.7 Generate race condition and sessionStorage

The `generate()` external function stores LLM output in `sessionStorage` as a backup in case the
loading-span DOM element is not found when the response arrives. This is unnecessary: the loading
span is appended to the DOM *synchronously* before the API call starts, so
`document.getElementById(nonce)` will always find it when the response arrives.

Fix: remove the `sessionStorage` read/write in `generateAndInsertInDOM` and the MutationObserver
fallback in `app.js`. Keep only the direct `el.innerHTML = data.result` update. Add a
`console.warn` if the element is not found, as a canary for future regressions.

### 4.8 Embed system: `embed.js` and `inkymain.js`

**`embed.js`** is the RequireJS module that the current story-embedding system uses.
`embed_entry_point.js` (a server-rendered Django template) configures RequireJS, defines a
`Story` AMD module with a cross-origin URL for the JSON endpoint, and then loads `embed.js`. This
is what external sites use today (documented in the user guide as "a bit messy").

**`inkymain.js`** is an IIFE that accepts inline story content as an argument. It is not
referenced anywhere in the app or the documentation site. It appears to be a reference
implementation from Inkle that was never integrated. Delete it.

After the `/stories/{id}/embed` route is built (§0.2) and the Vite migration is done (§2.1), the
new embed system is an `embed.ts` entry point compiled by Vite that hydrates a Vue
`<EmbedPlayer>` component. The old `embed.js`, `embed_entry_point.js`, and the RequireJS-based
embed instructions in the user guide are deprecated and removed.

---

## 5 — Frontend: Styling (P2)

### 5.1 Consolidate CSS

The following disconnected stylesheets have no shared design system:
- `base/base_style.css` — global styles
- `style/inkystyle.css` — story view
- `style/sms.css` — SMS-format story display
- `lib/inky/main.css` — editor layout (from Inky)
- `lib/inky/inkTheme.css` — ACE editor theme

**Proposed approach (to be adopted as part of the Vue migration):**

Use Vue's [Scoped CSS](https://vuejs.org/api/sfc-css-features.html) for component-level styles
within `.vue` files. Use CSS custom properties (variables) in a shared `tokens.css` for colors,
spacing, and typography, imported once in `src/main.ts`. This gives component isolation without
the weight of a full CSS-in-JS solution.

Against Tailwind: Tailwind is powerful but requires learning a new vocabulary and makes templates
visually noisy. For a project of this size and community context (students and researchers, not
frontend engineers), plain CSS with custom properties is lower friction and more readable.

Against SCSS: SCSS adds a compilation step and a preprocessor dependency for features (nesting,
variables) now available in plain CSS. Not necessary with Vite in the toolchain.

The ACE theme (`inkTheme.css`) and editor layout (`main.css`) are replaced by CodeMirror's
theming system and Vue component CSS when the editor is migrated (§3.1).

---

## 6 — Vue 3 Migration (P1)

### 6.1 Rationale and scope

The story view has UI logic spread across `app.js`, `player.js`, `editorView.js`, inline
`<script>` blocks, and jQuery handlers. Vue 3's component model provides:
- **Encapsulated state:** The player's running state, story point, choices, and AI seed become
  reactive `ref()`/`reactive()` values rather than object properties on an ad-hoc prototype.
- **Testable components:** Vue components are unit-testable with Vitest without a browser.
- **Cleaner templates:** Conditional display (`v-show`/`v-if`), event handling (`@click`), and
  list rendering (`v-for`) replace jQuery DOM manipulation.

### 6.2 Component architecture

```
<StoryPage>               # top-level page component (show_story.html)
  <StoryEditor>           # CodeMirror editor, emits save/compile events
  <StoryPlayer>           # ink runtime, receives compiled story JSON
    <ChoiceList>          # renders current choices
    <TextEntry>           # renders input() / continue() prompts
    <NarrativeBlock>      # renders a single text block with tag-based styling
  <StoryToolbar>          # save, share, fork, show/hide code buttons

<EmbedPlayer>             # standalone player for /stories/{id}/embed (§0.2)
  <StoryPlayer>           # reused
```

### 6.3 Migration sequence

1. **Setup:** Add Vite + Vue (§2.1). No existing code is changed yet.
2. **Player first:** Rewrite `player.js` as `<StoryPlayer>` Vue component in TypeScript. This is
   the most complex piece and where bugs live. Run the old and new players in parallel on a
   feature branch to compare behavior.
3. **Editor:** Rewrite `editorView.js` as `<StoryEditor>` using CodeMirror 6 (§3.1).
4. **Toolbar:** Replace inline `<script>` handlers (Save, Fork, Share, etc.) with `<StoryToolbar>`
   component.
5. **Embed player:** Build `<EmbedPlayer>` as part of the `/stories/{id}/embed` route (§0.2).
6. **Delete:** Remove RequireJS, old JS files, and server-rendered entry point views (§2.2).

### 6.4 State management

[Pinia](https://pinia.vuejs.org/) is Vue 3's recommended state store. Use it for state shared
between components (e.g., the compiled story JSON, which both `<StoryEditor>` and `<StoryPlayer>`
need). Simple component-local state stays in component `ref()`s.

---

## 7 — Redundant and Obsolete Assets

| Path | Status | Action |
|---|---|---|
| `static/scripts/ink_interface.js` | Superseded by inkjs | Delete (§4.1) |
| `static/inkfile.js` | Broken, unreferenced | Delete (§4.2) |
| `static/scripts/inkymain.js` | Unreferenced; role filled by embed.js | Delete (§4.8) |
| `static/lib/inky_old/` | Superseded by `lib/inky/` | Delete (§4.4) |
| `static/lib/ace_src/` | Vendored ACE source (16 MB) | Delete when CodeMirror adopted (§3.1) |
| `static/lib/inky/acesrc/` | Second copy of ACE source | Delete (§3.1) |
| `static/lib/inky/ace-ink-mode/` | ACE ink mode | Delete (§3.1) |
| `static/lib/inky/jquery-2.2.3.min.js` | Duplicate jQuery | Delete (§4.6) |
| `static/lib/require/` | RequireJS | Delete (§2.1) |
| `static/scripts/lib/jquery.2.1.4.js` | Old jQuery | Delete (§4.6) |
| `static/scripts/lib/underscore.1.8.3.js` | Dependency of dead code | Delete (§4.1) |
| `static/scripts/lib/backbone.1.2.3.js` | Unused | Delete |
| `static/scripts/lib/d3.3.5.9.js` | Unused | Delete |
| `static/scripts/lib/jsgame/` | Unused game library | Delete |
| `static/scripts/lib/qunit-*` | Test runner vendored in static | Move to npm dev dependency |
| `static/scripts/randomstring.js` | Not imported by active modules | Audit; delete if unused |
| `app.js::originalInit` | Dead code block | Delete (§4.3) |
| `inklecate_0.8.2/` | Old version | Delete (§1.13) |
| `inklecate_1.1.1/` | Old version | Delete (§1.13) |
| `results.csv` | Data file at project root; unclear purpose | Relocate or delete |

---

## 8 — Code Quality (P2)

### 8.1 `print()` in production code

`text_generation/views.py` has 7 active `print()` calls and 4 commented-out `#print()` calls.
`text_generation/flows/story_evaluation_flow.py` has `print("hi")` — development scaffolding.
Replace all with structlog calls and delete commented-out prints (see §8.2).

### 8.2 Structured logging with structlog

The project imports structlog in some places but uses bare `print()` in others. Adopt structlog
consistently.

**Implementation:**

1. `base_settings.py`: Add a `LOGGING` dict that routes structlog output to stdout (JSON in
   production, human-readable in development). The `django_structlog` middleware (already
   installed) adds `request_id` and `user_id` to every log entry automatically.

2. Every module that logs should have:
   ```python
   import structlog
   log = structlog.get_logger(__name__)
   ```

3. Replace:
   - `print(...)` → `log.debug(...)` or `log.info(...)` with structured kwargs
   - `except Exception as e: print(str(e))` → `log.exception("context message")` (captures full
     traceback automatically)
   - Bare `except:` → `except Exception:` minimum; log with `log.exception()`

4. Audit `text_generation/views.py` (most `print()` calls), `research/views.py` (bare `except:`),
   and `text_generation/flows/`.

5. Development: add `structlog[dev]` to display colored, human-readable log output locally.

### 8.3 Remove commented-out code

Version control provides history. Delete:
- `views.py:192, 273, 309, 334` — commented `messages.success(...)` calls
- `player.js:187–203` — commented-out `logPath` function body
- `player.js` — commented-out `ChoosePathString` calls
- `base_settings.py:164` — `"memoize": False` with surrounding context

### 8.4 Internationalization (Proposal)

> The request to adopt i18n was raised in the context of fixing string typos, so I want to clarify
> scope before speccing this out. Two options:
>
> **Option A — Full i18n (multi-language support):** Use Django's `gettext` framework: wrap all
> user-facing strings in `_()`, run `makemessages` to extract them into `.po` files, and provide
> translated `.po` files for each language. This is significant ongoing work (every new string must
> be wrapped; translators must maintain `.po` files). Recommended if Unfold Studio will serve
> non-English-speaking communities.
>
> **Option B — Better English string management:** Systematically move hardcoded user-facing
> strings out of Python and JS logic into a central location (Django message strings in templates,
> a `messages.py` constants file, or Vue i18n with a single English locale file). This prevents
> typos, inconsistency, and duplication without requiring translation infrastructure.
>
> Which are you aiming for?

### 8.5 Inline JavaScript in base template

`base/base.html:31–37` has jQuery-based delete-confirm logic that runs globally on every page.
Move this to the specific template that uses it, or (after the Vue migration) to a
`<ConfirmDelete>` component.

### 8.6 `setBook()` inline function

The `setBook(el)` function in `show_story.html` updates the "Add to Book" form's action URL when
a user picks a different book from the dropdown. The form is pre-generated with URL
`/books/{first_book_id}/add/{story_id}/`, and `setBook` rewrites `urlParts[4]` (the book ID
position) when selection changes. This is fragile: it depends on the URL segment position staying
stable.

Fix: change the "Add to Book" endpoint to accept `book_id` as a POST parameter rather than a URL
segment. A single endpoint `/stories/{story_id}/add_to_book/` takes `book_id` in the form body,
eliminating URL manipulation. After the Vue migration, this becomes a `<select>` with a `@change`
handler submitting to a `fetch()` call.

---

## 9 — Testing (P2)

### 9.1 Current state

Coverage is sparse. Known gaps:
- `text_generation/views.py` (`GenerateTextView`, `GetNextDirectionView`) — no tests
- `generated_text_evaluator/tests.py` — likely empty stub; `tests/` directory also exists in the
  same app (one is authoritative, the other should be deleted)
- `unfold_studio/tests/test_story_compilation.py` — verify coverage of preprocessing edge cases:
  circular includes, missing includes, variable shadowing
- No front-end tests

### 9.2 Test layout

Proposed consistent layout:

```
unfold_studio/           # Django project root
  pytest.ini             # or pyproject.toml [tool.pytest.ini_options]
  conftest.py            # shared fixtures (DB setup, test user creation)
  stories/
    tests/
      test_models.py
      test_views.py
      test_compilation.py
  text_generation/
    tests/
      test_backends.py
      test_views.py
  ...
```

Rules:
- Each app has a `tests/` package, not a `tests.py` file. Packages allow splitting tests into
  logical files.
- `conftest.py` lives at the project root (`unfold_studio/`), not nested inside an app.
- The root `conftest.py` provides fixtures used across apps (test user, test story, etc.).
- App-level `conftest.py` files provide app-specific fixtures.

Empty `tests.py` stubs in `comments`, `literacy_events`, `literacy_groups`, `profiles`, and
`prompts` are deleted; each gets a `tests/` package when tests are written.

### 9.3 Front-end tests

After the Vite migration (§2.1), add [Vitest](https://vitest.dev/) for unit-testing Vue
components and TypeScript modules. Priority targets:
- The ink compilation result parsing in `story.ts`
- The player state machine in `StoryPlayer.vue` (mocking inkjs)
- The `get_next_direction` API response parsing in `GetNextDirectionView`

---

## 10 — Infrastructure and Settings (P1)

### 10.1 `DEBUG=True` default

`base_settings.py:25`: `DEBUG = True`. Default to `DEBUG = False`; set `DEBUG = True` explicitly
only in `settings.py` (local dev).

### 10.2 `static_assets/` in `.gitignore`

`static_assets/` is the `collectstatic` target. Confirm it is in `.gitignore`. Generated files
should not be committed.

### 10.3 Duplicate settings (see §1.5)

This is the same issue as §1.5. `site_settings/unfold_studio.py` should import from
`base_settings` and only override production values.

### 10.4 Test layout (see §9.2)

`conftest.py` placement and test organization is addressed in §9.2.

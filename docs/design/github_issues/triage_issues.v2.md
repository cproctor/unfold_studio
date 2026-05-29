# GitHub Issues Triage — v2

Generated 2026-05-29. Based on v1 (2026-05-28) plus review of five branches merged into `refactor` since then: `story-genre`, `books-ui`, `frontend/account_signup`, `terminal/feedbackTab`, and `history-comments`. No changes have been made to GitHub.

**Changes from v1:** Three issues moved to "Already Complete" (#33, #23, #127); one issue promoted from "Needs Design" to "Open and Actionable" (#223); two issues have updated status notes (#261 partial progress, #217 partial progress).

---

## 1. Already Complete — Close with a note

These issues describe work that is definitively done in the current codebase.

| # | Title | Why it's done |
|---|-------|---------------|
| #55 | Rewrite front end in React or Vue | Front end fully rewritten in Vue 3 + TypeScript + Vite. All child issues this blocked are now addressed independently. |
| #81 | Version static distributions | Vite generates content-hashed filenames and a manifest; caching is no longer an issue. |
| #62 | Cached JS prevents newer features from working | Same root cause as #81; Vite hashing resolves it. |
| #79 | Allow story replay in front-end rewrite | Vue player has a replay button; replay no longer triggers a spurious save event. |
| #52 | Make API at least somewhat restful | HTTP verbs corrected during the 2.0 refactor; POST/PUT/DELETE used appropriately. |
| #35 | Update Google Sign-on | Replaced with `social-auth-app-django`; Google+ dependency gone. |
| #135 | Implement better logging | `django-structlog` integrated in the 2.0 refactor; structured JSON logs throughout. |
| #136 | Update README | README rewritten in the 2.0 refactor; points users to unfoldstudio.net and developers to the docs. |
| #196 | Create reproducible deployment | systemd unit files, `EnvironmentFile` secrets handling, and full deployment docs written in 2.0. |
| #36 | Allow user input | `INPUT()` external function is implemented and documented. (#210 is a follow-on about syntax ergonomics.) |
| #132 | LLM Generate feature: front-end | `generate()` external function works end-to-end with caching. Remaining gap is the `#generate` tag (tracked in #131). |
| #12 | Sharing (and unsharing) does not save a story | The Vue editor auto-saves; share/unshare is now a separate async action. The original GET-with-reload architecture is gone. (Chrome-specific regression was tracked separately in #241.) |
| #241 | Story sharing/unsharing does not work on Chrome | Race condition has been fixed. Close. |
| #230 | app.unfoldstudio.net crashes with 500 on login | Pertains to a state which cannot be reproduced and no longer exists. Close. |
| #131 | Implement `#generate` tag | Done. Close. |
| #33 | Reformat books page | **New since v1.** `books-ui` merge: `book_list.html` now shows `{{ book.stories.count }}` for every book, and the page lists up to five story titles per book with a "+N more" indicator. Close. |
| #23 | Show following users on profile page | **New since v1.** `user_self_detail.html` already renders a "Users you follow" section with unfollow links. Close. |
| #127 | Deterministic LLM interactions via `SEED` | **Misclassified in v1 as Needs Design.** The `seed_ai_function` branch (merged as #163) implemented `seed` throughout `text_generation/backends.py`. The `SEED` parameter is accepted, threaded through the cache key, and passed to the OpenAI API. Close. |

---

## 2. No Longer Relevant — Close with a note

These issues were valid at the time but are superseded by architectural decisions made in the 2.0 refactor.

| # | Title | Why it's no longer relevant |
|---|-------|-----------------------------|
| #82 | Inklecate v0.8.2 compiles invalid JSON | inklecate has been updated since; the scientific-notation JSON bug is a compiler defect fixed upstream. Verify the current binary version and close if confirmed. |
| #101 | HTML Base boilerplate | References a 2019 blog post; the Django base templates have been restructured in 2.0. The specific issues (lang, meta charset, etc.) are already addressed. |
| #76 | Filter LiteracyEvents on site affiliation | The sites framework is being removed (#233). LiteracyEvent cross-site filtering was only needed because of multi-site support; once that's gone the problem goes away. Close after #233 lands. |

---

## 3. Not Actionable — Close or move

These issues are empty, external to this repo, raw feedback dumps, or explicitly declined.

| # | Title | Recommendation |
|---|-------|----------------|
| #99 | Log management actions for future debugging | Empty body. If still relevant, replace with a concrete issue. Close. |
| #74 | Update citation reference on docs | Vague — which citation, which docs? The docs have been restructured. Close unless a specific change can be identified. |
| #68 | Update publication info on Unfold Studio research paper | External to this codebase; belongs in the paper's own repo or a personal to-do. Close. |
| #88 | Consider enterprise-ready features | Just a link to enterpriseready.io with no specific feature. Close; open concrete issues if specific features are wanted. |
| #218 | Explain data privacy and compliance on static site | The static site (unfoldstudio.net) is a separate repo. Move there or close. |
| #30 | Documentation story ideas | Content task, not engineering. Move to a curriculum/content repository or close. |
| #10 | Internationalization | No body, no context. Too vague to act on. Close unless a concrete need arises. |
| #70 | Create animated logo | Design/asset task, not code. No progress in six years. Close. |
| #120 | GMS Feedback | Raw dump of classroom feedback from 2019; not structured as actionable issues. Useful context but not a trackable ticket. Close; create specific issues if any items are still relevant. |
| #65 | Add "New Activity" link to prompt submission | Declined. Close. |

---

## 4. Open and Actionable — Ready to implement

### Bugs

**#231 — Form errors not displayed on story creation**

The story creation form requires title and description, but errors are silently swallowed.

*Plan:*
1. Find the story creation view (`stories/views.py`, likely `StoryCreateView`).
2. Ensure the template renders `{{ form.errors }}` or per-field `{{ field.errors }}`.
3. Add `required` attributes or field help text so users know fields are mandatory before submitting.

---

**#232 — Create error templates**

Django falls back to generic error pages in production unless custom templates exist.

*Plan:*
1. Create `unfold_studio/templates/400.html`, `403.html`, `404.html`, `500.html`.
2. Extend the base template; include a friendly message and a link to the home page.
3. Verify Django finds them by setting `DEBUG=False` locally and triggering a 404.

---

**#187 — Fix error display on stories**

Compilation errors show as an unformatted blob. They should be line-by-line with optional editor line highlighting. (#71 is folded into this.)

*Current state:* `StoryEditor.vue` defines `setErrors(errors: Array<{lineNumber, message}>)` and exposes it, but the implementation comment reads "Error display via CodeMirror linting — to be added in a future iteration. For now, errors are shown in the player panel." The data structure is in place; the CodeMirror decoration and per-line rendering are not.

*Plan:*
1. In `StoryEditor.vue`, implement the `setErrors` body: use the CodeMirror line-decoration API to highlight offending lines.
2. Render each error in the error panel on its own line (line number + message).
3. Test with a story containing a deliberate syntax error.

---

**#200 / #117 — TZ-naive datetimes**

Prod logs warn constantly; `dumpdata`/`loaddata` fails.

*Plan:*
1. Run `grep -rn "datetime.datetime(" unfold_studio --include="*.py"` to find naive instantiations.
2. Run `manage.py shell` against staging and query for rows where `creation_date < '1970-01-01 00:00:00+00'`.
3. Fix code to use `django.utils.timezone.now()` everywhere; write a data migration for bad rows.

---

**#198 — Ensure dependency migrations are specified**

`manage.py migrate` fails on a clean DB due to missing inter-app migration dependencies.

*Plan:*
1. `createdb unfold_studio_fresh && manage.py migrate` — record which migration fails.
2. Add the missing `dependencies = [('other_app', '0001_initial')]` entries.
3. Add `manage.py migrate` to the CI test suite.

---

**#197 — Some migrations which populate the database fail**

Two specific migrations (`unfold_studio.0005`, `unfold_studio.0037`) run data operations outside a transaction and fail non-atomically.

*Plan:*
1. Open each migration and wrap the `forwards` function body in `with transaction.atomic():`.
2. Verify against a clean database.
3. Consider squashing old Django 1.x-era migrations if the history is otherwise clean.

---

**#118 / #77 — Users with invalid usernames created via Google login**

Usernames containing `.` or other invalid characters slip through Google OAuth.

*Plan:*
1. In the `social-auth-app-django` pipeline, add a custom step that sanitizes the username after `social_core.pipeline.user.get_username`.
2. Strip or replace invalid characters (`.` → `_`); truncate to Django's 150-char limit; append a random suffix on collision.
3. Also address #143 (below) to handle existing bad usernames.

---

**#72 — Stories lock up when diverting to an invalid variable**

An uncaught runtime exception in inkjs causes the player to hang silently.

*Plan:*
1. In the ink player (wherever `story.Continue()` is called), wrap the call in a try/catch.
2. On catch, surface the error in the story player UI.
3. Test with `-> invalid_knot`.

---

**#28 — Catch infinite recursion runtime errors**

Stories that loop cause the browser tab to hang.

*Plan:*
1. Add a step counter in the ink player; after N steps (e.g. 5000) without a choice or end, halt and show a "possible infinite loop" error.

---

**#61 — Story disappears when returning to edit page via browser Back**

*Plan:*
1. Add `Cache-Control: no-store` to the story edit view response.

---

**#80 — Better 500 logging and handling**

Overlaps with #232. Remaining task: admin error emails in production.

*Plan:*
1. Verify `ADMINS` is set in production settings and `AdminEmailHandler` is in `LOGGING`.
2. Create the error templates (see #232).
3. Test with `raise Exception` in a view under `DEBUG=False`.

---

### Features

**#223 — Remove public stories** *(promoted from Needs Design)*

Decision reached in v1: remove public stories entirely; workshop participants can use join codes instead. JoinCode model and `/join-student/` route are now implemented (commit `8dc4672`), removing the primary blocker.

*Plan:*
1. `grep -rn "public\|is_public" unfold_studio --include="*.py"` — catalogue every usage of the `public` field (model, manager, views, templates, tests).
2. Remove `public` from `Story.StoryManager` queries (`Q(public=True)` appears in three places in `stories/models.py`).
3. Remove `public = models.BooleanField(default=False)` from the `Story` model; write a migration.
4. Remove the `public` flag from story create/edit forms and templates.
5. Remove the `{% if story.public %}` branch in `show_story.html`.
6. Remove any `public`-story routes or views.
7. Run full test suite.

---

**#261 — Genres should not be hard-coded** *(updated — partial work done)*

The `story-genre` and `books-ui` merges added genre support: `genres = JSONField(default=list, blank=True)` on both `Story` and `Book`; genre-pill UI on create/edit forms; genre filtering on story browse and book list. Hard-coded `GENRE_CHOICES` lives in `stories/forms.py` and `books/views.py`.

*What remains:* The original complaint was (a) genres are hard-coded, and (b) JSONField is the wrong type. The implementation chose JSONField + hard-coded choices — a deliberate simplification over the v1 plan's Genre model + M2M approach. Decide whether to:

- **Keep current approach** and close #261 (genres work; the hard-coded list is now in one well-known place per context rather than buried in model definitions). Open a separate issue if dynamic admin-managed genres are ever needed.
- **Finish the original plan**: create a `Genre` model, migrate data, replace JSONField with M2M.

Recommend the first option unless there is a concrete need to let admins manage genres without a deploy.

---

**#237 — Continue function loading indicator**

When `continue()` is generating, no feedback is shown.

*Plan:*
1. In the Vue player, add a reactive `isContinuing` boolean.
2. Set it `true` before the fetch to `/get_next_direction/` and `false` in the finally block.
3. Show a spinner (reuse the pattern used for `generate()`).

---

**#233 — Remove sites framework**

*Plan:*
1. `grep -rn "get_current_site\|sites\.get\|Site\.objects\|CurrentSiteManager\|SITE_ID" unfold_studio --include="*.py"` — usages are confirmed in `literacy_groups/mixins.py`, `literacy_groups/models.py`, `literacy_groups/views.py`, and `books/models.py`.
2. Remove `django.contrib.sites` from `INSTALLED_APPS` and `SITE_ID` from settings.
3. Remove the `site` FK from `LiteracyGroup` (write a migration); remove `sites` M2M from `Book` if present.
4. Replace site-filtered querysets with unfiltered equivalents.
5. Run full test suite. Note: #76 can be closed once this lands.

---

**#143 — Support changing usernames**

*Plan:*
1. Write a management command `rename_users` accepting a CSV of `old_username,new_username`.
2. Update `auth.User.username`, log old→new to a `DeprecatedUsername` model, update any string fields that stored usernames by value.
3. Block deprecated usernames from being claimed by new users.
4. Add a 301 redirect for any user-scoped URL that references an old username.

---

**#201 — Require auth for uncached AI calls**

*Plan:*
1. In `generate` and `get_next_direction` views, check cache before calling the LLM.
2. If not cached, require `request.user.is_authenticated`; return `401` otherwise.
3. Handle `401` gracefully in the Vue player.

---

**#210 — More intuitive input syntax**

Current: `~ input("Enter name", "varName")`. Desired: `~ varName = input("Enter name")`.

*Plan:*
1. Verify that inkjs external functions already support return-value assignment (`~ var = func()`).
2. Remove the second argument requirement from the `input` registration.
3. Update documentation.

---

**#86 — Pre-compile stories when forked**

*Plan:*
1. In the fork view, after copying the `Story` object, enqueue a Celery task to compile the new story immediately.

---

**#63 — Disable browser autocomplete in editor** *(scope narrowed in v1)*

Short-term fix only (longer-term Ink completion extension was declined).

*Plan:*
1. Add `autocomplete="off"` to the CodeMirror host `<div>` in `StoryEditor.vue`.

---

**#38 — Story code view should have an associated URL fragment**

`StoryToolbar.vue` already exposes `showCode` and an `emit('toggle-code')`. No hash binding is currently wired.

*Plan:*
1. In `StoryPage.vue`, watch `showCode` and push `#code` to history when true, remove it when false.
2. On mount, check `window.location.hash`; if `#code`, set `showCode = true`.

---

**#50 — Allow users to set a profile story**

*Plan:*
1. Add `profile_story = models.ForeignKey(Story, null=True, blank=True, on_delete=models.SET_NULL)` to `Profile`.
2. Add to the profile edit form.
3. Embed a read-only player on the profile page if set.

---

## 5. Needs Design Before Implementation

---

**#242 — Agent Feature — Project Plan** *(partial backend progress)*

The `terminal/feedbackTab and agent-prompt` merge (commit `062920f`) added `force_json=True` to the `get_next_direction` view, enabling structured JSON responses from the LLM — the infrastructure required for an agent that produces typed directives rather than raw text. The feedback link in the leader view now opens the story with `?feedback=1`. Core caching, evaluation, and context-windowing architecture remain unresolved. Still needs a design doc and phased milestones before further implementation.

---

**#246 — Extreme user stories for agent**

Depends on #242 design settling first.

---

**#217 — Support delegated authentication** *(partial progress)*

The `frontend/account_signup` merge implemented `JoinCode` records (replacing the shared `join_code` string on `LiteracyGroup`) and a `/join-student/` route that creates a new account on the spot when a valid course code is entered. This is the main student-facing part of delegated auth. Remaining design questions: full password-less teacher-managed accounts, password-reset flow, and COPPA/FERPA implications.

---

**#216 — Ensure compliance with privacy laws**

Meta-issue. Needs legal/policy input before engineering. Overlaps with #217, #226.

---

**#226 — Terms of service opt-in on profile**

Design of the email notification flow and consent record needs agreement before coding.

---

**#199 — Implement and test migration path from prod to dev**

Operational rather than code. Needs a runbook/checklist.

---

**#166 — Unify frontend events**

Removing page reloads during compilation requires real-time state reconciliation between editor and player — high complexity. Needs a design spike.

---

**#162 — Add support for A/B testing**

The issue itself asks for a proposal first.

---

**#146 — Implement AI affordances**

Meta-issue covering `#context`, `#hint`, `#bridge`, and agent. `continue()` is done; `#generate` is done; remaining sub-features need individual design docs.

---

**#126 — Model code/runtime relationship visually**

High implementation complexity. Needs a mockup before coding.

---

**#115 — Better story priority / gravity**

Log-word-weight and PageRank-style ranking need offline analysis of current data.

---

**#103 — Context directives**

`#context:map`, `#coordinates` etc. — needs a concrete proposal for at least one context type.

---

**#89 — Add `log()` function to Ink**

Straightforward to implement but the table schema and log pane UX need design.

---

**#87 — Allow citation of other stories**

The `@story_id` syntax is proposed but the bidirectional-link UI and backref storage need design.

---

**#73 — Convert event logging to ProgSnap2**

Research task (schema mapping) before engineering.

---

**#66 — Automatic story assessment**

Needs a concrete example use case and schema before implementation.

---

**#54 — Show story reading paths**

Requires a background task to build the directed graph from `LiteracyEvent` data, then a frontend visualization.

---

**#51 — Allow content styling**

The `pushStyle/popStyle` vs. line-tag approach is unresolved.

---

**#22 — Add Text/Context mode**

Very vague. No concrete proposal.

---

**#20 — Show viewer's relevant events on other users' feeds**

Needs a clear definition of "relevant."

---

**#69 — Better story priority**

Overlaps #115. Needs data analysis first.

---

**#67 — Change story timeline to use LiteracyEvents**

Requires verifying LiteracyEvents capture all data currently shown before switching.

---

**#161 — Improve frontend usability and styling**

Meta-issue. Should be broken into individual issues before any work is assigned.

---

## Summary Counts

| Category | v1 Count | v2 Count | Delta |
|----------|----------|----------|-------|
| Already complete — close | 15 | 18 | +3 (#33, #23, #127) |
| No longer relevant — close | 3 | 3 | — |
| Not actionable — close or move | 10 | 10 | — |
| Open and actionable (bugs) | 10 | 10 | — |
| Open and actionable (features) | 10 | 11 | +1 (#223 promoted from Needs Design; #33 and #23 removed) |
| Needs design | 23 | 21 | −2 (#223 promoted; #127 closed) |
| **Total** | **71** | **73** | *+2 net (previously grouped #33 and #23 now counted separately)* |

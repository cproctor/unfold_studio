# GitHub Issues Triage — v0

Generated 2026-05-28. Covers all 79 open issues. No changes have been made to GitHub.
This document is a proposal; review and leave feedback before any issues are closed or modified.

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
| #12 | Sharing (and unsharing) does not save a story | The Vue editor auto-saves; share/unshare is now a separate async action. The original GET-with-reload architecture is gone. (Chrome-specific regression tracked separately in #241.) |

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

These issues are empty, external to this repo, or raw feedback dumps with no clear engineering task.

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

---

## 4. Open and Actionable — Ready to implement

### Bugs

**#241 — Story sharing/unsharing does not work on Chrome**

A commenter identified the fix: the editor was sending a compile request on share, and the timing of that request caused the share to not take effect. Removing the spurious compile-on-share call should fix it.

*Plan:*
1. Find the share/unshare action in `StoryEditor.vue` (or wherever share is triggered).
2. Remove the compile call that fires alongside it.
3. Test share and unshare in Chrome and Firefox; verify the story is not re-compiled unnecessarily.

> No--this was actually a subtle race condition which has now been fixed. Close. 

---

**#231 — Form errors not displayed on story creation**

The story creation form requires title and description, but errors are silently swallowed.

*Plan:*
1. Find the story creation view (`stories/views.py`, likely `StoryCreateView`).
2. Ensure the template renders `{{ form.errors }}` or per-field `{{ field.errors }}`.
3. Add `required` attributes or field help text so users know fields are mandatory before submitting.

---

**#230 — 500 on login at app.unfoldstudio.net**

The traceback in the comments points to a server error on `/`. Likely caused by a missing migration, bad DB state, or a query that fails when no Site object exists.

*Plan:*
1. Reproduce locally against the staging DB.
2. Read the full traceback; check if it's a missing Site object (sites framework) or a missing migration.
3. Fix the root cause; add a 500 error template (#232 below) so future failures degrade gracefully.

> Close this. It pertains to a state which cannot be reproduced and no longer exists.

---

**#232 — Create error templates**

Django falls back to generic error pages in production unless custom templates exist.

*Plan:*
1. Create `unfold_studio/templates/400.html`, `403.html`, `404.html`, `500.html`.
2. Extend the base template; include a friendly message and a link to the home page.
3. Verify Django finds them by setting `DEBUG=False` locally and triggering a 404.

---

**#187 — Fix error display on stories**

Compilation errors show as an unformatted blob. They should be line-by-line with optional editor line highlighting.

*Plan:*
1. In `StoryEditor.vue`, parse the error string into an array of `{line, message}` objects.
2. Render each error on its own line in the error panel.
3. Use the CodeMirror line-decoration API to highlight the offending line in the editor.

---

**#200 / #117 — TZ-naive datetimes**

Prod logs warn constantly; `dumpdata`/`loaddata` fails. The issue body lists the unknowns well.

*Plan:*
1. Run `grep -rn "datetime.datetime(" unfold_studio --include="*.py"` to find naive instantiations.
2. Run `grep -rn "datetime.date.today()" unfold_studio --include="*.py"` for comparison uses.
3. Run `manage.py shell` against staging and query for rows where `creation_date < '1970-01-01 00:00:00+00'` (bad sentinel datetimes from old migrations).
4. Fix code to use `django.utils.timezone.now()` everywhere; write a data migration for bad rows.

---

**#198 — Ensure dependency migrations are specified**

`manage.py migrate` fails on a clean DB due to missing inter-app migration dependencies.

*Plan:*
1. `createdb unfold_studio_fresh && manage.py migrate` — record which migration fails.
2. Add the missing `dependencies = [('other_app', '0001_initial')]` entries.
3. Add `manage.py migrate` to the CI test suite (it currently only runs pytest).

---

**#197 — Some migrations which populate the database fail**

Two specific migrations (`unfold_studio.0005`, `unfold_studio.0037`) run data operations outside a transaction and fail non-atomically.

*Plan:*
1. Open each migration and wrap the `forwards` function body in `with transaction.atomic():`.
2. Verify against a clean database.
3. These are old Django 1.x-era migrations; consider squashing them if the history is otherwise clean.

---

**#118 / #77 — Users with invalid usernames created via Google login**

Usernames containing `.` or other invalid characters slip through Google OAuth.

*Plan:*
1. In the `social-auth-app-django` pipeline, add a custom pipeline step that sanitizes the username after `social_core.pipeline.user.get_username`.
2. Strip or replace invalid characters (`.` → `_`; truncate to Django's 150-char limit).
3. If the sanitized username is taken, append a random suffix.
4. Also address #143 (below) to handle existing bad usernames already in the DB.

---

**#72 — Stories lock up when diverting to an invalid variable**

An uncaught runtime exception in inkjs causes the player to hang silently.

*Plan:*
1. In `InkPlayer` (or wherever `story.Continue()` is called), wrap the call in a try/catch.
2. On catch, surface the error message in the story player UI (same path as other runtime errors).
3. Test with a story that has `-> invalid_knot`.

---

**#71 — Unhelpful error when there is an error on a code line**

When an Ink error references a line number, the current UI doesn't make the connection clear.

*Plan:* Combine with #187 — the per-line error display will resolve both.

---

**#28 — Catch infinite recursion runtime errors**

Stories that divert to themselves in a loop cause the browser tab to hang.

*Plan:*
1. inkjs does not have a built-in step counter. Add a step counter in `InkPlayer`; after N steps (e.g. 5000) without a choice or end, halt and show a "possible infinite loop" error.
2. This is a client-side safeguard; it doesn't need a compiler change.

---

**#63 — Turn off autocomplete in the editor**

Browser autocomplete interferes with Ink keyword entry in CodeMirror.

*Plan:*
1. Set `autocorrect="off" autocomplete="off" autocapitalize="off" spellcheck="false"` on the CodeMirror host element. CodeMirror 6 sets most of these by default on its content editable; verify and add any missing ones to the editor config.

> Now that we have a modern code editor, shall we consider a LSP for Ink? The old implementation was very annoying--constantly interrupting students' writing with unhelpful suggestions. 
> A LSP would be the starting place for some UI testing and iteration to find out whether autocomplete is useful. Can you find an ink LSP, or write one? 

---

**#61 — Story disappears when returning to edit page via browser Back**

The browser cache serves a stale page after navigating away and back.

*Plan:*
1. Add `Cache-Control: no-store` to the story edit view response.
2. Alternatively, the Vue editor could detect an empty story on mount and re-fetch from the server.

---

### Features

**#261 — Genres should not be hard-coded**

Currently genres are a hard-coded list on `Story`. A commenter notes they're also incorrectly a `JSONField`.

*Plan:*
1. Create a `Genre` model with `name` (CharField, unique) and `slug`.
2. Add a `ManyToManyField` from `Story` to `Genre`.
3. Write a data migration that reads the current hard-coded list and populates `Genre` rows; assigns existing story genres.
4. Remove the old genre field from `Story`.
5. Update the story creation/edit form to use a multi-select widget backed by `Genre.objects.all()`.

> Also check views that filter on genre aren't using hard-coded values. 

---

**#237 — Continue function loading indicator**

When `continue()` is generating, no feedback is shown.

*Plan:*
1. In the Vue player, add a reactive `isContinuing` boolean.
2. Set it `true` before the `fetch` to `/get_next_direction/` and `false` in the finally block.
3. Show a "Continuing…" spinner (can reuse the same pattern used for `generate()`).

---

**#233 — Remove sites framework**

Sites framework adds cruft; not needed now that multi-tenancy is off the table.

*Plan:*
1. `grep -rn "get_current_site\|sites\.get\|Site\.objects\|CurrentSiteManager\|SITE_ID" unfold_studio --include="*.py"` — list all usages.
2. Remove `django.contrib.sites` from `INSTALLED_APPS` and remove `SITE_ID` from settings.
3. Remove any `Site` foreign keys from models (write migrations to drop the columns).
4. Replace any site-filtered querysets with unfiltered equivalents.
5. Run full test suite.

---

**#223 — Remove public stories**

Anonymous "public" stories are a security/abuse risk and will be replaced by workshop QR-code flows.

*Plan:*
1. Remove the "create public story" code path from views and templates.
2. Add a migration that sets `author` to a designated "workshop" account on any existing public stories (or deletes them if none exist in prod).
3. Remove the `public` field from `Story` once the alternative workshop flow is in place.

> This issue needs more thought. I recognize public stories are an abuse risk (an unauthenticated request can create stories visible to others). 
> At the same time, I do need a way for users (e.g. in a conference workshop) to be able to immediately create stories without needing to make an account. 
> Propose a way to accomplish this which minimizes the risk. 

---

**#143 — Support changing usernames**

Some existing usernames contain PII and need to be renamed even if the user is inactive.

*Plan:*
1. Write a management command `rename_users` that accepts a CSV of `old_username,new_username` (or auto-generates friendly usernames).
2. The command updates `auth.User.username`, logs the old→new mapping to a `DeprecatedUsername` model, and updates any string fields that stored usernames by value (check `LiteracyEvent`, `StoryPlay`, etc.).
3. Also add the sanitization pipeline step from #118/#77 to prevent new bad usernames.

> Ensure that deprecated usernames are not available for new users. 
> Old URLs containing deprecated usernames should redirect to the new username. 

---

**#131 — Implement `#generate` tag**

The `generate()` function works; the `#generate` line tag does not.

*Plan:*
1. In `InkPlayer`, after calling `story.Continue()`, inspect `story.currentTags` for each text chunk.
2. If a chunk has a `generate` tag, POST to `/generate/` with the chunk as the prompt (same as the external function path).
3. Show a waiting animation; replace the chunk text with the LLM response on success; crash the story on failure (per the issue spec).

> Close--this is done. 

---

**#201 — Require auth for uncached AI calls**

Free-tier users could make expensive LLM calls. Cached responses should remain public; uncached calls should require login.

*Plan:*
1. In the `generate` and `get_next_direction` views, check if the response is in cache before calling the LLM.
2. If not cached, require `request.user.is_authenticated`; return `401` otherwise.
3. In the Vue player, handle a `401` response gracefully (show a "sign in to use AI features" message rather than crashing the story).

---

**#210 — More intuitive input syntax**

Current: `~ input("Enter name", "varName")`. Desired: `~ varName = input("Enter name")`.

*Plan:*
1. In the external function registration code (wherever `input` is bound), change the signature so the variable name is inferred from the assignment context — or register `input` to return the string and let Ink assign it normally.
2. inkjs external functions receive their arguments; the return value is assigned by the Ink runtime when used in `~ var = func()`. Verify this is already how it works and remove the second argument requirement.
3. Update documentation.

---

**#86 — Pre-compile stories when forked**

Forked stories start uncompiled.

*Plan:*
1. In the fork view/action, after copying the `Story` object, enqueue a Celery task to compile the new story immediately.
2. The existing `compile` Celery task can be reused.

---

**#33 — Reformat books page**

Show story count per book.

*Plan:*
1. In `BooksListView`, annotate the queryset with `Count('stories')`.
2. Display the count in the book list template.

---

**#38 — Story code view should have an associated URL fragment**

Deep-linking to the code view (`#code`) is currently not possible.

*Plan:*
1. In `StoryPage.vue`, watch `showCode` and push `#code` to the router/history when it's true, remove it when false.
2. On mount, check `window.location.hash`; if `#code`, set `showCode = true`.

---

**#80 — Better 500 logging and handling**

Overlaps with #232. The remaining task is ensuring admin error emails are sent in production.

*Plan:*
1. Verify `ADMINS` is set in production settings and `django.utils.log.AdminEmailHandler` is in `LOGGING`.
2. Create the error templates (see #232).
3. Test with `raise Exception` in a view under `DEBUG=False`.

---

**#65 — Add "New Activity" indicator to prompt submissions**

Teachers want to see when a student has updated their story or received a comment since the teacher's last review.

*Plan:*
1. On the prompt submission list view, compare `submission.story.updated_at` and `last_comment.created_at` against the last teacher comment timestamp.
2. Add a badge/indicator in the template when either is newer.

> Close this--I don't want it implemented. 

---

**#23 — Show following users on profile page**

*Plan:*
1. In `ProfileView`, add `following = profile.following.all()` to context.
2. Render as a simple list in the profile template.

---

**#50 — Allow users to set a profile story**

*Plan:*
1. Add a nullable `ForeignKey(Story)` named `profile_story` to the `Profile` model.
2. Add a field to the profile edit form.
3. On the profile page, if `profile_story` is set, embed a read-only player.

---

## 5. Needs Design Before Implementation

These issues describe real needs but require a design discussion before work begins.

| # | Title | What's unclear |
|---|-------|----------------|
| #242 | Agent Feature — Project Plan | Core architecture is described but caching, evaluation, and context windowing are unresolved. The feature is large enough to need a proper design doc and phased milestones. |
| #246 | Extreme user stories for agent | Depends on #242 design settling first. |
| #217 | Support delegated authentication | "Password-less accounts managed by a teacher" is the right UX direction, but the auth flow, password reset, and COPPA/FERPA implications need design work. |
| #216 | Ensure compliance with privacy laws | Meta-issue. Needs legal/policy input before engineering. Overlaps with #217, #226. |
| #226 | Terms of service opt-in on profile | Design of the email notification flow and the consent record (who tracks it, what triggers the email) needs agreement before coding. |
| #199 | Implement and test migration path from prod to dev | The prod→dev migration is more operational than code. Needs a runbook/checklist rather than a feature. |
| #166 | Unify frontend events | Removing page reloads during compilation requires real-time state reconciliation between editor and player — high complexity. Needs a design spike. |
| #162 | Add support for A/B testing | The issue itself asks for a proposal first. Needs a concrete proposal before any implementation. |
| #146 | Implement AI affordances | Meta-issue covering `#context`, `#hint`, `#bridge`, and agent. Most sub-features need individual design docs. `continue()` is done; `#generate` is in #131; the rest needs planning. |
| #127 | Deterministic LLM interactions via `SEED` | Caching already achieves de-facto determinism for identical prompts. Whether a `SEED` directive adds value beyond this is an open design question. |
| #126 | Model code/runtime relationship visually | Interesting UX concept but high implementation complexity. Needs a mockup before coding. |
| #115 | Better story priority / gravity | Log-word-weight and PageRank-style ranking need offline analysis of the current data before picking an algorithm. |
| #103 | Context directives | `#context:map`, `#coordinates` etc. — rich but undefined. Needs a concrete proposal for at least one context type. |
| #89 | Add `log()` function to Ink | Straightforward to implement but the table schema (`ReadEvents`) and the log pane UX need to be designed first. |
| #87 | Allow citation of other stories | Good idea; the `@story_id` syntax is proposed but the bidirectional-link UI and backref storage need design. |
| #73 | Convert event logging to ProgSnap2 | ProgSnap2 is a research standard; adoption requires understanding the schema fully and mapping our events to it. Research task before engineering. |
| #66 | Automatic story assessment | Complex pedagogical + technical feature. Needs a concrete example use case and schema before implementation. |
| #54 | Show story reading paths | Requires a background task to build the directed graph from `LiteracyEvent` data, then a frontend visualization. Design needed for both the data pipeline and the UI. |
| #51 | Allow content styling | Comments in the issue suggest abandoning the `pushStyle/popStyle` approach in favor of line tags. The final approach is unresolved. |
| #22 | Add Text/Context mode | Very vague — "text might be video, or a map." No concrete proposal. |
| #20 | Show viewer's relevant events on other users' feeds | Needs a clear definition of "relevant." |
| #69 | Better story priority | Partially overlaps #115. Needs data analysis first. |
| #67 | Change story timeline to use LiteracyEvents | Straightforward but requires verifying that LiteracyEvents capture all the data currently shown in the timeline before switching. Design review needed. |
| #161 | Improve frontend usability and styling | Meta-issue listing many small UX problems. Should be broken into individual issues; each is probably actionable but the parent is too broad to assign. |

---

## Summary Counts

| Category | Count |
|----------|-------|
| Already complete — close | 12 |
| No longer relevant — close | 3 |
| Not actionable — close or move | 9 |
| Open and actionable (bugs) | 11 |
| Open and actionable (features) | 13 |
| Needs design | 21 |
| **Total** | **69** |

*Note: issues #241 and #12 are counted once (#241 under actionable bugs; #12 under complete). Issues #71 and #28 are folded into #187 and the step-counter approach respectively. A few issues (e.g. #80/#232) have overlapping scope and are grouped.*

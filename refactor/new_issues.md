# New Issues Discovered During Implementation

Issues found during implementation that are non-trivial to fix inline.
Track here for a future refactor pass.

---

## NI-1 — SECRET_KEY in git history requires manual purge

The `SECRET_KEY` value (`afg+8)$...`) appears in git history as far back as the initial commit,
in `base_settings.py` and `site_settings/unfold_studio.py`. It has now been replaced with an env
var. **Production must rotate to a freshly generated key** — never reuse the committed value.

To purge from history (requires `git-filter-repo`; not installed at time of writing):
```bash
pip install git-filter-repo
git filter-repo --replace-text <(echo 'afg+8)$-yk((4fppx2a6@vb1$49)2)obmd6pz3ijg+r7)qy@z^==>REMOVED')
```
This rewrites history and requires a force-push. Coordinate with anyone else working from this
repo. The revoked OpenAI API key was **not** in git history (only in the gitignored
`settings.py`) so no purge is needed for it.

## NI-2 — conftest.py uses an incompatible TEXT_GENERATION format

`conftest.py:56–62` defines `TEXT_GENERATION` with a different format than the current
`base_settings.py`:
```python
TEXT_GENERATION={
    'BACKEND': 'text_generation.backends.openai.OpenAIBackend',
    'API_KEY': 'test-key',
    ...
}
```
This will be superseded when the backend abstraction (§11.1) is implemented. At that point,
update `conftest.py` to use the new format and update `TextGenerationFactory` accordingly.

## NI-3 — text_generation app absent from site_settings INSTALLED_APPS

The old (now replaced) `site_settings/unfold_studio.py` did not include `text_generation` or
`generated_text_evaluator` in `INSTALLED_APPS`, suggesting these apps were never active in
production. The new settings file inherits them from `base_settings`. Verify this is correct
when next deploying.

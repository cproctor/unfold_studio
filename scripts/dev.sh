#!/bin/bash
# Dev server launcher. Ensures Django is killed on exit regardless of how
# the script terminates (Control+C, kill, normal exit).

cleanup() {
    lsof -ti :8000 | xargs kill 2>/dev/null || true
}
trap cleanup EXIT

.venv/bin/python unfold_studio/manage.py runserver &
npm --prefix unfold_studio run dev

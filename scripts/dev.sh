#!/bin/bash
# Dev server launcher. Ensures Django is killed on exit regardless of how
# the script terminates (Control+C, kill, normal exit).

cleanup() {
    kill "$DJANGO_PID" 2>/dev/null || true
}
trap cleanup EXIT

.venv/bin/python unfold_studio/manage.py runserver &
DJANGO_PID=$!
npm --prefix unfold_studio run dev

Unfold Studio — UI Redesign Prototype (client review only)
============================================================

This folder is a standalone front-end mockup. It is NOT wired to Django
and does not replace any application templates or backend code.

Open in your browser:
  1) index.html         — home + featured
  2) browse.html        — browse (Top/New, dual search bars, filters)
  3) story-preview.html   — public story view (show_story–style: player + optional code)
  4) story-editor.html    — two-pane editor after Create Story (draft saved in sessionStorage)
  5) new-story.html     — title/description form → redirects to story-editor.html
  6) books.html         — books listing mock
  7) login.html         — login + sign up mocks

Header: dark bar with tan accent strip under the top edge, white diamond, sans
"Unfold Studio", mono nav in one row, search with focus ring, Log in / Sign up.

Search: type in the header (or browse toolbar) and press Search or type live — story cards
filter in the page (no server).

Hover cards for opening excerpt preview.

All relative paths work for file://

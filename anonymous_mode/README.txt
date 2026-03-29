Anonymous entry point (real Django flow)
=======================================

The anonymous experience is implemented in the main Unfold Studio app (sessions,
Story model, views). This folder supplies:

- anonymous_mode_entry.html — landing page rendered at /anonymous/ (see urls.base)
- style.css — copied to static/anonymous_mode/style.css for styling that page

Do not open the old static HTML prototypes (index.html, script.js, etc.) expecting
a working app: use a running Django server and start at:

  /anonymous/

From there, links go to real routes: /stories/new/, /stories/, /signup, etc.

Session ownership of anonymous drafts is stored server-side in
request.session["anonymous_owned_story_ids"]. The browser may also keep a
localStorage backup of ink text for the same story id (see static/app.js).

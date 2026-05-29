Development Setup
=================

This guide gets the app running on your machine. If you haven't read
:doc:`introduction` yet, start there — it explains what all the moving parts are.

Prerequisites
-------------

Install these before starting:

* **Python 3.11+** — ``python3 --version`` to check
* **Node.js 20+** — install via `nvm <https://github.com/nvm-sh/nvm>`_ (recommended)
  or from `nodejs.org <https://nodejs.org/>`_
* **PostgreSQL 14+** — only needed if you want to match production; SQLite works fine
  for most dev work
* **uv** — a fast Python package manager (we use this instead of pip directly)::

      pip install uv

Quick Start
-----------

All commands run from the **project root** (the directory containing ``unfold_studio/``
and ``docs/``).

**1. Clone and install Python dependencies**::

    git clone git@github.com:cproctor/unfold_studio.git
    cd unfold_studio
    uv sync

**2. Install the Ink compiler**

The Ink compiler (``inklecate``) turns ``.ink`` source files into JSON that the
browser can run::

    bash scripts/install_inklecate.sh

This downloads the right binary for your OS and places it at ``ink/inklecate``.

**3. Create a local settings file**

Django looks for ``unfold_studio/settings.py`` (gitignored, so it never gets
committed). Create one::

    cat > unfold_studio/settings.py << 'EOF'
    from unfold_studio.base_settings import *

    DEBUG = True
    SECRET_KEY = 'local-dev-key-not-for-production'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

    CELERY_TASK_ALWAYS_EAGER = True

    TEXT_GENERATION = {
        'backend': 'OpenAI',
        'api_key': 'your-openai-api-key-here',
        'model': 'gpt-4o-mini',
        'temperature': 0.7,
    }
    EOF

See `Getting an OpenAI API key`_ below for the ``api_key`` value.

**4. Run database migrations**::

    .venv/bin/python unfold_studio/manage.py migrate

**5. Create an admin account**::

    .venv/bin/python unfold_studio/manage.py createsuperuser

**6. Install Node.js dependencies and build the frontend**::

    npm --prefix unfold_studio install
    npm --prefix unfold_studio run build

**7. Start the development server**::

    make dev

This runs Django's dev server and Vite's watch mode in parallel. Both stop cleanly
when you press Control+C. Open http://localhost:8000 in your browser.

Getting an OpenAI API key
--------------------------

AI text generation (the ``generate()`` and ``continue_function()`` Ink calls) requires
an OpenAI API key. Without one, those features will error but everything else works.

**Option A — use the project key (recommended for contributors)**
   Ask the project lead for a dev API key. This charges to the project account and
   has usage limits appropriate for development.

**Option B — use your own key**
   Create an account at `platform.openai.com <https://platform.openai.com/>`_, add a
   payment method, and generate a key under API Keys. Be careful not to commit the
   key — ``settings.py`` is gitignored, so as long as you put it there you are safe.

Once you have a key, put it in ``unfold_studio/settings.py``::

    TEXT_GENERATION = {
        'backend': 'OpenAI',
        'api_key': 'sk-...',
        'model': 'gpt-4o-mini',
        'temperature': 0.7,
    }

Makefile Reference
------------------

All targets run from the **project root**:

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Target
     - What it does
   * - ``make dev``
     - Start Django dev server + Vite watch mode (Control+C stops both)
   * - ``make build``
     - Production frontend build + collect static files
   * - ``make test``
     - Run Python tests (pytest) and frontend tests (Vitest)
   * - ``make lint``
     - Run ruff (Python) and ESLint (TypeScript/Vue)
   * - ``make docs``
     - Build these docs (output goes to ``docs/_build/html/``)

Running Tests
-------------

All at once::

    make test

Python only::

    .venv/bin/python -m pytest unfold_studio

Frontend only::

    npm --prefix unfold_studio run test

Google Social Auth (optional)
------------------------------

To enable Google sign-in, add to ``settings.py``::

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret'

Configure the OAuth consent screen and redirect URI
(``http://localhost:8000/social-auth/complete/google-oauth2/``) in the
`Google Cloud Console <https://console.cloud.google.com/>`_.

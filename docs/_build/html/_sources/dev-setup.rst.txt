Development Setup
=================

Prerequisites
-------------

* Python 3.11+
* Node.js 20+ (via `nvm <https://github.com/nvm-sh/nvm>`_ recommended)
* PostgreSQL 14+ (or SQLite for local dev)
* Redis (optional; ``CELERY_TASK_ALWAYS_EAGER = True`` in local settings bypasses it)
* Inklecate (Ink compiler) — see installation below

Quick Start
-----------

::

    # Clone the repository
    git clone git@github.com:cproctor/unfold_studio.git
    cd unfold_studio

    # Create and activate Python virtualenv
    python3 -m venv .venv
    source .venv/bin/activate
    pip install uv
    uv sync

    # Install Inklecate
    bash scripts/install_inklecate.sh

    # Create a local settings file
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
    EOF

    # Run Django migrations
    cd unfold_studio
    python manage.py migrate
    python manage.py createsuperuser

    # Install Node.js dependencies and build frontend
    npm install
    npm run build

    # Start development server
    python manage.py runserver

Frontend Development (Vite watch mode)
---------------------------------------

To rebuild frontend assets automatically on file changes, run Vite in watch mode
alongside the Django dev server::

    cd unfold_studio
    python manage.py runserver &
    npm run dev

Or use the Makefile target::

    make dev

Makefile Targets
----------------

Run from the ``unfold_studio/`` directory:

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Target
     - Description
   * - ``make dev``
     - Start Django dev server and Vite watch mode
   * - ``make build``
     - Build frontend assets and collect static files
   * - ``make test``
     - Run Python tests (pytest) and frontend tests (Vitest)
   * - ``make lint``
     - Run ruff (Python) and ESLint (TypeScript/Vue)

Running Tests
-------------

Python tests (pytest)::

    cd unfold_studio
    python -m pytest

Frontend tests (Vitest)::

    cd unfold_studio
    npm run test

Both at once::

    cd unfold_studio
    make test

Inklecate Installation
----------------------

The Ink compiler is required for story compilation. Install it with::

    bash scripts/install_inklecate.sh

This downloads the appropriate binary for your OS and places it at
``ink/inklecate``. The path is configured in ``base_settings.py`` via
``INKLECATE_PATH``.

Google Social Auth (optional)
------------------------------

To enable Google sign-in, add to ``settings.py``::

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret'

Configure the OAuth consent screen and redirect URI
(``http://localhost:8000/social-auth/complete/google-oauth2/``) in the
`Google Cloud Console <https://console.cloud.google.com/>`_.

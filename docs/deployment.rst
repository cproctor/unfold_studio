Deployment
==========

This guide covers deploying Unfold Studio on a fresh Ubuntu server.

System Requirements
-------------------

* Ubuntu 22.04 LTS or newer
* Python 3.11+
* PostgreSQL 14+
* Redis (for Celery task queue)
* Nginx
* Supervisor

Environment Variables
---------------------

All secrets are passed via environment variables. Never commit secrets to version control.

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Variable
     - Description
     - Required
   * - ``SECRET_KEY``
     - Django secret key (rotate on each deployment)
     - Yes
   * - ``OPENAI_API_KEY``
     - OpenAI API key (if using OpenAI backend)
     - No
   * - ``ANTHROPIC_API_KEY``
     - Anthropic API key (if using Anthropic backend)
     - No
   * - ``DATABASE_URL``
     - PostgreSQL connection string
     - Yes (production)
   * - ``CELERY_BROKER_URL``
     - Redis connection string (default: ``redis://localhost:6379/0``)
     - No
   * - ``DJANGO_SETTINGS_MODULE``
     - Set to ``unfold_studio.site_settings.unfold_studio`` for production
     - Yes

Generate a fresh ``SECRET_KEY`` with::

    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Setup Steps
-----------

**1. Create a dedicated user**::

    sudo adduser unfold_studio
    su - unfold_studio

**2. Install system packages**::

    sudo apt update -y && sudo apt upgrade -y
    sudo apt install python3 python3-pip python3-venv nginx git supervisor -y
    sudo apt install build-essential libpq-dev -y
    sudo apt install certbot python3-certbot-nginx unzip -y
    sudo apt install redis-server fail2ban -y

**3. Prepare directories**::

    sudo mkdir -p /opt/unfold_studio
    sudo chown -R $USER:$USER /opt/unfold_studio

**4. Clone repository**::

    git clone --branch master git@github.com:cproctor/unfold_studio.git /opt/unfold_studio

**5. Install Python dependencies**::

    cd /opt/unfold_studio
    python3 -m venv .venv
    .venv/bin/pip install uv
    .venv/bin/uv sync

**6. Install Inklecate (Ink compiler)**::

    cd /opt/unfold_studio
    bash scripts/install_inklecate.sh

**7. Build frontend assets**::

    cd /opt/unfold_studio/unfold_studio
    npm install
    npm run build

**8. Run migrations and collect static files**::

    cd /opt/unfold_studio/unfold_studio
    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        ../.venv/bin/python manage.py migrate
    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        ../.venv/bin/python manage.py collectstatic --noinput

Gunicorn / Supervisor Configuration
------------------------------------

Create ``/etc/supervisor/conf.d/unfold_studio.conf``::

    [program:unfold_studio]
    directory=/opt/unfold_studio/unfold_studio
    command=/opt/unfold_studio/.venv/bin/gunicorn unfold_studio.wsgi:application \
        --bind unix:/opt/unfold_studio/unfold_studio.sock \
        --workers 3 --threads 2 --log-level info
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/unfold_studio.err.log
    stdout_logfile=/var/log/unfold_studio.out.log
    user=unfold_studio
    environment=
        PYTHONPATH="/opt/unfold_studio:/opt/unfold_studio/unfold_studio",
        DJANGO_SETTINGS_MODULE="unfold_studio.site_settings.unfold_studio",
        SECRET_KEY="%(ENV_SECRET_KEY)s",
        OPENAI_API_KEY="%(ENV_OPENAI_API_KEY)s"
    redirect_stderr=true

Reload Supervisor::

    sudo supervisorctl reread && sudo supervisorctl update
    sudo supervisorctl start unfold_studio

Nginx Configuration
-------------------

Create ``/etc/nginx/sites-available/unfold_studio``::

    server {
        listen 80;
        server_name app.unfoldstudio.net;

        location /static/ {
            alias /opt/unfold_studio/static_assets/;
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }

        location / {
            proxy_pass http://unix:/opt/unfold_studio/unfold_studio.sock;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Host $host;
            proxy_connect_timeout 300s;
            proxy_read_timeout 300s;
        }
    }

Enable and configure SSL::

    sudo ln -sf /etc/nginx/sites-available/unfold_studio /etc/nginx/sites-enabled/
    sudo certbot --nginx -d app.unfoldstudio.net
    sudo nginx -t && sudo systemctl reload nginx

Celery Workers
--------------

Add a Celery worker to Supervisor for async story compilation::

    [program:unfold_studio_celery]
    directory=/opt/unfold_studio/unfold_studio
    command=/opt/unfold_studio/.venv/bin/celery -A unfold_studio worker --loglevel=info
    autostart=true
    autorestart=true
    user=unfold_studio
    environment=
        PYTHONPATH="/opt/unfold_studio:/opt/unfold_studio/unfold_studio",
        DJANGO_SETTINGS_MODULE="unfold_studio.site_settings.unfold_studio",
        SECRET_KEY="%(ENV_SECRET_KEY)s"

Cron Jobs
---------

Add to crontab for the ``unfold_studio`` user::

    # Delete old public stories (older than PUBLIC_STORY_MAX_AGE_DAYS)
    0 3 * * * cd /opt/unfold_studio/unfold_studio && \
        DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        ../.venv/bin/python manage.py delete_old_public_stories

    # Purge soft-deleted records older than 90 days
    0 4 * * 0 cd /opt/unfold_studio/unfold_studio && \
        DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        ../.venv/bin/python manage.py purge_deleted_records

Upgrade Steps
-------------

::

    cd /opt/unfold_studio
    git pull
    .venv/bin/uv sync
    cd unfold_studio
    npm install && npm run build
    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        ../.venv/bin/python manage.py migrate
    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        ../.venv/bin/python manage.py collectstatic --noinput
    sudo supervisorctl restart unfold_studio unfold_studio_celery

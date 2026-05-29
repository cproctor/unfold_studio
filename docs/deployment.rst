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
   * - ``LLM_API_KEY``
     - API key for the configured LLM backend
     - No
   * - ``DATABASE_URL``
     - PostgreSQL connection string
     - Yes
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
    sudo apt install python3 python3-pip python3-venv nginx git -y
    sudo apt install build-essential libpq-dev -y
    sudo apt install certbot python3-certbot-nginx unzip -y
    sudo apt install redis-server fail2ban -y

**3. Prepare directories**::

    sudo mkdir -p /opt/unfold_studio
    sudo chown -R unfold_studio:unfold_studio /opt/unfold_studio

**4. Clone repository**::

    git clone --branch master git@github.com:cproctor/unfold_studio.git /opt/unfold_studio

**5. Install Python dependencies**::

    cd /opt/unfold_studio
    python3 -m venv .venv
    .venv/bin/pip install uv
    .venv/bin/uv sync

**6. Install Inklecate (Ink compiler)**::

    bash scripts/install_inklecate.sh

**7. Build frontend assets**::

    npm --prefix unfold_studio install
    npm --prefix unfold_studio run build

**8. Run migrations and collect static files**::

    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        .venv/bin/python unfold_studio/manage.py migrate
    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        .venv/bin/python unfold_studio/manage.py collectstatic --noinput

Gunicorn / systemd
------------------

Create an environment file at ``/etc/unfold_studio.env`` (readable only by root and
the service)::

    sudo touch /etc/unfold_studio.env
    sudo chmod 600 /etc/unfold_studio.env
    sudo nano /etc/unfold_studio.env

Paste your secrets::

    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio
    SECRET_KEY=your-secret-key-here
    LLM_API_KEY=your-llm-api-key-here

Create ``/etc/systemd/system/unfold_studio.service``::

    [Unit]
    Description=Unfold Studio (Gunicorn)
    After=network.target

    [Service]
    User=unfold_studio
    Group=unfold_studio
    WorkingDirectory=/opt/unfold_studio/unfold_studio
    EnvironmentFile=/etc/unfold_studio.env
    Environment=PYTHONPATH=/opt/unfold_studio:/opt/unfold_studio/unfold_studio
    ExecStart=/opt/unfold_studio/.venv/bin/gunicorn unfold_studio.wsgi:application \
        --bind unix:/opt/unfold_studio/unfold_studio.sock \
        --workers 3 --threads 2 --log-level info
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target

Enable and start::

    sudo systemctl daemon-reload
    sudo systemctl enable unfold_studio
    sudo systemctl start unfold_studio

Check status and logs::

    sudo systemctl status unfold_studio
    sudo journalctl -u unfold_studio -f

Celery Worker
-------------

Create ``/etc/systemd/system/unfold_studio_celery.service``::

    [Unit]
    Description=Unfold Studio Celery Worker
    After=network.target redis.service

    [Service]
    User=unfold_studio
    Group=unfold_studio
    WorkingDirectory=/opt/unfold_studio/unfold_studio
    EnvironmentFile=/etc/unfold_studio.env
    Environment=PYTHONPATH=/opt/unfold_studio:/opt/unfold_studio/unfold_studio
    ExecStart=/opt/unfold_studio/.venv/bin/celery -A unfold_studio worker --loglevel=info
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target

Enable and start::

    sudo systemctl daemon-reload
    sudo systemctl enable unfold_studio_celery
    sudo systemctl start unfold_studio_celery

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

Cron Jobs
---------

Add to crontab for the ``unfold_studio`` user (``sudo crontab -u unfold_studio -e``)::

    # Delete old public stories (older than PUBLIC_STORY_MAX_AGE_DAYS)
    0 3 * * * DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        /opt/unfold_studio/.venv/bin/python /opt/unfold_studio/unfold_studio/manage.py \
        delete_old_public_stories

    # Purge soft-deleted records older than 90 days
    0 4 * * 0 DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        /opt/unfold_studio/.venv/bin/python /opt/unfold_studio/unfold_studio/manage.py \
        purge_deleted_records

Upgrade Steps
-------------

::

    cd /opt/unfold_studio
    git pull
    .venv/bin/uv sync
    npm --prefix unfold_studio install
    npm --prefix unfold_studio run build
    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        .venv/bin/python unfold_studio/manage.py migrate
    DJANGO_SETTINGS_MODULE=unfold_studio.site_settings.unfold_studio \
        .venv/bin/python unfold_studio/manage.py collectstatic --noinput
    sudo systemctl restart unfold_studio unfold_studio_celery

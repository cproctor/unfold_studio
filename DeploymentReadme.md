# Unfold Studio Server Setup Guide

This document provides a complete step-by-step guide to deploy the **Unfold Studio** application on a fresh Ubuntu server.

---

## 1. Create a New User

```bash
sudo adduser unfold_studio
su - unfold_studio
```

---

## 2. Install Required Packages

```bash
sudo apt update -y
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx git supervisor -y
sudo apt install build-essential libpq-dev python3-poetry -y
sudo apt install certbot python3-certbot-nginx unzip -y
```

---

## 3. Prepare Directory Structure and SSH

```bash
sudo mkdir -p /opt/unfold_studio
sudo chown -R $USER:$USER /opt/unfold_studio
sudo chown -R $USER:$USER ~/.ssh
```

---

## 4. Generate SSH Key and Clone Repository

```bash
# Generate key pair
ssh-keygen -t rsa -b 4096 -C "prod-instance-key-pair"

# Add the public key from /home/unfold_studio/.ssh/id_rsa.pub to your GitHub account

# Clone the repository
git clone --branch development --single-branch git@github.com:cproctor/unfold_studio.git /opt/unfold_studio
```

---

## 5. Install Project Dependencies

```bash
cd /opt/unfold_studio
rm -rf poetry.lock

# Start poetry environment
poetry shell

# Install project requirements
poetry install

# Add Gunicorn
poetry add gunicorn
```

---

## 6. Install Inklecate (Ink Compiler)

```bash
mkdir ink
wget -O inklecate.zip https://github.com/inkle/ink/releases/download/v.1.2.0/inklecate_linux.zip
unzip inklecate.zip -d inklecate_1.2.0
rm inklecate.zip
```

---

## 7. (Optional) Add Swap Space (for low RAM instances)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 8. Update Django Settings

```bash
cd unfold_studio/unfold_studio/
nano settings.py
```

Paste your settings file into `settings.py`:


---

## 9. Collect Static Files

```bash
cd /opt/unfold_studio/unfold_studio
python manage.py collectstatic
```

---

## 10. Set Up Gunicorn Using Supervisor

```bash
sudo nano /etc/supervisor/conf.d/unfold_studio.conf
```

Paste the following:

```ini
[program:unfold_studio]
directory=/opt/unfold_studio/unfold_studio
command=/usr/bin/poetry run gunicorn unfold_studio.wsgi:application --bind unix:/opt/unfold_studio/unfold_studio.sock --workers 3 --threads 2 --log-level debug
autostart=true
autorestart=true
stderr_logfile=/var/log/unfold_studio.err.log
stdout_logfile=/var/log/unfold_studio.out.log
user=unfold_studio
environment=PYTHONPATH="/opt/unfold_studio:/opt/unfold_studio/unfold_studio",DJANGO_SETTINGS_MODULE="unfold_studio.settings"
redirect_stderr=true
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
```

---

## 11. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/unfold_studio
```

Paste the following:

```nginx
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
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        send_timeout 300s;
    }
}
```

```bash
# Enable the Nginx site
sudo ln -sf /etc/nginx/sites-available/unfold_studio /etc/nginx/sites-enabled/
```

---

## 12. Setup SSL Certificate (HTTPS)

```bash
sudo certbot --nginx -d app.unfoldstudio.net
```

---

## 13. Start and Manage Services

```bash
# Reload Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl stop unfold_studio
sudo supervisorctl start unfold_studio

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## 14. Check Service Status

```bash
sudo supervisorctl status
sudo systemctl status nginx
```

---

# ✅ Done!

Your Unfold Studio server should now be live at [https://app.unfoldstudio.net](https://app.unfoldstudio.net) 🚀

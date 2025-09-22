# Unfold Studio

[Unfold Studio](https://unfoldstudio.net) is an online community for interactive 
storytelling powered by a programming language called Ink. Interactive storytelling 
brings together the power of programming with the ability of stories to represent 
and explore our lived realities. Unfold Studio is free and open-source.

Unfold Studio is used in schools, clubs, and by many individual writers. 
Interactive storytelling can be a way to integrate Computer Science into English, 
Social Studies, or other subjects. It can also be an excellent way to introduce 
Computer Science as a subject relevant to questions of identity, culture, and 
social justice. (We are currently doing research with a school which uses Unfold 
Studio for several months as part of its core CS curriculum.)

Unfold Studio's main documentation is at 
[unfoldstudio.net](https://unfoldstudio.net/about).

## Development

### Setup

These steps should get a development instance running on MacOS. The process should be similar on Linux or Unix systems.

0. Prerequisites

- Install [Homebrew](https://brew.sh/). 
- Install [Poetry](https://python-poetry.org/).
- Install [Postgresql](https://www.postgresql.org/download/) (`brew install postgresql@16`)
  
    Set up default postgres user
  
        sudo passwd postgres

1. Route `local.unfoldstudio.net` to localhost. Add the following line to the bottom of `/etc/hosts` 
   (requires admin permissions). Unfold Studio uses Django's Sites framework, which depends on the 
   domain name of incoming requests.

        127.0.0.1	local.unfoldstudio.net

2. Prepare the database.

        createuser unfold_studio_user; createdb unfold_studio -O unfold_studio_user

    Set password for `unfold_studio_user`

        sudo -u postgres psql
        alter user unfold_studio_user with password '<password>';


3. Get the code.

        cd /opt # (Or wherever you want to install)
        git clone https://github.com/cproctor/unfold_studio.git
        cd unfold_studio
        poetry install
        cp unfold_studio/unfold_studio/base_settings.py unfold_studio/unfold_studio/settings.py

    You will need to ensure the `PASSWORD`, `HOST`, and `PORT` fields are set correctly in `settings.py[DATABASES.default]` based on your postgres configuration

4. Inklecate. To save (and compile) stories, you'll also need an Inklecate executable, which you can 
   get from https://github.com/inkle/ink/releases. Ensure that the backend Inklecate version, the frontend
   inkjs version, and `INK_VERSION` in `settings.py` are synchronized. 

   For the default installation, download ink 1.2.0 and unpack it into the `inklecate_1.2.0` directory in 
   the Unfold Studio repository's root. Additionally, create an `ink` directory in the repository root; 
   ink stories will be saved here during compilation.

   You may also need to give the inklecate file executable permissions

        chmod +x inklecate_1.2.0/inklecate

5. Last steps.

        ./manage.py migrate
        ./manage.py collectstatic
        ./manage.py dev_init
        python manage.py runserver

   This should be enough to get a local server running; you can test it by navigating to
   http://local.unfoldstudio.net:8000.

6. (Optional) Cron jobs

   Stories and books are weighted according to priority, which depends on factors defined in settings.
   Content is subject to 'gravity,' causing older content to fall and make room for newer content.  
   Therefore, stories need to be re-weighted from time to time. At the same time, when there's a lot of 
   content, it becomes burdensome to re-weight it all every few minutes. The cron jobs below achieve a 
   good compromise, updating the weights of top stories every ten minutes, and then updating all the content
   once a day. 

        0 3 * * * python3 /opt/unfold_studio/manage.py update_story_priority
        */10 * * * * python3 /opt/unfold_studio/manage.py update_story_priority -n 100
        0 * * * * python3 /opt/unfold_studio/manage.py update_book_priority

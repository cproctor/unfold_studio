# Unfold Studio

[Unfold Studio](https://unfold.studio) is an online community for interactive storytelling powered by a programming language called Ink. Interactive storytelling brings together the power of programming with the ability of stories to represent and explore our lived realities. Unfold Studio is free and open-source.

Unfold Studio is used in schools, clubs, and by many individual writers. Interactive storytelling can be a way to integrate Computer Science into English, Social Studies, or other subjects. It can also be an excellent way to introduce Computer Science as a subject relevant to questions of identity, culture, and social justice. (We are currently doing research with a school which uses Unfold Studio for several months as part of its core CS curriculum.)

Unfold Studio's main documentation is at [docs.unfold.studio](http://docs.unfold.studio).

## Development

Development of Unfold Studio is currently migrating to this repository's issues page. New bug reports should be filed here. 
There is additional code to support school and teacher features which is not currently open-source.

### Setup

These steps should get a development instance running on linux or MacOS.

0. From bare-bones digital ocean droplet, running as root. Probably not necessary for other contexts.

        apt-get update
        apt-get install python3-venv

1. Basic setup

        cd /opt # (Or wherever you want to install)
        python3 -m venv env
        source env/bin/activate
        git clone https://github.com/cproctor/unfold_studio.git
        cd unfold_studio
        pip install -r requirements.txt
        cp unfold_studio/base_settings.py unfold_studio/settings.py
        python manage.py migrate
        python manage.py collectstatic
        python manage.py runserver

   This should be enough to get a local server running; you can test it by navigating to
   http://localhost:8000.

2. Inklecate

   To save (and compile) stories, you'll also need an Inklecate executable, which you can get
   from https://github.com/inkle/ink/releases. You'll probably have to configure settings.py a
   bit to get it to work. 

3. Cron jobs

   Stories and books are weighted according to priority, which depends on factors defined in settings.
   Content is subject to 'gravity,' causing older content to fall and make room for newer content.  
   Therefore, stories need to be re-weighted from time to time. At the same time, when there's a lot of 
   content, it becomes burdensome to re-weight it all every few minutes. The cron jobs below achieve a 
   good compromise, updating the weights of top stories every ten minutes, and then updating all the content
   once a day. 

        0 3 * * * python3 /opt/unfold_studio/manage.py update_story_priority
        */10 * * * * python3 /opt/unfold_studio/manage.py update_story_priority -n 100
        0 * * * * python3 /opt/unfold_studio/manage.py update_book_priority

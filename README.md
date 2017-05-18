
## Suggested Improvements 4/4
- Only show line numbers when there's an error
- How will we deal with long programs?
- Allow typography (bold, italic)
- Usernames, passwords, private stories
- Organize, search, tag stories
- Allow images, sound
- remix stories

- BUG: Starting a knot with a list yields [object Object]
- BUG: Whitespace control 
- BUG: DONE doesn't actually stop--this is a result of using a call stack; they said there
  was no call stack. 
 
## Installation

0. Basics
-- set up box; ssh...

1. Mono (http://www.mono-project.com/docs/getting-started/install/linux/)
-- create and run script: 
http://www.mono-project.com/docs/compiling-mono/linux/
-- then build inklecate
xbuild /p:Configuration=Release ink.sln 

FOOL! Just get the release: https://github.com/inkle/ink/releases

2. Get Python deps
rm /usr/bin/python
ln -s python3 /usr/bin/python
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install django

3. Get source code
cd /opt
git clone https://github.com/cproctor/unfold_studio.git
cd unfold_studio
python manage.py migrate

4. Set up apache


Bumped to 10: Added overview guide for serialisation

ssh root@unfold.studio

Revision a5db240e83ad0e6c93f94ef86c4791f67105d5bb seems to work for version 9.

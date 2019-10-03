*******************
Using Unfold Studio
*******************

Anonymous usage
===============
You can participate in Unfold Studio without signing up.
Before you have an account, all the stories you write are public. This means anybody can play and edit them. You can also play public stories and stories other authors have shared. 

Public stories are good for quick experiments, but once you're ready to write stories that matter to you, you should
create an account. 

Accounts
=============
When you are logged in to your account, you are the author of your stories and nobody else can 
edit them.

Unfold Studio is free and open-source, and signing up is safe and easy. You will be asked to enter your email and choose 
a username and password. If you forget your password, you can have a reset code sent to your email address. 
If you prefer, you can also log in with a Google account. 

Reading
=======

The easiest way to start reading stories is to browse the stories on the homepage or on the "browse" page. If you know what you're looking for, there is also a search bar on the browse page. 

Anybody can see a story's code. (Stories are open-source.) When you're reading a story, click "show code" to see its code. This provides a different way to read the story, and also lets you learn techniques used by other authors.

Following other users
---------------------

Once you become part of the community, you might want to start following certain authors. You can follow (or unfollow) an author from their profile page. 

Feed notifications
------------------

Your profile page has a feed showing your community's activity. You will get notifications when an author you follow publishes a new story or a new version of a story. 
You will also see notifications related to your own activity. 
The rules for who gets which notifications are complex (check out `the source code`_), but the goal is that nobody should be surprised by who gets notifications. 

.. _the source code: https://github.com/cproctor/unfold_studio/blob/master/literacy_events/signals.py

Loving stories
--------------
One low-key way to show appreciation for a story is to "love" it. Loving a story is also useful for getting a link back to it, because you'll have a notification in your feed.

Which stories get to the homepage?
----------------------------------
Each story is assigned a score based on a bunch of factors. These include the length of the story, whether it has errors, the number of loves it has, how many times it has been forked, whether it includes or is included by other stories, versions and comments, and so on. The homepage tries to balance high scores with freshness using the `gravity algorithm borrowed from Hacker News`_. 

.. _gravity algorithm borrowed from Hacker News: https://medium.com/hacking-and-gonzo/how-hacker-news-ranking-algorithm-works-1d9b0cf2c08d


Writing 
=======

When you are writing, there are two views of a story side-by-side. The story's code is on the left and the running story is on the right. When you save changes to the code, you will see the updated version of the story on the right. Sometimes there are errors preventing a story from compiling; you will see these on the right as well. 

Forking
-------

Unfold Studio is designed around the principles of the open-source software community, where it's important to give credit for authorship but it's also important to share and reuse code. All stories on Unfold Studio are open-source, meaning you can see their code. You can also **fork** a story, making your own version of it. Forked stories keep a link back to their source. 

Please use forking respectfully. Forks are great for starting from templates, borrowing functionality from other stories, and fanfiction. When you fork a story, you should give credit to the original author. 

Who can see your stories
------------------------

When you are logged in, your stories will be private until you choose to share them. Sharing a story makes it visible to everybody. If you are part of a class using Unfold Studio, you might be assigned :ref:`prompts`. When you submit a story to a prompt, the leaders of the group (probably your teacher) will be able to see it whether or not it's shared publicly. If you remove a story from a prompt, they will no longer be able to see your story. 

For users who are part of :ref:`private installations`, the administrator is able to see all content on Unfold Studio.

.. _story_versions:

Version history
---------------

You can **save a version** of your story to keep track of how it is changing over time. When you save a version, your followers also get a notification. This is useful when you've added a new chapter or some significant new features. In the future, it will also be possible to fork old versions of stories.

.. _comments:

Comments
--------

Comments appear in a story's history.

Who can comment?
++++++++++++++++

Whoever can see a story can also see the story's comments. The only people who can comment on your stories are people you follow and the creators of prompts you have submitted the story to. If you unfollow a user, all their comments disappear. If you withdraw a story from a prompt (or leave the group in which the prompt was assigned), the group leader's comments will disappear. So you are always in control of who can comment on your stories. 


Advanced
========

.. _link_references:

References
----------

There are some places where you might need to write about stories, books, or other users. These include comments, book descriptions, and story prompts. In these contexts, you can add references by using codes like `@story:1184`, `@book:503`, `@user:chris`, and `@prompt:102`. These references will be shown as links to the story, book, or user which will stay up to date as the name changes. If you reference a story, it will only be linked for users who are allowed to see it. 

Embedding stories in other sites
--------------------------------

Unfold Studio supports embedding stories into other webpages. (They must be public or shared.) Use the following code:

.. code:: html

        <div id="story"></div>
        <script>
            EMBED_TARGET = "#story"
            STORY_ID = 8849;
        </script>
        <script src="https://unfold.studio/static/scripts/ink.js"></script>
        <script data-main="https://unfold.studio/embed_entry_point.js"
                src="https://unfold.studio/static/lib/require/require.js">
        </script>

This method of embedding is a bit messy, and will be improved in the upcoming fromt-end rewrite. 


Community standards
===================

Unfold Studio is a YA community, so the kind of content that's appropriate here is the same as what you would find in YA literature. There are some topics and some kinds of language that are legitimate and important, but which don't belong here. If you want a private installation of Unfold Studio that has different community standards, please get in touch (:ref:`contact`). 

Unfold Studio is a place where people sometimes get very real in their stories. There is no room here for hate or intolerance. We can't prevent somebody from saying something mean (welcome to the Internet), but Unfold Studio has been designed to be a safer online experience. For example, users have control over who can see their content and who can leave comments. :ref:`private_installations` can be made even more restrictive, limiting access to certain users.

If you see inappropriate content on Unfold Studio, please let us know (:ref:`contact`).

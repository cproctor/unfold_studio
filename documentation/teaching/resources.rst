.. _teaching_resources:

********************
Teaching Resources
********************

These resources may be helpful in teaching with `Unfold Studio`_.  
They can be used as part of a coherent :ref:`curriculum_unit`, or you can mix and match them
to fit your needs. Unless otherwise
noted, all were written by Chris Proctor, and are released free for noncommercial use.

Assessments
===========

.. _portfolio:

Story Portfolio
~~~~~~~~~~~~~~~

At the end of the unit, students will submit two stories they are proud of. One should show off the student's best storytelling skills; the other should show off their technical skills.

.. table:: Story portfolio rubric
   :widths: auto

   ================  ==========================================================================================================================================================================================  =============================================================================================================================================================================================================================================================================  ==============================================================================================================================================================================================================================================================================
   Objective         Advanced                                                                                                                                                                                    Proficient                                                                                                                                                                                                                                                                     Basic
   ================  ==========================================================================================================================================================================================  =============================================================================================================================================================================================================================================================================  ==============================================================================================================================================================================================================================================================================
   Storytelling      AND The story feels fresh, bold, and powerful. Even if your story is completely fictional, it’s about real identities and worlds.                                                           The story creates a rich experience for the player. It’s a substantial story which includes lots of details so the reader can feel like they’re in the world.                                                                                                                  BUT the story might be short on details or might feel like it came together at the last minute. You might not have clearly explained what kind of experience you were trying to create, or it might be hard to see how the story matches the kind of experience you described.
   Technical: State  AND the story uses state skillfully, doing something important in the story. The story wouldn’t be the same without them. The story uses some explicit state, probably declared variables.  The story uses flow correctly and meaningfully. Flow means using options to branch the story.                                                                                                                                                                                  BUT the use of state might be based closely on another story (for example, a fork). The use of state might “check the boxes” but not have much effect on the story’s meaning.
   Technical: Flow   AND the story uses flow skillfully, doing something important in the story. The story wouldn’t be the same without them. The story uses some advanced flow control.                         The story uses state correctly and meaningfully. Using state means using variables (either the built-in variables counting the number of visits to a knot, or your own variables), to keep track of something in the story and using it to change what happens in the future.  BUT the use of flow might be based closely on another story (for example, a fork). The use of flow might “check the boxes” but not have much effect on the story’s meaning.
   ================  ==========================================================================================================================================================================================  =============================================================================================================================================================================================================================================================================  ==============================================================================================================================================================================================================================================================================

.. _fairy_assessment:

Broken Story
~~~~~~~~~~~~~~~~~~~~~

Students are given a broken interactive story and asked to fix it. 
`Here is an example`_ you may use as-is or adapt a version to fit 
your teaching context and the skills you want to assess.

This strategy for assessing computational 
thinking was developed by :cite:`werner_fairy_2012`. Creating a standardized assessment of computational 
thinking is tricky because a student's ability to demonstrate mastery depends on her mastery of the 
programming language being used. The Broken Story assessment is particularly
attractive for `Unfold Studio`_ because the assessment is much more like the practice of writing interactive
stories than something like a multiple-choice test. It is also possible to automatically assess Broken Stories, 
though this is not yet available. 

Rubric
^^^^^^

.. table:: Broken Story Rubric
   :widths: auto

   ======================= ======================================================================
   Skill                   Evidence
   ======================= ======================================================================
   Syntax                  - Story compiles with no errors
   Choices match the graph - Add a choice to go from ``enter_peets`` to ``use_wifi``.
   Sticky choices          - Make choice from ``use_wifi`` to ``read_news`` sticky (``+``) 
                           - Make choice from ``use_wifi`` to ``minecraft`` sticky (``+``) 
                           - Make choice from ``read_news`` to ``minecraft`` sticky (``+``)
                           - Make choice from ``minecraft`` to ``read_news`` sticky (``+``)
   Conditional choices     -  ``read_news`` to ``buy_tea`` should have ``{not buy_tea}`` condition
                           - ``read_news`` to ``leave`` should have ``{buy_tea}`` condition
   Conditional text        -  ``leave`` should have ``{minecraft: text | other text}``
   ======================= ======================================================================

.. _story_templates:

Story templates
===============

These templates can be helpful in introducing new skills or concepts, or as prewriting exercises. 

.. _childhood_prompt:

A map of your childhood
~~~~~~~~~~~~~~~~~~~~~~~

.. note:: This story prompt is a great first introduction to ink. It demonstrates some of the core
    language features and invites authors to explore using a simple structure.

Think of about five places you remember well from your childhood. Draw a graph showing how the places are connected to each other, like the one below. Choose one place where the player should start and add an arrow pointing to that place. Then take some time to freewrite descriptions of each place, as well as how you get from one place to another. For now, there will be no conditions on moving between connected places--it's just a map the player can wander around.

.. image:: ../images/childhood_prompt_graph.png
   :width: 400px
   :align: center
   :alt: A graph of childhood places

Now write this as an interactive story. Here is an example. Hold off on adding lots of description until you're sure it works.

.. literalinclude:: ../stories/childhood.ink
   :linenos:
   :language: text

Now think of two or three objects which might be found in this world, particularly objects that have some meaning for you. We are going to extend the world-map so that the player can collect these objects. Then we'll have the world change depending on which objects the player has collected. To keep it simple, the model story will only add one object: a Slurpee. We'll use a simple boolean (true/false) variable to keep track of whether we have a Slurpee. 
Note that we need to initialize the variable (line 1) before we can modify it (line 38). 

.. literalinclude:: ../stories/childhood2.ink
   :linenos:
   :language: text

Now the player can get a Slurpee, but it has no effect on the rest of the story. Let's make the story react. This is an opportunity to craft an experience for your readers: when they take an action, even something seemingly insignificant like choosing to buy a Slurpee, they become invested in your world. This can be a chance to let them feel an emotion, have a sensory experience, or experience life in someone else's shoes. 

.. literalinclude:: ../stories/childhood3.ink
   :linenos:
   :language: text

Collaborative world-building
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is about discovering the possibilities in working together to create a story. 

Architecture: there should be one central story which stubs out all the locations and intiializes all the variables. Make this public so everyone can update it. 

People might want to grow this further; they could create libraries of descriptions or functions to re-use. You might be able to create various characters who could be put in conversation with one another!

Argumentation
~~~~~~~~~~~~~
Many disciplines have an essentially dialogic argumentation style (Elbow's You Say, I Say). You could implement this in stories. Particularly valuable for seeing how people argue through stories. 

Literary analysis
~~~~~~~~~~~~~~~~~
Multiple levels of meaning. I'm currently working on an example where the main character reads and re-reads a sonnet, layering in more possibilities each time. 

Personalizing political, economic, and historical forces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write a first-person story in which the main character interacts with broad-scale political, economic, or historical forces. The consequences following a player's choices should illustrate how the forces work, and should be supported by evidence. As part of the research process, interview at least two people who have experienced similar situations. Part of each interview should include playing and discussing your draft of the story. 

For example, you might read `this article about cash bail in America`_ and then write an interactive story playing out the various choices someone might make after being arrested and unable to make bail. You might then interview someone who has been arrested, someone whose family member has been arrested, a police officer, an employer, etc. 

.. _mini_lessons:

Mini-lessons
============

Inventory
~~~~~~~~~

.. todo:: Add inventory mini-lesson



.. _Unfold Studio: http://unfold.studio/
.. _Here is an example: http://unfold.studio/stories/905
.. _this article about cash bail in America: https://www.globalcitizen.org/en/content/its-a-crime-to-be-poor-in-america-bail-reform/


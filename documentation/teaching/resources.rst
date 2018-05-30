********************
Teaching Resources
********************

These resources may be helpful in teaching with `Unfold Studio`_. Unless otherwise
noted, all were written by Chris Proctor, and are released free for noncommercial use. 
If you would like to see how these can be combined into a coherent eel free to combine and adapt these resources. 

Assessments
===========


.. _prewriting_assessment:

Prewriting Assesssment
~~~~~~~~~~~~~~~~~~~~~~

.. todo:: Describe the portfolio and write a rubric.

.. _portfolio:

Story Portfolio
~~~~~~~~~~~~~~~

.. todo:: Describe the portfolio and write a rubric.

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
   Choices match the graph - Add a choice to go from ``enter_peets`` to ``use_wifi``.
   Sticky choices          - Make choice from ``use_wifi`` to ``read_news`` sticky (``+``) 
                           - Make choice from ``use_wifi`` to ``minecraft`` sticky (``+``) 
                           - Make choice from ``read_news`` to ``minecraft`` sticky (``+``)
                           - Make choice from ``minecraft`` to ``read_news`` sticky (``+``)
   Conditional choices     -  ``read_news`` to ``buy_tea`` should have ``{not buy_tea}`` condition
   Conditional text        -  ``leave`` should have ``{minecraft: text | other text}``
   ======================= ======================================================================

.. _story_prompts:

Story Prompts
=============

These prompts can be helpful in introducing new skills or concepts, or as prewriting exercises. 

.. _childhood_prompt:

The world of your childhood
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Think of about five places you remember well from your childhood. Draw a graph showing how the places are connected to each other, like the one below. Choose one place where the player should start and add an arrow pointing to that place. Then take some time to freewrite descriptions of each place, as well as how you get from one place to another. 

.. image:: ../images/childhood_prompt_graph.png
   :width: 400px
   :align: center
   :alt: A graph of childhood places

Now write this as an interactive story. Here is an example. Hold off on adding lots of description until you're sure it works.

.. literalinclude:: ../stories/childhood.ink
   :linenos:
   :language: text




.. _Unfold Studio: http://unfold.studio/
.. _Here is an example: http://unfold.studio/stories/905


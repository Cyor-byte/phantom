phantom.faces
=============

.. module:: phantom.faces

Face detection, landmarks, encoding, comparison, grouping and age and gender
estimation. Everything documented on this page can be imported directly from
``phantom.faces``, for example ``from phantom.faces import detect``.

Functions and classes
---------------------

.. automodule:: phantom.faces.faces
   :no-index-entry:

Age groups
----------

.. data:: phantom.faces.age_tags

   List of ``(lower age, higher age, description)`` tuples. The value returned
   by :func:`~phantom.faces.faces.estimate_age_onnx` is an index into this
   list. The first element, ``(-1, -1, "none")``, is a placeholder and is not
   used.

phantom.faces.align
-------------------

.. automodule:: phantom.faces.align

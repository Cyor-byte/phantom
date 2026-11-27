phantom
=======

**phantom** is a Python library for digital image processing, designed to help
digital forensic experts work with photographs, videos and other media.

.. note::
   This project is under active development. The API may still change before
   version 1.0.

What you can do with phantom
----------------------------

* **Faces** (:mod:`phantom.faces`): detect faces, locate their landmarks,
  encode them as 128-d vectors, compare them, group large sets of faces and
  estimate age and gender.
* **Measures** (:mod:`phantom.measures`): calibrate cameras, find vanishing
  points and estimate heights and distances in a scene.
* **Similarity** (:mod:`phantom.similarity`): perceptual hashes to find
  visually similar images.
* **Utilities** (:mod:`phantom.utils`): JPG ghosts to detect editing, color
  correction and drawing helpers.
* **Enhancement** (:mod:`phantom.enhance`): Lucy-Richardson deconvolution to
  reduce blur.
* **Geometry** and **video** helpers.

Start with :doc:`installation`, then follow the :doc:`quickstart`.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   quickstart
   api/index
   changelog

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

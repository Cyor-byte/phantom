Quickstart
==========

This page shows how to do the most common tasks, assuming phantom is already
installed (see :doc:`installation`). phantom works with images loaded by
OpenCV, which are NumPy arrays in **BGR** color order, so every example starts
with ``cv2.imread``.

The ``examples`` folder of the repository has complete scripts for each task,
including webcam demos.

Finding faces
-------------

:func:`~phantom.faces.faces.detect` returns the location of each face as a
``(left, top, right, bottom)`` tuple:

.. code-block:: python

   import cv2
   from phantom.faces import detect

   img = cv2.imread("photo.jpg")
   locations = detect(img)
   print(locations)  # e.g. [(218, 219, 373, 374)]

``detect`` can miss small faces. Raising ``upsample`` (1 by default) helps
find them, but makes detection slower.

Landmarks and drawing
---------------------

:func:`~phantom.faces.faces.landmark` finds the facial landmarks (eyes, nose,
mouth, jawline) of each face. It returns a list of
:class:`~phantom.faces.faces.Shape68p` objects, one per face.
:func:`~phantom.utils.draw_faces` draws them over the image:

.. code-block:: python

   import cv2
   from phantom.faces import landmark
   from phantom.utils import draw_faces

   img = cv2.imread("photo.jpg")
   faces = landmark(img)

   shape = faces[0]
   print(len(shape.points))      # 68 (x, y) points
   print(shape.dict["eye_left"]) # points grouped by facial feature

   output = draw_faces(img, faces)
   cv2.imwrite("photo_landmarks.jpg", output)

For a faster but less detailed result, use the 5-point model:
``landmark(img, model=Shape5p)``, importing it with
``from phantom.faces import Shape5p``.

Comparing faces
---------------

:func:`~phantom.faces.faces.encode` turns each face into a 128-dimensional
vector. :func:`~phantom.faces.faces.compare` measures the distance between two
of those vectors. A distance **under 0.6** means that both faces most likely
belong to the same person:

.. code-block:: python

   import cv2
   from phantom.faces import encode, compare

   known = encode(cv2.imread("suspect.jpg"))[0]
   candidates = encode(cv2.imread("crowd.jpg"))

   for i, face in enumerate(candidates):
       distance = compare(known, face)
       if distance < 0.6:
           print(f"Face {i} matches (distance {distance:.3f})")

If you already called :func:`~phantom.faces.faces.detect`, pass its result as
``locations=`` so the faces are not detected twice.

Estimating age and gender
-------------------------

Age and gender are estimated from a face encoding. These examples use the
ONNX versions of the functions, which work with any version of dlib and
scikit-learn:

.. code-block:: python

   import cv2
   from phantom.faces import encode, estimate_age_onnx, estimate_gender_onnx, age_tags

   encoding = encode(cv2.imread("photo.jpg"))[0]

   age_class = estimate_age_onnx(encoding)[0][0]
   low, high, label = age_tags[age_class]
   print(f"Age: {label} ({low}-{high})")

   gender = estimate_gender_onnx(encoding)[0][0][0]
   print(f"Gender score: {gender:.2f}")

The gender score goes roughly from -1 (male) to 1 (female). Treat values close
to 0 as unknown: the model is not certain.

Grouping many faces
-------------------

:class:`~phantom.faces.faces.Atlas` groups a large set of faces by
similarity. This tells you how many different people appear in a set of
images, and lets you match new faces against those groups:

.. code-block:: python

   from phantom.faces import Atlas, Face

   # encodings: a list of face encodings gathered from many images
   atlas = Atlas([Face(encoding=e) for e in encodings], "faces.atlas")
   atlas.save()   # save the faces to disk

   atlas.fit()    # group the faces
   for group, distance in atlas.predict([new_encoding]):
       print(f"Closest group: {group} (distance {distance:.3f})")

In phantom 0.8.3, calling :meth:`~phantom.faces.faces.Atlas.save` after
:meth:`~phantom.faces.faces.Atlas.fit` raises a ``TypeError``, so save the
atlas before grouping it. ``examples/cluster.py`` is a complete script that
groups the faces found in a folder of images.

Finding similar images
----------------------

Perceptual hashes summarize how an image *looks*, so resized or recompressed
copies of an image get the same or very similar hashes. Compare them with
:func:`phantom.similarity.compare`:

.. code-block:: python

   import cv2
   from phantom.similarity import p_hash, compare

   h1 = p_hash(cv2.imread("original.jpg"))
   h2 = p_hash(cv2.imread("resized_copy.jpg"))
   print(compare(h1, h2))  # True if they look alike

:func:`~phantom.similarity.a_hash` and :func:`~phantom.similarity.d_hash`
are faster alternatives. ``examples/lookalike.py`` searches a whole folder
with them.

Looking for signs of editing
----------------------------

:func:`~phantom.utils.jpg_ghosts` recompresses a JPG image at several
quality levels and returns one difference image per level. A region pasted
from a JPG saved at a different quality shows up as a dark area (a "ghost")
in the difference image for that quality, while the rest of the image does
not:

.. code-block:: python

   import cv2
   from phantom.utils import jpg_ghosts

   img = cv2.imread("evidence.jpg")
   qualities = [50, 60, 70, 80, 90, 100]
   for quality, ghost in zip(qualities, jpg_ghosts(img, qualities)):
       cv2.imwrite(f"ghost_{quality}.png", ghost)

Working with video
------------------

:class:`~phantom.video.Video` lets you loop over the frames of a video file.
:class:`~phantom.video.VideoThreaded` does the same while reading from a
separate thread, which is usually faster:

.. code-block:: python

   from phantom.faces import detect
   from phantom.video import VideoThreaded

   for frame in VideoThreaded("camera.mp4"):
       if detect(frame, upsample=0):
           print("Face found")

Next steps
----------

The :doc:`api/index` documents every module and function in detail. To
reduce blur in an image, see :doc:`lucy_richardson`.

Installation
============

Requirements
------------

phantom supports the latest version of Python [#latest]_, currently
**Python 3.14**. Python 3.11 and later are still supported, but we recommend
the latest version. You can check your version by running:

.. code-block:: console

   $ python --version

The following dependencies are installed in step 3 below:

* NumPy
* SciPy
* matplotlib
* scikit-learn
* OpenCV (``opencv-python``)
* dlib (``dlib-bin``, a prebuilt package that needs no compiler)
* ONNX Runtime (``onnxruntime``)

Installing phantom
------------------

These steps work on Linux, Windows and macOS.

1. Download the source code from the
   `GitHub repository <https://github.com/bconstanzo/phantom>`_, either with
   ``git clone`` or as a ZIP file.

   .. code-block:: console

      $ git clone https://github.com/bconstanzo/phantom.git
      $ cd phantom

2. Create and activate a virtual environment (recommended).

   .. code-block:: console

      $ python -m venv .venv

   On Linux and macOS:

   .. code-block:: console

      $ source .venv/bin/activate

   On Windows:

   .. code-block:: console

      > .venv\Scripts\activate

3. Install the dependencies and then phantom itself:

   .. code-block:: console

      (.venv) $ pip install -r requirements.txt
      (.venv) $ pip install .

   If you plan to modify phantom, use ``pip install -e .`` instead, so your
   changes take effect without reinstalling.

4. Check the installation. This command should print phantom's version:

   .. code-block:: console

      (.venv) $ python -c "import phantom; print(phantom.__version__)"

.. [#latest] As far as can reasonably be expected.

Troubleshooting
---------------

Warnings about the age and gender models
   Importing :mod:`phantom.faces` may show a ``UserWarning`` saying that no
   gender model matches the installed dlib version, or that no age model
   matches the installed scikit-learn version. This happens because
   :func:`~phantom.faces.faces.estimate_gender` and
   :func:`~phantom.faces.faces.estimate_age` use models saved with specific
   versions of those libraries (dlib 19.8, 19.16, 19.23 and 19.24;
   scikit-learn 0.20, 1.0 and 1.1). Only those two functions are affected.
   Use :func:`~phantom.faces.faces.estimate_gender_onnx` and
   :func:`~phantom.faces.faces.estimate_age_onnx` instead, which work with any
   version.

``ImportError`` when importing dlib on Windows
   This only happens with the older dlib wheels for Windows found in the
   ``tools`` folder of the repository, not with ``dlib-bin``. Those wheels need
   Intel MKL: install it from https://software.intel.com/en-us/mkl and add its
   folders to the ``PATH``, ``LIB`` and ``INCLUDE`` environment variables. The
   repository's ``README.md`` lists the exact folders.

``DLL load failed while importing cv2``
   Some OpenCV builds for Windows fail if ``cv2`` is imported before NumPy.
   Import ``numpy`` first in your own scripts (phantom already does this
   internally).


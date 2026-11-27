:orphan:

.. _lucy-richardson:

===============================
Lucy-Richardson deconvolution
===============================

.. contents:: On this page
   :local:
   :depth: 2

Overview
========

Real images are never a perfect copy of the scene they capture. Lens
aberrations, defocus, camera shake and atmospheric turbulence spread the
light of every point over its neighbors, producing a blurred image.
*Deconvolution* is the process of undoing that blur.

:func:`phantom.enhance.lucy_richardson_deconv` implements the
**Lucy-Richardson (LR)** algorithm [R1972]_ [L1974]_, an iterative
deconvolution method. It assumes that the blur follows a Gaussian point
spread function (PSF).

.. code-block:: python

   import cv2
   from phantom.enhance import lucy_richardson_deconv

   img = cv2.imread("blurry.png")
   sharp = lucy_richardson_deconv(img, num_iterations=30, sigmag=3.0)

.. note::

   The current implementation has some known issues, one of which gives
   wrong results for ``uint8`` and ``float32`` images. Read
   :ref:`lr-known-issues` before using it on evidence.


Background
==========

Image formation model
---------------------

The observed image is modeled as the convolution of the true image with the
PSF, plus noise:

.. math::

   g = f \ast h + n

where:

.. list-table::
   :widths: 15 85
   :header-rows: 0

   * - :math:`g`
     - observed (blurred) image
   * - :math:`f`
     - true image, the unknown we want to estimate
   * - :math:`h`
     - point spread function (PSF): the image of an ideal point source
   * - :math:`n`
     - noise
   * - :math:`\ast`
     - 2D convolution

Deconvolution means estimating :math:`f` from :math:`g` and :math:`h`.

Why Lucy-Richardson?
--------------------

Inverting the convolution directly (inverse filtering) is numerically
unstable: wherever the PSF has near-zero frequency components, the noise is
amplified enormously. LR avoids this problem, and it is a popular choice for
these reasons:

* **Iterative, no inversion.** Instead of inverting an operator, each step
  refines the previous estimate, and the process can stop as soon as the
  result is good enough.
* **Non-negativity.** Updates are multiplicative, so if the starting image is
  non-negative the estimate stays non-negative. This matches the physical
  nature of light intensity.
* **Statistical foundation.** Under a Poisson noise model (photon shot
  noise, the dominant noise in many imaging sensors) the iterations converge
  towards the *maximum-likelihood* estimate of :math:`f`.
* **Energy conservation.** With a normalized PSF, the basic algorithm
  preserves the total intensity of the image at every iteration. This
  implementation preserves it only approximately, because of the image
  borders and the acceleration step.
* **Simplicity.** It only needs convolutions and point-wise divisions.

Compared with Wiener filtering, LR does not need an estimate of the noise
power spectrum, and it respects non-negativity. In exchange, the PSF must be
known and a stopping criterion must be chosen.


The algorithm
=============

Starting from the observed image as the initial guess, :math:`f_0 = g`, LR
iterates:

.. math::

   f_{k+1} = f_k \cdot \left( \hat{h} \ast \frac{g}{h \ast f_k} \right)

where :math:`\hat{h}` is the PSF flipped in both axes. Each iteration:

#. **Re-blurs** the current estimate: :math:`h \ast f_k`.
#. **Compares** it to the observation: :math:`g / (h \ast f_k)`. A ratio close
   to 1 means that the estimate already explains that region well.
#. **Back-projects** the ratio using the flipped PSF.
#. **Corrects** the estimate by multiplying it by the result.


Implementation in ``phantom``
=============================

.. autofunction:: phantom.enhance.lucy_richardson_deconv
   :no-index:

Number of iterations
--------------------

The main loop runs ``num_iterations - 1`` times, so the function performs one
update fewer than requested. With ``num_iterations=1`` it performs no update
and returns the input unchanged (only clipped, see `Data types`_).

Gaussian PSF
------------

The PSF is assumed to be an isotropic Gaussian with standard deviation
``sigmag`` (in pixels). The convolutions use :func:`cv2.GaussianBlur` with a
square window of ``int(8 * sigmag + 1)`` pixels, which truncates the Gaussian
at about :math:`\pm 4\sigma`. OpenCV requires that size to be odd, so values
of ``sigmag`` that produce an even window (for example ``0.7`` or ``2.2``)
raise a ``cv2.error``. Any multiple of 0.25 (``1``, ``1.5``, ``2.25``,
``3``...) always produces a valid window.

Because a Gaussian is symmetric, :math:`\hat{h} = h`, so both convolutions of
the update step use the same blur. Pixels outside the image are filled by
reflection (OpenCV's default ``BORDER_REFLECT_101``).

Convergence acceleration
------------------------

Plain LR can need hundreds of iterations. This implementation uses a
vector-extrapolation acceleration in the style of Biggs and Andrews
[BA1997]_. Before each update the estimate is extrapolated along the
direction of the previous change:

.. math::

   y_k = f_k + \lambda_k \, (f_k - f_{k-1})

with the acceleration factor computed from the last two corrections
:math:`d_k = f_k - y_{k-1}`:

.. math::

   \lambda_k = \frac{\sum d_k \, d_{k-1}}{\sum d_{k-1}^2 + \varepsilon}

where :math:`\varepsilon = 2.2204 \times 10^{-16}`. The LR update is then
applied to :math:`y_k` (clamped to be non-negative) instead of :math:`f_k`.

* :math:`\lambda = 0` during the first two updates, because there are not yet
  two previous corrections to compare. Those updates follow the standard
  algorithm.
* :math:`\lambda_k` is not clamped to any range.
* For multi-channel (color) images, the sums are computed over the **first
  channel only** (blue, for images loaded with OpenCV) and the resulting
  :math:`\lambda_k` is applied to every channel. See :ref:`lr-known-issues`.

Data types
----------

The output is clipped to a range that depends on the input data type and
returned with that same type:

.. list-table::
   :header-rows: 1
   :widths: 40 20 20

   * - Input ``dtype``
     - Clip minimum
     - Clip maximum
   * - ``uint8``
     - 0
     - 255
   * - ``uint16``
     - 0
     - 65535
   * - any other type (meant for floats)
     - 0.0
     - 1.0

.. note::

   * Floating point images must be in the range ``[0, 1]``.
   * Any other integer type (for example ``int16`` or ``int32``) falls in the
     last row: its values are clipped to ``[0, 1]``, which destroys the
     image. Convert it to ``uint16`` or to a float in ``[0, 1]`` first.
   * When the input is ``uint8`` or ``uint16``, the result is converted back
     to that type by **truncation**, not rounding, so every pixel can lose up
     to one intensity level.
   * Clipping is always applied: the ``clip`` argument is currently ignored.
   * In phantom 0.8.3, only ``float64`` images give correct results. See
     :ref:`lr-known-issues`.

Example
-------

The following snippet (see ``examples/enhancements.py``) blurs an image with a
Gaussian of :math:`\sigma = 3` and then recovers it:

.. code-block:: python

   import cv2
   from phantom.enhance import lucy_richardson_deconv

   sigma = 3.0
   win_size = int(8 * sigma + 1)

   img = cv2.imread("lena.png")
   blurred = cv2.GaussianBlur(img, (win_size, win_size), sigma, sigma)

   restored = lucy_richardson_deconv(blurred, 100, sigma)

   cv2.imshow("blurred", blurred)
   cv2.imshow("restored", restored)
   cv2.waitKey(0)


Choosing parameters
===================

``sigmag``
   Should match the real blur of the image. A much smaller value leaves the
   image blurry, and a much larger one produces ringing artifacts. If the
   real blur is unknown, try a few values and keep the one that gives the
   sharpest result without halos. Use multiples of 0.25 to avoid an invalid
   window size (see `Gaussian PSF`_).

``num_iterations``
   Start low (10 to 30) and increase it while the image keeps improving. More
   iterations recover more detail, but eventually start amplifying noise.


Limitations
===========

.. warning::

   LR amplifies noise as the number of iterations grows. If the input is
   noisy, denoise it first or limit the number of iterations.

* The PSF must be known or well estimated, and here it is restricted to an
  isotropic Gaussian. Motion blur or non-symmetric PSFs are not supported.
* **Ringing:** halos or double edges may appear around strong contours.
* Deconvolution recovers detail that was *attenuated* by the blur, not
  detail that was lost completely.


.. _lr-known-issues:

Known issues
============

These issues of the current implementation (phantom 0.8.3) will be fixed in a
future version. They are documented here so that results can be reproduced
and justified.

#. **Wrong results for uint8 and float32 images.** An internal division
   result is discarded unless the image is ``float64``. With ``float32``
   images the result fades towards black. With ``uint8`` images the first
   update is wrong, and later updates only partly correct it (with 10
   iterations, some pixels differ by up to 12 intensity levels from the
   correct result). Until this is fixed, convert the image to ``float64``
   in ``[0, 1]`` first, with ``img.astype(np.float64) / 255``.
#. **One update fewer than requested** (see `Number of iterations`_).
#. **Color images share the acceleration factor of the first channel.**
   Because of this, the result for each channel depends on the channel
   order: a BGR image and its RGB version give slightly different results.
   Grayscale images are not affected. See `Convergence acceleration`_.
#. **Some sigmag values raise an error** (see `Gaussian PSF`_).
#. **Integer types other than uint8 and uint16 are clipped to [0, 1]**, and
   integer results are truncated instead of rounded (see `Data types`_).
#. **The clip argument has no effect**: the output is always clipped.


References
==========

.. [R1972] W. H. Richardson, "Bayesian-Based Iterative Method of Image
   Restoration", *Journal of the Optical Society of America*, 62(1),
   55-59, 1972. doi:10.1364/JOSA.62.000055

.. [L1974] L. B. Lucy, "An iterative technique for the rectification of
   observed distributions", *The Astronomical Journal*, 79, 745-754, 1974.
   doi:10.1086/111605

.. [BA1997] D. S. C. Biggs and M. Andrews, "Acceleration of iterative image
   restoration algorithms", *Applied Optics*, 36(8), 1766-1775, 1997.
   doi:10.1364/AO.36.001766

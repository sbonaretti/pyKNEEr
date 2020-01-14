.. _installation:

Installation
================================================================================


.. raw:: html

  An overview of <i>pyKNEEr</i>, its installation, and its demo are presented in a <a href="https://www.youtube.com/watch?v=7WPf5KFtYi8" target="_blank">youtube video</a>, which we recommend watching as a comprehensive introduction.
  The current and following pages provide more details.
  <br>


.. note::

   The commands in this documentation are for Mac OS. If you work on Windows:

   - Substitute ``/`` with ``\``
   - Use the python :ref:`terminal <terminal>` provided in the Anaconda distribution



python
--------------------------------------------------------------------------------
We recommend to install python through Anaconda, a platform providing a complete distribution

-  Download the latest release of `Anaconda <https://www.anaconda.com/download/>`_ with Python version greater than 3
-  Install Anaconda (`official documentation <https://docs.anaconda.com/anaconda/install/>`_)




*pyKNEEr*
--------------------------------------------------------------------------------

Go to :ref:`terminal <terminal>`, copy/paste the following line and press ``enter``:

.. code-block:: bash

  pip install pykneer

The installation contains *elastix v4.8* for atlas-based segmentation. If you work on a Windows or a Linux computer,
you might need to :ref:`set the environment variables for elastix <elastix>`

Note: We recommend to install *pyKNEEr* in a python :ref:`virtual environment <virtualenv_what>`, although it is not necessary




.. _demo:

Demo
--------------------------------------------------------------------------------

To become familiar with *pyKNEEr*, we provide a demo that you can replicate following the step-by-step instructions in the following pages

- .. raw:: html

    Download the newest version of the demo images <a href="https://www.doi.org/10.5281/zenodo.3262307" target="_blank">here</a> (2.1 GB)

  *Note*: Make sure that all the folder names that constitute the path to the demo images have **no spaces**.
  E.g. ``/home/learning_pykneer/demo/`` and **not** ``/home/learning pykneer/demo/``

- Unzip the file and open it. It contains two folders:

  - ``input``: It is the basic folder to work with *pyKNEEr*:

    .. figure:: _figures/demoFolders.png
                 :align: center
                 :scale: 30%

    The folder ``original`` contains images of subjects ``01``, which contains:

    - ``DESS`` images to get familiar with atlas-based segmentation and :math:`T_2` mapping
    - ``cubeQuant`` images to get familiar with multimodal segmentation and :math:`T_{1 \rho}` mapping

    Both acquisitions will be used to get familiar with preprocessing and morphology analysis

    The folder ``reference`` contains the folder ``newsubject``, which contains:

    - ``reference.mha``: Reference image for the atlas-based segmentation
    - ``reference_f.mha``: Femur mask of the reference image
    - ``reference_fc.mha``: Femoral cartilage mask of the reference image

    *Note*: You can use this reference image and its masks also when segmenting your **own** data

    In the folder you will also find input files (``.txt``) to run *pyKNEEr* workflow and a subset of Jupyter notebooks (``.ipynb``):

    .. figure:: _figures/demoNotebooks.png
       :align: center
       :scale: 22%

    For the demo, the notebook ``segmentation_sa.ipynb`` is duplicated in
    ``segmentation_sa_ns.ipynb`` to segment a new subject (ns), and
    ``segmentation_sa_mm.ipynb`` to segment a multimodal (mm) acquisition of the same subject

    .. note::

       In the following instructions we will assume that ``input`` is our working directory


  - ``output``: It contains the outputs of the demo, so you can compare your findings with ours

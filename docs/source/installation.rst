.. _installation:

Installation
================================================================================

.. note::

   The following commands are for Mac OS. If you work on Windows:

   - Substitute ``/`` with ``\``
   - Use the python terminal provided in the Anaconda distribution



python
--------------------------------------------------------------------------------
We recommend to install python through Anaconda, a platform providing a complete distribution

-  Download the latest release of `Anaconda <https://www.anaconda.com/download/>`_ with Python version greater than 3
-  Install Anaconda (`official documentation <https://docs.anaconda.com/anaconda/install/>`_)




*pyKNEEr*
--------------------------------------------------------------------------------

Go to :ref:`terminal <terminal>`, copy/paste each line and press ``enter``:

(in future versions the first two lines will not be necessary)

.. code-block:: bash

  pip install itk-core==4.13.1.post1 itk-numerics==4.13.1.post1 itk-filtering==4.13.1.post1 itk-io==4.13.1.post1 itk-segmentation==4.13.1.post1 itk-registration==4.13.1.post1 --force-reinstall --no-cache-dir
  pip install itk==4.13.1.post1
  pip install pykneer

The installation contains *elastix v4.8* for atlas-based segmentation

Note: We recommend to install *pyKNEEr* in a python :ref:`virtual environment <virtualenv_what>`




.. _demo:

Demo
--------------------------------------------------------------------------------

To become familiar with *pyKNEEr*, we provide a demo that you can replicate following the step-by-step instructions in the following pages

- .. raw:: html

    Download the demo images <a href="https://www.doi.org/10.5281/zenodo.3262307" target="_blank">here</a>

- Unzip the file and open it. It contains two folders:

  - ``input``: It is the basic folder to work with *pyKNEEr*:

    .. figure:: _figures/demoFolders.png
                 :align: center
                 :scale: 30%

    The folder ``original`` contains images of subjects ``01``, which contains:

    - ``DESS`` images to get familiar with atlas-based segmentation and :math:`T_2` mapping
    -  ``cubeQuant`` images to get familiar with multimodal segmentation and :math:`T_{1 \rho}` mapping

    Both acquisitions will be used to get familiar with preprocessing and morphology analysis

    The folder ``reference`` contains the folder ``newsubject``, which contains:

    - ``reference.mha``: Reference image for the atlas-based segmentation
    - ``reference_f.mha``: Femur mask of the reference image
    - ``reference_fc.mha``: Femoral cartilage mask of the reference image

    You can use this reference image and its masks also when you segment your **own** data

    In the folder you will also find Jupyter notebooks (``.ipynb``) and input files (``.txt``) to run *pyKNEEr* workflow

    .. note::

       In the following instructions we will assume that ``input`` is your working directory


  - ``output``: It contains the outputs of the demo, so you can compare your findings with ours

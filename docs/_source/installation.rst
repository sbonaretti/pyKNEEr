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

In terminal type:

.. code-block:: bash

  pip install pykneer

The installation contains *elastix v4.8* for atlas-based segmentation

Note: We recommend to install *pyKNEEr* in a python :ref:`virtual environment <virtualenv_what>`


.. _demo:


Jupyter notebooks
--------------------------------------------------------------------------------

.. raw:: html

    You can download the Jupyter notebooks serving as a user interface from <i>pyKNEEr</i> <a href="https://github.com/sbonaretti/pyKNEEr/tree/master/code" target="_blank">GitHub</a> repository



Demo
--------------------------------------------------------------------------------

To become familiar with *pyKNEEr*, we provide a demo example that you can replicate following the instructions in the next pages

.. raw:: html

    Download or clone <i>pyKNEEr</i> package from <a href="https://github.com/sbonaretti/pyKNEEr/" target="_blank">GitHub</a> repository
    

Go to ``./code/demo``. The folder is structured as follows:

.. figure:: _figures/demoFolders.png
            :align: center
            :scale: 35%


The folder ``original`` contains images of subjects ``01``, which contains:

- ``DESS`` images to get familiar with atlas-based segmentation and :math:`T_2` mapping
-  ``cubeQuant`` images to get familiar with multimodal segmentation and :math:`T_{1 \rho}` mapping

Both acquisitions will be used to get familiar with preprocessing and morphology analysis

The folder ``reference`` contains the folder ``newsubject``, which contains:

- ``reference.mha``: Reference image for the atlas-based segmentation
- ``reference_f.mha``: Femur mask of the reference image
- ``reference_fc.mha``: Femoral cartilage mask of the reference image

You can use this reference image and its masks also when you segment your **own** data

In the folder you will also find Jupyter notebooks and input ``.txt`` files

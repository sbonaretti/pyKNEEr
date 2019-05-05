.. _faq:

FAQ
================================================================================

:ref:`Why the name pyKNEEr? <name>`

:ref:`How do I determine knee laterality? <faqLaterality>`

.. _:howToJupyter:

:ref:`How do I launch Jupyter notebook? <launch_jup>`

:ref:`How do I run a Jupyter notebook? <run_jup>`

:ref:`How do I save a Jupyter notebook? <save_jup>`

:ref:`What is a virtual environment? <virtualenv_what>`

:ref:`How do I create a virtual environment? <virtualenv_how>`

:ref:`What is ITK-SNAP? <itksnap>`

:ref:`How do I compare 3D images in ITK-SNAP? <itksnapCompare>`

:ref:`How do I visualize a segmentation in ITK-SNAP? <itksnapMask>`

:ref:`How do run subsequent analysis? <analysis>`

:ref:`Issues? <issues>`

:ref:`How do I cite pyKNEEr? <citation>`

|

.. _name:

**Why the name pyKNEEr?**

  ``py`` is for python, ``KNEE`` is for femoral knee cartilage, and ``r`` is for reproducibility



.. _faqLaterality:

**How do I determine knee laterality?**

  A practical way to determine knee laterality in *pyKNEEr* coordinate system is by considering the position of the fibula next to the tibia:

  - If the fibula is on the right side of the tibia, the knee laterality is *left*
  - If the fibula is on the left side of the tibia, the knee laterality is *right*

  .. figure:: _figures/laterality.png
     :align: center
     :scale: 40%


.. _launch_jup:

**How do I launch Jupyter notebook?**

  Open Anaconda and click ``Launch`` under the JupyterLab icon



.. _run_jup:

**How do I run a Jupyter notebook?**

  Click in the cell, and then:

  - MacOS: press ``return`` + ``shift``
  - Windows: press ``enter`` + ``shift``



.. _save_jup:

**How do I save a Jupyter notebook?**

  You can save the notebook as:

  - ``.ipynb`` (File :math:`\rightarrow` Save Notebook As): Text, cells, and output are still editable
  - ``.html``, ``.pdf``, etc. (File :math:`\rightarrow` Export Notebook As): Text, cells, and outputs are not editable



.. _virtualenv_what:

**What is a virtual environment?**

  A virtual environment is like an uncontaminated island on your computer that contains the code of your current project.
  It allows you to avoid conflicts among projects that could be due to different versions of packages and dependences, and thus implies less issues when running code.
  Creating a virtual environment is not compulsory, but highly recommended



.. _virtualenv_how:

**How do I create a virtual environment?**

  MacOS:
    Open the terminal: Applications :math:`\rightarrow` Utilities :math:`\rightarrow` Terminal

  Windows:
    Open the Anaconda prompt: Start Menu :math:`\rightarrow` Anaconda :math:`\rightarrow` Anaconda Prompt

  Type the following commands:

  .. code-block:: bash

      # install the package to create virtual environments
        conda install virtualenv

      # go to your chosen folder
      # MacOS:
        cd /Users/.../yourFolder
      # Windows:
        cd C:\...\yourFolder

      # create the virtual environment
        virtualenv yourFolder

      # activate the virtual environment
      # MacOS:
        source yourFolder/bin/activate
      # Windows
        - go to the folder: C:\...\yourFolder\
        - double-click on activate.bat


.. _itksnap:

**What is ITK-SNAP?**

  ITK-SNAP is a software for image processing that has an excellent interface to visualize segmented images. All the images and masks created in this framework are in metafile format (``.mha``), and they can be easily visualized with ITK-SNAP.
  Download the latest release `here <http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3>`_.



.. _itksnapCompare:

**How do I compare 3D images in ITK-SNAP?**

  Open ITK-SNAP and load:

  - The original image: Go to ``File`` :math:`\rightarrow` ``Open Main Image``, and select your image ``*_orig.mha`` (you can also drag and drop the image)
  - The preprocessed imaged: Go to ``File`` :math:`\rightarrow` ``Add another image``, and select the corresponding image ``*_prep.mha`` (you can also drag and drop the image, and click ``Load as additional image``)

  To visualize the two images next to each other, toggle to tiled layout by clicking the middle icon in the top-right side of the viewer.



.. _itksnapMask:

**How do I visualize a segmentation in ITK-SNAP?**

  Open ITK-SNAP and load:

  - The original image: Go to ``File`` :math:`\rightarrow` ``Open Main Image``, and select ``*_prep.mha`` (you can also drag and drop the image)
  - The cartilage mask: Go to ``Segmentation`` :math:`\rightarrow` ``Open Segmentation``, and select ``*_prep_fc.mha`` (you can also drag and drop the image, and click ``Load as segmentation``).

.. _analysis:

**How do run subsequent analysis?**

  You can find examples of subsequent analysis in our :ref:`paper <citation>` (see Fig. 4)


.. _issues:

**Issues?**

  .. raw:: html

    Ask your questions  <a href="https://github.com/sbonaretti/pyKNEEr/issues" target="_blank">here</a>


.. _citation:

**How do I cite pyKNEEr?**

  You can cite paper, code, and data:

  .. raw:: html

     Paper: <br>
     Bonaretti S., Gold G., Beaupre G. <i>pyKNEEr: An image analysis workflow for open and reproducible research on femoral knee cartilage</i>.
     <a href="https://doi.org/10.1101/556423" target="_blank">bioRxiv 10.1101/556423 2019</a> <br />

     <br>

     Code:
     <br>
     Bonaretti S. "pyKNEER" (v0.0.1). Zenodo. 2019. 10.5281/zenodo.2574172
     <a href="https://zenodo.org/badge/latestdoi/155445441"><img src="https://zenodo.org/badge/155445441.svg" alt="DOI"></a> <br>

     <br>

     Data: <br>
     Dataset in (Bonaretti S. et al. 2019). Zenodo. 10.5281/zenodo.2530609
     <a href="https://doi.org/10.5281/zenodo.2530609"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.2530609.svg" alt="DOI"></a>

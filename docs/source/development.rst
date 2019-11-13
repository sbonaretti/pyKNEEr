.. _developmnet:

Development
================================================================================



Code structure
--------------------------------------------------------------------------------
*pyKNEEr* is written in a modular way to favor modifications and extensions. There are three levels of files associated with each step of the workflow:

1. Jupyter notebooks (``.ipynb``) representing both a user-interface and a record of the method and results obtained, to be attached to publications
2. Python scripts for notebooks (``for_nb.py``) containing functions called by the notebook and used to process images and visualize outputs, using parallel computing
3. Basic python scripts (``.py``) containing core algorithms and classes

The figure below depicts the code scheme (arrows = "uses functions from"):

.. figure:: _figures/codeScheme.png
   :align: center
   :scale: 26%



For example, to evaluate morphology of femoral knee cartilage, the code structure is:

1. ``morphology.ipynb``: Jupyter notebook used to run computations and visualize results. It uses functions from:
2. ``morphology_for_nb.py``: python module that contains functions to calculate knee cartilage morphology and visualize results. It uses functions from:
3. ``morphology_functions.py``: python module that contains the actual algorithms to compute cartilage thickness and volume


Variable names
--------------------------------------------------------------------------------
When reading the ``.txt`` file at the beginning of each notebook, *pyKNEEr* creates a dictionary (i.e. a struct) called ``image_data``.
In ``image_data``, each cell contains all the variables associated with one image and that will be used throughout the whole notebook.
Specifically, each cell contains an array of strings, representing paths, input and output file names, and other information needed to perform the computations in the notebook.

As an example, for the demo images, the content of the first cell of ``image_data`` in  the ``preprocessing.ipynb`` notebook can be printed out using :

.. code-block:: python

   image_data = io.load_image_data_preprocessing(input_file_name)
   image_data[0] # 0 is the ID of the first image


And the variables associated with the first image are:

.. list-table::
   :widths: 25 50
   :header-rows: 0

   * - **Folders**
     - **Example**
   * - original_folder
     - /.original/
   * - preprocessed_folder
     - /.preprocessed/
   * - image_folder_file_name
     - 01/DESS/01
   * - **File Names**
     - **Example**
   * - original_file_name
     - ./preprocessed/01_DESS_01_orig.mha
   * - preprocessed_file_name
     - ./preprocessed/01_DESS_01_prep.mha
   * - info_file_name
     - ./preprocessed/01_DESS_01_orig.txt
   * - temp_file_name
     - ./preprocessed/01_DESS_01_temp.mha
   * - **Other Information**
     - **Example**
   * - image_name_root
     - subject1_DESS
   * - laterality
     - right




Changelog
--------------------------------------------------------------------------------

.. raw:: html

    Changelog with the changes in new <i>pyKNEEr</i> versions are in the <a href="https://github.com/sbonaretti/pyKNEEr/blob/master/README.md" target="_blank">readMe</a> file of the GitHub repository



Contributing
--------------------------------------------------------------------------------

.. raw:: html

    Thanks so much for contributing!
    <br>
    The easiest way is to fork the repository from <a href="https://github.com/sbonaretti/pyKNEEr" target="_blank">GitHub</a> and then send a pull request.
    <br>
    If you want to coordinate or need any information, do not hesitate to write at serena dot bonaretti dot research at gmail dot com

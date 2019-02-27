.. _introduction:

Introduction
================================================================================

*pyKNEEr* is an image analysis workflow for **open** and **reproducible** research on femoral knee cartilage
Characteristics of *pyKNEEr* are exensively covered in :ref:`our paper<citation>`. Find below a concise summary

Workflow
--------------------------------------------------------------------------------

*pyKNEEr* workflow is composed of three **modules**:

1. **Preprocessing** to homogenize spatial characteristics and enhance intensities
2. **Segmentation** of femoral knee cartilage using an atlas-based method
3. **Analysis** of cartilage morphometry (thickness and volume) and relaxometry (fitting and EPG modeling)


Code
--------------------------------------------------------------------------------

*pyKNEEr*:

.. raw:: html

  <ul>
    <li> Uses <a href="http://jupyter.org" target="_blank">Jupyter notebook</a> as a user-interface.
         If you are not familiar with Jupyter notebook, find basic commands <a href="./faq.html">here</a>
         and tutorials on <a href="https://www.youtube.com/results?search_query=jupyter+notebook+tutorial" target="_blank">YouTube</a> </li>

    <li> Is written in <a href="https://www.python.org/" target="_blank">python</a>
         with <a href="http://www.simpleitk.org" target="_blank">SimpleITK</a> to process images </li>

    <li> Calls <a href="http://elastix.isi.uu.nl" target="_blank">elastix</a>, a toolbox for image registration used for atlas-based segmentation

  </ul>



Jupyter notebook structure
--------------------------------------------------------------------------------
For each module of *pyKNEEr* there are one or more Jupyter notebooks. All notebooks have a similar structure:

- Link to GitHub repository
- Link to documentation (this website)
- Introduction, about the algorithms in the notebook
- User input, i.e. input text files containing lists of images
- Commands
- Visualization of outputs, i.e. figures and graphs
- References, of the used algorithms
- Dependencies, for reproducibility of the computational environment


File formats
--------------------------------------------------------------------------------

Inputs and output files are in:

- **dicom (.dcm)**: Format of original images to be processed
- **metafile (.mha)**: Format of images throughout the workflow
- **text (.txt)**: Format of image list inputs and morphology outputs
- **tabular (.csv)**: Format of output descriptive statistics in morphology and relaxometry analysis

Data structure
--------------------------------------------------------------------------------

*pyKNEEr* requires data folders to be structured as follows:

.. _folderStructure:

.. figure:: _figures/folderStructure.png
            :align: center
            :scale: 40%

- **reference**: contains the reference (or target) image for the atlas-based segmentation
- **original**: contains dicom folders of the images to analyze
- **preprocessed**: contains images after preprocessing
- **registered**: contains by-products of registration and it can be deleted after computations
- **segmented**: contains segmentation masks
- **morphology**: contains cartilage surfaces, thickness, and volume
- **relaxometry**: contains masked relaxometry maps

When analyzing your own data, create only the folders ``reference`` and ``original``. *pyKNEEr* will automatically create the other folders

# *pyKNEEr*

### An image analysis workflow for **open** and **reproducible** research on **femoral knee cartilage**

- See the video on [Youtube](https://www.youtube.com/embed/7WPf5KFtYi8) for presentation, installation, and demo:   

[![Video](https://img.youtube.com/vi/7WPf5KFtYi8/0.jpg)](https://www.youtube.com/embed/7WPf5KFtYi8)



- Try *pyKNEEr* on Binder:   
  - Example #1: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sbonaretti/2019_QMSKI_Transparent_Research_WS/master?filepath=pykneer_example%2Fpykneer_example.ipynb)
  - Example #2: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sbonaretti/2019_QMSKI_Transparent_Research_WS/master?filepath=pykneer_example_2%2Fpykneer_example_2.ipynb)


- Documentation at [sbonaretti.github.io/pykneer/](https://sbonaretti.github.io/pyKNEEr/)  
- Paper: *S. Bonaretti ,G.E. Gold, G.S. Beaupre [pyKNEEr: An image analysis workflow for open and reproducible research on femoral knee cartilage](https://journals.plos.org/plosone/article/metrics?id=10.1371/journal.pone.0226501) Plos one 15.1 (2020): e0226501.*

- Release on Zenodo (with DOI for citation): [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7695948.svg)](https://doi.org/10.5281/zenodo.7695948)
---

### Contributors

Project and new code:
- [Serena Bonaretti](https://sbonaretti.github.io/)  

Open source code included in pyKNEEr:  
- [Intensity preprocessing](https://bitbucket.org/marcniethammer/ksrt/src) by Liang Shan and [Marc Niethammer](http://wwwx.cs.unc.edu/~mn/?q=content/overview) 
- [Elastix](https://github.com/SuperElastix/elastix) for registration in atlas-based segmentation by [Stefan Klein](http://bigr.nl/people/StefanKlein/)
- Cylinder fitting for cartilage flattening by https://github.com/xingjiepan/cylinder_fitting

User feedbacks and suggestions for improvements:
- Tijmen Van Zadelhoff  
- Piyush Kumar Prajapati  
- Tadiwa Waungana

---  

### Changelog 

*v 0.0.6.3*:
(Complicated version number due to issues while uploading to Pypi)
- Substituted the filter `sitk.BinaryDilate()` with the filter `sitk.BinaryDilateImageFilter()` in the function `dilate_mask()` of the module `sitk_functions` (-> Closure of issues 13 and 15)
- Added `raise FileNotFoundError` in the `elastix_transformix` module to provide feedback during the registration process

*v 0.0.5*:  
- Solved ITK bug about the Orient function in preprocessing - different way to set direction in ITK4.13  
- Added option to show images with slider in notebooks  
- Added demo_v3 to Zenodo (added sliders to notebooks)

*v 0.0.4*:  
- Added test functions
- Added relative and absolute imports within pyKNEEr package for easier debug, code extension, and testing
- Changed all variable names to python convention (e.g. from ``fileName`` to ``file_name``)  
- Improved dependences print outs in notebooks (added pyKNEEr, watermark itself, and date)
- Added demo_v2 to Zenodo (minor changes, listed in Zenodo)  
- Added page Development.html in the website

*v 0.0.3*: 
- Reduced mask file size  
- Added check to end of string in input .txt files  
- Fixing issue with ITK version to download for image orientation in preprocessing  
- Added demo_v1 to Zenodo  

*v 0.0.2*:  
- Minor   

*v 0.0.1*:   
- First release   

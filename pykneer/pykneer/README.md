## *pyKNEEr* source code

The code is modular and built in three layers:   
![code_scheme](https://sbonaretti.github.io/pyKNEEr/_images/codeScheme.png)

Modules called by notebooks:  
- `preprocessing_for_nb.py`, called by `preprocessing.ipynb`  
- `segmentation_sa_for_nb.py`, called by `segmentation_sa.ipynb` 
- `find_reference_for_nb.py`, called by `find_reference.ipynb`
- `segmentation_quality_for_nb.py`, called by `segmentation_quality.ipynb` 
- `morphology_for_nb.py`, called by `morphology.ipynb`
- `relaxometry_for_nb.py`, called by `relaxometry_fitting.ipynb` and `relaxometry_EPG.ipynb` 

Other modules, called by the previous ones:  
- `elastix_transformix.py`: class that calls elastix and transformix  
- `find_reference_functions.py`  
- `find_reference_random_gen.py`: provides random generator to pick seed images IDs
- `morphology_functions.py`  
- `relaxometry_functions.py`
- `sitk_functions.py`: functions using SimpleITK
- `pykneer_io.py`: reads input files and write output text files

Additional folders:  
- `cylinder_fitting`: code to fit cylinder to flatten cartilage. By https://github.com/xingjiepan/cylinder_fitting  
- `elastix`: elastix and transformix executables, version 4.8, downloaded from [here](http://elastix.isi.uu.nl/download.php)  
- `parameterFiles`: parameters for elastix and transformix  
- `tests`: testing calling elastix and transformix

Package file:  
- `__init__.py`: with `pyKNEEr` includes

Additional information in the documentation:
- [development](https://sbonaretti.github.io/pyKNEEr/development.html)

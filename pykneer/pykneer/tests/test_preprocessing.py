# Serena Bonaretti, 2019

"""
Test the outputs of the pyKNEEr notebook preprocessing.ipynb
To see print outs, from terminal run: pytest -s test_preprocessing.py
"""

import pytest
import papermill as pm

import test_general_functions as tgs


# --- variables ---

gt_folder               = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_distribution/outputs/"
cv_folder               = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_testing/"
notebook_name           = "preprocessing.ipynb"
input_file_name         = "image_list_preprocessing.txt"
original_file_names     = ["preprocessed/01_DESS_01_orig.mha", 
                          "preprocessed/01_DESS_02_orig.mha",
                          "preprocessed/01_cubeQuant_01_orig.mha",
                          "preprocessed/01_cubeQuant_02_orig.mha",
                          "preprocessed/01_cubeQuant_03_orig.mha",
                          "preprocessed/01_cubeQuant_04_orig.mha"
                          ]
preprocessed_file_names = ["preprocessed/01_DESS_01_prep.mha", 
                           "preprocessed/01_DESS_02_prep.mha",
                           "preprocessed/01_cubeQuant_01_prep.mha",
                           "preprocessed/01_cubeQuant_02_prep.mha",
                           "preprocessed/01_cubeQuant_03_prep.mha",
                           "preprocessed/01_cubeQuant_04_prep.mha"
                           ]
  
txt_file_names          = ["preprocessed/01_DESS_01_orig.txt", 
                           "preprocessed/01_DESS_02_orig.txt",
                           "preprocessed/01_cubeQuant_01_orig.txt",
                           "preprocessed/01_cubeQuant_02_orig.txt",
                           "preprocessed/01_cubeQuant_03_orig.txt",
                           "preprocessed/01_cubeQuant_04_orig.txt"
                           ]


# --- test functions: function names describe what is tested ---

@pytest.mark.parametrize("gt_folder, cv_folder, input_file_name", [(gt_folder, cv_folder, input_file_name)])
def test_input_files_identical (gt_folder, cv_folder, input_file_name):
        
    print ("\n-> test_input_files_identical")
    print (input_file_name)
    gt_input_file_name = gt_folder + input_file_name
    cv_input_file_name = cv_folder + input_file_name 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0
  

@pytest.mark.parametrize("cv_folder, notebook_name", [(cv_folder, notebook_name)])
def test_run_notebook (cv_folder, notebook_name):
    
    print ("\n-> test_run_notebook")
    print (notebook_name)
    assert pm.execute_notebook(
              cv_folder + notebook_name, # input
              cv_folder + notebook_name  # output
              )

    
@pytest.mark.parametrize("gt_folder, cv_folder, original_file_names", [(gt_folder, cv_folder, original_file_names)])
def test_images_after_spatial_prep_identical (gt_folder, cv_folder, original_file_names):
      
    print ("\n-> test_images_after_spatial_prep_identical")
    for i in range (0,len(original_file_names)):
        print(original_file_names[i])
        assert tgs.compare_images (gt_folder + original_file_names[i], cv_folder + original_file_names[i]) == 0
 
 
@pytest.mark.parametrize("gt_folder, cv_folder, preprocessed_file_names", [(gt_folder, cv_folder, preprocessed_file_names)])
def test_images_after_intensity_prep_identical (gt_folder, cv_folder, preprocessed_file_names):
        
    print ("\n-> test_images_after_intensity_prep_identical")
    for i in range (0,len(preprocessed_file_names)):
        print(preprocessed_file_names[i])
        assert tgs.compare_images (gt_folder + preprocessed_file_names[i], cv_folder + preprocessed_file_names[i]) == 0


@pytest.mark.parametrize("gt_folder, cv_folder, txt_file_names", [(gt_folder, cv_folder, txt_file_names)])
def test_txt_with_dicom_header_identical (gt_folder, cv_folder, txt_file_names):
    
    print ("\n-> test_txt_with_dicom_header_identical")
    for i in range (0,len(txt_file_names)):
        print(txt_file_names[i])
        assert tgs.compare_txt_files (gt_folder + txt_file_names[i], cv_folder + txt_file_names[i]) == 0
    

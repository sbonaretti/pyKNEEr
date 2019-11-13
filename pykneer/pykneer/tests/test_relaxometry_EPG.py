# Serena Bonaretti, 2019

"""
Test the outputs of the pyKNEEr notebook relaxometry_EPG.ipynb
To see print outs, from terminal run: pytest -s test_relaxometry_EPG.py
"""

import pytest
import papermill as pm

import test_general_functions as tgs


# --- variables ---

gt_folder            = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_distribution/outputs/"
cv_folder            = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_testing/"
notebook_name        = "relaxometry_EPG.ipynb"
input_file_names     = ["image_list_relaxometry_EPG.txt"]
map_file_names       = ["relaxometry/01_DESS_01_orig_T2map.mha",
                        "relaxometry/01_DESS_01_orig_T2map_masked.mha"]


# --- test functions: function names describe what is tested ---

@pytest.mark.parametrize("gt_folder, cv_folder, input_file_names", [(gt_folder, cv_folder, input_file_names)])
def test_input_files_identical (gt_folder, cv_folder, input_file_names):
    
    print ("\n-> test_input_files_identical")
    for i in range (0,len(input_file_names)):
        print(input_file_names[i])
        gt_input_file_name = gt_folder + input_file_names[i] 
        cv_input_file_name = cv_folder + input_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0


#@pytest.mark.parametrize("cv_folder, notebook_name", [(cv_folder, notebook_name)])
#def test_run_notebook (cv_folder, notebook_name):
#    
#    print ("\n-> test_run_notebook")
#    print (notebook_name)
#    assert pm.execute_notebook(
#              cv_folder + notebook_name, # input
#              cv_folder + notebook_name  # output
#              )


@pytest.mark.parametrize("gt_folder, cv_folder, map_file_names", [(gt_folder, cv_folder, map_file_names)])
def test_map_images_identical (gt_folder, cv_folder, map_file_names):
      
    print ("\n-> test_map_images_identical")
    for i in range (0,len(map_file_names)):
        print(map_file_names[i])
        assert tgs.compare_images (gt_folder + map_file_names[i], cv_folder + map_file_names[i]) == 0


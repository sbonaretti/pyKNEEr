# Serena Bonaretti, 2019

"""
Test the outputs of the pyKNEEr notebook segmentation.ipynb
To see print outs, from terminal run: pytest -s test_segmentation.py
"""

import os
import pytest
import papermill as pm
import pkg_resources
import platform
import subprocess

import test_general_functions as tgs


# --- variables ---

gt_folder             = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_distribution/outputs/"
cv_folder             = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_testing/"
parameter_files       = ["parameterFiles/MR_param_rigid.txt"]
notebook_name_1       = "segmentation_newsubject.ipynb"
notebook_name_2       = "segmentation_multimodal.ipynb"
input_file_names      = ["image_list_newsubject.txt", 
                         "image_list_multimodal.txt"]
newsubject_file_names = ["segmented/01_DESS_01_prep_fc.mha", 
                         "segmented/01_DESS_01_prep_f.mha"
                        ]
multimodal_file_names = ["segmented/01_cubeQuant_01_prep_fc.mha",
                         "segmented/01_cubeQuant_01_prep_f.mha"
                        ]



# --- test functions: function names describe what is tested ---
    
@pytest.mark.parametrize("input_file_names", [(input_file_names)])
def test_registration_parameter_files_exist (input_file_names):
    
    print ("\n-> test_registration_parameter_files_exist")
    for i in range(0, len(parameter_files)): 
        print(parameter_files[i])
        parameterFile = pkg_resources.resource_filename('pykneer', parameter_files[i])
        assert os.path.isfile(parameterFile)
        
def test_elastix_transformix_repond ():

    print ("\n-> test_elastix_transformix_repond")
    # --- elastix and transformix ---
    sys = platform.system()
    
    # get the folder depending on the OS
    if sys == "Linux":
        dirpath = pkg_resources.resource_filename('pykneer','elastix/Linux/')
    elif sys == "Windows":
        dirpath = pkg_resources.resource_filename('pykneer','elastix/Windows/')
    elif sys == "Darwin":
        dirpath = pkg_resources.resource_filename('pykneer','elastix/Darwin/')
    
    # create the full path
    completeElastixPath     = dirpath + "elastix"
    completeTransformixPath = dirpath + "transformix"

    # call elastix to see if it reponds
    cmd = [completeElastixPath]
    output = subprocess.call(cmd, cwd=dirpath)
    assert output == 0, "Elastix not responding"

    # call transformix to see if it responds
    cmd = [completeTransformixPath]
    output = subprocess.call(cmd, cwd=dirpath)
    assert output == 0, "Transformix not responding"


@pytest.mark.parametrize("gt_folder, cv_folder, input_file_names", [(gt_folder, cv_folder, input_file_names)])
def test_input_files_identical (gt_folder, cv_folder, input_file_names):
    
    print ("\n-> test_input_files_identical")
    for i in range (0,len(input_file_names)):
        print(input_file_names[i])
        gt_input_file_name = gt_folder + input_file_names[i] 
        cv_input_file_name = cv_folder + input_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0
  

#@pytest.mark.parametrize("cv_folder, notebook_name_1", [(cv_folder, notebook_name_1)])
#def test_run_notebook_1 (cv_folder, notebook_name_1):
#    
#    print ("\n-> test_run_notebook_1")
#    print (notebook_name_1)
#    assert pm.execute_notebook(
#              cv_folder + notebook_name_1, # input
#              cv_folder + notebook_name_1  # output
#              )
#
#
#@pytest.mark.parametrize("cv_folder, notebook_name_2", [(cv_folder, notebook_name_2)])
#def test_run_notebook_2 (cv_folder, notebook_name_2):
#    
#    print ("\n-> test_run_notebook_2")
#    print (notebook_name_2)
#    assert pm.execute_notebook(
#              cv_folder + notebook_name_2, # input
#              cv_folder + notebook_name_2  # output
#              )

    
@pytest.mark.parametrize("gt_folder, cv_folder, newsubject_file_names", [(gt_folder, cv_folder, newsubject_file_names)])
def test_newsubject_images_identical (gt_folder, cv_folder, newsubject_file_names):
      
    print ("\n-> test_multimodal_images_identical")
    for i in range (0,len(newsubject_file_names)):
        print(newsubject_file_names[i])
        assert tgs.compare_images (gt_folder + newsubject_file_names[i], cv_folder + newsubject_file_names[i]) == 0


@pytest.mark.parametrize("gt_folder, cv_folder, multimodal_file_names", [(gt_folder, cv_folder, multimodal_file_names)])
def test_multimodal_images_identical (gt_folder, cv_folder, multimodal_file_names):
      
    print ("\n-> test_multimodal_images_identical")
    for i in range (0,len(multimodal_file_names)):
        print(multimodal_file_names[i])
        assert tgs.compare_images (gt_folder + multimodal_file_names[i], cv_folder + multimodal_file_names[i]) == 0



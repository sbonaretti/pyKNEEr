# Serena Bonaretti, 2019

"""
Test the outputs of the pyKNEEr notebook morphology.ipynb
To see print outs, from terminal run: pytest -s test_morphology.py
"""

import pytest
import papermill as pm

import test_general_functions as tgs


# --- variables ---

gt_folder                 = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_distribution/outputs/"
cv_folder                 = "/Users/sbonaretti/Dropbox/Work/projects/pykneer/code/python/pyKNEEr/pykneer/demo/for_testing/"
notebook_name             = "morphology.ipynb"
input_file_names          = ["image_list_morphology.txt"]
cart_file_names           = ["morphology/01_DESS_01_prep_fc_arti_cart.txt",
                             "morphology/01_DESS_01_prep_fc_bone_cart.txt"]
cartFlet_file_names       = ["morphology/01_DESS_01_prep_fc_arti_cart_flat.txt",
                             "morphology/01_DESS_01_prep_fc_bone_cart_flat.txt"]
phi_file_names            = ["morphology/01_DESS_01_prep_fc_arti_phi.txt",
                             "morphology/01_DESS_01_prep_fc_bone_phi.txt"]
thickness_file_names      = ["morphology/01_DESS_01_prep_fc_thickness_1.txt"]
thickness_flat_file_names = ["morphology/01_DESS_01_prep_fc_thickness_flat_1.txt"]
volume_file_names         = ["morphology/01_DESS_01_prep_fc_volume.txt"]


#####################
#####################
#####################
#####################
#####################
# What is 01_DESS_01_prep_fc_thickness_flat_1.txt?
#####################
#####################
#####################
#####################
#####################

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

@pytest.mark.parametrize("gt_folder, cv_folder, cart_file_names", [(gt_folder, cv_folder, cart_file_names)])
def test_cart_files_identical (gt_folder, cv_folder, cart_file_names):
    
    print ("\n-> test_cart_files_identical")
    for i in range (0,len(cart_file_names)):
        print(cart_file_names[i])
        gt_input_file_name = gt_folder + cart_file_names[i] 
        cv_input_file_name = cv_folder + cart_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0


@pytest.mark.parametrize("gt_folder, cv_folder, cartFlet_file_names", [(gt_folder, cv_folder, cartFlet_file_names)])
def test_cartFlet_files_identical (gt_folder, cv_folder, cartFlet_file_names):
    
    print ("\n-> test_cartFlet_files_identical")
    for i in range (0,len(cartFlet_file_names)):
        print(cartFlet_file_names[i])
        gt_input_file_name = gt_folder + cartFlet_file_names[i] 
        cv_input_file_name = cv_folder + cartFlet_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0


@pytest.mark.parametrize("gt_folder, cv_folder, phi_file_names", [(gt_folder, cv_folder, phi_file_names)])
def test_phi_files_identical (gt_folder, cv_folder, phi_file_names):
    
    print ("\n-> test_phi_files_identical")
    for i in range (0,len(phi_file_names)):
        print(phi_file_names[i])
        gt_input_file_name = gt_folder + phi_file_names[i] 
        cv_input_file_name = cv_folder + phi_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0


@pytest.mark.parametrize("gt_folder, cv_folder, thickness_file_names", [(gt_folder, cv_folder, thickness_file_names)])
def test_thickness_files_identical (gt_folder, cv_folder, thickness_file_names):
    
    print ("\n-> test_thickness_files_identical")
    for i in range (0,len(thickness_file_names)):
        print(thickness_file_names[i])
        gt_input_file_name = gt_folder + thickness_file_names[i] 
        cv_input_file_name = cv_folder + thickness_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0

@pytest.mark.parametrize("gt_folder, cv_folder, thickness_flat_file_names", [(gt_folder, cv_folder, thickness_flat_file_names)])
def test_thickness_flat_files_identical (gt_folder, cv_folder, thickness_flat_file_names):
    
    print ("\n-> test_thickness_flat_files_identical")
    for i in range (0,len(thickness_flat_file_names)):
        print(thickness_flat_file_names[i])
        gt_input_file_name = gt_folder + thickness_flat_file_names[i] 
        cv_input_file_name = cv_folder + thickness_flat_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0


@pytest.mark.parametrize("gt_folder, cv_folder, volume_file_names", [(gt_folder, cv_folder, volume_file_names)])
def test_volume_files_identical (gt_folder, cv_folder, volume_file_names):
    
    print ("\n-> test_volume_files_identical")
    for i in range (0,len(volume_file_names)):
        print(volume_file_names[i])
        gt_input_file_name = gt_folder + volume_file_names[i] 
        cv_input_file_name = cv_folder + volume_file_names[i] 
    assert tgs.compare_txt_files (gt_input_file_name, cv_input_file_name) == 0






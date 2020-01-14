# Serena Bonaretti, 2018

"""
Module with functions to read/write .txt files in pykneer

Functions:
    - folder_divider
    - load_image_data_preprocessing
    - load_image_data_find_reference
    - load_image_data_segmentation
    - add_names_to_image_data
    - load_image_data_segmentation_quality
    - load_image_data_morphology
    - load_image_data_EPG
    - load_image_data_fitting
    - read_txt_to_np_array
    - write_np_array_to_txt
"""


import numpy as np
import os
import pkg_resources
import platform
import re


# ---------------------------------------------------------------------------------------------------------------------------
# BASIC FUNCTIONS  ----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def folder_divider():

    """
    Based on the OS determines if file path strings contain "\" or "/"

    """

    # determine the system to define the folder divider ("\" or "/")
    sys = platform.system()
    if sys == "Linux":
        folder_div = "/"
    elif sys == "Darwin":
        folder_div = "/"
    elif sys == "Windows":
        folder_div = "\\"

    return folder_div


# ---------------------------------------------------------------------------------------------------------------------------
# PREPROCESSING -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_preprocessing(input_file_name):

    """
    Parses the input file of preprocessing.ipynb
    """

    folder_div = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(input_file_name):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (input_file_name) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get input_file_name content
    file_content=[]
    for line in open(input_file_name):
        file_content.append(line.rstrip("\n"))

    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content)):
        file_content[i] = file_content[i].rstrip()

    # ----------------------------------------------------------------------------------------------------------------------
    # folders

    # line 1 is the original folder of acquired dcm
    # add slash or back slash at the end
    original_folder = file_content[0]
    if not original_folder.endswith(folder_div):
        original_folder = original_folder + folder_div
    # make sure the last folder is called "original"
    temp = os.path.basename(os.path.normpath(original_folder))
    if temp != "original":
        print("----------------------------------------------------------------------------------------")
        print("""ERROR: Put your dicoms in a parent folder called "original" """)
        print("----------------------------------------------------------------------------------------")
        return {}
    # make sure that the path exists
    if not os.path.isdir(original_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The original folder %s does not exist" % (original_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the preprocessed folder
    preprocessed_folder = os.path.split(original_folder)[0]     # remove the slash or backslash
    preprocessed_folder = os.path.split(preprocessed_folder)[0] # remove "original"
    preprocessed_folder = preprocessed_folder + folder_div + "preprocessed" + folder_div
    if not os.path.isdir(preprocessed_folder):
        os.mkdir(preprocessed_folder)
        print("-> preprocessed_folder %s created" % (preprocessed_folder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    all_image_data = []
    for i in range(1,len(file_content),2):

        # current image folder name
        image_folder_file_name = file_content[i]

        # if there are empty lines at the end of the file skip them
        if len(image_folder_file_name) != 0:

            # make sure the folder exists
            if not os.path.isdir(original_folder + image_folder_file_name):
                print("----------------------------------------------------------------------------------------")
                print("ERROR: The folder %s does not exist" % (image_folder_file_name) )
                print("----------------------------------------------------------------------------------------")
                return {}

            # make sure there are dicom files in the folder
            for fname in os.listdir(original_folder + image_folder_file_name):
                if fname.endswith(".dcm") or fname.endswith(".DCM") or fname.endswith(""):
                    a = 1 #print(original_folder + image_folder_file_name)
                else:
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The folder %s does not contain dicom files" % (original_folder + image_folder_file_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # knee laterality
            laterality = file_content[i+1]
            if laterality != "right" and laterality != "Right" and laterality != "left" and laterality != "left":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Knee laterality must be 'right' or 'left'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # create the dictionary
            image_data = {}
            # add inputs
            image_data["original_folder"]        = original_folder
            image_data["preprocessed_folder"]    = preprocessed_folder
            image_data["image_folder_file_name"] = image_folder_file_name
            image_data["laterality"]             = laterality
            # add outputs
            image_name_root = image_folder_file_name.replace(folder_div, "_")
            image_data["image_name_root"]        = image_name_root
            image_data["temp_file_name"]         = preprocessed_folder + image_data["image_name_root"] + "_temp.mha"
            image_data["original_file_name"]     = preprocessed_folder + image_data["image_name_root"] + "_orig.mha"
            image_data["preprocessed_file_name"] = preprocessed_folder + image_data["image_name_root"] + "_prep.mha"
            image_data["info_file_name"]         = preprocessed_folder + image_data["image_name_root"] + "_orig.txt"

            # print current file name
            print (image_data["image_name_root"])

            # send to the data list
            all_image_data.append(image_data)

    print ("-> information loaded for " + str(len(all_image_data)) + " subjects")

    # return the dictionary
    return all_image_data


# ---------------------------------------------------------------------------------------------------------------------------
# FIND REFERENCE ------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_find_reference(input_file_name):

    """
    Parses the input file of find_reference.ipynb
    """

    folder_div = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(input_file_name):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (input_file_name) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get input_file_name content
    file_content=[]
    for line in open(input_file_name):
        file_content.append(line.rstrip("\n"))

    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content)):
        file_content[i] = file_content[i].rstrip()

    # ----------------------------------------------------------------------------------------------------------------------
    # get folders
    # line 1 is the parent folder
    parent_folder = file_content[0]
    if not parent_folder.endswith(folder_div):
        parent_folder = parent_folder + folder_div
    if not os.path.isdir(parent_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The parent folder %s does not exist" % (parent_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    all_image_data = []

    for i in range(1,len(file_content)):

        current_line = file_content[i]

        # if there are empty lines at the end of the file
        if len(current_line) != 0:

            # get image type (image or mask)
            image_type = current_line[0]
            if image_type != "r" and image_type != "m":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'r' or 'm'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the refence image
            if image_type == "r":
                # get image name
                reference_name = current_line[2:len(current_line)]
                # check that the reference image exists
                if not os.path.isfile(parent_folder + reference_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (parent_folder + reference_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the moving image
            if image_type == "m":
                # get image name
                moving_name = current_line[2:len(current_line)]
                # check that the reference image exists
                if not os.path.isfile(parent_folder + moving_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (parent_folder + moving_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # current image in a struct to the registration class
                image_data = {}

                # from input file
                image_data["parent_folder"]     = parent_folder
                image_data["reference_name"]    = reference_name
                image_data["moving_name"]       = moving_name

                # added to uniform with requirements in ElastixTransformix classes
                reference_root, image_ext       = os.path.splitext(reference_name)
                moving_root, image_ext          = os.path.splitext(moving_name)
                image_data["reference_root"]    = reference_root
                image_data["moving_root"]       = moving_root
                image_data["moving_folder"]     = parent_folder
                image_data["cartilage"]         = "fc"
                image_data["bone"]              = "f"
                image_data["current_anatomy"]   = "f"
                image_data["registered_folder"] = parent_folder
                image_data["segmented_folder"]  = []
                image_data["vector_field_name"] = moving_root +"_VF.mha"

                # add extra filenames and paths
                image_data = add_names_to_image_data(image_data,0)

                # send to the data list
                all_image_data.append(image_data)

    print ("-> image information loaded")

    # return the image info
    return all_image_data


# ---------------------------------------------------------------------------------------------------------------------------
# SEGMENTATION --------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_segmentation(registration_type, input_file_name):

    """
    Parses the input file of segmentation.ipynb
    """

    folder_div = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if registration_type is allowed
    if registration_type != "newsubject" and registration_type != "longitudinal" and registration_type != "multimodal":
        print("----------------------------------------------------------------------------------------")
        print("ERROR: Please add 'newsubject' or 'longitudinal' or 'multimodal' as first input")
        print("----------------------------------------------------------------------------------------")
        return {}

#    # ----------------------------------------------------------------------------------------------------------------------
#    # check if anatomy is allowed
#    if anatomy != "femur_cart" and anatomy != "tibia_cart" and anatomy != "patella_cart":
#        print("----------------------------------------------------------------------------------------")
#        print("ERROR: Please add 'femur_cart' or 'tibia_cart' or 'patella_cart' as second input")
#        print("----------------------------------------------------------------------------------------")
#        return {}
#    if anatomy == "femur_cart":
#        bone = "f"
#        cartilage = "fc"
#    elif anatomy == "tibia_cart":
#        bone = "t"
#        cartilage = "tc"
#    elif anatomy == "patella_cart":
#        bone = "p"
#        cartilage = "pc"
    # In the future, extensions for all knee cartilages
    #anatomy = "femur_cart"
    bone = "f"
    cartilage = "fc"

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(input_file_name):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (input_file_name) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get input_file_name content
    file_content=[]
    for line in open(input_file_name):
        file_content.append(line.rstrip("\n"))

    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content)):
        file_content[i] = file_content[i].rstrip()


    # ----------------------------------------------------------------------------------------------------------------------
    # get folders
    # line 1 is folder of reference image
    reference_folder = file_content[0]
    if not reference_folder.endswith(folder_div):
        reference_folder = reference_folder + folder_div
    if not os.path.isdir(reference_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The reference folder %s does not exist" % (reference_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # line 2 is folder of the preprocessed (*_prep.mha) images, i.e. the moving image folder
    moving_folder = file_content[1]
    if not moving_folder.endswith(folder_div):
        moving_folder = moving_folder + folder_div
    if not os.path.isdir(moving_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The preprocessed folder %s does not exist" % (moving_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the registered folder
    registered_folder = os.path.split(moving_folder)[0] # remove the slash or backslash
    registered_folder = os.path.split(registered_folder)[0] # remove "original"
    registered_folder = registered_folder + folder_div + "registered" + folder_div
    if not os.path.isdir(registered_folder):
        os.mkdir(registered_folder)
        print("-> registered_folder %s created" % (registered_folder) )

    # create the segmented folder
    segmented_folder = os.path.split(moving_folder)[0] # remove the slash or backslash
    segmented_folder = os.path.split(segmented_folder)[0] # remove "original"
    segmented_folder = segmented_folder + folder_div + "segmented" + folder_div
    if not os.path.isdir(segmented_folder):
        os.mkdir(segmented_folder)
        print("-> segmented_folder %s created" % (segmented_folder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    all_image_data = []

    for i in range(2,len(file_content)):

        current_line = file_content[i]

        # if there are empty lines at the end of the file
        if len(current_line) != 0:

            # get image type (reference or moving)
            image_type = current_line[0]
            if image_type != "r" and image_type != "m":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'r' or 'm'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the reference image
            if image_type == "r":
                # get image name
                reference_name = current_line[2:len(current_line)]
                # check that the reference image exists
                if not os.path.isfile(reference_folder + reference_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (reference_folder + reference_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}
            # if the current image is the moving image
            if image_type == "m":
                # get image name
                moving_name = current_line[2:len(current_line)]
                # check that the reference image exists
                if not os.path.isfile(moving_folder + moving_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (moving_folder + moving_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # current image in a struct to the registration class
                reference_root, reference_ext = os.path.splitext(reference_name)
                moving_root, moving_ext = os.path.splitext(moving_name)
                image_data = {}
                image_data["registration_type"]     = registration_type
                image_data["cartilage"]             = cartilage
                image_data["bone"]                  = bone
                image_data["current_anatomy"]       = []
                image_data["reference_folder"]      = reference_folder
                image_data["reference_name"]        = reference_name
                image_data["reference_root"]        = reference_root
                image_data["moving_folder"]         = moving_folder
                image_data["moving_name"]           = moving_name
                image_data["moving_root"]           = moving_root
                image_data["registered_folder"]     = registered_folder
                image_data["segmented_folder"]      = segmented_folder

                # add extra filenames and paths
                image_data = add_names_to_image_data(image_data,1)

                # send to the data list
                all_image_data.append(image_data)

    print ("-> image information loaded")

    # return all the info on the images to be segmented
    return all_image_data


# ---------------------------------------------------------------------------------------------------------------------------
# ADD NAMES -----------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

# Function used by loadimage_dataSegmentation and loadimage_dataFindReference
def add_names_to_image_data(image_data,folderFlag):

    """
    Adds file and folder names for registration (atlas-based segmentation)
    Called by load_image_data_find_reference and load_image_data_segmentation
    """

    folder_div = folder_divider()

    # output folders
    image_data["registered_sub_folder"]        = image_data["registered_folder"] + image_data["moving_root"] + folder_div
    image_data["i_registered_sub_folder"]       = image_data["registered_sub_folder"] + "invert" + folder_div

    # create output folders that do not exist
    if folderFlag ==1:
        if not os.path.isdir(image_data["registered_sub_folder"]):
            os.makedirs(image_data["registered_sub_folder"])
        if not os.path.isdir(image_data["i_registered_sub_folder"]):
            os.makedirs(image_data["i_registered_sub_folder"])

    # get current bone and cartilage
    bone      = image_data["bone"]
    cartilage = image_data["cartilage"]

    # reference mask file names
    image_data["dilate_radius"]                        = 15
    image_data[bone + "mask_file_name"]                = image_data["reference_root"] + "_" + bone + ".mha"
    image_data[bone + "dil_mask_file_name"]            = image_data["reference_root"] + "_" + bone + "_" + str(image_data["dilate_radius"]) + ".mha"
    image_data[bone + "levelset_mask_file_name"]      = image_data["reference_root"] + "_" + bone + "_levelSet.mha"
    image_data[cartilage + "mask_file_name"]           = image_data["reference_root"] + "_" + cartilage + ".mha"
    image_data[cartilage + "dil_mask_file_name"]       = image_data["reference_root"] + "_" + cartilage + "_" + str(image_data["dilate_radius"]) + ".mha"
    image_data[cartilage + "levelset_mask_file_name"] = image_data["reference_root"] + "_" + cartilage + "_levelSet.mha"

    # output image file names
    image_data[bone + "rigid_name"]            = bone + "_rigid.mha"
    image_data[bone + "similarity_name"]       = bone + "_similarity.mha"
    image_data[bone + "spline_name"]           = bone + "_spline.mha"
    image_data[cartilage + "spline_name"]      = cartilage + "_spline.mha"

    # output mask file names
    image_data[bone + "m_rigid_name"]           = bone + "_rigidMask.mha"
    image_data[bone + "m_similarity_name"]      = bone + "_similarityMask.mha"
    image_data[bone + "m_spline_name"]          = bone + "_splineMask.mha"
    image_data[bone + "mask"]                   = image_data["moving_root"] + "_" + bone + ".mha"
    image_data[cartilage + "m_rigid_name"]      = cartilage + "_rigidMask.mha"
    image_data[cartilage + "m_similarity_name"] = cartilage + "_similarityMask.mha"
    image_data[cartilage + "m_spline_name"]     = cartilage + "_splineMask.mha"
    image_data[cartilage + "mask"]              = cartilage + "_mask.mha"
    image_data[cartilage + "mask"]              = image_data["moving_root"] + "_" + cartilage + ".mha"

    # output transformation names
    image_data[bone + "rigid_transf_name"]         = "TransformParameters."  + bone + "_rigid.txt"
    image_data[bone + "similarity_transf_name"]    = "TransformParameters."  + bone + "_similarity.txt"
    image_data[bone + "spline_transf_name"]        = "TransformParameters."  + bone + "_spline.txt"
    image_data[bone + "i_rigid_transf_name"]       = "iTransformParameters." + bone + "_rigid.txt"
    image_data[bone + "i_similarity_transf_name"]  = "iTransformParameters." + bone + "_similarity.txt"
    image_data[bone + "i_spline_transf_name"]      = "iTransformParameters." + bone + "_spline.txt"
    image_data[bone + "m_rigid_transf_name"]       = "mTransformParameters." + bone + "_rigid.txt"
    image_data[bone + "m_similarity_transf_name"]  = "mTransformParameters." + bone + "_similarity.txt"
    image_data[bone + "m_spline_transf_name"]      = "mTransformParameters." + bone + "_spline.txt"
    image_data[cartilage + "spline_transf_name"]   = "TransformParameters."  + cartilage + "_spline.txt"
    image_data[cartilage + "i_spline_transf_name"] = "iTransformParameters." + cartilage + "_spline.txt"
    image_data[cartilage + "m_spline_transf_name"] = "mTransformParameters." + cartilage + "_spline.txt"

    # parameter files 
    # if during development
    if __package__ is None or __package__ == '':
        parameter_folder = os.path.dirname(os.path.realpath(__file__)) + "/parameterFiles"
    # if using package
    else:
        parameter_folder = pkg_resources.resource_filename('pykneer','parameterFiles') + folder_div
      
    if not parameter_folder.endswith(folder_div):
        parameter_folder = parameter_folder + folder_div
    if not os.path.isdir(parameter_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The parameter folder %s does not exist" % (parameter_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}
    # check if the folder contains all the parameter files
    param_file_rigid        = parameter_folder + "MR_param_rigid.txt"
    i_param_file_rigid      = parameter_folder + "MR_iparam_rigid.txt"
    param_file_similarity   = parameter_folder + "MR_param_similarity.txt"
    i_param_file_similarity = parameter_folder + "MR_iparam_similarity.txt"
    param_file_spline       = parameter_folder + "MR_param_spline.txt"
    i_param_file_spline     = parameter_folder + "MR_iparam_spline.txt"
    if not os.path.isfile(param_file_rigid):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (param_file_rigid) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(i_param_file_rigid):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (i_param_file_rigid) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(param_file_similarity):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (param_file_similarity) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(i_param_file_similarity):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (i_param_file_similarity) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(param_file_spline):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (param_file_spline) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(i_param_file_spline):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (i_param_file_spline) )
        print("----------------------------------------------------------------------------------------")
        return {}
    # add parameter files to image_data
    image_data["param_file_rigid"]        = param_file_rigid
    image_data["i_param_file_rigid"]      = i_param_file_rigid
    image_data["param_file_similarity"]   = param_file_similarity
    image_data["i_param_file_similarity"] = i_param_file_similarity
    image_data["param_file_spline"]       = param_file_spline
    image_data["i_param_file_spline"]     = i_param_file_spline

    # elastix path (from binaries in pykneer package)
    sys = platform.system()
    if sys == "Linux":
        dirpath = pkg_resources.resource_filename('pykneer','elastix/Linux/')
    elif sys == "Windows":
        dirpath = pkg_resources.resource_filename('pykneer','elastix\\Windows\\')
    elif sys == "Darwin":
        # For debugging - I am working on a MacOS
        if __package__ is None or __package__ == '':
            dirpath = os.path.dirname(os.path.realpath(__file__)) + "/elastix/Darwin/"
        # if using package
        else:
            dirpath = pkg_resources.resource_filename('pykneer','elastix/Darwin/')
    image_data["elastix_folder"]            = dirpath
    image_data["complete_elastix_path"]     = dirpath + "elastix"
    image_data["complete_transformix_path"] = dirpath + "transformix"

    return image_data


# ---------------------------------------------------------------------------------------------------------------------------
# SEGMENTATION QUALITY ------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_segmentation_quality(input_file_name):

    """
    Parses the input file of segmentation_quality.ipynb
    """

    folder_div = folder_divider()

     # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(input_file_name):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (input_file_name) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get input_file_name content
    file_content=[]
    for line in open(input_file_name):
        file_content.append(line.rstrip("\n"))

    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content)):
        file_content[i] = file_content[i].rstrip()


    # line 0 is folder of the registered images
    segmented_folder = file_content[0]
    if not segmented_folder.endswith(folder_div):
        segmented_folder = segmented_folder + folder_div
    if not os.path.isdir(segmented_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The segmented folder %s does not exist" % (segmented_folder) )
        print("----------------------------------------------------------------------------------------")

    # line 1 is folder of the segmented masks
    ground_truth_folder = file_content[1]
    if not ground_truth_folder.endswith(folder_div):
        ground_truth_folder = ground_truth_folder + folder_div
    if not os.path.isdir(ground_truth_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The ground truth folder %s does not exist" % (ground_truth_folder) )
        print("----------------------------------------------------------------------------------------")

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    all_image_data = []

    for i in range(2,len(file_content)):

        current_line = file_content[i]

        # if there are empty lines at the end of the file
        if len(current_line) != 0:

            # get image type (reference or moving)
            image_type = current_line[0]
            if image_type != "s" and image_type != "g":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 's' or 'g'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the segmented image
            if image_type == "s":
                # get image name
                segmented_name = current_line[2:len(current_line)]
                # check that the segmented image exists
                if not os.path.isfile(segmented_folder + segmented_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmented_folder + segmented_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}
            # if the current image is the moving image
            if image_type == "g":
                # get image name
                ground_truth_name = current_line[2:len(current_line)]
                # check that the groundTruth image exists
                if not os.path.isfile(ground_truth_folder + ground_truth_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (ground_truth_folder + ground_truth_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # put pair in a list
                image_data = {}
                image_data["segmented_folder"]         = segmented_folder
                image_data["ground_truth_folder"]      = ground_truth_folder
                image_data["segmented_name"]           = segmented_name
                image_data["ground_truth_name"]        = ground_truth_name

                # send to the data list
                all_image_data.append(image_data)

    print ("-> image information loaded")

    # return the image info
    return all_image_data


# ---------------------------------------------------------------------------------------------------------------------------
# MORPHOLOGY ----------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_morphology(input_file_name):

    """
    Parses the input file of morphology.ipynb
    """

    folder_div = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(input_file_name):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (input_file_name) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get input_file_name content
    file_content=[]
    for line in open(input_file_name):
        file_content.append(line.rstrip("\n"))

    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content)):
        file_content[i] = file_content[i].rstrip()


    # ----------------------------------------------------------------------------------------------------------------------
    # get folder - line 1 is the input folder
    input_folder = file_content[0]
    if not input_folder.endswith(folder_div):
        input_folder = input_folder + folder_div
    if not os.path.isdir(input_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The input folder %s does not exist" % (input_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the morphology folder
    morphology_folder = os.path.split(input_folder)[0] # remove the slash or backslash
    morphology_folder = os.path.split(morphology_folder)[0] # remove "original"
    morphology_folder = morphology_folder + folder_div + "morphology" + folder_div
    if not os.path.isdir(morphology_folder):
        os.mkdir(morphology_folder)
        print("-> morphology_folder %s created" % (morphology_folder) )


    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    all_image_data = []

    for i in range(1,len(file_content)):

        mask_name = file_content[i]

        # if there are empty lines at the end of the file
        if len(mask_name) != 0:

            # check that the mask exists
            if not os.path.isfile(input_folder + mask_name):
                print("----------------------------------------------------------------------------------------")
                print("ERROR: The file %s does not exist" % (input_folder + mask_name) )
                print("----------------------------------------------------------------------------------------")
                return {}

            # create the dictionary
            image_data = {}
            # input names
            image_data["input_folder"]        = input_folder
            image_data["mask_name"]           = mask_name
            # output names
            mask_name_root, mask_name_ext       = os.path.splitext(mask_name)
            image_data["bone_cart_name"]      = mask_name_root + "_bone_cart.txt"
            image_data["arti_cart_name"]      = mask_name_root + "_arti_cart.txt"
            image_data["thickness_name"]      = []
            image_data["thickness_flat_name"] = []
            image_data["algorithm"]           = []
            image_data["volume_name"]         = mask_name_root + "_volume.txt"
            image_data["morphology_folder"]   = morphology_folder
            # for visualization
            image_data["bone_cart_flat_name"] = mask_name_root + "_bone_cart_flat.txt"
            image_data["arti_cart_flat_name"] = mask_name_root + "_arti_cart_flat.txt"
            image_data["bone_phi_name"]       = mask_name_root + "_bone_phi.txt"
            image_data["arti_phi_name"]       = mask_name_root + "_arti_phi.txt"

            # send to the whole data array
            all_image_data.append(image_data)

    print ("-> image information loaded")

    # return the image info
    return all_image_data


# ---------------------------------------------------------------------------------------------------------------------------
# EPG (T2 from DESS)---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_EPG(input_file_name):

    """
    Parses the input file of relaxation_EPG.ipynb
    """

    # determine the sistem to define the folder divider ("\" or "/")
    folder_div = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(input_file_name):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (input_file_name) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get input_file_name content
    file_content=[]
    for line in open(input_file_name):
        file_content.append(line.rstrip("\n"))

    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content)):
        file_content[i] = file_content[i].rstrip()

    # ----------------------------------------------------------------------------------------------------------------------
    # look for needed folders
    # preprocessed folder
    preprocessed_folder = file_content[0]
    if not preprocessed_folder.endswith(folder_div):
        preprocessed_folder = preprocessed_folder + folder_div
    if not os.path.isdir(preprocessed_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The preprocessing folder %s does not exist" % (preprocessed_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # segmented folder
    segmented_folder = file_content[1]
    if not segmented_folder.endswith(folder_div):
        segmented_folder = segmented_folder + folder_div
    if not os.path.isdir(segmented_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The segmented folder %s does not exist" % (segmented_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the t2mapping folder
    relaxometry_folder = os.path.split(preprocessed_folder)[0] # remove the slash or backslash
    relaxometry_folder = os.path.split(relaxometry_folder)[0] # remove "original"
    relaxometry_folder = relaxometry_folder + folder_div + "relaxometry" + folder_div
    if not os.path.isdir(relaxometry_folder):
        os.mkdir(relaxometry_folder)
        print("-> relaxometry folder %s created" % (relaxometry_folder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    all_image_data = []

    for i in range(2,len(file_content)):

        current_line = file_content[i]

        # if there are empty lines at the end of the file
        if len(current_line) != 0:

            # get image type (reference or moving)
            image_type = current_line[0:2]
            if image_type != "i1" and image_type != "i2" and image_type != "cm":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'i1' or 'i2' or 'cm' ")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the i1 image
            if image_type == "i1":
                # get image name
                i1_file_name = current_line[3:len(current_line)]
                # check that the segmented image exists
                if not os.path.isfile(preprocessed_folder + i1_file_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessed_folder + i1_file_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # check that the info file exists
            image_name_root, image_ext         = os.path.splitext(i1_file_name)
            info_file_name = image_name_root + ".txt"
            if not os.path.isfile(preprocessed_folder + info_file_name):
                print("----------------------------------------------------------------------------------------")
                print("ERROR: The file %s does not exist" % (preprocessed_folder + info_file_name) )
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the i2 image
            if image_type == "i2":
                # get image name
                i2_file_name = current_line[3:len(current_line)]
                # check that the segmented image exists
                if not os.path.isfile(preprocessed_folder + i2_file_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessed_folder + i2_file_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the cartilage mask
            if image_type == "cm":
                # get image name
                mask_file_name = current_line[3:len(current_line)]
                # check that the segmented image exists
                if not os.path.isfile(segmented_folder + mask_file_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmented_folder + mask_file_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # create the dictionary
                image_data = {}
                # add folders
                image_data["preprocessed_folder"]   = preprocessed_folder
                image_data["segmented_folder"]      = segmented_folder
                image_data["relaxometry_folder"]    = relaxometry_folder
                # add input file names
                image_data["i1_file_name"]          = i1_file_name
                image_data["i2_file_name"]          = i2_file_name
                image_data["mask_file_name"]        = mask_file_name
                image_data["info_file_name"]        = info_file_name
                # add output file names
                image_data["t2_map_file_name"]      = image_name_root + "_T2map.mha"
                image_data["t2_map_mask_file_name"] = image_name_root + "_T2map_masked.mha"
                # others
                image_data["image_name_root"]       = image_name_root

                print (image_data["image_name_root"])

                # send to the data dictionary
                all_image_data.append(image_data)



    print ("-> information loaded for " + str(len(all_image_data)) + " subjects")

    # return the image info
    return all_image_data


# ---------------------------------------------------------------------------------------------------------------------------
# FITTING FOR RELAXOMETRY MAPS ----------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_fitting(input_file_name, method_flag, registrationFlag):

    """
    Parses the input file of relaxation_fitting.ipynb
    """

    # determine the sistem to define the folder divider ("\" or "/")
    folder_div = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(input_file_name):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (input_file_name) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get input_file_name content
    file_content=[]
    for line in open(input_file_name):
        file_content.append(line.rstrip("\n"))

    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content)):
        file_content[i] = file_content[i].rstrip()

    # ----------------------------------------------------------------------------------------------------------------------
    # look for needed folders
    # preprocessed folder
    preprocessed_folder = file_content[0]
    if not preprocessed_folder.endswith(folder_div):
        preprocessed_folder = preprocessed_folder + folder_div
    if not os.path.isdir(preprocessed_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The preprocessing folder %s does not exist" % (preprocessed_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # segmented folder
    segmented_folder = file_content[1]
    if not segmented_folder.endswith(folder_div):
        segmented_folder = segmented_folder + folder_div
    if not os.path.isdir(segmented_folder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The segmented folder %s does not exist" % (segmented_folder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the relaxometry folder
    relaxometry_folder = os.path.split(preprocessed_folder)[0] # remove the slash or backslash
    relaxometry_folder = os.path.split(relaxometry_folder)[0] # remove "original"
    relaxometry_folder = relaxometry_folder + folder_div + "relaxometry" + folder_div
    if not os.path.isdir(relaxometry_folder):
        os.mkdir(relaxometry_folder)
        print("-> relaxometry %s created" % (relaxometry_folder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # number of acquisitions
    n_of_acquisitions = int(file_content[2])
    # create the IDs for the acquisitions
    acquisition_ID = []
    for a in range(0,n_of_acquisitions):
        acquisition_ID.append("i" + str(a+1))

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    all_image_data     = []
    acquisition_file_names = []
    info_file_names        = []

    for i in range(3,len(file_content)):

        current_line = file_content[i]


        # if the line is not empty (there might be empty lines at the end of the file)
        if len(current_line) != 0:

            # get image type (reference or moving)
            image_type = current_line[0:2]


            #if image_type != "i1" and image_type != "i2" and image_type != "i3" and image_type != "i4" and image_type != "bm" and image_type != "cm":
            if image_type not in acquisition_ID and image_type != "bm" and image_type != "cm":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'i1' or 'i2' or 'i3' or 'i4' or 'bm' or 'cm' ")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is an acquisition
            if image_type in acquisition_ID:
            #if image_type == "i1":
                # get image name
                #i1_file_name = current_line[3:len(current_line)]
                acquisition_file_names.append(current_line[3:len(current_line)])
                # check that the preprocessed image exists
                if not os.path.isfile(preprocessed_folder + acquisition_file_names[-1]):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessed_folder + acquisition_file_names[-1]) )
                    print("----------------------------------------------------------------------------------------")
                    return {}
                # check that the info file exists
                image_name_root, image_ext         = os.path.splitext(acquisition_file_names[-1])
                info_file_names.append(image_name_root + ".txt")
                if not os.path.isfile(preprocessed_folder + info_file_names[-1]):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessed_folder + info_file_names[-1]) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the bone mask
            if image_type == "bm":
                # get image name
                bone_mask_file_name = current_line[3:len(current_line)]
                # check that the segmented image exists
                if not os.path.isfile(segmented_folder + bone_mask_file_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmented_folder + bone_mask_file_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the cartilage mask
            if image_type == "cm":
                # get image name
                cart_mask_file_name = current_line[3:len(current_line)]
                # check that the segmented image exists
                if not os.path.isfile(segmented_folder + cart_mask_file_name):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmented_folder + cart_mask_file_name) )
                    print("----------------------------------------------------------------------------------------")
                    return {}


                # create the dictionary
                image_data = {}

                # folders
                image_data["preprocessed_folder"]    = preprocessed_folder
                image_data["segmented_folder"]       = segmented_folder
                image_data["relaxometry_folder"]     = relaxometry_folder

                # input file names
                image_data["acquisition_file_names"] = acquisition_file_names
                image_data["info_file_names"]        = info_file_names
                image_data["bone_mask_file_name"]    = bone_mask_file_name
                image_data["cart_mask_file_name"]    = cart_mask_file_name

                # fitting type
                image_data["method_flag"]            = method_flag

                # output file names
                image_name_root, image_ext           = os.path.splitext(acquisition_file_names[0])
                if registrationFlag == 1:
                    if method_flag == 0: # linear fitting
                        image_data["map_file_name"] = image_name_root + "_map_lin_aligned.mha"
                    elif method_flag == 1: # exponential fitting
                        image_data["map_file_name"] = image_name_root + "_map_exp_aligned.mha"
                else:
                    if method_flag == 0: # linear fitting
                        image_data["map_file_name"] = image_name_root + "_map_lin.mha"
                    elif method_flag == 1: # exponential fitting
                        image_data["map_file_name"] = image_name_root + "_map_exp.mha"

                # alignment: fixed variables for elastix_transformix.py
                image_data["current_anatomy"]        = 'femurCart' #### to be parametrized in a later release
                bone                               = "f"         #### to be parametrized in a later release
                image_data["bone"]                  = bone
                image_data["dilate_radius"]          = 15
                registered_folder = os.path.split(preprocessed_folder)[0] # remove the slash or backslash
                registered_folder = os.path.split(registered_folder)[0] # remove "original"
                registered_folder = registered_folder + folder_div + "registered" + folder_div
                image_data["registered_folder"]      = registered_folder
                # parameter files 
                # if during development
                if __package__ is None or __package__ == '':
                    parameter_folder = os.path.dirname(os.path.realpath(__file__)) + "/parameterFiles"
                # if using package
                else:
                    parameter_folder = pkg_resources.resource_filename('pykneer','parameterFiles') + folder_div
                image_data["parameter_folder"]       = parameter_folder
                image_data["param_file_rigid"]       = "MR_param_rigid.txt"

                # elastix path (from binaries in pykneer package)
                sys = platform.system()
                if sys == "Linux":
                    dirpath = pkg_resources.resource_filename('pykneer','elastix/Linux/')
                elif sys == "Windows":
                    dirpath = pkg_resources.resource_filename('pykneer','elastix\\Windows\\')
                elif sys == "Darwin":
                    # For debugging - I am working on a MacOS
                    if __package__ is None or __package__ == '':
                        dirpath = os.path.dirname(os.path.realpath(__file__)) + "/elastix/Darwin/"
                    # if using package
                    else:
                        dirpath = pkg_resources.resource_filename('pykneer','elastix/Darwin/')
                image_data["elastix_folder"]           = dirpath
                image_data["complete_elastix_path"]     = dirpath + "elastix"
                # alignment: image-dependent variables for elastix_transformix.py
                image_data["reference_name"]                = image_data["acquisition_file_names"][0]
                reference_root, image_ext                   = os.path.splitext(image_data["reference_name"] )
                image_data["reference_root"]                = reference_root
                image_data["mask_file_name"]                 = image_data["bone_mask_file_name"]
                image_data[bone + "mask_file_name"]          = image_data["bone_mask_file_name"]
                image_data[bone + "dil_mask_file_name"]       = image_data["reference_root"] + "_" + bone + "_" + str(image_data["dilate_radius"]) + ".mha"
                image_data[bone + "levelset_mask_file_name"] = image_data["reference_root"] + "_" + bone + "_levelSet.mha"
                image_data["moving_folder"]                 = image_data["preprocessed_folder"]

                # send to the data dictionary
                all_image_data.append(image_data)

                # get variables ready for the next subject
                acquisition_file_names = []
                info_file_names        = []


    print ("-> information loaded for " + str(len(all_image_data)) + " subjects")
    print ("-> for each subjects there are " + str(n_of_acquisitions) + " acquisitions")

    # return the image info
    return all_image_data


# ---------------------------------------------------------------------------------------------------------------------------
# .TXT FILES  ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def read_txt_to_np_array(file_name):

    """
    Reads .txt files and saves in a numpy array
    """


    # read the file rows
    file_content=[]
    for line in open(file_name):
        file_content.append(line.rstrip("\n"))

    # allocate the array width
    firstRow = re.findall('\d+\.\d+', file_content[0])
    array = np.ndarray((len(firstRow)))

    # fill array
    for i in range(0,len(file_content)):
    #for i in range(0,2):
        if file_content[i] != []: # if the string is not empty

            # get the numbers in the string
            value_str = re.findall(r"[-+]?\d*\.\d+|\d+", file_content[i])

            # transform strings to float
            value_float = []
            for j in range(0,len(value_str)):
                value_float.append(float(value_str[j]))
            value_float = np.asarray(value_float)

            # assing to array
            array = np.vstack((array,value_float))

    # delete first line for allocation
    array = np.delete(array,0,0)

    return array


def write_np_array_to_txt(array, file_name):

    """
    Writes numpy array to .txt file
    """

    file = open(file_name, "w")

    # array is a matrix
    if len(array.shape) > 1:
        for i in range (0, array.shape[0]):
            for j in range (0, array.shape[1]):
                file.write("%0.2f " % array[i][j] )
            file.write("\n")
    # array is a 1D array
    elif len(array.shape) == 1:
        for i in range (0, array.shape[0]):
            file.write("%0.2f " % array[i])
            file.write("\n")

    file.close()

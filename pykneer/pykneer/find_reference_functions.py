# Serena Bonaretti, 2018

import multiprocessing
import numpy as np
import os
import platform
import shutil
import SimpleITK as sitk


# pyKNEER imports 
# ugly way to use relative vs. absolute imports when developing vs. when using package - cannot find a better way
if __package__ is None or __package__ == '':
    # uses current directory visibility
    import elastix_transformix

else:
    # uses current package visibility
    from . import elastix_transformix



def folder_divider():

    # determine the sistem to define the folder divider ("\" or "/")
    sys = platform.system()
    if sys == "Linux":
        folderDiv = "/"
    elif sys == "Darwin":
        folderDiv = "/"
    elif sys == "Windows":
        folderDiv = "\\"

    return folderDiv


def prepare_reference(all_image_data, reference_names, iteration_no):

#    anatomy = all_image_data[0]["currentAnatomy"] # it is "f" for femur (assigned in loadimage_dataFindReference)
#    refID   = iteration_no
#    # get new reference ID in all_image_data
#    reference_name = reference_names[iteration_no]
#    for i in range (0, len(all_image_data)):
#        if all_image_data[i]["moving_name"] == reference_name:
#            refID = i
#            break

    # variables
    standard_reference_name            = "reference.mha"
    standardreference_root             = "reference"
    standard_mask_name                 = "reference_f.mha"
    standard_f_dil_mask_filename       = "reference_f_15.mha"
    standard_f_levelsets_mask_filename = "reference_f_levelSet.mha"
    standard_reference_suffix          = "prep.mha"
    standard_mask_suffix               = "f.mha"

    # get the system for folderDiv
    folderDiv = folder_divider()

    # 0. create parent output folder (first iteration only)
    if iteration_no == 1:
        # create global output folder for this reference
        #if not os.path.isdir(all_image_data[0]["registered_sub_folder"]):
        #    os.makedirs(all_image_data[0]["registered_sub_folder"])
        output_folder = all_image_data[0]["parent_folder"] + all_image_data[0]["reference_root"] + folderDiv

        if not os.path.isdir (output_folder): # automatically created by addNamesToimage_data in pyKNEErIO
            os.makedirs(output_folder)

        # assign output folder to all cells of all_image_data (adapting to requests of elastixTransformix class)
        for i in range(0,len(all_image_data)):
            all_image_data[i]["output_folder"]             = output_folder
            all_image_data[i]["reference_name"]            = standard_reference_name
            all_image_data[i]["reference_root"]            = standardreference_root
            all_image_data[i]["fmask_file_name"]           = standard_mask_name # this has to be fmask_file_name (not f_mask_file_name)
            all_image_data[i]["f_dil_mask_filename"]       = standard_f_dil_mask_filename
            all_image_data[i]["f_levelsets_mask_filename"] = standard_f_levelsets_mask_filename
            all_image_data[i]["registration_type"]         = "newsubject"


    # 1. create new reference image folder and add it to every image in the dictionary
    currentreference_root, referenceExt = os.path.splitext(reference_names[iteration_no])
    new_reference_folder = all_image_data[0]["output_folder"] + str(iteration_no) + "_" + currentreference_root + folderDiv
    if not os.path.isdir(new_reference_folder):
        os.makedirs(new_reference_folder)
    for i in range(0,len(all_image_data)):
        all_image_data[i]["reference_folder"] = new_reference_folder

    # 2. create new file names for reference image and mask (using dictionary of image 0 of all_image_data)
    # image
    old_ref_image_name = all_image_data[0]["parent_folder"] + reference_names[iteration_no]
    new_ref_image_name = new_reference_folder               + reference_names[iteration_no]
    # mask
    mask_name        = reference_names[iteration_no].replace(standard_reference_suffix, standard_mask_suffix) # this is hardcoded and determines the way file names are
    old_ref_mask_name  = all_image_data[0]["parent_folder"] + mask_name
    new_ref_mask_name  = new_reference_folder               + mask_name

    # 3. move reference image and mask to the new folder and change names
    shutil.copy(old_ref_image_name, new_ref_image_name)
    shutil.copy(old_ref_mask_name , new_ref_mask_name)
    os.rename(new_ref_image_name, new_reference_folder + standard_reference_name)
    os.rename(new_ref_mask_name , new_reference_folder + standard_mask_name)

    # 4. dilate mask and convert to level set (use folder and image names of first cell in all_image_data)
    bone = elastix_transformix.bone()

    print ("here")
    print (all_image_data[0]["fmask_file_name"])
    print ("here")
    bone.prepare_reference (all_image_data[0])

    return all_image_data



def calculate_vector_fields_s(image_data):

    # get the system for folderDiv
    folderDiv = folder_divider()

    # create output folders that do not exist
    image_data["registered_folder"]      = image_data["reference_folder"]
    image_data["registered_sub_folder"]  = image_data["registered_folder"] + image_data["moving_root"] + folderDiv
    if not os.path.isdir(image_data["registered_sub_folder"]):
        os.makedirs(image_data["registered_sub_folder"])

    # register the femur
    bone = elastix_transformix.bone()
    bone.rigid     (image_data)
    bone.similarity(image_data)
    bone.spline    (image_data)
    bone.vf_spline (image_data)

def calculate_vector_fields(all_image_data, nOfProcesses):

    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(calculate_vector_fields_s, all_image_data)
    print ("-> Vector fields calculated")



def find_reference_as_minimum_distance_to_average(all_image_data, reference_names, min_distance, iteration_no):

    fieldFolder = all_image_data[0]["reference_folder"]

    # allocate an empty field (with first field characteristisc) and convert to numpy matrix
    image_data        = all_image_data[0]
    firstField        = sitk.ReadImage(fieldFolder + image_data["vector_field_name"])
    average_field     = sitk.Image(firstField.GetSize(),sitk.sitkVectorFloat32)
    average_field_py  = sitk.GetArrayFromImage(average_field)

    # calculate average field
    for i in range(0,len(all_image_data)):

        # get current field
        image_data     = all_image_data[i]
        fieldFileName  = fieldFolder + image_data["vector_field_name"]
#        print ("    " + image_data["vector_field_name"] )
        field          = sitk.ReadImage(fieldFileName)
        # transform to numpy matrix
        field_py = sitk.GetArrayFromImage(field)
        # sum up the field to the average field
        average_field_py = average_field_py + field_py

    # divide by the number of fields
    average_field_py = average_field_py / len(all_image_data)

    # back to sitk
    average_field = sitk.GetImageFromArray(average_field_py)
    average_field.SetSpacing  (firstField.GetSpacing  ())
    average_field.SetOrigin   (firstField.GetOrigin   ())
    average_field.SetDirection(firstField.GetDirection())

    # write the average field
#    average_fieldFileName = firstImage["registered_folder"] + "average_field_" + str(iteration_no) + ".mha"
#    sitk.WriteImage(average_field, average_fieldFileName)

    # calculate norms between average field and each moving field
    norms = np.zeros(len(all_image_data))

    for i in range(0,len(all_image_data)):

        # re-load the field
        image_data       = all_image_data[i]
        fieldFileName    = fieldFolder + image_data["vector_field_name"]
        field            = sitk.ReadImage(fieldFileName)
        # transform to python array
        average_field_py = sitk.GetArrayFromImage(average_field)
        field_py         = sitk.GetArrayFromImage(field)
        # extract values under dilated mask
        mask_dil                = sitk.ReadImage(all_image_data[0]["reference_folder"] + all_image_data[0]["f_dil_mask_filename"])
        mask_dil_py             = sitk.GetArrayFromImage(mask_dil)
        average_field_py_masked = np.extract(mask_dil_py == 1, average_field_py)
        field_py_masked         = np.extract(mask_dil_py == 1, field_py)
        n_of_masked_voxels      = len(average_field_py_masked)
        # calculate norm of distances
        norm = np.linalg.norm(average_field_py_masked-field_py_masked)
        print ("    " + image_data["vector_field_name"] )
        print ("      norm before normalization: " + str(norm))
        norm = norm / n_of_masked_voxels
        print ("      norm after normalization: " + str(norm))
        print ("      number of image voxels: "   + str(average_field.GetSize()[0]*average_field.GetSize()[1]*average_field.GetSize()[2]))
        print ("      snumber of masked voxels: " + str(n_of_masked_voxels))
        # assign to vector of norms
        norms[i] = norm

    # get minimum norm
    min_norm    = min(norms)
    min_norm_id = np.where(norms == norms.min())
    min_norm_id = int(min_norm_id[0][0]) # previous function provides a tuple
    print ("   -> Distances to average field are: " + np.array2string(norms, precision=8) )
    print ("   -> Minimum distance is %.8f" % min_norm)

    # pick corresponding image as new reference
    newreference_name = all_image_data[min_norm_id]["moving_name"]
    print ("   -> Reference of next iteration is " + all_image_data[min_norm_id]["moving_name"])

    # add values to all_image_data
    reference_names[iteration_no+1] = newreference_name
    min_distance   [iteration_no]   = min_norm

    return reference_names, min_distance #refID?

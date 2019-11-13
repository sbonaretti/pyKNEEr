# Serena Bonaretti, 2018

"""
Module with the functions called by the notebook preprocessing.ipynb

Functions are in pairs for parallelization. Example:
read_dicom_stack launches read_dicom_stack_s as many times as the length of all_image_data (subtituting a for loop).
pool.map() takes care of sending one single element of the list all_image_data (all_image_data[i]) to read_dicom_stack_s, as if it was a for loop.

"""

import os
import matplotlib.pyplot as plt
import time
import multiprocessing

import SimpleITK      as sitk
from . import sitk_functions  as sitkf



# ---------------------------------------------------------------------------------------------------------------------------
# READ DICOM IMAGES AND PRINT HEADER ----------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def read_dicom_stack_s(image_data):

    # read dicom stack and put it in a 3D matrix
    img = sitkf.read_dicom_stack(image_data["original_folder"] + image_data["image_folder_file_name"])

    # print out image information
    print("-> " + image_data["image_name_root"])
    sitkf.print_image_info(img)

    # save image to temp
    sitk.WriteImage(img, image_data["temp_file_name"])

def read_dicom_stack(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(read_dicom_stack_s, all_image_data)
    print ("-> Dicom images read")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def print_dicom_header_s(image_data):

    # read header
    meta_data_keys, meta_data = sitkf.read_dicom_header(image_data["original_folder"] + image_data["image_folder_file_name"])

    # write header to file
    file = open(image_data["info_file_name"], "w")

    for i in range(0,len(meta_data_keys)):
        file.write(meta_data_keys[i] +  " " + meta_data[i] + "\n")

    file.close()

def print_dicom_header(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(print_dicom_header_s, all_image_data)
    print ("-> Dicom headers written")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



# ---------------------------------------------------------------------------------------------------------------------------
# SPATIAL PREPROCESSING -----------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def orientation_to_rai_s(image_data):
    '''
    This function will be used when SimpleIKT includes the filter OrientImageFilter in the release
    For now we use the ITK filter
    '''
    
    # read the image
    img = sitk.ReadImage(image_data["temp_file_name"])

    # change orientation
    img = sitkf.orientation_to_rai(img)

    # save image to temp
    sitk.WriteImage(img, image_data["temp_file_name"])

def orientation_to_rai(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(orientation_to_rai_s, all_image_data)
    print ("-> Image orientation changed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def flip_rl_s(image_data):

    # read the image
    img = sitk.ReadImage(image_data["temp_file_name"])

    # change laterality
    laterality = image_data["laterality"]
    if laterality == "right" or laterality == "Right":
        img = sitkf.flip_rl(img, True)

        # save image to temp
        sitk.WriteImage(img, image_data["temp_file_name"])

def flip_rl(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(flip_rl_s, all_image_data)
    print ("-> Image laterality changed for right images")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def origin_to_zero_s(image_data):

    # read the image
    img = sitk.ReadImage(image_data["temp_file_name"])

    # set origin to (0,0,0)
    img = sitkf.origin_to_zero(img)

    # save image to temp
    sitk.WriteImage(img, image_data["temp_file_name"])

    # save image to *_orig.mha
    sitk.WriteImage(img, image_data["original_file_name"])

    # delete temp image
    os.remove(image_data["temp_file_name"])


def origin_to_zero(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(origin_to_zero_s, all_image_data)
    print ("-> Image origin changed")
    print ("-> _orig.mha images saved")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



# ---------------------------------------------------------------------------------------------------------------------------
# INTENSITY PREPROCESSING ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def field_correction_s(image_data):

    start_time = time.time()

    # read the image
    img = sitk.ReadImage(image_data["original_file_name"])

    # correct for the magnetic field
    img = sitkf.field_correction(img)

    # save image to temp
    sitk.WriteImage(img, image_data["temp_file_name"])

    print ("-> The total time for image " + image_data["image_name_root"] + " was %d seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))

def field_correction(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(field_correction_s, all_image_data)
    print ("-> Magnetic field bias corrected")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def rescale_to_range_s(image_data):

    # read the image
    img = sitk.ReadImage(image_data["temp_file_name"])

    # rescale filtering out the outliers
    img = sitkf.rescale_to_range(img)

    # save image to temp
    sitk.WriteImage(img, image_data["temp_file_name"])

def rescale_to_range(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(rescale_to_range_s, all_image_data)
    print ("-> Image intensities rescaled")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def edge_preserving_smoothing_s(image_data):

    # read the image
    img = sitk.ReadImage(image_data["temp_file_name"])

    # smooth while preserving sharp edges
    img = sitkf.edge_preserving_smoothing(img)

    # save image to prep
    sitk.WriteImage(img, image_data["preprocessed_file_name"])

    # delete temp image
    os.remove(image_data["temp_file_name"])

def edge_preserving_smoothing(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(edge_preserving_smoothing_s, all_image_data)
    print ("-> Image smoothed")
    print ("-> _prep.mha images saved")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



# ---------------------------------------------------------------------------------------------------------------------------
# VISUALIZING PREPROCESSED IMAGES -------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def show_preprocessed_images(all_image_data,intensity_standardization):

    n_of_images   = len(all_image_data)
    img_LW        = 4
    figure_width  = img_LW * 2
    figure_length = img_LW * n_of_images
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (n_of_images can be larger)
    fig, ax = plt.subplots(nrows=n_of_images, ncols=2)
    fig.tight_layout() # avoids subplots overlap
    
    for i in range(0, n_of_images):

        # plot spatially standardized image

        # get paths and file names of the current image
        image_data     = all_image_data[i]
        orig_file_name = image_data["original_file_name"]

        # read the images
        img_orig = sitk.ReadImage(orig_file_name)

        # convert images to numpy arrays
        img_orig_py = sitk.GetArrayFromImage(img_orig)

        # extract slice at 2/3 of the image size
        size       = img_orig_py.shape
        slice_ID   = round(size[2] / 3 * 2)
        slice_orig = img_orig_py[:,:,slice_ID]

        # plot slice of original image in left axis
        if n_of_images == 1:
            ax1 = ax[0]
        else:
            ax1 = ax[i,0]
        ax1.set_title(image_data["image_name_root"] + "_orig.mha")
        ax1.imshow(slice_orig, cmap=plt.cm.gray, origin='lower',interpolation=None)
        ax1.axis('off')


        # plot intensity standardized image (if present)

        # get paths and file names of the current image
        prep_file_name = image_data["preprocessed_file_name"]

        if intensity_standardization==1:

            # read the images
            img_prep = sitk.ReadImage(prep_file_name)

            # convert images to numpy arrays
            img_prep_py = sitk.GetArrayFromImage(img_prep)

            # extract slice at 2/3 of the image size
            slice_prep = img_prep_py[:,:,slice_ID]

            # plot slice of preprocessed image in right axis
            if n_of_images == 1:
                ax2 = ax[1]
            else:
                ax2 = ax[i,1]
            ax2.set_title(image_data["image_name_root"] + "_prep.mha")
            ax2.imshow(slice_prep, cmap=plt.cm.gray, origin='lower',interpolation=None)
            ax2.axis('off')

        else:
            # turn off the second axis showing the intensity-standardized image
            if n_of_images == 1:
                ax2 = ax[1]
            else:
                ax2 = ax[i,1]
            ax2.axis('off')

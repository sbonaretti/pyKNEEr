# Serena Bonaretti, 2018

import os
import matplotlib.pyplot as plt
import time
import multiprocessing

import SimpleITK      as sitk
from . import sitk_functions  as sitkf

# print("--- process " + str(os.getpid()) + " working on " + imageData["imageFolderFileName"] )
# print("--- process " + str(os.getpid()) + " done")
# start_time = time.time()
# print ("-> The total time in readDicomStack_s was %d seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))

# Functions are in pairs for parallelization. Example:
# readDicomStack launches readDicomStack_s as many times as the length of allImageData (subtituting a for loop).
# pool.map() takes care of sending one single element of the list allImageData (allImageData[i]) to readDicomStack_s, as if it was a for loop.

def read_dicom_stack_s(imageData):

    # read dicom stack and put it in a 3D matrix
    img         = sitkf.read_dicom_stack(imageData["originalFolder"] + imageData["imageFolderFileName"])

    # print out image information
    print("-> " + imageData["imageNameRoot"])
    sitkf.print_image_info(img)

    # save image to temp
    sitk.WriteImage(img, imageData["tempFileName"])

def read_dicom_stack(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(read_dicom_stack_s, allImageData)
    print ("-> Dicom images read")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def print_dicom_header_s(imageData):

    # read header
    metaDataKeys, metaData = sitkf.read_dicom_header(imageData["originalFolder"] + imageData["imageFolderFileName"])

    # write header to file
    file = open(imageData["infoFileName"], "w")

    for i in range(0,len(metaDataKeys)):
        file.write(metaDataKeys[i] +  " " + metaData[i] + "\n")

    file.close()

def print_dicom_header(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(print_dicom_header_s, allImageData)
    print ("-> Dicom headers written")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def orientation_to_rai_s(imageData):

    # read the image
    img = sitk.ReadImage(imageData["tempFileName"])

    # change orientation
    img = sitkf.orientation_to_rai(img)

    # save image to temp
    sitk.WriteImage(img, imageData["tempFileName"])

def orientation_to_rai(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(orientation_to_rai_s, allImageData)
    print ("-> Image orientation changed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def flip_rl_s(imageData):

    # read the image
    img = sitk.ReadImage(imageData["tempFileName"])

    # change laterality
    laterality = imageData["laterality"]
    if laterality == "right" or laterality == "Right":
        img = sitkf.flip_rl(img, True)

        # save image to temp
        sitk.WriteImage(img, imageData["tempFileName"])

def flip_rl(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(flip_rl_s, allImageData)
    print ("-> Image laterality changed for right images")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def origin_to_zero_s(imageData):

    # read the image
    img = sitk.ReadImage(imageData["tempFileName"])

    # set origin to (0,0,0)
    img = sitkf.origin_to_zero(img)

    # save image to temp
    sitk.WriteImage(img, imageData["tempFileName"])

    # save image to *_orig.mha
    sitk.WriteImage(img, imageData["originalFileName"])

    # delete temp image
    os.remove(imageData["tempFileName"])


def origin_to_zero(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(origin_to_zero_s, allImageData)
    print ("-> Image origin changed")
    print ("-> _orig.mha images saved")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def field_correction_s(imageData):

    start_time = time.time()

    # read the image
    img = sitk.ReadImage(imageData["originalFileName"])

    # correct for the magnetic field
    img = sitkf.field_correction(img)

    # save image to temp
    sitk.WriteImage(img, imageData["tempFileName"])

    print ("-> The total time for image " + imageData["imageNameRoot"] + " was %d seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))

def field_correction(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(field_correction_s, allImageData)
    print ("-> Magnetic field bias corrected")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def rescale_to_range_s(imageData):

    # read the image
    img = sitk.ReadImage(imageData["tempFileName"])

    # rescale filtering out the outliers
    img = sitkf.rescale_to_range(img)

    # save image to temp
    sitk.WriteImage(img, imageData["tempFileName"])

def rescale_to_range(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(rescale_to_range_s, allImageData)
    print ("-> Image intensities rescaled")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def edge_preserving_smoothing_s(imageData):

    # read the image
    img = sitk.ReadImage(imageData["tempFileName"])

    # smooth while preserving sharp edges
    img = sitkf.edge_preserving_smoothing(img)

    # save image to prep
    sitk.WriteImage(img, imageData["preprocessedFileName"])

    # delete temp image
    os.remove(imageData["tempFileName"])

def edge_preserving_smoothing(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(edge_preserving_smoothing_s, allImageData)
    print ("-> Image smoothed")
    print ("-> _prep.mha images saved")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))


def show_preprocessed_images(allImageData,intensity_standardization):

    nOfImages   = len(allImageData)
    imgLW       = 4
    figureWidth = imgLW * 2
    figLength   = imgLW * nOfImages
    plt.rcParams['figure.figsize'] = [figureWidth, figLength] # figsize=() seems to be ineffective on notebooks
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (nOfImages can be larger)
    fig, ax = plt.subplots(nrows=nOfImages, ncols=2)
    fig.tight_layout() # avoids subplots overlap

    for i in range(0, nOfImages):

        # plot spatially standardized image

        # get paths and file names of the current image
        imageData    = allImageData[i]
        origFileName = imageData["originalFileName"]

        # read the images
        img_orig = sitk.ReadImage(origFileName)

        # convert images to numpy arrays
        img_orig_py = sitk.GetArrayFromImage(img_orig)

        # extract slice at 2/3 of the image size
        size = img_orig_py.shape
        sliceID = round(size[2] / 3 * 2)
        slice_orig = img_orig_py[:,:,sliceID]

        # plot slice of original image in left axis
        ax1 = ax[i,0]
        ax1.set_title(imageData["imageNameRoot"] + "_orig.mha")
        ax1.imshow(slice_orig, cmap=plt.cm.gray, origin='lower',interpolation=None)
        ax1.axis('off')


        # plot intensity standardized image (if present)

        # get paths and file names of the current image
        prepFileName = imageData["preprocessedFileName"]

        if intensity_standardization==1:

            # read the images
            img_prep = sitk.ReadImage(prepFileName)

            # convert images to numpy arrays
            img_prep_py = sitk.GetArrayFromImage(img_prep)

            # extract slice at 2/3 of the image size
            slice_prep = img_prep_py[:,:,sliceID]

            # plot slice of preprocessed image in right axis
            ax2 = ax[i,1]
            ax2.set_title(imageData["imageNameRoot"] + "_prep.mha")
            ax2.imshow(slice_prep, cmap=plt.cm.gray, origin='lower',interpolation=None)
            ax2.axis('off')

        else:
            # turn off the second axis showing the intensity-standardized image
            ax2 = ax[i,1]
            ax2.axis('off')

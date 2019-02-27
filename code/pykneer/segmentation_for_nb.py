# Serena Bonaretti, 2018

import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import SimpleITK      as sitk
import time

from . import elastix_transformix
from . import sitk_functions  as sitkf


def prepare_reference(allImageData):

    imageData  = allImageData[0]

    # in "newsubject" there is only one reference
    if imageData["registrationType"] == "newsubject":

        # get paths and file names of the first image
        imageData  = allImageData[0]
        print (imageData["referenceName"])

        # instanciate bone class and prepare reference
        imageData["currentAnatomy"] = imageData["bone"]
        bone = elastix_transformix.bone()
        bone.prepare_reference (imageData)

        # instanciate cartilage class and prepare reference
        imageData["currentAnatomy"] = imageData["cartilage"]
        cartilage = elastix_transformix.cartilage()
        cartilage.prepare_reference (imageData)

    # in "longitudinal" and "multimodal" there are several references
    elif imageData["registrationType"] == "longitudinal" or imageData["registrationType"] == "multimodal":

        for i in range(0,len(allImageData)):

            # get paths and file names of the first image
            imageData  = allImageData[i]
            print (imageData["referenceName"])

            # instanciate bone class and prepare reference
            imageData["currentAnatomy"] = imageData["bone"]
            bone = elastix_transformix.bone()
            bone.prepare_reference (imageData)

            # instanciate cartilage class and prepare reference
            imageData["currentAnatomy"] = imageData["cartilage"]
            cartilage = elastix_transformix.cartilage()
            cartilage.prepare_reference (imageData)


    print ("-> Reference preparation completed")




def register_bone_to_reference_s(imageData):

#    print ("-> Registering " + imageData["movingRoot"])

    # instantiate bone class and provide bone to segment
    imageData["currentAnatomy"] = imageData["bone"]
    bone = elastix_transformix.bone()

    # register
    if imageData["registrationType"] == "newsubject":
        bone.rigid     (imageData)
        bone.similarity(imageData)
        bone.spline    (imageData)
    elif imageData["registrationType"] == "longitudinal":
        bone.rigid     (imageData)

        bone.spline(imageData)
    elif imageData["registrationType"] == "multimodal":
        bone.rigid     (imageData)


def register_bone_to_reference(allImageData, nOfProcesses):

    # print
    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(register_bone_to_reference_s, allImageData)
    print ("-> Registration completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def invert_bone_transformations_s(imageData):

#    print ("-> Inverting transformation of " + imageData["movingRoot"])

    # instantiate bone class and provide bone to segment
    imageData["currentAnatomy"] = imageData["bone"]
    bone = elastix_transformix.bone()

    # invert transformations
    if imageData["registrationType"] == "newsubject":
        bone.irigid     (imageData)
        bone.isimilarity(imageData)
        bone.ispline    (imageData)
    elif imageData["registrationType"] == "longitudinal":
        bone.irigid     (imageData)
        bone.ispline    (imageData)
    elif imageData["registrationType"] == "multimodal":
        bone.irigid     (imageData)

def invert_bone_transformations(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(invert_bone_transformations_s, allImageData)
    print ("-> Inversion completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def warp_bone_mask_s(imageData):

#    print ("-> Warping bone mask of " + imageData["movingRoot"])

    # instantiate bone class and provide bone to segment
    imageData["currentAnatomy"] = imageData["bone"]
    bone = elastix_transformix.bone()

    # get moving image properties (size and spacing for modify_transformation(rigid) and transformix)
    movingName  = imageData["movingFolder"] + imageData["movingName"]
    movingImage = sitk.ReadImage(movingName)
    imageData["imageSize"]      = movingImage.GetSize()
    imageData["imageSpacing"]   = movingImage.GetSpacing()

    # modify transformations for mask warping
    if imageData["registrationType"] == "newsubject":
        bone.modify_transformation(imageData,"rigid")
        bone.modify_transformation(imageData,"similarity")
        bone.modify_transformation(imageData,"spline")
    elif imageData["registrationType"] == "longitudinal":
        bone.modify_transformation(imageData,"rigid")
        bone.modify_transformation(imageData,"spline")
    elif imageData["registrationType"] == "multimodal":
        #change filename of something
        bone.modify_transformation(imageData,"rigid")

    # warp mask
    if imageData["registrationType"] == "newsubject":
        bone.tspline    (imageData)
        bone.tsimilarity(imageData)
        bone.trigid     (imageData)
    elif imageData["registrationType"] == "longitudinal":
        bone.tspline    (imageData)
        # change filename of something
        bone.trigid     (imageData)
    elif imageData["registrationType"] == "multimodal":
        # change filename of something
        bone.trigid     (imageData)

    # levelsets to binary
    anatomy        = imageData["currentAnatomy"]
    inputFileName  = imageData["iregisteredSubFolder"] + imageData[anatomy + "mRigidName"]
    outputFileName = imageData["segmentedFolder"]      + imageData[anatomy + "mask"]
    mask = sitk.ReadImage(inputFileName)
    mask = sitkf.levelset2binary(mask)
    sitk.WriteImage(mask, outputFileName)

def warp_bone_mask(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(warp_bone_mask_s, allImageData)
    print ("-> Warping completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def register_cartilage_to_reference_s(imageData):

#    print ("-> Registering " + imageData["movingRoot"])

    if imageData["registrationType"] == "newsubject" or imageData["registrationType"] == "longitudinal":
        # instantiate cartilage class and provide cartilage to segment
        imageData["currentAnatomy"] = imageData["cartilage"]
        cartilage = elastix_transformix.cartilage()

        # register
        cartilage.spline(imageData)
    else:
        print ("-> Step skipped")

def register_cartilage_to_reference(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(register_cartilage_to_reference_s, allImageData)
    print ("-> Registration completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def invert_cartilage_transformations_s(imageData):

#    print ("-> Inverting transformation of " + imageData["movingRoot"])

    if imageData["registrationType"] == "newsubject" or imageData["registrationType"] == "longitudinal":

        # instantiate cartilage class and provide cartilage to segment
        imageData["currentAnatomy"] = imageData["cartilage"]
        cartilage = elastix_transformix.cartilage()

        # invert transformations
        cartilage.ispline    (imageData)

    elif imageData["registrationType"] == "multimodal":
        print ("-> Step skipped")

def invert_cartilage_transformations(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(invert_cartilage_transformations_s, allImageData)
    print ("-> Inversion completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def warp_cartilage_mask_s(imageData):

#    print ("-> Warping cartilage mask of " + imageData["movingRoot"])

    # instantiate cartilage class and provide cartilage to segment
    imageData["currentAnatomy"] = imageData["cartilage"]
    cartilage = elastix_transformix.cartilage()

    # get moving image properties (size and spacing for transformix)
    movingName  = imageData["movingFolder"] + imageData["movingName"]
    movingImage = sitk.ReadImage(movingName)
    imageData["imageSize"]      = movingImage.GetSize()
    imageData["imageSpacing"]   = movingImage.GetSpacing()

    if imageData["registrationType"] == "newsubject":

        # modify transformations for mask warping
        cartilage.modify_transformation(imageData,"spline")

        # warp mask
        cartilage.tspline    (imageData)
        cartilage.tsimilarity(imageData)
        cartilage.trigid     (imageData)

    elif imageData["registrationType"] == "longitudinal":

        # modify transformations for mask warping
        cartilage.modify_transformation(imageData,"spline")

        # warp mask
        cartilage.tspline    (imageData)
        # change some filename here
        cartilage.trigid     (imageData)

    elif imageData["registrationType"] == "multimodal":
        cartilage.trigid     (imageData)


    # levelsets to binary
    anatomy        = imageData["currentAnatomy"]
    inputFileName  = imageData["iregisteredSubFolder"] + imageData[anatomy + "mRigidName"]
    outputFileName = imageData["segmentedFolder"]      + imageData[anatomy + "mask"]
    mask = sitk.ReadImage(inputFileName)
    mask = sitkf.levelset2binary(mask)
    sitk.WriteImage(mask, outputFileName)

def warp_cartilage_mask(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(warp_cartilage_mask_s, allImageData)
    print ("-> Warping completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def show_segmented_images(allImageData):

    nOfImages   = len(allImageData)
    imgLW       = 4
    figureWidth = imgLW * 3
    figLength   = imgLW * nOfImages
    plt.rcParams['figure.figsize'] = [figureWidth, figLength] # figsize=() seems to be ineffective on notebooks
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (nOfImages can be larger)
    fig.tight_layout() # avoids subplots overlap
    # subplots characteristics
    nOfColumns = 3
    nOfRows    = nOfImages
    axisIndex = 1;


    for i in range(0, nOfImages):


        # get paths and file names of the current image
        imageData                   =  allImageData[i]
        imageData["currentAnatomy"] = imageData["cartilage"]
        anatomy                     = imageData["currentAnatomy"]
        movingFileName              = imageData["movingFolder"]    + imageData["movingName"]
        maskFileName                = imageData["segmentedFolder"] + imageData[anatomy + "mask"]
        movingRoot                  = imageData["movingRoot"]


        # read the images
        moving = sitk.ReadImage(movingFileName)
        mask   = sitk.ReadImage(maskFileName)

        # images from simpleitk to numpy
        moving_py = sitk.GetArrayFromImage(moving)
        mask_py   = sitk.GetArrayFromImage(mask)


        # extract slices at 2/5, 3/5, and 4/5 of the image size
        size = np.size(mask_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = mask_py[:,:,b]
            if np.sum(slice) != 0:
                firstValue = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = mask_py[:,:,b]
            if np.sum(slice) != 0:
                lastValue = b
                break

        sliceStep = int ((lastValue-firstValue)/4)
        sliceID = (firstValue + sliceStep, firstValue + 2*sliceStep, firstValue + 3*sliceStep)

        for a in range (0,len(sliceID)):

            # create subplot
            ax1 = fig.add_subplot(nOfRows,nOfColumns,axisIndex)

            # get slices
            slice_moving_py = moving_py[:,:,sliceID[a]]
            slice_mask_py   = mask_py[:,:,sliceID[a]]
            slice_mask_masked = np.ma.masked_where(slice_mask_py == 0, slice_mask_py)

            # show image
            ax1.imshow(slice_moving_py,   'gray', interpolation=None, origin='lower')
            ax1.imshow(slice_mask_masked, 'hsv' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            ax1.set_title(movingRoot + " - Slice: " + str(sliceID[a]))
            ax1.axis('off')

            axisIndex = axisIndex + 1

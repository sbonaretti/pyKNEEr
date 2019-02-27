# Serena Bonaretti, 2018

from datetime import datetime
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import os
import pandas as pd
import platform
import SimpleITK as sitk
import shutil
import time

from . import relaxometry_functions as rf
from . import elastix_transformix
from . import pykneer_io as io



# ---------------------------------------------------------------------------------------------------------------
# EXPONENTIAL AND LINEAR FITTING MAPS
# ---------------------------------------------------------------------------------------------------------------


def align_acquisitions_s(imageData):
    """
    Function for images acquired with CubeQuant sequence.
    Alignment of following acquisitions to image 1 using rigid registration. This is done because images are acquired one after the other, and the subject can move among acquisitions
    The alignment consists in the rigid registration implemented in the class elastix_transformix
    This function mainly moves files to the t1rhoMap folder and creates dictionaries of filenames as requested by the class elastix_transformix
    """

    # get folderDiv
    sys = platform.system()
    if sys == "Linux":
        folderDiv = "/"
    elif sys == "Darwin":
        folderDiv = "/"
    elif sys == "windows":
        folderDiv = "\\"

    # get image names for current subject
    acquisitionFileNames = imageData["acquisitionFileNames"]

    # create folder named after the first image in the folder "relaxometry" for registration (the first image is the reference for the rigid registration)
    mapFolder = imageData["relaxometryFolder"]
    referenceRoot, imageExt    = os.path.splitext(acquisitionFileNames[0])
    registeredFolder = mapFolder + referenceRoot + folderDiv
    if not os.path.isdir(registeredFolder):
        os.mkdir(registeredFolder)

    print ("-> " + acquisitionFileNames[0])


    # --- REFERENCE -----------------------------------------------------------------------------------------------------------------

    # create the reference folder
    referenceFolder = registeredFolder + "reference" + folderDiv
    if not os.path.isdir(referenceFolder):
        os.mkdir(referenceFolder)

    # move the reference (first image) to the reference folder and rename it
    referenceRoot = "reference"
    referenceName = referenceRoot + ".mha"
    shutil.copyfile(imageData["preprocessedFolder"] + acquisitionFileNames[0],
                    referenceFolder + referenceName)

    # move the femur and femoral cartilage masks to the reference folder and rename them
    boneMaskFileName = referenceRoot + "_f.mha"
    shutil.copyfile(imageData["segmentedFolder"] + imageData["boneMaskFileName"],
                    referenceFolder + boneMaskFileName)
    cartMaskFileName = referenceRoot + "_fc.mha" # not needed but the function 'prepare_reference' of the class 'elastix_transformix' will look for it
    shutil.copyfile(imageData["segmentedFolder"] + imageData["cartMaskFileName"],
                    referenceFolder + cartMaskFileName)

    # create new dictionary specifically for the elastix_transformix class (trick)
    reference = {}
    reference["currentAnatomy"]  = imageData["bone"]
    reference["referenceFolder"] = referenceFolder
    reference[reference["currentAnatomy"] + "maskFileName"]          = boneMaskFileName
    reference[reference["currentAnatomy"] + "dilMaskFileName"]       = referenceRoot + "_" + reference["currentAnatomy"] + "_" + str(imageData["dilateRadius"]) + ".mha"
    reference[reference["currentAnatomy"] + "levelSetsMaskFileName"] = referenceRoot + "_" + reference["currentAnatomy"] + "_" + "levelSet.mha"
    reference["dilateRadius"]    = imageData["dilateRadius"]

    # instanciate bone class and prepare reference
    bone = elastix_transformix.bone()
    bone.prepare_reference (reference)


    # --- MOVING IMAGES -----------------------------------------------------------------------------------------------------------------

    # image file names will contain "align"
    acquisitionFileNames_new = []

    # move and rename image 1 (reference) to the folder preprocessing to calculate the fitting in the function calculate_t1rho_maps
    fileNameRoot, fileExt   = os.path.splitext(acquisitionFileNames[0])
    acquisitionFileNames_new.append(fileNameRoot + "_aligned.mha")
    shutil.copyfile(imageData["preprocessedFolder"] + acquisitionFileNames[0],
                    imageData["preprocessedFolder"] + acquisitionFileNames_new[0])

    # move all prep images 2,3,4 (1 is the reference) to the registration folder
    for a in range (1, len(acquisitionFileNames)):
        shutil.copyfile(imageData["preprocessedFolder"] + acquisitionFileNames[a],
                        registeredFolder  + acquisitionFileNames[a])

    # rigid registration
    for a in range(1,len(acquisitionFileNames)):

        # create new dictionary for current image for the elastix_transformix class (trick)
        img = {}
        img["movingName"]          = acquisitionFileNames[a]
        img["movingFolder"]        = registeredFolder
        img["currentAnatomy"]      = imageData["bone"]
        img["referenceFolder"]     = referenceFolder
        img["referenceName"]       = referenceName
        img[img["currentAnatomy"] + "dilMaskFileName"] = referenceRoot + "_" + reference["currentAnatomy"] + "_" + str(imageData["dilateRadius"]) + ".mha"
        img["paramFileRigid"]      = imageData["parameterFolder"] + imageData["paramFileRigid"]
        img["elastixFolder"]       = imageData["elastixFolder"]
        img["completeElastixPath"] = imageData["completeElastixPath"]
        img["registeredSubFolder"] = registeredFolder
        img[img["currentAnatomy"] + "rigidName"]       = "rigid_2.mha"
        img[img["currentAnatomy"] + "rigidTransfName"] = "transf_2.txt"

        # register
        #print ("   registering " + acquisitionFileNames[a])
        bone.rigid (img)
        # copy aligned image to the folder preprocessing
        fileNameRoot, fileExt = os.path.splitext(acquisitionFileNames[a])
        acquisitionFileNames_new.append(fileNameRoot + "_aligned.mha")
        shutil.copyfile(img["registeredSubFolder"] + img[img["currentAnatomy"] + "rigidName"],
                        imageData["preprocessedFolder"]  + acquisitionFileNames_new[-1])

    # assign new file names to the main dictionary for the function calculate_fitting_maps
    imageData["acquisitionFileNames"] = acquisitionFileNames_new

def align_acquisitions(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(align_acquisitions_s, allImageData)
    print ("-> Acquisitions aligned")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def calculate_fitting_maps_s(imageData):


    # define the kind of fitting to compute (linear or exponential)
    methodFlag = imageData["methodFlag"] # get info from the first image

    # get fileNames
    preprocessedFolder   = imageData["preprocessedFolder"]
    acquisitionFileNames = imageData["acquisitionFileNames"]
    infoFileNames        = imageData["infoFileNames"]
    # mask
    segmentedFolder      = imageData["segmentedFolder"]
    maskFileName         = imageData["cartMaskFileName"] #maskFileName
    # output maps
    mapFolder            = imageData["relaxometryFolder"]
    mapFileName          = imageData["mapFileName"]

    print(acquisitionFileNames[0])

    # read info files and get spin lock time (saved as echo time) (x-values for fitting)
    tsl = []
    for currentInfo in infoFileNames:
        for line in open(preprocessedFolder + currentInfo):
            if "0018|0081" in line:
                tsl.append(float(line[10:len(line)]))

    # read the mask
    mask = sitk.ReadImage(segmentedFolder + maskFileName)
    # from SimpleITK to numpy
    mask_py = sitk.GetArrayFromImage(mask)
    # rotate mask to be compatible with flat bone surface for visualization later
    mask_py = np.rot90(mask_py)
    mask_py = np.flip(mask_py,0)

    # from 3D matrix to array
    mask_py_array = np.reshape(mask_py, np.size(mask_py,0)*np.size(mask_py,1)*np.size(mask_py,2))
    # get only non zero values (= masked cartilage) to speed up computation
    index = np.where(mask_py_array != 0)

    # get values from images (y-values of fitting)
    array_of_masked_images = []

    for a in range(0, len(acquisitionFileNames)):
        # read image
        img = sitk.ReadImage(preprocessedFolder + acquisitionFileNames[a])
        # from SimpleITK to numpy
        img_py = sitk.GetArrayFromImage(img)
        # rotate images to be compatible with flat bone surface for visualization later
        img_py = np.rot90(img_py)
        img_py = np.flip(img_py,0)
        # from 3D matrix to array
        img_py_array = np.reshape(img_py, np.size(img_py,0)*np.size(img_py,1)*np.size(img_py,2))
        # get only non zero values (= masked cartilage) to speed up computation
        array = img_py_array[index]
        # add array to array of images for current subject
        array_of_masked_images.append(array)

    # calculate fitting
    if methodFlag == 0: # linear fitting
        map_py_v = rf.calculate_fitting_maps_lin(tsl, array_of_masked_images)
    elif methodFlag == 1: # exponential fitting
        map_py_v = rf.calculate_fitting_maps_exp(tsl, array_of_masked_images)

    # assign map to image-long vector
    map_vector = np.full((np.size(mask_py,0)*np.size(mask_py,1)*np.size(mask_py,2)), 0.00)
    map_vector[index] = map_py_v

    # resize vector to matrix
    map_py = np.reshape(map_vector,(np.size(mask_py,0),np.size(mask_py,1),np.size(mask_py,2)))
    # rotate it back to be consistent with image
    map_py = np.flip(map_py,0)
    map_py = np.rot90(map_py, k=-1)


    # back to SimpleITK
    fitting_map = sitk.GetImageFromArray(map_py)
    fitting_map.SetSpacing  (mask.GetSpacing())
    fitting_map.SetOrigin   (mask.GetOrigin())
    fitting_map.SetDirection(mask.GetDirection())
    fitting_map = sitk.Cast(fitting_map,sitk.sitkInt16)

    # write map
    sitk.WriteImage(fitting_map, (mapFolder + mapFileName))

def calculate_fitting_maps(allImageData, nOfProcesses):

    methodFlag = allImageData[0]["methodFlag"]
    if methodFlag == 0: # linear fitting
        print ('-> using linear fitting ')
    elif methodFlag == 1: # exponential fitting
        print ('-> using exponential fitting ')

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(calculate_fitting_maps_s, allImageData)
    print ("-> Fitting maps calculated")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))


def show_fitting_maps(allImageData):

    nOfImages   = len(allImageData)
    imgLW       = 6
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
        preprocessedFolder = allImageData[i]["preprocessedFolder"]
        i1fileName         = allImageData[i]["acquisitionFileNames"][0]
        mapFolder          = allImageData[i]["relaxometryFolder"]
        mapFileName        = allImageData[i]["mapFileName"]
        imageNameRoot, imageExt = os.path.splitext(i1fileName)

        # read images
        img  = sitk.ReadImage(preprocessedFolder + i1fileName)
        map_ = sitk.ReadImage(mapFolder + mapFileName)

        # images from simpleitk to numpy
        img_py = sitk.GetArrayFromImage(img)
        map_py = sitk.GetArrayFromImage(map_)


        # extract slices at 2/5, 3/5 and 4/3 of the image size
        size = np.size(map_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                firstValue = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                lastValue = b
                break
        sliceStep = int ((lastValue-firstValue)/4)
        sliceID = (firstValue + sliceStep, firstValue + 2*sliceStep, firstValue + 3*sliceStep)

        # show slices with maps
        for a in range (0,len(sliceID)):

            # create subplot
            ax1 = fig.add_subplot(nOfRows,nOfColumns,axisIndex)

            # get slices
            slice_img_py = img_py[:,:,sliceID[a]]
            slice_map_py = map_py[:,:,sliceID[a]]
            slice_map_masked = np.ma.masked_where(slice_map_py == 0, slice_map_py)

            # show image
            ren1 = ax1.imshow(slice_img_py    , 'gray', interpolation=None, origin='lower')
            ren2 = ax1.imshow(slice_map_masked, 'jet' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            clb = plt.colorbar(ren2, orientation='vertical', shrink=0.60, ticks=[0, 20, 40, 60, 80, 100])
            clb.ax.set_title('[ms]')
            ax1.set_title(str(i+1) + ". " + imageNameRoot + " - Slice: " + str(sliceID[a]))
            ax1.axis('off')

            axisIndex = axisIndex + 1


def show_fitting_graph(allImageData):

    # calculate average and standard deviation
    average = []
    stdDev  = []
    for i in range(0, len(allImageData)):
        # file name
        mapFolder      = allImageData[i]["relaxometryFolder"]
        mapFileName    = allImageData[i]["mapFileName"]
        # read image
        mapImage = sitk.ReadImage(mapFolder + mapFileName)
        # from SimpleITK to numpy
        map_py = sitk.GetArrayFromImage(mapImage)
        # from 3D matrix to array
        map_py_array = np.reshape(map_py, np.size(map_py,0)*np.size(map_py,1)*np.size(map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(map_py_array != 0)
        map_vector = map_py_array[index]
        # calculate average and stddev
        average.append(np.average(map_vector))
        stdDev.append(np.std(map_vector))

    average = np.asarray(average)
    stdDev  = np.asarray(stdDev)
    x = np.arange(len(allImageData))

    # figure size
    figureWidth = 18
    figLength   = 8
    plt.rcParams['figure.figsize'] = [figureWidth, figLength] # figsize=() seems to be ineffective on notebooks

    # error bar
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (nOfImages can be larger)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.errorbar(x, average, yerr=stdDev, linestyle='None', marker='o')

    # set ticks and labels
    plt.xticks(x)
    imageNames= []
    for i in range(0, len(allImageData)):
        imageRoot, imageExt = os.path.splitext(allImageData[i]["mapFileName"])
        imageNames.append(imageRoot)
    ax.set_xticklabels(imageNames, rotation='vertical')
    ax.set_ylabel('t1rho [ms]')

    # show
    plt.show()


def show_fitting_table(allImageData, outputFileName):

    # read and calculate values for table
    imageNames = []
    average = []
    stdDev  = []

    for i in range(0, len(allImageData)):
        # file name
        mapFolder      = allImageData[i]["relaxometryFolder"]
        mapFileName    = allImageData[i]["mapFileName"]
        imageRoot, imageExt = os.path.splitext(allImageData[i]["mapFileName"])
        imageNames.append(imageRoot)
        # read image
        imageMap = sitk.ReadImage(mapFolder + mapFileName)
        # from SimpleITK to numpy
        map_py = sitk.GetArrayFromImage(imageMap)
        # from 3D matrix to array
        map_py_array = np.reshape(map_py, np.size(map_py,0)*np.size(map_py,1)*np.size(map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(map_py_array != 0)
        map_vector = map_py_array[index]
        # calculate average and stddev
        average.append(np.average(map_vector))
        stdDev.append(np.std(map_vector))

    # create table
    table = pd.DataFrame(
        {
            "subjects"      : mapFileName,
            "average"       : average,
            "std.dev"       : stdDev
        }
    )
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table = table.round(2) #show 2 decimals

    # show all the lines of the table
    dataDimension = table.shape # get number of rows
    pd.set_option("display.max_rows",dataDimension[0]) # show all the rows

    # save table as csv
    table.to_csv(outputFileName,  index = False)
    print("Table saved as: " + outputFileName)

    return table




# ---------------------------------------------------------------------------------------------------------------
# T2 USING EPG MODELING FROM DESS ACQUISITIONS
# ---------------------------------------------------------------------------------------------------------------

def calculate_t2_maps_s(imageData):


    # get fileNames
    # images
    preprocessedFolder = imageData["preprocessedFolder"]
    infoFileName       = imageData["infoFileName"]
    i1fileName         = imageData["i1fileName"]
    i2fileName         = imageData["i2fileName"]
    # mask
    segmentedFolder    = imageData["segmentedFolder"]
    maskFileName       = imageData["maskFileName"]
    # t2 maps
    relaxometryFolder  = imageData["relaxometryFolder"]
    t2mapFileName      = imageData["t2mapFileName"]
    t2mapMaskFileName  = imageData["t2mapMaskFileName"]
    imageNameRoot      = imageData["imageNameRoot"]

    print (imageNameRoot)

    # read txt file and get acquisition parameters
    for line in open(preprocessedFolder + infoFileName):
        if "0018|0080" in line:
            repetitionTime = float(line[10:len(line)])
        if "0018|0081" in line:
            echoTime       = float(line[10:len(line)])
        if "0018|1314" in line:
            alpha_deg_L    = float(line[10:len(line)]) #alpha_deg_L = flipAngle

    # read images
    img1L = sitk.ReadImage(preprocessedFolder + i1fileName)
    img2L = sitk.ReadImage(preprocessedFolder + i2fileName)
    mask  = sitk.ReadImage(segmentedFolder    + maskFileName)

    # compute T2 map
    T2map = rf.calculate_t2_maps_from_dess(img1L, img2L, repetitionTime, echoTime, alpha_deg_L)

    # write T2 map
    sitk.WriteImage(T2map, relaxometryFolder + t2mapFileName)

    # mask T2 map
    masked_map = rf.mask_map(T2map, mask)

    # write masked T2 map
    sitk.WriteImage(masked_map, relaxometryFolder + t2mapMaskFileName)

def calculate_t2_maps(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(calculate_t2_maps_s, allImageData)
    print ("-> T2 maps calculated")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def show_t2_maps(allImageData):

    nOfImages   = len(allImageData)
    imgLW       = 6
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
        preprocessedFolder = allImageData[i]["preprocessedFolder"]
        i1fileName         = allImageData[i]["i1fileName"]
        relaxometryFolder  = allImageData[i]["relaxometryFolder"]
        t2mapMaskFileName  = allImageData[i]["t2mapMaskFileName"]
        imageNameRoot      = allImageData[i]["imageNameRoot"]

        # read images
        img = sitk.ReadImage(preprocessedFolder + i1fileName)
        map = sitk.ReadImage(relaxometryFolder + t2mapMaskFileName)

        # images from simpleitk to numpy
        img_py = sitk.GetArrayFromImage(img)
        map_py = sitk.GetArrayFromImage(map)


        # extract slices at 2/5, 3/5, and 4/5 of the image size
        size = np.size(map_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                firstValue = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                lastValue = b
                break

        sliceStep = int ((lastValue-firstValue)/4)
        sliceID = (firstValue + sliceStep, firstValue + 2*sliceStep, firstValue + 3*sliceStep)

        for a in range (0,len(sliceID)):

            # create subplot
            ax1 = fig.add_subplot(nOfRows,nOfColumns,axisIndex)

            # get slices
            slice_img_py = img_py[:,:,sliceID[a]]
            slice_map_py = map_py[:,:,sliceID[a]]
            slice_map_masked = np.ma.masked_where(slice_map_py == 0, slice_map_py)

            # show image
            ren1 = ax1.imshow(slice_img_py    , 'gray', interpolation=None, origin='lower')
            ren2 = ax1.imshow(slice_map_masked, 'jet' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            clb = plt.colorbar(ren2, orientation='vertical', shrink=0.60, ticks=[0, 20, 40, 60, 80, 100])
            clb.ax.set_title('[ms]')
            ax1.set_title(str(i+1) + ". " + imageNameRoot + " - Slice: " + str(sliceID[a]))
            ax1.axis('off')

            axisIndex = axisIndex + 1


def show_t2_graph(allImageData):

    # calculate average and standard deviation
    average = []
    stdDev  = []
    for i in range(0, len(allImageData)):
        # file name
        relaxometryFolder = allImageData[i]["relaxometryFolder"]
        t2MapFileName     = allImageData[i]["t2mapFileName"]
        # read image
        t2Map = sitk.ReadImage(relaxometryFolder + t2MapFileName)
        # from SimpleITK to numpy
        t2Map_py = sitk.GetArrayFromImage(t2Map)
        # from 3D matrix to array
        t2Map_py_array = np.reshape(t2Map_py, np.size(t2Map_py,0)*np.size(t2Map_py,1)*np.size(t2Map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(t2Map_py_array != 0)
        t1rho_vector = t2Map_py_array[index]
        # calculate average and stddev
        average.append(np.average(t1rho_vector))
        stdDev.append(np.std(t1rho_vector))

    average = np.asarray(average)
    stdDev  = np.asarray(stdDev)
    x = np.arange(len(allImageData))

    # figure size
    figureWidth = 18
    figLength   = 8
    plt.rcParams['figure.figsize'] = [figureWidth, figLength] # figsize=() seems to be ineffective on notebooks

    # error bar
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (nOfImages can be larger)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.errorbar(x, average, yerr=stdDev, linestyle='None', marker='o')

    # set ticks and labels
    plt.xticks(x)
    imageNames= []
    for i in range(0, len(allImageData)):
        imageRoot, imageExt = os.path.splitext(allImageData[i]["t2mapFileName"])
        imageNames.append(imageRoot)
    ax.set_xticklabels(imageNames, rotation='vertical')
    ax.set_ylabel('t2 [ms]')

    # show
    plt.show()


def show_t2_table(allImageData, outputFileName):

    # read and calculate values for table
    imageNames = []
    average = []
    stdDev  = []

    for i in range(0, len(allImageData)):
        # file name
        relaxometryFolder = allImageData[i]["relaxometryFolder"]
        t2MapFileName     = allImageData[i]["t2mapFileName"]
        imageRoot, imageExt = os.path.splitext(allImageData[i]["t2mapFileName"])
        imageNames.append(imageRoot)
        # read image
        t2Map = sitk.ReadImage(relaxometryFolder + t2MapFileName)
        # from SimpleITK to numpy
        t2Map_py = sitk.GetArrayFromImage(t2Map)
        # from 3D matrix to array
        t2Map_py_array = np.reshape(t2Map_py, np.size(t2Map_py,0)*np.size(t2Map_py,1)*np.size(t2Map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(t2Map_py_array != 0)
        t2_vector = t2Map_py_array[index]
        # calculate average and stddev
        average.append(np.average(t2_vector))
        stdDev.append(np.std(t2_vector))

    # create table
    table = pd.DataFrame(
        {
            "subjects" : t2MapFileName,
            "average"  : average,
            "stddev"   : stdDev
        }
    )
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table = table.round(2) #show 2 decimals

    # show all the lines of the table
    dataDimension = table.shape # get number of rows
    pd.set_option("display.max_rows",dataDimension[0]) # show all the rows

    # save table as csv
    #now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    #csvFileName = allImageData[0]["relaxometryFolder"] + now + "_t2.csv"
    #table.to_csv(csvFileName,  index = False)
    table.to_csv(outputFileName,  index = False)
    print("Table saved as: " + outputFileName)

    return table

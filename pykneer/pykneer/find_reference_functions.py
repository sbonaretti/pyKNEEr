# Serena Bonaretti, 2018

import multiprocessing
import numpy as np
import os
import platform
import shutil
import SimpleITK as sitk

from . import elastix_transformix

#import sitk_functions  as sitkf


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


def prepare_reference(allImageData, reference_names, iterationNo):

#    anatomy = allImageData[0]["currentAnatomy"] # it is "f" for femur (assigned in loadImageDataFindReference)
#    refID   = iterationNo
#    # get new reference ID in allImageData
#    reference_name = reference_names[iterationNo]
#    for i in range (0, len(allImageData)):
#        if allImageData[i]["movingName"] == reference_name:
#            refID = i
#            break

    # variables
    standardreference_name          = "reference.mha"
    standardreference_root          = "reference"
    standardMaskName               = "reference_f.mha"
    standardFdilMaskFileName       = "reference_f_15.mha"
    standardFlevelSetsMaskFileName = "reference_f_levelSet.mha"
    standardReferenceSuffix        = "prep.mha"
    standardMaskSuffix             = "f.mha"

    # get the system for folderDiv
    folderDiv = folder_divider()

    # 0. create parent output folder (first iteration only)
    if iterationNo == 1:
        # create global output folder for this reference
        #if not os.path.isdir(allImageData[0]["registeredSubFolder"]):
        #    os.makedirs(allImageData[0]["registeredSubFolder"])
        output_folder = allImageData[0]["parent_folder"] + allImageData[0]["reference_root"] + folderDiv
        if not os.path.isdir (output_folder): # automatically created by addNamesToImageData in pyKNEErIO
            os.makedirs(output_folder)

        # assign output folder to all cells of allImageData (adapting to requests of elastixTransformix class)
        for i in range(0,len(allImageData)):
            allImageData[i]["output_folder"]           = output_folder
            allImageData[i]["reference_name"]          = standardreference_name
            allImageData[i]["reference_root"]          = standardreference_root
            allImageData[i]["fmaskFileName"]          = standardMaskName
            allImageData[i]["fdilMaskFileName"]       = standardFdilMaskFileName
            allImageData[i]["flevelSetsMaskFileName"] = standardFlevelSetsMaskFileName
            allImageData[i]["registrationType"]       = "newsubject"


    # 1. create new reference image folder and it to every image in the dictionary
    currentreference_root, referenceExt = os.path.splitext(reference_names[iterationNo])
    newReferenceFolder = allImageData[0]["output_folder"] + str(iterationNo) + "_" + currentreference_root + folderDiv
    if not os.path.isdir(newReferenceFolder):
        os.makedirs(newReferenceFolder)
    for i in range(0,len(allImageData)):
        allImageData[i]["referenceFolder"] = newReferenceFolder

    # 2. create new file names for reference image and mask (using dictionary of image 0 of allImageData)
    # image
    oldRefImageName = allImageData[0]["parent_folder"]  + reference_names[iterationNo]
    newRefImageName = newReferenceFolder               + reference_names[iterationNo]
    # mask
    maskName        = reference_names[iterationNo].replace(standardReferenceSuffix, standardMaskSuffix) # this is hardcoded and determines the way file names are
    oldRefMaskName  = allImageData[0]["parent_folder"]  + maskName
    newRefMaskName  = newReferenceFolder               + maskName

    # 3. move reference image and mask to the new folder and change names
    shutil.copy(oldRefImageName, newRefImageName)
    shutil.copy(oldRefMaskName , newRefMaskName)
    os.rename(newRefImageName, newReferenceFolder + standardreference_name)
    os.rename(newRefMaskName , newReferenceFolder + standardMaskName)

    # 4. dilate mask and convert to level set (use folder and image names of first cell in allImageData)
    bone = elastix_transformix.bone()
    bone.prepare_reference (allImageData[0])

    return allImageData



def calculate_vector_fields_s(imageData):

    # get the system for folderDiv
    folderDiv = folder_divider()

    # create output folders that do not exist
    imageData["registeredFolder"]           = imageData["referenceFolder"]
    imageData["registeredSubFolder"]        = imageData["registeredFolder"] + imageData["movingRoot"] + folderDiv
    if not os.path.isdir(imageData["registeredSubFolder"]):
        os.makedirs(imageData["registeredSubFolder"])

    # register the femur
    bone = elastix_transformix.bone()
    bone.rigid     (imageData)
    bone.similarity(imageData)
    bone.spline    (imageData)
    bone.vfspline  (imageData)

def calculate_vector_fields(allImageData, nOfProcesses):

    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(calculate_vector_fields_s, allImageData)
    print ("-> Vector fields calculated")



def find_reference_as_minimum_distance_to_average(allImageData, reference_names, minDistance, iterationNo):

    fieldFolder = allImageData[0]["referenceFolder"]

    # allocate an empty field (with first field characteristisc) and convert to numpy matrix
    imageData = allImageData[0]
    firstField       = sitk.ReadImage(fieldFolder + imageData["vectorFieldName"])
    averageField     = sitk.Image(firstField.GetSize(),sitk.sitkVectorFloat32)
    averageField_py  = sitk.GetArrayFromImage(averageField)

    # calculate average field
    for i in range(0,len(allImageData)):

        # get current field
        imageData        = allImageData[i]
        fieldFileName    = fieldFolder + imageData["vectorFieldName"]
#        print ("    " + imageData["vectorFieldName"] )
        field            = sitk.ReadImage(fieldFileName)
        # transform to numpy matrix
        field_py = sitk.GetArrayFromImage(field)
        # sum up the field to the average field
        averageField_py = averageField_py + field_py

    # divide by the number of fields
    averageField_py = averageField_py / len(allImageData)

    # back to sitk
    averageField = sitk.GetImageFromArray(averageField_py)
    averageField.SetSpacing  (firstField.GetSpacing  ())
    averageField.SetOrigin   (firstField.GetOrigin   ())
    averageField.SetDirection(firstField.GetDirection())

    # write the average field
#    averageFieldFileName = firstImage["registeredFolder"] + "averageField_" + str(iterationNo) + ".mha"
#    sitk.WriteImage(averageField, averageFieldFileName)

    # calculate norms between average field and each moving field
    norms = np.zeros(len(allImageData))

    for i in range(0,len(allImageData)):

        # re-load the field
        imageData       = allImageData[i]
        fieldFileName   = fieldFolder + imageData["vectorFieldName"]
        field           = sitk.ReadImage(fieldFileName)
        # transform to python array
        averageField_py = sitk.GetArrayFromImage(averageField)
        field_py        = sitk.GetArrayFromImage(field)
        # extract values under dilated mask
        maskDil               = sitk.ReadImage(allImageData[0]["referenceFolder"] + allImageData[0]["fdilMaskFileName"])
        maskDil_py            = sitk.GetArrayFromImage(maskDil)
        averageField_pyMasked = np.extract(maskDil_py == 1, averageField_py)
        field_pyMasked        = np.extract(maskDil_py == 1, field_py)
        nOfMaskedVoxels       = len(averageField_pyMasked)
        # calculate norm of distances
        norm            = np.linalg.norm(averageField_pyMasked-field_pyMasked)
        print ("    " + imageData["vectorFieldName"] )
        print ("      norm before normalization: " + str(norm))
        norm = norm / nOfMaskedVoxels
        print ("      norm after normalization: " + str(norm))
        print ("      number of image voxels: "  + str(averageField.GetSize()[0]*averageField.GetSize()[1]*averageField.GetSize()[2]))
        print ("      snumber of masked voxels: " + str(nOfMaskedVoxels))
        # assign to vector of norms
        norms[i]        = norm

    # get minimum norm
    minNorm   = min(norms)
    minNormID = np.where(norms == norms.min())
    minNormID = int(minNormID[0][0]) # previous function provides a tuple
    print ("   -> Distances to average field are: " + np.array2string(norms, precision=8) )
    print ("   -> Minimum distance is %.8f" % minNorm)

    # pick corresponding image as new reference
    newreference_name = allImageData[minNormID]["movingName"]
    print ("   -> Reference of next iteration is " + allImageData[minNormID]["movingName"])

    # add values to allImageData
    reference_names[iterationNo+1] = newreference_name
    minDistance   [iterationNo]   = minNorm

    return reference_names, minDistance #refID?

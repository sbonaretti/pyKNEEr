# Serena Bonaretti, 2018

import numpy as np
import os
import pkg_resources
import platform
import re

# ---------------------------------------------------------------------------------------------------------------------------
# PREPROCESSING -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

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


def load_image_data_preprocessing(inputFileName):

    folderDiv = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(inputFileName):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (inputFileName) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get inputFileName content
    fileContent=[]
    for line in open(inputFileName):
        fileContent.append(line.rstrip("\n"))

    # ----------------------------------------------------------------------------------------------------------------------
    # folders

    # line 1 is the original folder of acquired dcm
    # add slash or back slash at the end
    originalFolder = fileContent[0]
    if not originalFolder.endswith(folderDiv):
        originalFolder = originalFolder + folderDiv
    # make sure the last folder is called "original"
    temp = os.path.basename(os.path.normpath(originalFolder))
    if temp != "original":
        print("----------------------------------------------------------------------------------------")
        print("""ERROR: Put your dicoms in a parent folder called "original" """)
        print("----------------------------------------------------------------------------------------")
        return {}
    # make sure that the path exists
    if not os.path.isdir(originalFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The original folder %s does not exist" % (originalFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the preprocessed folder
    preprocessedFolder = os.path.split(originalFolder)[0] # remove the slash or backslash
    preprocessedFolder = os.path.split(preprocessedFolder)[0] # remove "original"
    preprocessedFolder = preprocessedFolder + folderDiv + "preprocessed" + folderDiv
    if not os.path.isdir(preprocessedFolder):
        os.mkdir(preprocessedFolder)
        print("-> preprocessedFolder %s created" % (preprocessedFolder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    allImageData = []
    for i in range(1,len(fileContent),2):

        # current image folder name
        imageFolderFileName = fileContent[i]

        # if there are empty lines at the end of the file
        if len(imageFolderFileName) != 0:

            if not os.path.isdir(originalFolder + imageFolderFileName):
                print("----------------------------------------------------------------------------------------")
                print("ERROR: The folder %s does not exist" % (imageFolderFileName) )
                print("----------------------------------------------------------------------------------------")
                return {}
            # make sure there are dicom files in the folder
            for fname in os.listdir(originalFolder + imageFolderFileName):
                if fname.endswith(".dcm") or fname.endswith(".DCM") or fname.endswith(""):
                    a = 1
                    #print(originalFolder + imageFolderFileName)
                else:
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The folder %s does not contain dicom files" % (originalFolder + imageFolderFileName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # knee laterality
            #print (fileContent[i+1])
            laterality = fileContent[i+1]
            if laterality != "right" and laterality != "Right" and laterality != "left" and laterality != "left":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Knee laterality must be 'right' or 'left'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # create the dictionary
            imageData = {}
            imageData["originalFolder"]       = originalFolder
            imageData["preprocessedFolder"]   = preprocessedFolder
            imageData["imageFolderFileName"]  = imageFolderFileName
            imageData["laterality"]           = laterality
            # add output file names
            imageNameRoot = imageFolderFileName.replace(folderDiv, "_")
            imageData["imageNameRoot"]        = imageNameRoot
            imageData["tempFileName"]         = preprocessedFolder + imageData["imageNameRoot"] + "_temp.mha"
            imageData["originalFileName"]     = preprocessedFolder + imageData["imageNameRoot"] + "_orig.mha"
            imageData["preprocessedFileName"] = preprocessedFolder + imageData["imageNameRoot"] + "_prep.mha"
            imageData["infoFileName"]         = preprocessedFolder + imageData["imageNameRoot"] + "_orig.txt"

            # print out file name
            print (imageData["imageNameRoot"])

            # send to the data list
            allImageData.append(imageData)

    print ("-> information loaded for " + str(len(allImageData)) + " subjects")

    # return the image info
    return allImageData



# ---------------------------------------------------------------------------------------------------------------------------
# FIND REFERENCE ------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_find_reference(inputFileName):

    folderDiv = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(inputFileName):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (inputFileName) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get inputFileName content
    fileContent=[]
    for line in open(inputFileName):
        fileContent.append(line.rstrip("\n"))

    # ----------------------------------------------------------------------------------------------------------------------
    # get folders
    # line 1 is the parent folder
    parentFolder = fileContent[0]
    if not parentFolder.endswith(folderDiv):
        parentFolder = parentFolder + folderDiv
    if not os.path.isdir(parentFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The parent folder %s does not exist" % (parentFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    allImageData = []

    for i in range(1,len(fileContent)):

        currentLine = fileContent[i]

        # if there are empty lines at the end of the file
        if len(currentLine) != 0:

            # get image type (image or mask)
            imageType = currentLine[0]
            if imageType != "r" and imageType != "m":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'r' or 'm'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the refence image
            if imageType == "r":
                # get image name
                referenceName = currentLine[2:len(currentLine)]
                # check that the reference image exists
                if not os.path.isfile(parentFolder + referenceName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (parentFolder + referenceName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the moving image
            if imageType == "m":
                # get image name
                movingName = currentLine[2:len(currentLine)]
                # check that the reference image exists
                if not os.path.isfile(parentFolder + movingName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (parentFolder + movingName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # current image in a struct to the registration class
                imageData = {}

                # from input file
                imageData["parentFolder"]     = parentFolder
                imageData["referenceName"]    = referenceName
                imageData["movingName"]       = movingName

                # added to uniform with requirements in ElastixTransformix classes
                referenceRoot, imageExt       = os.path.splitext(referenceName)
                movingRoot, imageExt          = os.path.splitext(movingName)
                imageData["referenceRoot"]    = referenceRoot
                imageData["movingRoot"]       = movingRoot
                imageData["movingFolder"]     = parentFolder
                imageData["cartilage"]        = "fc"
                imageData["bone"]             = "f"
                imageData["currentAnatomy"]   = "f"
                imageData["registeredFolder"] = parentFolder
                imageData["segmentedFolder"]  = []
                imageData["vectorFieldName"]  = movingRoot +"_VF.mha"

                # add extra filenames and paths
                imageData = add_names_to_image_data(imageData,0)

                # send to the data list
                allImageData.append(imageData)

    print ("-> image information loaded")

    # return the image info
    return allImageData



# ---------------------------------------------------------------------------------------------------------------------------
# SEGMENTATION --------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_segmentation(registrationType, inputFileName):

    folderDiv = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if registrationType is allowed
    if registrationType != "newsubject" and registrationType != "longitudinal" and registrationType != "multimodal":
        print("----------------------------------------------------------------------------------------")
        print("ERROR: Please add 'newsubject' or 'longitudinal' or 'multimodal' as first input")
        print("----------------------------------------------------------------------------------------")
        return {}

#    # ----------------------------------------------------------------------------------------------------------------------
#    # check if anatomy is allowed
#    if anatomy != "femurCart" and anatomy != "tibiaCart" and anatomy != "patellaCart":
#        print("----------------------------------------------------------------------------------------")
#        print("ERROR: Please add 'femurCart' or 'tibiaCart' or 'patellaCart' as second input")
#        print("----------------------------------------------------------------------------------------")
#        return {}
#    if anatomy == "femurCart":
#        bone = "f"
#        cartilage = "fc"
#    elif anatomy == "tibiaCart":
#        bone = "t"
#        cartilage = "tc"
#    elif anatomy == "patellaCart":
#        bone = "p"
#        cartilage = "pc"
    # In the future, extensions for all knee cartilages
    anatomy = "femurCart"
    bone = "f"
    cartilage = "fc"

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(inputFileName):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (inputFileName) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get inputFileName content
    fileContent=[]
    for line in open(inputFileName):
        fileContent.append(line.rstrip("\n"))

    # ----------------------------------------------------------------------------------------------------------------------
    # get folders
    # line 1 is folder of reference image
    referenceFolder = fileContent[0]
    if not referenceFolder.endswith(folderDiv):
        referenceFolder = referenceFolder + folderDiv
    if not os.path.isdir(referenceFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The reference folder %s does not exist" % (referenceFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # line 2 is folder of the preprocessed (*_prep.mha) images, i.e. the moving image folder
    movingFolder = fileContent[1]
    if not movingFolder.endswith(folderDiv):
        movingFolder = movingFolder + folderDiv
    if not os.path.isdir(movingFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The preprocessed folder %s does not exist" % (movingFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the registered folder
    registeredFolder = os.path.split(movingFolder)[0] # remove the slash or backslash
    registeredFolder = os.path.split(registeredFolder)[0] # remove "original"
    registeredFolder = registeredFolder + folderDiv + "registered" + folderDiv
    if not os.path.isdir(registeredFolder):
        os.mkdir(registeredFolder)
        print("-> registeredFolder %s created" % (registeredFolder) )

    # create the segmented folder
    segmentedFolder = os.path.split(movingFolder)[0] # remove the slash or backslash
    segmentedFolder = os.path.split(segmentedFolder)[0] # remove "original"
    segmentedFolder = segmentedFolder + folderDiv + "segmented" + folderDiv
    if not os.path.isdir(segmentedFolder):
        os.mkdir(segmentedFolder)
        print("-> segmentedFolder %s created" % (segmentedFolder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    allImageData = []

    for i in range(2,len(fileContent)):

        currentLine = fileContent[i]

        # if there are empty lines at the end of the file
        if len(currentLine) != 0:

            # get image type (reference or moving)
            imageType = currentLine[0]
            if imageType != "r" and imageType != "m":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'r' or 'm'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the reference image
            if imageType == "r":
                # get image name
                referenceName = currentLine[2:len(currentLine)]
                # check that the reference image exists
                if not os.path.isfile(referenceFolder + referenceName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (referenceFolder + referenceName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}
            # if the current image is the moving image
            if imageType == "m":
                # get image name
                movingName = currentLine[2:len(currentLine)]
                # check that the reference image exists
                if not os.path.isfile(movingFolder + movingName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (movingFolder + movingName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # current image in a struct to the registration class
                referenceRoot, referenceExt = os.path.splitext(referenceName)
                movingRoot, movingExt = os.path.splitext(movingName)
                imageData = {}
                imageData["registrationType"]     = registrationType
                imageData["cartilage"]            = cartilage
                imageData["bone"]                 = bone
                imageData["currentAnatomy"]       = []
                imageData["referenceFolder"]      = referenceFolder
                imageData["referenceName"]        = referenceName
                imageData["referenceRoot"]        = referenceRoot
                imageData["movingFolder"]         = movingFolder
                imageData["movingName"]           = movingName
                imageData["movingRoot"]           = movingRoot
                imageData["registeredFolder"]     = registeredFolder
                imageData["segmentedFolder"]      = segmentedFolder

                # add extra filenames and paths
                imageData = add_names_to_image_data(imageData,1)

                # send to the data list
                allImageData.append(imageData)

    print ("-> image information loaded")

    # return all the info on the images to be segmented
    return allImageData


# ---------------------------------------------------------------------------------------------------------------------------
# ADD NAMES -----------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

# Function used by loadImageDataSegmentation and loadImageDataFindReference
def add_names_to_image_data(imageData,folderFlag):

    folderDiv = folder_divider()

    # output folders
    imageData["registeredSubFolder"]        = imageData["registeredFolder"] + imageData["movingRoot"] + folderDiv
    imageData["iregisteredSubFolder"]       = imageData["registeredSubFolder"] + "invert" + folderDiv

    # create output folders that do not exist
    if folderFlag ==1:
        if not os.path.isdir(imageData["registeredSubFolder"]):
            os.makedirs(imageData["registeredSubFolder"])
        if not os.path.isdir(imageData["iregisteredSubFolder"]):
            os.makedirs(imageData["iregisteredSubFolder"])

    # get current bone and cartilage
    bone      = imageData["bone"]
    cartilage = imageData["cartilage"]

    # reference mask file names
    imageData["dilateRadius"]                      = 15
    imageData[bone + "maskFileName"]               = imageData["referenceRoot"] + "_" + bone + ".mha"
    imageData[bone + "dilMaskFileName"]            = imageData["referenceRoot"] + "_" + bone + "_" + str(imageData["dilateRadius"]) + ".mha"
    imageData[bone + "levelSetsMaskFileName"]      = imageData["referenceRoot"] + "_" + bone + "_levelSet.mha"
    imageData[cartilage + "maskFileName"]          = imageData["referenceRoot"] + "_" + cartilage + ".mha"
    imageData[cartilage + "dilMaskFileName"]       = imageData["referenceRoot"] + "_" + cartilage + "_" + str(imageData["dilateRadius"]) + ".mha"
    imageData[cartilage + "levelSetsMaskFileName"] = imageData["referenceRoot"] + "_" + cartilage + "_levelSet.mha"

    # output image file names
    imageData[bone + "rigidName"]            = bone + "_rigid.mha"
    imageData[bone + "similarityName"]       = bone + "_similarity.mha"
    imageData[bone + "splineName"]           = bone + "_spline.mha"
    imageData[cartilage + "splineName"]      = cartilage + "_spline.mha"

    # output mask file names
    imageData[bone + "mRigidName"]           = bone + "_rigidMask.mha"
    imageData[bone + "mSimilarityName"]      = bone + "_similarityMask.mha"
    imageData[bone + "mSplineName"]          = bone + "_splineMask.mha"
    imageData[bone + "mask"]                 = imageData["movingRoot"] + "_" + bone + ".mha"
    imageData[cartilage + "mRigidName"]      = cartilage + "_rigidMask.mha"
    imageData[cartilage + "mSimilarityName"] = cartilage + "_similarityMask.mha"
    imageData[cartilage + "mSplineName"]     = cartilage + "_splineMask.mha"
    imageData[cartilage + "mask"]            = cartilage + "_mask.mha"
    imageData[cartilage + "mask"]            = imageData["movingRoot"] + "_" + cartilage + ".mha"

    # output transformation names
    imageData[bone + "rigidTransfName"]        = "TransformParameters."  + bone + "_rigid.txt"
    imageData[bone + "similarityTransfName"]   = "TransformParameters."  + bone + "_similarity.txt"
    imageData[bone + "splineTransfName"]       = "TransformParameters."  + bone + "_spline.txt"
    imageData[bone + "iRigidTransfName"]       = "iTransformParameters." + bone + "_rigid.txt"
    imageData[bone + "iSimilarityTransfName"]  = "iTransformParameters." + bone + "_similarity.txt"
    imageData[bone + "iSplineTransfName"]      = "iTransformParameters." + bone + "_spline.txt"
    imageData[bone + "mRigidTransfName"]       = "mTransformParameters." + bone + "_rigid.txt"
    imageData[bone + "mSimilarityTransfName"]  = "mTransformParameters." + bone + "_similarity.txt"
    imageData[bone + "mSplineTransfName"]      = "mTransformParameters." + bone + "_spline.txt"
    imageData[cartilage + "splineTransfName"]  = "TransformParameters."  + cartilage + "_spline.txt"
    imageData[cartilage + "iSplineTransfName"] = "iTransformParameters." + cartilage + "_spline.txt"
    imageData[cartilage + "mSplineTransfName"] = "mTransformParameters." + cartilage + "_spline.txt"

    # parameter files
    parameterFolder = pkg_resources.resource_filename('pykneer','parameterFiles') + folderDiv
    if not parameterFolder.endswith(folderDiv):
        parameterFolder = parameterFolder + folderDiv
    if not os.path.isdir(parameterFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The parameter folder %s does not exist" % (parameterFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}
    # check if the folder contains all the parameter files
    paramFileRigid       = parameterFolder + "MR_param_rigid.txt"
    iparamFileRigid      = parameterFolder + "MR_iparam_rigid.txt"
    paramFileSimilarity  = parameterFolder + "MR_param_similarity.txt"
    iparamFileSimilarity = parameterFolder + "MR_iparam_similarity.txt"
    paramFileSpline      = parameterFolder + "MR_param_spline.txt"
    iparamFileSpline     = parameterFolder + "MR_iparam_spline.txt"
    if not os.path.isfile(paramFileRigid):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (paramFileRigid) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(iparamFileRigid):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (iparamFileRigid) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(paramFileSimilarity):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (paramFileSimilarity) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(iparamFileSimilarity):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (iparamFileSimilarity) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(paramFileSpline):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (paramFileSpline) )
        print("----------------------------------------------------------------------------------------")
        return {}
    if not os.path.isfile(iparamFileSpline):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (iparamFileSpline) )
        print("----------------------------------------------------------------------------------------")
        return {}
    # add parameter files to imageData
    imageData["paramFileRigid"]       = paramFileRigid
    imageData["iparamFileRigid"]      = iparamFileRigid
    imageData["paramFileSimilarity"]  = paramFileSimilarity
    imageData["iparamFileSimilarity"] = iparamFileSimilarity
    imageData["paramFileSpline"]      = paramFileSpline
    imageData["iparamFileSpline"]     = iparamFileSpline

    # elastix path (from binaries in pykneer package)
    sys = platform.system()
    if sys == "Linux":
        dirpath = pkg_resources.resource_filename('pykneer','elastix/Linux/')
    elif sys == "Windows":
        dirpath = pkg_resources.resource_filename('pykneer','elastix/Windows/')
    elif sys == "Darwin":
        dirpath = pkg_resources.resource_filename('pykneer','elastix/Darwin/')
    imageData["elastixFolder"]           = dirpath
    imageData["completeElastixPath"]     = dirpath + "elastix"
    imageData["completeTransformixPath"] = dirpath + "transformix"

    return imageData


# ---------------------------------------------------------------------------------------------------------------------------
# SEGMENTATION QUALITY ------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_segmentation_quality(inputFileName):

    folderDiv = folder_divider()

     # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(inputFileName):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (inputFileName) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get inputFileName content
    fileContent=[]
    for line in open(inputFileName):
        fileContent.append(line.rstrip("\n"))

    # line 0 is folder of the registered images
    segmentedFolder = fileContent[0]
    if not segmentedFolder.endswith(folderDiv):
        segmentedFolder = segmentedFolder + folderDiv
    if not os.path.isdir(segmentedFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The segmented folder %s does not exist" % (segmentedFolder) )
        print("----------------------------------------------------------------------------------------")

    # line 1 is folder of the segmented masks
    groundTruthFolder = fileContent[1]
    if not groundTruthFolder.endswith(folderDiv):
        groundTruthFolder = groundTruthFolder + folderDiv
    if not os.path.isdir(groundTruthFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The ground truth folder %s does not exist" % (groundTruthFolder) )
        print("----------------------------------------------------------------------------------------")

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    allImageData = []

    for i in range(2,len(fileContent)):

        currentLine = fileContent[i]

        # if there are empty lines at the end of the file
        if len(currentLine) != 0:

            # get image type (reference or moving)
            imageType = currentLine[0]
            if imageType != "s" and imageType != "g":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 's' or 'g'")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the segmented image
            if imageType == "s":
                # get image name
                segmentedName = currentLine[2:len(currentLine)]
                # check that the segmented image exists
                if not os.path.isfile(segmentedFolder + segmentedName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmentedFolder + segmentedName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}
            # if the current image is the moving image
            if imageType == "g":
                # get image name
                groundTruthName = currentLine[2:len(currentLine)]
                # check that the groundTruth image exists
                if not os.path.isfile(groundTruthFolder + groundTruthName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (groundTruthFolder + groundTruthName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # put pair in a list
                imageData = {}
                imageData["segmentedFolder"]        = segmentedFolder
                imageData["groundTruthFolder"]      = groundTruthFolder
                imageData["segmentedName"]          = segmentedName
                imageData["groundTruthName"]        = groundTruthName

                # send to the data list
                allImageData.append(imageData)

    print ("-> image information loaded")

    # return the image info
    return allImageData


# ---------------------------------------------------------------------------------------------------------------------------
# MORPHOLOGY ----------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_morphology(inputFileName):

    folderDiv = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(inputFileName):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (inputFileName) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get inputFileName content
    fileContent=[]
    for line in open(inputFileName):
        fileContent.append(line.rstrip("\n"))

    # ----------------------------------------------------------------------------------------------------------------------
    # get folder - line 1 is the input folder
    inputFolder = fileContent[0]
    if not inputFolder.endswith(folderDiv):
        inputFolder = inputFolder + folderDiv
    if not os.path.isdir(inputFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The input folder %s does not exist" % (inputFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the morphology folder
    morphologyFolder = os.path.split(inputFolder)[0] # remove the slash or backslash
    morphologyFolder = os.path.split(morphologyFolder)[0] # remove "original"
    morphologyFolder = morphologyFolder + folderDiv + "morphology" + folderDiv
    if not os.path.isdir(morphologyFolder):
        os.mkdir(morphologyFolder)
        print("-> morphologyFolder %s created" % (morphologyFolder) )


    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    allImageData = []

    for i in range(1,len(fileContent)):

        maskName = fileContent[i]

        # if there are empty lines at the end of the file
        if len(maskName) != 0:

            # check that the mask exists
            if not os.path.isfile(inputFolder + maskName):
                print("----------------------------------------------------------------------------------------")
                print("ERROR: The file %s does not exist" % (inputFolder + maskName) )
                print("----------------------------------------------------------------------------------------")
                return {}

            # create the dictionary
            imageData = {}
            # input names
            imageData["inputFolder"]      = inputFolder
            imageData["maskName"]         = maskName
            # output names
            maskNameRoot, maskNameExt     = os.path.splitext(maskName)
            imageData["boneCartName"]     = maskNameRoot + "_boneCart.txt"
            imageData["artiCartName"]     = maskNameRoot + "_artiCart.txt"
            imageData["thicknessName"]    = []
            imageData["algorithm"]        = []
            imageData["volumeName"]       = maskNameRoot + "_volume.txt"
            imageData["morphologyFolder"] = morphologyFolder
            # for visualization
            imageData["boneCartFletName"] = maskNameRoot + "_boneCartFlet.txt"
            imageData["artiCartFletName"] = maskNameRoot + "_artiCartFlet.txt"
            imageData["bonePhiName"]      = maskNameRoot + "_bonePhi.txt"
            imageData["artiPhiName"]      = maskNameRoot + "_artiPhi.txt"

            # send to the whole data array
            allImageData.append(imageData)

    print ("-> image information loaded")

    # return the image info
    return allImageData


# ---------------------------------------------------------------------------------------------------------------------------
# EPG (T2 from DESS)---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_EPG(inputFileName):

    # determine the sistem to define the folder divider ("\" or "/")
    folderDiv = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(inputFileName):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file %s does not exist" % (inputFileName) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get inputFileName content
    fileContent=[]
    #i=0;
    for line in open(inputFileName):
        fileContent.append(line.rstrip("\n"))

    # ----------------------------------------------------------------------------------------------------------------------
    # look for needed folders
    # preprocessed folder
    preprocessedFolder = fileContent[0]
    if not preprocessedFolder.endswith(folderDiv):
        preprocessedFolder = preprocessedFolder + folderDiv
    if not os.path.isdir(preprocessedFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The preprocessing folder %s does not exist" % (preprocessedFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # segmented folder
    segmentedFolder = fileContent[1]
    if not segmentedFolder.endswith(folderDiv):
        segmentedFolder = segmentedFolder + folderDiv
    if not os.path.isdir(segmentedFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The segmented folder %s does not exist" % (segmentedFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the t2mapping folder
    relaxometryFolder = os.path.split(preprocessedFolder)[0] # remove the slash or backslash
    relaxometryFolder = os.path.split(relaxometryFolder)[0] # remove "original"
    relaxometryFolder = relaxometryFolder + folderDiv + "relaxometry" + folderDiv
    if not os.path.isdir(relaxometryFolder):
        os.mkdir(relaxometryFolder)
        print("-> relaxometry folder %s created" % (relaxometryFolder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    allImageData = []

    for i in range(2,len(fileContent)):

        currentLine = fileContent[i]

        # if there are empty lines at the end of the file
        if len(currentLine) != 0:

            # get image type (reference or moving)
            imageType = currentLine[0:2]
            if imageType != "i1" and imageType != "i2" and imageType != "cm":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'i1' or 'i2' or 'cm' ")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the i1 image
            if imageType == "i1":
                # get image name
                i1fileName = currentLine[3:len(currentLine)]
                # check that the segmented image exists
                if not os.path.isfile(preprocessedFolder + i1fileName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessedFolder + i1fileName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # check that the info file exists
            imageNameRoot, imageExt         = os.path.splitext(i1fileName)
            infoFileName = imageNameRoot + ".txt"
            if not os.path.isfile(preprocessedFolder + infoFileName):
                print("----------------------------------------------------------------------------------------")
                print("ERROR: The file %s does not exist" % (preprocessedFolder + infoFileName) )
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is the i2 image
            if imageType == "i2":
                # get image name
                i2fileName = currentLine[3:len(currentLine)]
                # check that the segmented image exists
                if not os.path.isfile(preprocessedFolder + i2fileName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessedFolder + i2fileName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the cartilage mask
            if imageType == "cm":
                # get image name
                maskFileName = currentLine[3:len(currentLine)]
                # check that the segmented image exists
                if not os.path.isfile(segmentedFolder + maskFileName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmentedFolder + maskFileName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

                # create the dictionary
                imageData = {}
                # add folders
                imageData["preprocessedFolder"] = preprocessedFolder
                imageData["segmentedFolder"]    = segmentedFolder
                imageData["relaxometryFolder"]  = relaxometryFolder
                # add input file names
                imageData["i1fileName"]         = i1fileName
                imageData["i2fileName"]         = i2fileName
                imageData["maskFileName"]       = maskFileName
                imageData["infoFileName"]       = infoFileName
                # add output file names
                imageData["t2mapFileName"]      = imageNameRoot + "_T2map.mha"
                imageData["t2mapMaskFileName"]  = imageNameRoot + "_T2map_masked.mha"
                # others
                imageData["imageNameRoot"]      = imageNameRoot

                print (imageData["imageNameRoot"])

                # send to the data dictionary
                allImageData.append(imageData)



    print ("-> information loaded for " + str(len(allImageData)) + " subjects")

    # return the image info
    return allImageData



# ---------------------------------------------------------------------------------------------------------------------------
# FITTING FOR RELAXOMETRY MAPS ----------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def load_image_data_fitting(inputFileName, methodFlag, registrationFlag):

    # determine the sistem to define the folder divider ("\" or "/")
    folderDiv = folder_divider()

    # ----------------------------------------------------------------------------------------------------------------------
    # check if input file exists
    if not os.path.exists(inputFileName):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The file  %s does not exist" % (inputFileName) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # ----------------------------------------------------------------------------------------------------------------------
    # get inputFileName content
    fileContent=[]
    #i=0;
    for line in open(inputFileName):
        fileContent.append(line.rstrip("\n"))

    # ----------------------------------------------------------------------------------------------------------------------
    # look for needed folders
    # preprocessed folder
    preprocessedFolder = fileContent[0]
    if not preprocessedFolder.endswith(folderDiv):
        preprocessedFolder = preprocessedFolder + folderDiv
    if not os.path.isdir(preprocessedFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The preprocessing folder %s does not exist" % (preprocessedFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # segmented folder
    segmentedFolder = fileContent[1]
    if not segmentedFolder.endswith(folderDiv):
        segmentedFolder = segmentedFolder + folderDiv
    if not os.path.isdir(segmentedFolder):
        print("----------------------------------------------------------------------------------------")
        print("ERROR: The segmented folder %s does not exist" % (segmentedFolder) )
        print("----------------------------------------------------------------------------------------")
        return {}

    # create the relaxometry folder
    relaxometryFolder = os.path.split(preprocessedFolder)[0] # remove the slash or backslash
    relaxometryFolder = os.path.split(relaxometryFolder)[0] # remove "original"
    relaxometryFolder = relaxometryFolder + folderDiv + "relaxometry" + folderDiv
    if not os.path.isdir(relaxometryFolder):
        os.mkdir(relaxometryFolder)
        print("-> relaxometry %s created" % (relaxometryFolder) )

    # ----------------------------------------------------------------------------------------------------------------------
    # number of acquisitions
    nOfAcquisitions = int(fileContent[2])
    # create the IDs for the acquisitions
    acquisitionID = []
    for a in range(0,nOfAcquisitions):
        acquisitionID.append("i" + str(a+1))

    # ----------------------------------------------------------------------------------------------------------------------
    # get images and create a dictionary for each of them
    allImageData     = []
    acquisitionFileNames = []
    infoFileNames        = []

    for i in range(3,len(fileContent)):

        currentLine = fileContent[i]


        # if the line is not empty (there might be empty lines at the end of the file)
        if len(currentLine) != 0:

            # get image type (reference or moving)
            imageType = currentLine[0:2]


            #if imageType != "i1" and imageType != "i2" and imageType != "i3" and imageType != "i4" and imageType != "bm" and imageType != "cm":
            if imageType not in acquisitionID and imageType != "bm" and imageType != "cm":
                print("----------------------------------------------------------------------------------------")
                print("ERROR: Image type must be 'i1' or 'i2' or 'i3' or 'i4' or 'bm' or 'cm' ")
                print("----------------------------------------------------------------------------------------")
                return {}

            # if the current image is an acquisition
            if imageType in acquisitionID:
            #if imageType == "i1":
                # get image name
                #i1fileName = currentLine[3:len(currentLine)]
                acquisitionFileNames.append(currentLine[3:len(currentLine)])
                # check that the preprocessed image exists
                if not os.path.isfile(preprocessedFolder + acquisitionFileNames[-1]):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessedFolder + acquisitionFileNames[-1]) )
                    print("----------------------------------------------------------------------------------------")
                    return {}
                # check that the info file exists
                imageNameRoot, imageExt         = os.path.splitext(acquisitionFileNames[-1])
                infoFileNames.append(imageNameRoot + ".txt")
                if not os.path.isfile(preprocessedFolder + infoFileNames[-1]):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (preprocessedFolder + infoFileNames[-1]) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the bone mask
            if imageType == "bm":
                # get image name
                boneMaskFileName = currentLine[3:len(currentLine)]
                # check that the segmented image exists
                if not os.path.isfile(segmentedFolder + boneMaskFileName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmentedFolder + boneMaskFileName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}

            # if the current image is the cartilage mask
            if imageType == "cm":
                # get image name
                cartMaskFileName = currentLine[3:len(currentLine)]
                # check that the segmented image exists
                if not os.path.isfile(segmentedFolder + cartMaskFileName):
                    print("----------------------------------------------------------------------------------------")
                    print("ERROR: The file %s does not exist" % (segmentedFolder + cartMaskFileName) )
                    print("----------------------------------------------------------------------------------------")
                    return {}


                # create the dictionary
                imageData = {}

                # folders
                imageData["preprocessedFolder"]    = preprocessedFolder
                imageData["segmentedFolder"]       = segmentedFolder
                imageData["relaxometryFolder"]     = relaxometryFolder

                # input file names
                imageData["acquisitionFileNames"]  = acquisitionFileNames
                imageData["infoFileNames"]         = infoFileNames
                imageData["boneMaskFileName"]      = boneMaskFileName
                imageData["cartMaskFileName"]      = cartMaskFileName

                # fitting type
                imageData["methodFlag"]            = methodFlag

                # output file names
                imageNameRoot, imageExt      = os.path.splitext(acquisitionFileNames[0])
                if registrationFlag == 1:
                    if methodFlag == 0: # linear fitting
                        imageData["mapFileName"] = imageNameRoot + "_map_lin_aligned.mha"
                    elif methodFlag == 1: # exponential fitting
                        imageData["mapFileName"] = imageNameRoot + "_map_exp_aligned.mha"
                else:
                    if methodFlag == 0: # linear fitting
                        imageData["mapFileName"] = imageNameRoot + "_map_lin.mha"
                    elif methodFlag == 1: # exponential fitting
                        imageData["mapFileName"] = imageNameRoot + "_map_exp.mha"

                # alignment: fixed variables for elastix_transformix.py
                imageData["currentAnatomy"]        = 'femurCart' #### to be parametrized in a later release
                bone                               = "f"         #### to be parametrized in a later release
                imageData["bone"]                  = bone
                imageData["dilateRadius"]          = 15
                registeredFolder = os.path.split(preprocessedFolder)[0] # remove the slash or backslash
                registeredFolder = os.path.split(registeredFolder)[0] # remove "original"
                registeredFolder = registeredFolder + folderDiv + "registered" + folderDiv
                imageData["registeredFolder"]      = registeredFolder
                imageData["parameterFolder"]       = pkg_resources.resource_filename('pykneer','parameterFiles') + folderDiv
                imageData["paramFileRigid"]        = "MR_param_rigid.txt"
                
                # elastix path (from binaries in pykneer package)
                sys = platform.system()
                if sys == "Linux":
                    dirpath = pkg_resources.resource_filename('pykneer','elastix/Linux/')
                elif sys == "Windows":
                    dirpath = pkg_resources.resource_filename('pykneer','elastix/Windows/')
                elif sys == "Darwin":
                    dirpath = pkg_resources.resource_filename('pykneer','elastix/Darwin/')
                imageData["elastixFolder"]           = dirpath
                imageData["completeElastixPath"]     = dirpath + "elastix"
                # alignment: image-dependent variables for elastix_transformix.py
                imageData["referenceName"]                = imageData["acquisitionFileNames"][0]
                referenceRoot, imageExt                   = os.path.splitext(imageData["referenceName"] )
                imageData["referenceRoot"]                = referenceRoot
                imageData["maskFileName"]                 = imageData["boneMaskFileName"]
                imageData[bone + "maskFileName"]          = imageData["boneMaskFileName"]
                imageData[bone + "dilMaskFileName"]       = imageData["referenceRoot"] + "_" + bone + "_" + str(imageData["dilateRadius"]) + ".mha"
                imageData[bone + "levelSetsMaskFileName"] = imageData["referenceRoot"] + "_" + bone + "_levelSet.mha"
                imageData["movingFolder"]                 = imageData["preprocessedFolder"]

                # send to the data dictionary
                allImageData.append(imageData)

                # get variables ready for the next subject
                acquisitionFileNames = []
                infoFileNames        = []


    print ("-> information loaded for " + str(len(allImageData)) + " subjects")
    print ("-> for each subjects there are " + str(nOfAcquisitions) + " acquisitions")

    # return the image info
    return allImageData





# ---------------------------------------------------------------------------------------------------------------------------
# .TXT FILES  ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def read_txt_to_np_array(fileName):


    # read the file rows
    fileContent=[]
    for line in open(fileName):
        fileContent.append(line.rstrip("\n"))

    # allocate the array width
    firstRow = re.findall('\d+\.\d+', fileContent[0])
    array = np.ndarray((len(firstRow)))

    # fill array
    for i in range(0,len(fileContent)):
    #for i in range(0,2):
        if fileContent[i] != []: # if the string is not empty

            # get the numbers in the string
            value_str = re.findall(r"[-+]?\d*\.\d+|\d+", fileContent[i])

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


def write_np_array_to_txt(array, filename):

    file = open(filename, "w")

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

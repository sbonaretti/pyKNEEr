# Serena Bonaretti, 2018

from abc import ABC, abstractmethod
import os
import subprocess
import SimpleITK       as sitk

from . import sitk_functions  as sitkf


# ----------------------------------------------------------------------------------------------------------------------------------------
# abstract class for registration
class registration(ABC):

    @abstractmethod
    def rigid(self):
        pass

    @abstractmethod
    def similarity(self):
        pass

    @abstractmethod
    def spline(self):
        pass

    @abstractmethod
    def irigid(self):
        pass

    @abstractmethod
    def isimilarity(self):
        pass

    @abstractmethod
    def ispline(self):
        pass

    @abstractmethod
    def trigid(self):
        pass

    @abstractmethod
    def tsimilarity(self):
        pass

    @abstractmethod
    def tspline(self):
        pass

    @abstractmethod
    def vfspline(self):
        pass


    def prepare_reference(self, imageData):

        anatomy                   = imageData["currentAnatomy"]
        referenceMaskName         = imageData["referenceFolder"] + imageData[anatomy + "maskFileName"]
        referenceMaskDilName      = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        referenceMaskLevelSetName = imageData["referenceFolder"] + imageData[anatomy + "levelSetsMaskFileName"]
        radius                    = imageData["dilateRadius"]

        # dilate mask
        if not os.path.isfile(referenceMaskDilName):
            mask    = sitk.ReadImage(referenceMaskName)
            maskDil = sitkf.dilate_mask(mask, radius)
            sitk.WriteImage(maskDil, referenceMaskDilName)

        # convert mask from binary to levelset for warping
        if not os.path.isfile(referenceMaskLevelSetName):
            mask   = sitk.ReadImage(referenceMaskName)
            maskLS = sitkf.binary2levelset(mask)
            sitk.WriteImage(maskLS, referenceMaskLevelSetName)


    def modify_transformation(self, imageData, transformation):

        anatomy = imageData["currentAnatomy"]

        # transformation file name
        if transformation   == "rigid":
            inputFileName  = imageData["iregisteredSubFolder"] + imageData[anatomy + "iRigidTransfName"]
            outputFileName = imageData["iregisteredSubFolder"] + imageData[anatomy + "mRigidTransfName"]
        elif transformation == "similarity":
            inputFileName  = imageData["iregisteredSubFolder"] + imageData[anatomy + "iSimilarityTransfName"]
            outputFileName = imageData["iregisteredSubFolder"] + imageData[anatomy + "mSimilarityTransfName"]
        elif transformation == "spline":
            inputFileName  = imageData["iregisteredSubFolder"] + imageData[anatomy + "iSplineTransfName"]
            outputFileName = imageData["iregisteredSubFolder"] + imageData[anatomy + "mSplineTransfName"]
        else:
            print("----------------------------------------------------------------------------------------")
            print("ERROR: This transformation is not supported. Use 'rigid', 'similarity', or 'spline'")
            print("----------------------------------------------------------------------------------------")
            return

        # check if transformation file exists
        if not os.path.exists(inputFileName):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: The file  %s does not exist" % (inputFileName) )
            print("----------------------------------------------------------------------------------------")
            return

        # read the file and modify the needed lines
        fileContent=[]
        i = 0
        for line in open(inputFileName):
            fileContent.append(line)
            if "InitialTransformParametersFileName" in fileContent[i]:
                fileContent[i] = "(InitialTransformParametersFileName \"NoInitialTransform\")\n"
            if "DefaultPixelValue" in fileContent[i]:
                fileContent[i] = "(DefaultPixelValue -4)\n"
            if "Size" in fileContent[i] and transformation == "rigid":
                fileContent[i] = "(Size %s %s %s)\n" % (imageData["imageSize"][0], imageData["imageSize"][1], imageData["imageSize"][2])
            if "Spacing" in fileContent[i] and transformation == "rigid":
                fileContent[i] = "(Spacing %s %s %s)\n" % (imageData["imageSpacing"][0], imageData["imageSpacing"][1], imageData["imageSpacing"][2])
            i = i+1

        # write the file
        f = open(outputFileName,"w")
        for i in range(0,len(fileContent)):
            f.write(fileContent[i])
        f.close()







# ----------------------------------------------------------------------------------------------------------------------------------------
# registration class to segment bone
class bone (registration):

    # This function is specific for each bone
    def rigid(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"] + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        completeMovingName           = imageData["movingFolder"]    + imageData["movingName"]
        # parameters
        params                       = imageData["paramFileRigid"]
        # output folder
        outputFolder                 = imageData["registeredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        # print ("     Rigid registration")
        # os.path.abspath because working directory is where elastix is in pykneer, so images need whole path, not only relative
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeMovingName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder)]

        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["registeredSubFolder"] + "result.0.mha"):
            print("-------------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.rigid()")
            print("-------------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["registeredSubFolder"] + "result.0.mha",
                      imageData["registeredSubFolder"] + imageData[anatomy + "rigidName"])
            os.rename(imageData["registeredSubFolder"] + "TransformParameters.0.txt",
                      imageData["registeredSubFolder"] + imageData[anatomy + "rigidTransfName"])


    def similarity(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"] + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        completeMovingName           = imageData["registeredSubFolder"] + imageData[anatomy + "rigidName"]
        # parameters
        params                       = imageData["paramFileSimilarity"]
        # output folder
        outputFolder                 = imageData["registeredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        #print ("     Similarity registration")
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeMovingName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["registeredSubFolder"] + "result.0.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.similarity()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["registeredSubFolder"] + "result.0.mha",
                      imageData["registeredSubFolder"] + imageData[anatomy + "similarityName"])
            os.rename(imageData["registeredSubFolder"] + "TransformParameters.0.txt",
                      imageData["registeredSubFolder"] + imageData[anatomy + "similarityTransfName"])


    def spline(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"] + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        if imageData["registrationType"] == "newsubject" or imageData["registrationType"] == "multimodal":
            completeMovingName       = imageData["registeredSubFolder"] + imageData[anatomy + "similarityName"]
        elif imageData["registrationType"] == "longitudinal":
            completeMovingName       = imageData["registeredSubFolder"] + imageData[anatomy + "rigidName"]
        # parameters
        params                       = imageData["paramFileSpline"]
        # output folder
        outputFolder                 = imageData["registeredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        #print ("     Spline registration")
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeMovingName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["registeredSubFolder"] + "result.0.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.spline()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["registeredSubFolder"] + "result.0.mha",
                      imageData["registeredSubFolder"] + imageData[anatomy + "splineName"])
            os.rename(imageData["registeredSubFolder"] + "TransformParameters.0.txt",
                      imageData["registeredSubFolder"] + imageData[anatomy + "splineTransfName"])


    def irigid(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"] + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        # parameters
        params                       = imageData["iparamFileRigid"]
        # tranformation
        transformation               = imageData["registeredSubFolder"] + imageData[anatomy + "rigidTransfName"]
        # output folder
        outputFolder                 = imageData["iregisteredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        #print ("     Inverting rigid transformation")
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeReferenceName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder),
                                    "-t0",    os.path.abspath(transformation)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.irigid()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt",
                  imageData["iregisteredSubFolder"] + imageData[anatomy + "iRigidTransfName"])


    def isimilarity(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"] + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        # parameters
        params                       = imageData["iparamFileSimilarity"]
         # tranformation
        transformation               = imageData["registeredSubFolder"] + imageData[anatomy + "similarityTransfName"]
        # output folder
        outputFolder                 = imageData["iregisteredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        #print ("     Inverting similarity transformation")
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeReferenceName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder),
                                    "-t0",    os.path.abspath(transformation)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.isimilarity()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt",
                      imageData["iregisteredSubFolder"] + imageData[anatomy + "iSimilarityTransfName"])


    def ispline(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"] + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        # parameters
        params                       = imageData["iparamFileSpline"]
        # tranformation
        transformation               = imageData["registeredSubFolder"] + imageData[anatomy + "splineTransfName"]
        # output folder
        outputFolder                 = imageData["iregisteredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        #print ("     Inverting spline transformation")
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeReferenceName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder),
                                    "-t0",    os.path.abspath(transformation)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.ispline()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt",
                      imageData["iregisteredSubFolder"] + imageData[anatomy + "iSplineTransfName"])


    def trigid(self, imageData):

        # anatomy
        anatomy                 = imageData["currentAnatomy"]
        # input mask name
        if imageData["registrationType"] == "newsubject":
            maskToWarp          = imageData["iregisteredSubFolder"] + imageData[anatomy+"mSimilarityName"]
        elif imageData["registrationType"] == "multimodal":
            maskToWarp          = imageData["referenceFolder"] + imageData[anatomy + "levelSetsMaskFileName"]
        elif imageData["registrationType"] == "longitudinal":
            maskToWarp          = imageData["iregisteredSubFolder"] + imageData[anatomy+"mSplineName"]

        # tranformation
        transformation          = imageData["iregisteredSubFolder"] + imageData[anatomy + "mRigidTransfName"]
        # output folder
        outputFolder            = imageData["iregisteredSubFolder"]
        # transformix path
        completeTransformixPath = imageData["completeTransformixPath"]

        # execute transformation
        #print ("     Rigid warping")
        cmd = [completeTransformixPath, "-in",  os.path.abspath(maskToWarp),
                                        "-tp",  os.path.abspath(transformation),
                                        "-out", os.path.abspath(outputFolder)]
        elastixPath                  = imageData["elastixFolder"]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "result.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.trigid()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "result.mha",
                      imageData["iregisteredSubFolder"] + imageData[anatomy + "mRigidName"])


    def tsimilarity(self, imageData):

        # anatomy
        anatomy                 = imageData["currentAnatomy"]
        # input mask name
        maskToWarp              = imageData["iregisteredSubFolder"] + imageData[anatomy+"mSplineName"]
        # tranformation
        transformation          = imageData["iregisteredSubFolder"] + imageData[anatomy + "mSimilarityTransfName"]
        # output folder
        outputFolder            = imageData["iregisteredSubFolder"]
        # transformix path
        elastixPath             = imageData["elastixFolder"]
        completeTransformixPath = imageData["completeTransformixPath"]

        # execute transformation
        #print ("     Similarity warping")
        cmd = [completeTransformixPath, "-in",  os.path.abspath(maskToWarp),
                                        "-tp",  os.path.abspath(transformation),
                                        "-out", os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "result.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.tsimilarity()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "result.mha",
                      imageData["iregisteredSubFolder"] + imageData[anatomy+"mSimilarityName"])


    def tspline(self, imageData):

        # anatomy
        anatomy                 = imageData["currentAnatomy"]
        # input mask name
        maskToWarp              = imageData["referenceFolder"] + imageData[anatomy + "levelSetsMaskFileName"]
        # tranformation
        transformation          = imageData["iregisteredSubFolder"] + imageData[anatomy + "mSplineTransfName"]
        # output folder
        outputFolder            = imageData["iregisteredSubFolder"]
        # transformix path
        elastixPath             = imageData["elastixFolder"]
        completeTransformixPath = imageData["completeTransformixPath"]

        # execute transformation
        #print ("     Spline warping")
        cmd = [completeTransformixPath, "-in",  os.path.abspath(maskToWarp),
                                        "-tp",  os.path.abspath(transformation),
                                        "-out", os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output name
        if not os.path.exists(imageData["iregisteredSubFolder"] + "result.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.tspline()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "result.mha",
                  imageData["iregisteredSubFolder"] + imageData[anatomy+"mSplineName"])


    def vfspline(self, imageData):

        # transformation
        bone                    = imageData["bone"]
        transformation          = imageData["registeredSubFolder"] + imageData[bone + "similarityTransfName"]
        # output folder for  "deformationField.mha" (different from folder for "vectorFieldName")
        # (needing 2 folders for //isation. "deformationField.mha" gets overwritten when more produced by parallel processes)
        outputFolder            = imageData["registeredSubFolder"]
        # transformix path
        elastixPath             = imageData["elastixFolder"]
        completeTransformixPath = imageData["completeTransformixPath"]

        # get vector field
        cmd = [completeTransformixPath, "-def", "all",
                                        "-tp",  os.path.abspath(transformation),
                                        "-out", os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output name
        if not os.path.exists(imageData["registeredSubFolder"] + "deformationField.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in bone.vfspline()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["registeredSubFolder"] + "deformationField.mha",
                      imageData["registeredFolder"]    + imageData["vectorFieldName"])




# ----------------------------------------------------------------------------------------------------------------------------------------
# registration class to segment cartilage
class cartilage (registration):

    def rigid(self, imageData):
        pass

    def similarity(self, imageData):
        pass

    def spline(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        bone                         = imageData["bone"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"]     + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"]     + imageData[anatomy + "dilMaskFileName"]
        if imageData["registrationType"] == "newsubject" or imageData["registrationType"] == "multimodal":
            completeMovingName       = imageData["registeredSubFolder"] + imageData[bone + "similarityName"]
        elif imageData["registrationType"] == "longitudinal":
            completeMovingName       = imageData["registeredSubFolder"] + imageData[bone + "rigidName"]
        # parameters
        params                       = imageData["paramFileSpline"]
        # output folder
        outputFolder                 = imageData["registeredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        #print ("     Spline registration")
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeMovingName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["registeredSubFolder"] + "result.0.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in cartilage.spline()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["registeredSubFolder"] + "result.0.mha",
                      imageData["registeredSubFolder"] + imageData[anatomy + "splineName"])
            os.rename(imageData["registeredSubFolder"] + "TransformParameters.0.txt",
                      imageData["registeredSubFolder"] + imageData[anatomy + "splineTransfName"])


    def irigid(self, imageData):
        pass

    def isimilarity(self, imageData):
        pass

    def ispline(self, imageData):

        # anatomy
        anatomy                      = imageData["currentAnatomy"]
        # input image names
        completeReferenceName        = imageData["referenceFolder"] + imageData["referenceName"]
        completeReferenceMaskDilName = imageData["referenceFolder"] + imageData[anatomy + "dilMaskFileName"]
        # parameters
        params                       = imageData["iparamFileSpline"]
        # tranformation
        transformation               = imageData["registeredSubFolder"] + imageData[anatomy + "splineTransfName"]
        # output folder
        outputFolder                 = imageData["iregisteredSubFolder"]
        # elastix path
        elastixPath                  = imageData["elastixFolder"]
        completeElastixPath          = imageData["completeElastixPath"]

        # execute registration
        #print ("     Inverting spline transformation")
        cmd = [completeElastixPath, "-f",     os.path.abspath(completeReferenceName),
                                    "-fMask", os.path.abspath(completeReferenceMaskDilName),
                                    "-m",     os.path.abspath(completeReferenceName),
                                    "-p",     os.path.abspath(params),
                                    "-out",   os.path.abspath(outputFolder),
                                    "-t0",    os.path.abspath(transformation)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in cartilage.ispline()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "TransformParameters.0.txt",
                      imageData["iregisteredSubFolder"] + imageData[anatomy + "iSplineTransfName"])


    def trigid(self, imageData):

        # anatomy
        anatomy                 = imageData["currentAnatomy"]
        bone                    = imageData["bone"]
        # input mask name
        if imageData["registrationType"] == "newsubject":
            maskToWarp          = imageData["iregisteredSubFolder"] + imageData[anatomy+"mSimilarityName"]
        elif imageData["registrationType"] == "multimodal":
            maskToWarp          = imageData["referenceFolder"]      + imageData[anatomy + "levelSetsMaskFileName"]
        elif imageData["registrationType"] == "longitudinal":
            maskToWarp          = imageData["iregisteredSubFolder"] + imageData[anatomy+"mSplineName"]
        # tranformation
        transformation          = imageData["iregisteredSubFolder"] + imageData[bone + "mRigidTransfName"]
        # output folder
        outputFolder            = imageData["iregisteredSubFolder"]
        # transformix path
        elastixPath             = imageData["elastixFolder"]
        completeTransformixPath = imageData["completeTransformixPath"]

        # execute transformation
        #print ("     Rigid warping")
        cmd = [completeTransformixPath, "-in",  os.path.abspath(maskToWarp),
                                        "-tp",  os.path.abspath(transformation),
                                        "-out", os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "result.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in cartilage.trigid()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "result.mha",
                      imageData["iregisteredSubFolder"] + imageData[anatomy + "mRigidName"])


    def tsimilarity(self, imageData):

        # anatomy
        anatomy                 = imageData["currentAnatomy"]
        bone                    = imageData["bone"]
        # input mask name
        maskToWarp              = imageData["iregisteredSubFolder"] + imageData[anatomy+"mSplineName"]
        # tranformation
        transformation          = imageData["iregisteredSubFolder"] + imageData[bone + "mSimilarityTransfName"]
        # output folder
        outputFolder            = imageData["iregisteredSubFolder"]
        # transformix path
        elastixPath             = imageData["elastixFolder"]
        completeTransformixPath = imageData["completeTransformixPath"]

        # execute transformation
        #print ("     Similarity warping")
        cmd = [completeTransformixPath, "-in",  os.path.abspath(maskToWarp),
                                        "-tp",  os.path.abspath(transformation),
                                        "-out", os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "result.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in cartilage.tsimilarity()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "result.mha",
                  imageData["iregisteredSubFolder"] + imageData[anatomy+"mSimilarityName"])


    def tspline(self, imageData):

        # anatomy
        anatomy                 = imageData["currentAnatomy"]
        # input mask name
        maskToWarp              = imageData["referenceFolder"] + imageData[anatomy + "levelSetsMaskFileName"]
        # tranformation
        transformation          = imageData["iregisteredSubFolder"] + imageData[anatomy + "mSplineTransfName"]
        # output folder
        outputFolder            = imageData["iregisteredSubFolder"]
        # transformix path
        elastixPath             = imageData["elastixFolder"]
        completeTransformixPath = imageData["completeTransformixPath"]

        # execute transformation
        #print ("     Spline warping")
        cmd = [completeTransformixPath, "-in",  os.path.abspath(maskToWarp),
                                        "-tp",  os.path.abspath(transformation),
                                        "-out", os.path.abspath(outputFolder)]
        subprocess.run(cmd, cwd=elastixPath)

        # change output names
        if not os.path.exists(imageData["iregisteredSubFolder"] + "result.mha"):
            print("----------------------------------------------------------------------------------------")
            print("ERROR: No output created in cartilage.tspline()")
            print("----------------------------------------------------------------------------------------")
            return
        else:
            os.rename(imageData["iregisteredSubFolder"] + "result.mha",
                  imageData["iregisteredSubFolder"] + imageData[anatomy+"mSplineName"])


    def vfspline(self):
        pass

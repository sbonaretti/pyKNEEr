# Serena Bonaretti, 2018

import numpy as np
import SimpleITK as sitk
import itk



def print_image_info(img):

    print ("Size:      %d   %d   %d"   % (img.GetSize   ()[0], img.GetSize   ()[1], img.GetSize   ()[2]))
    print ("Spacing:   %.2f %.2f %.2f" % (img.GetSpacing()[0], img.GetSpacing()[1], img.GetSpacing()[2]))
    print ("Origin:    %.2f %.2f %.2f" % (img.GetOrigin ()[0], img.GetOrigin ()[1], img.GetOrigin ()[2]))
    print ("Direction: \n%.2f %.2f %.2f \n%.2f %.2f %.2f \n%.2f %.2f %.2f" %     \
           (img.GetDirection()[0], img.GetDirection()[1], img.GetDirection()[2], \
            img.GetDirection()[3], img.GetDirection()[4], img.GetDirection()[5], \
            img.GetDirection()[6], img.GetDirection()[7], img.GetDirection()[8]))


def print_image_info_ITK(img_itk):

    print("Size:    %d %d %d"       % (img_itk.GetLargestPossibleRegion().GetSize()[0], img_itk.GetLargestPossibleRegion().GetSize()[1], img_itk.GetLargestPossibleRegion().GetSize()[2]))
    print("Spacing: %.2f %.2f %.2f" % (img_itk.GetSpacing()[0], img_itk.GetSpacing()[1], img_itk.GetSpacing()[2]))
    print("Origin:  %.2f %.2f %.2f" % (img_itk.GetOrigin ()[0], img_itk.GetOrigin ()[1], img_itk.GetOrigin ()[2]))
    print("Direction:")
    for i in range(0,3):
        print (    "%.2f %.2f %.2f" % (img_itk.GetDirection().GetVnlMatrix().get(i,0), img_itk.GetDirection().GetVnlMatrix().get(i,1), img_itk.GetDirection().GetVnlMatrix().get(i,2)))


def read_dicom_stack(imageFolder):

    # read dicom series
    reader     = sitk.ImageSeriesReader()
    dicomNames = reader.GetGDCMSeriesFileNames(imageFolder)
    reader.SetFileNames(dicomNames)
    img        = reader.Execute()

    return img


def read_dicom_header(imageFolder):

    # get file names of the dicom slices in the folder
    series_IDs        = sitk.ImageSeriesReader.GetGDCMSeriesIDs(imageFolder)
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(imageFolder, series_IDs[0])

    # read the header of one slice (not selecting a specific slice)
    reader = sitk.ImageFileReader()
    #reader.LoadPrivateTagsOn()
    reader.SetFileName(series_file_names[0])
    img = reader.Execute()

    # get metaDataKeys and metaData
    metaDataKeys = img.GetMetaDataKeys()
    metaData     = []
    for k in range (0,len(metaDataKeys)):
        metaData.append(img.GetMetaData( img.GetMetaDataKeys()[k]))

    return metaDataKeys, metaData


def orientation_to_rai(img):
    
    # this function is implemented using ITK since SimpleITK has not implemented the filter "OrientImageFilter" yet
    # the ITK orientation system is from this blog post: https://itk.org/pipermail/insight-users/2017-May/054606.html

    # change image name
    img_sitk = img

    # get characteristics of simpleITK image
    sizeIn_sitk      = img_sitk.GetSize()
    spacingIn_sitk   = img_sitk.GetSpacing()
    originIn_sitk    = img_sitk.GetOrigin()
    directionIn_sitk = img_sitk.GetDirection()

    # allocate ITK image (type and size)
    Dimension   = 3
    PixelType   = itk.F
    ImageTypeIn = itk.Image[PixelType, Dimension]
    img_itk = ImageTypeIn.New()
    sizeIn_itk = itk.Size[Dimension]()
    for i in range (0,Dimension):
        sizeIn_itk[i] = sizeIn_sitk[i]
    region = itk.ImageRegion[Dimension]()
    region.SetSize(sizeIn_itk)
    img_itk.SetRegions(region)
    img_itk.Allocate()

    # pass image from simpleITK to numpy
    img_py  = sitk.GetArrayFromImage(img_sitk)

    # pass image from numpy to ITK
    img_itk = itk.GetImageViewFromArray(img_py)

    # pass characteristics from simpleITK image to ITK image (except size, assigned in allocation)
    spacingIn_itk = itk.Vector[itk.F, Dimension]()
    for i in range (0,Dimension):
        spacingIn_itk[i] = spacingIn_sitk[i]
    img_itk.SetSpacing(spacingIn_itk)

    originIn_itk  = itk.Point[itk.F, Dimension]()
    for i in range (0,Dimension):
        originIn_itk[i]  = originIn_sitk[i]
    img_itk.SetOrigin(originIn_itk)

    directionIn_itk = itk.Matrix[itk.F,3,3]()
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(0,0,directionIn_sitk[0]) # r,c,value
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(0,1,directionIn_sitk[1])
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(0,2,directionIn_sitk[2])
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(1,0,directionIn_sitk[3]) # r,c,value
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(1,1,directionIn_sitk[4])
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(1,2,directionIn_sitk[5])
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(2,0,directionIn_sitk[6]) # r,c,value
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(2,1,directionIn_sitk[7])
    directionIn_itk = img_itk.GetDirection().GetVnlMatrix().set(2,2,directionIn_sitk[8])

    # make sure image is float for the orientation filter (GetImageViewFromArray sets it to unsigned char)
    ImageTypeIn_afterPy = type(img_itk)
    ImageTypeOut        = itk.Image[itk.F, 3]
    CastFilterType      = itk.CastImageFilter[ImageTypeIn_afterPy, ImageTypeOut]
    castFilter          = CastFilterType.New()
    castFilter.SetInput(img_itk)
    castFilter.Update()
    img_itk             = castFilter.GetOutput()

    # define ITK orientation system  (from the blog post: https://itk.org/pipermail/insight-users/2017-May/054606.html)
    ITK_COORDINATE_UNKNOWN   = 0
    ITK_COORDINATE_Right     = 2
    ITK_COORDINATE_Left      = 3
    ITK_COORDINATE_Posterior = 4
    ITK_COORDINATE_Anterior  = 5
    ITK_COORDINATE_Inferior  = 8
    ITK_COORDINATE_Superior  = 9
    ITK_COORDINATE_PrimaryMinor   = 0
    ITK_COORDINATE_SecondaryMinor = 8
    ITK_COORDINATE_TertiaryMinor  = 16
    ITK_COORDINATE_ORIENTATION_RAI = ( ITK_COORDINATE_Right    << ITK_COORDINATE_PrimaryMinor ) \
                                   + ( ITK_COORDINATE_Anterior << ITK_COORDINATE_SecondaryMinor ) \
                                   + ( ITK_COORDINATE_Inferior << ITK_COORDINATE_TertiaryMinor )

    # change orientation to RAI
    OrientType = itk.OrientImageFilter[ImageTypeOut,ImageTypeOut]
    filter     = OrientType.New()
    filter.UseImageDirectionOn()
    filter.SetDesiredCoordinateOrientation(ITK_COORDINATE_ORIENTATION_RAI)
    filter.SetInput(img_itk)
    filter.Update()
    img_itk    = filter.GetOutput()

    # get characteristics of ITK image
    spacingOut_itk   = img_itk.GetSpacing()
    originOut_itk    = img_itk.GetOrigin()

    # pass image from itk to numpy
    img_py = itk.GetArrayViewFromImage(img_itk)

    # pass image from numpy to simpleitk
    img = sitk.GetImageFromArray(img_py)

    # pass characteristics from ITK image to simpleITK image (except size, implicitely passed)
    spacing = []
    for i in range (0, Dimension):
        spacing.append(spacingOut_itk[i])
    img.SetSpacing(spacing)

    origin = []
    for i in range (0, Dimension):
        origin.append(originOut_itk[i])
    img.SetOrigin(origin)

    direction = []
    direction.append(1.0)
    direction.append(0.0)
    direction.append(0.0)
    direction.append(0.0)
    direction.append(1.0)
    direction.append(0.0)
    direction.append(0.0)
    direction.append(0.0)
    direction.append(1.0)
    img.SetDirection(direction)

    return img


def flip_rl(img, flag):

    # flip the image
    flipDirection = [True, False, False]
    img = sitk.Flip(img, flipDirection)

    if flag == True:
        # put direction back to identity (direction(0,0) becomes -1 after flip)
        direction = []
        direction.append(1.0)
        direction.append(0.0)
        direction.append(0.0)
        direction.append(0.0)
        direction.append(1.0)
        direction.append(0.0)
        direction.append(0.0)
        direction.append(0.0)
        direction.append(1.0)
        img.SetDirection(direction)

    return img


def origin_to_zero(img):

    # set image origin to (0,0,0)
    newOrigin = [0,0,0]
    img.SetOrigin(newOrigin)

    return img


def field_correction(img):

    # Parameters and pipeline from ksrt by Shan-Niethammer, UNC (translated to python)

    # creating Otsu mask
    otsu = sitk.OtsuThresholdImageFilter()
    otsu.SetInsideValue(0)
    otsu.SetOutsideValue(1)
    otsu.SetNumberOfHistogramBins(200)
    mask = otsu.Execute(img)

    # correct field
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    corrector.SetMaskLabel(1)
    corrector.SetNumberOfHistogramBins(600)
    corrector.SetWienerFilterNoise(10)
    corrector.SetBiasFieldFullWidthAtHalfMaximum(15)
    corrector.SetMaximumNumberOfIterations([50])
    corrector.SetConvergenceThreshold(0.001)
    img = corrector.Execute(img, mask)

    return img


def rescale_to_range(img):

    # Code from ksrt by Shan-Niethammer, UNC (translated to python)
    # The algorithm assumes that the image has only positive values

    # set arbitrary variables
    newMaxValue  = 100
    ratio        = 0.0
    numOutliers  = 0
    numOfIter    = 0
    maxNumOfIter = 100
    thresh       = 0.001

    # get image characteristics for numpy-SimpleITK conversion
    spacing   = img.GetSpacing()
    origin    = img.GetOrigin ()
    direction = img.GetDirection()

    # convert image from SimpleITK to numpy
    img_py = sitk.GetArrayFromImage(img)

    # get image max and min values
    maxValue = np.amax(img_py)
    minValue = np.amin(img_py)

    # set other variables
    cutValue = maxValue
    numTotal = img.GetNumberOfPixels()

    # calculate cutValue
    while ((ratio < thresh) and (numOfIter < maxNumOfIter)):

        numOfIter   = numOfIter + 1
        numOutliers = 0

        # calculate cutValue
        cutValue    = (cutValue + minValue) * 0.95

        # get the number of voxels that are above the cutValue (outliers)
        outliers    = img_py[img_py > cutValue]
        numOutliers = numOutliers + len(outliers)

        # calculate the new proportion of outlier voxels over the total number of voxles
        ratio = numOutliers / numTotal

    # assign new voxel values
    img_py[img_py < cutValue] = img_py[img_py < cutValue] / cutValue * newMaxValue
    img_py[img_py > cutValue] = newMaxValue

    # back to SimpleITK
    img = sitk.GetImageFromArray (img_py)
    img.SetSpacing  (spacing)
    img.SetOrigin   (origin)
    img.SetDirection(direction)

    return img


def edge_preserving_smoothing(img):

    # Parameters from ksrt by Shan-Niethammer, UNC 

    # smoothing using CurvatureAnisotropicDiffusionImageFilter
    filter = sitk.CurvatureAnisotropicDiffusionImageFilter()
    filter.SetNumberOfIterations(5);
    filter.SetTimeStep(0.019);
    filter.SetConductanceParameter(10);
    img = filter.Execute(img);

    return img


def dilate_mask(mask,  radius):

    # dilate reference binary mask 
    mask    = sitk.Cast(mask,sitk.sitkInt16) # make sure that input of BinaryDilate is int
    maskDil = sitk.BinaryDilate(mask,radius)
    
    return maskDil


def binary2levelset(mask):

    # transform reference binary mask to levelset mask 
    mask = sitk.Cast(mask,sitk.sitkInt16) # make sure that input of AntiAliasBinary is int
    maskLS = sitk.AntiAliasBinary(mask)
    
    return maskLS


def levelset2binary(maskLSitk):

    # transform moving level set mask to binary mask 
    maskLSnp  = sitk.GetArrayFromImage(maskLSitk)
    maskBnp   = maskLSnp > 0.0      # bool
    maskBnp   = maskBnp.astype(int) #int
    maskBitk  = sitk.GetImageFromArray(maskBnp)
    maskBitk.SetSpacing  (maskLSitk.GetSpacing())
    maskBitk.SetOrigin   (maskLSitk.GetOrigin())
    maskBitk.SetDirection(maskLSitk.GetDirection())

    return maskBitk


def overlap_measures(mask1, mask2):
    
    # make sure the masks have the same type
    mask1 = sitk.Cast(mask1,sitk.sitkInt8) 
    mask2 = sitk.Cast(mask2,sitk.sitkInt8) 
    
    # makes sure that the masks have spacing approximated at the same decimal 
    # (error: Inputs do not occupy the same physical space)
    spacing1    = mask1.GetSpacing() # it's a tuple
    spacing1    = list(spacing1)
    spacing1[0] = round(spacing1[0], 4)
    spacing1[1] = round(spacing1[1], 4)
    spacing1[2] = round(spacing1[2], 4)
    mask1.SetSpacing(spacing1)
    spacing2    = mask2.GetSpacing() # it's a tuple
    spacing2    = list(spacing2)
    spacing2[0] = round(spacing2[0], 4)
    spacing2[1] = round(spacing2[1], 4)
    spacing2[2] = round(spacing2[2], 4)
    mask2.SetSpacing(spacing2)
    
    # calculate dice coefficient, jaccard coefficient, and volume similarity
    filter    = sitk.LabelOverlapMeasuresImageFilter()
    filter.Execute(mask1, mask2)
    diceCoeff = filter.GetDiceCoefficient()
    jaccCoeff = filter.GetJaccardCoefficient()
    volSimil  = filter.GetVolumeSimilarity ()
    
    return diceCoeff, jaccCoeff, volSimil
    

def distance_measure(mask1, mask2):
    
    # calculate Hausdorff distance
    filter            = sitk.HausdorffDistanceImageFilter()
    filter.Execute(mask1, mask2)
    hausdorffDistance = filter.GetHausdorffDistance()
    
    return hausdorffDistance
    
    
    
    
    
    
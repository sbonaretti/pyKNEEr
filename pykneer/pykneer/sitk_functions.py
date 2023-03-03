# Serena Bonaretti, 2018

"""
Mix of image processing functions mainly using SimpleITK and ITK:
    - print_image_info
    - print_image_info_ITK
    - read_dicom_stack
    - read_dicom_header
    - orientation_to_rai
    - flip_rl
    - origin_to_zero
    - field_correction
    - rescale_to_range
    - edge_preserving_smoothing
    - dilate_mask
    - binary2levelset
    - levelset2binary
    - overlap_measures
    - distance_measure
    - surface_distance_measures
"""

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


def read_dicom_stack(image_folder):

    # read dicom series
    reader      = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(image_folder)
    reader.SetFileNames(dicom_names)
    img         = reader.Execute()

    return img


def read_dicom_header(image_folder):

    # get file names of the dicom slices in the folder
    series_IDs        = sitk.ImageSeriesReader.GetGDCMSeriesIDs(image_folder)
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(image_folder, series_IDs[0])

    # read the header of one slice (not selecting a specific slice)
    reader = sitk.ImageFileReader()
    #reader.LoadPrivateTagsOn()
    reader.SetFileName(series_file_names[0])
    img = reader.Execute()

    # get metaDataKeys and metaData
    meta_data_keys = img.GetMetaDataKeys()
    meta_data     = []
    for k in range (0,len(meta_data_keys)):
        meta_data.append(img.GetMetaData( img.GetMetaDataKeys()[k]))

    return meta_data_keys, meta_data



def orientation_to_rai(img):

    # this function is implemented using ITK since SimpleITK has not implemented the filter "OrientImageFilter" yet
    # the ITK orientation system is from this blog post: https://itk.org/pipermail/insight-users/2017-May/054606.html
    # comparison ITK - simpleITK filters: https://itk.org/SimpleITKDoxygen/html/Filter_Coverage.html
    # see also: https://github.com/fedorov/lidc-idri-conversion/blob/master/seg/seg_converter.py

    # change image name
    img_sitk = img

    # get characteristics of simpleITK image
    size_in_sitk      = img_sitk.GetSize()
    spacing_in_sitk   = img_sitk.GetSpacing()
    origin_in_sitk    = img_sitk.GetOrigin()
    direction_in_sitk = img_sitk.GetDirection()

    # allocate ITK image (type and size)
    Dimension   = 3
    PixelType   = itk.F
    ImageTypeIn = itk.Image[PixelType, Dimension]
    img_itk = ImageTypeIn.New()
    sizeIn_itk = itk.Size[Dimension]()
    for i in range (0,Dimension):
        sizeIn_itk[i] = size_in_sitk[i]
    region = itk.ImageRegion[Dimension]()
    region.SetSize(sizeIn_itk)
    img_itk.SetRegions(region)
    img_itk.Allocate()

    # pass image from simpleITK to numpy
    img_py  = sitk.GetArrayFromImage(img_sitk)

    # pass image from numpy to ITK
    img_itk = itk.GetImageViewFromArray(img_py)

    # pass characteristics from simpleITK image to ITK image (except size, assigned in allocation)
    spacing_in_itk = itk.Vector[itk.F, Dimension]()
    for i in range (0,Dimension):
        spacing_in_itk[i] = spacing_in_sitk[i]
    img_itk.SetSpacing(spacing_in_itk)

    origin_in_itk  = itk.Point[itk.F, Dimension]()
    for i in range (0,Dimension):
        origin_in_itk[i]  = origin_in_sitk[i]
    img_itk.SetOrigin(origin_in_itk)

    # old way of assigning direction (until ITK 4.13)
#     direction_in_itk = itk.Matrix[itk.F,3,3]()
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(0,0,direction_in_sitk[0]) # r,c,value
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(0,1,direction_in_sitk[1])
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(0,2,direction_in_sitk[2])
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(1,0,direction_in_sitk[3]) # r,c,value
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(1,1,direction_in_sitk[4])
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(1,2,direction_in_sitk[5])
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(2,0,direction_in_sitk[6]) # r,c,value
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(2,1,direction_in_sitk[7])
#     direction_in_itk = img_itk.GetDirection().GetVnlMatrix().set(2,2,direction_in_sitk[8])

    direction_in_itk = np.eye(3)
    direction_in_itk[0][0] = direction_in_sitk[0]
    direction_in_itk[0][1] = direction_in_sitk[1]
    direction_in_itk[0][2] = direction_in_sitk[2]
    direction_in_itk[1][0] = direction_in_sitk[3]
    direction_in_itk[1][1] = direction_in_sitk[4]
    direction_in_itk[1][2] = direction_in_sitk[5]
    direction_in_itk[2][0] = direction_in_sitk[6]
    direction_in_itk[2][1] = direction_in_sitk[7]
    direction_in_itk[2][2] = direction_in_sitk[8]
    img_itk.SetDirection(itk.matrix_from_array(direction_in_itk))

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
    spacing_out_itk   = img_itk.GetSpacing()
    origin_out_itk    = img_itk.GetOrigin()

    # pass image from itk to numpy
    img_py = itk.GetArrayViewFromImage(img_itk)

    # pass image from numpy to simpleitk
    img = sitk.GetImageFromArray(img_py)

    # pass characteristics from ITK image to simpleITK image (except size, implicitely passed)
    spacing = []
    for i in range (0, Dimension):
        spacing.append(spacing_out_itk[i])
    img.SetSpacing(spacing)

    origin = []
    for i in range (0, Dimension):
        origin.append(origin_out_itk[i])
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
    flip_direction = [True, False, False]
    img = sitk.Flip(img, flip_direction)

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
    new_origin = [0,0,0]
    img.SetOrigin(new_origin)

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
    new_max_value = 100
    ratio         = 0.0
    num_outliers  = 0
    num_iter      = 0
    max_num_iter  = 100
    thresh        = 0.001

    # get image characteristics for numpy-SimpleITK conversion
    spacing   = img.GetSpacing()
    origin    = img.GetOrigin ()
    direction = img.GetDirection()

    # convert image from SimpleITK to numpy
    img_py = sitk.GetArrayFromImage(img)

    # get image max and min values
    max_value = np.amax(img_py)
    min_value = np.amin(img_py)

    # set other variables
    cut_value = max_value
    num_total = img.GetNumberOfPixels()

    # calculate cut_value
    while ((ratio < thresh) and (num_iter < max_num_iter)):

        num_iter     = num_iter + 1
        num_outliers = 0

        # calculate cut_value
        cut_value    = (cut_value + min_value) * 0.95

        # get the number of voxels that are above the cut_value (outliers)
        outliers    = img_py[img_py > cut_value]
        num_outliers = num_outliers + len(outliers)

        # calculate the new proportion of outlier voxels over the total number of voxles
        ratio = num_outliers / num_total

    # assign new voxel values
    img_py[img_py < cut_value] = img_py[img_py < cut_value] / cut_value * new_max_value
    img_py[img_py > cut_value] = new_max_value

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
    mask     = sitk.Cast(mask,sitk.sitkUInt16) # make sure that input of BinaryDilate is int
    print (mask.GetPixelIDTypeAsString())
    # mask_dil = sitk.BinaryDilate(mask,radius) # this does not work anymore, not sure why - changed to BinaryDilateImageFilter in version 0.6
    # mask_dil = sitk.BinaryDilate(mask,3)
    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelRadius(radius)
    mask_dil = dilate_filter.Execute(mask)

    return mask_dil


def binary2levelset(mask):

    # transform reference binary mask to levelset mask
    mask    = sitk.Cast(mask,sitk.sitkInt16) # make sure that input of AntiAliasBinary is int
    mask_LS = sitk.AntiAliasBinary(mask)

    return mask_LS


def levelset2binary(mask_LS_itk):

    # transform moving level set mask to binary mask
    mask_LS_np  = sitk.GetArrayFromImage(mask_LS_itk)
    mask_B_np   = mask_LS_np > 0.0      # bool
    mask_B_np   = mask_B_np.astype(int) #int
    mask_B_itk  = sitk.GetImageFromArray(mask_B_np)
    mask_B_itk.SetSpacing  (mask_LS_itk.GetSpacing())
    mask_B_itk.SetOrigin   (mask_LS_itk.GetOrigin())
    mask_B_itk.SetDirection(mask_LS_itk.GetDirection())

    return mask_B_itk


def overlap_measures(mask_1, mask_2):

    # make sure the masks have the same type
    mask_1 = sitk.Cast(mask_1,sitk.sitkInt8)
    mask_2 = sitk.Cast(mask_2,sitk.sitkInt8)

    # makes sure that the masks have spacing approximated at the same decimal
    # (error: Inputs do not occupy the same physical space)
    spacing_1    = mask_1.GetSpacing() # it's a tuple
    spacing_1    = list(spacing_1)
    spacing_1[0] = round(spacing_1[0], 4)
    spacing_1[1] = round(spacing_1[1], 4)
    spacing_1[2] = round(spacing_1[2], 4)
    mask_1.SetSpacing(spacing_1)
    spacing_2    = mask_2.GetSpacing() # it's a tuple
    spacing_2    = list(spacing_2)
    spacing_2[0] = round(spacing_2[0], 4)
    spacing_2[1] = round(spacing_2[1], 4)
    spacing_2[2] = round(spacing_2[2], 4)
    mask_2.SetSpacing(spacing_2)

    # calculate dice coefficient, jaccard coefficient, and volume similarity
    filter    = sitk.LabelOverlapMeasuresImageFilter()
    filter.Execute(mask_1, mask_2)
    dice_coeff = filter.GetDiceCoefficient()
    jacc_coeff = filter.GetJaccardCoefficient()
    vol_simil  = filter.GetVolumeSimilarity ()

    return dice_coeff, jacc_coeff, vol_simil


def hausdorff_distance(mask_1, mask_2):

    # calculate Hausdorff distance
    filter            = sitk.HausdorffDistanceImageFilter()
    filter.Execute(mask_1, mask_2)
    hausdorff_distance = filter.GetHausdorffDistance()

    return hausdorff_distance


def mask_euclidean_distance(mask_1,mask_2):

    """
    Code modified from the SimpleITK example notebook: http://insightsoftwareconsortium.github.io/SimpleITK-Notebooks/Python_html/34_Segmentation_Evaluation.html
    Steps of the function:
    - In mask_1, calculate the distances between each point of the mask and the mask contour, to obtain a map of distances. Do the same for mask_2.
    - Multiply the map of distances of mask_1 and the contour of mask_2. This is an implicit way to extract the distances corresponding to the contour of mask_2 from mask_1 distance map. Do the same for mask_2.
    - Convert the masked maps to numpy
    - Extract all the points that are not zero, and pad the difference between this last array and the number of points with zeros (there could be some distances == 0)


    Input:
        mask_1 and mask 2: two masks to compare (usually one is a newly segmented mask and the other is a ground truth mask)
    Outputs:
        average surface distance, root mean square distance, and maximum distance
    """

    # Use the absolute values of the distance map to compute the surface distances (distance map sign, outside or inside
    # relationship, is irrelevant)
    mask_1_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(mask_1, squaredDistance=False))
    mask_1_surface = sitk.LabelContour(mask_1)

    # Symmetric surface distance measures
    mask_2_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(mask_2, squaredDistance=False))
    mask_2_surface = sitk.LabelContour(mask_2)

    # Multiply the binary surface segmentations with the distance maps. The resulting distance
    # maps contain non-zero values only on the surface (they can also contain zero on the surface)
    m1_to_m2_distance_map = mask_1_distance_map*sitk.Cast(mask_2_surface, sitk.sitkFloat32)
    m2_to_m1_distance_map = mask_2_distance_map*sitk.Cast(mask_1_surface, sitk.sitkFloat32)

    statistics_image_filter = sitk.StatisticsImageFilter()

    # Get the number of pixels in the mask_1 surface by counting all pixels that are 1
    statistics_image_filter.Execute(mask_1_surface)
    num_mask_1_surface_pixels = int(statistics_image_filter.GetSum())

    # Get the number of pixels in the mask_2 surface by counting all pixels that are 1
    statistics_image_filter.Execute(mask_2_surface)
    num_mask_2_surface_pixels = int(statistics_image_filter.GetSum())

    # Get all non-zero distances and then add zero distances if required.
    m1_to_m2_distance_map_arr = sitk.GetArrayViewFromImage(m1_to_m2_distance_map)
    m1_to_m2_distances = list(m1_to_m2_distance_map_arr[m1_to_m2_distance_map_arr!=0])
    m1_to_m2_distances = m1_to_m2_distances + list(np.zeros(num_mask_2_surface_pixels - len(m1_to_m2_distances)))

    m2_to_m1_distance_map_arr = sitk.GetArrayViewFromImage(m2_to_m1_distance_map)
    m2_to_m1_distances = list(m2_to_m1_distance_map_arr[m2_to_m1_distance_map_arr!=0])
    m2_to_m1_distances = m2_to_m1_distances + list(np.zeros(num_mask_1_surface_pixels - len(m2_to_m1_distances)))

    all_surface_distances = m1_to_m2_distances + m2_to_m1_distances

    # average surface distance
    mean_distance = np.mean(all_surface_distances)
    # maximum distance
    stddev_distance = np.std(all_surface_distances)

    return mean_distance, stddev_distance

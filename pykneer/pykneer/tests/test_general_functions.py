# Serena Bonaretti, 2019

"""
Module with general functions used in the other test_* modules
"""

import SimpleITK as sitk

def compare_txt_files (file_name_1, file_name_2): 
    """
    compares the content of two txt files
    """
    
    # get content of first file
    file_content_1=[]
    for line in open(file_name_1):
        file_content_1.append(line.rstrip("\n"))
    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content_1)):
        file_content_1[i] = file_content_1[i].rstrip()
    
    # get content of second file
    file_content_2=[]
    for line in open(file_name_2):
        file_content_2.append(line.rstrip("\n"))
    # clear empty spaces at the end of strings (if human enters spaces by mistake)
    for i in range(0,len(file_content_2)):
        file_content_2[i] = file_content_2[i].rstrip()
    
    # test if the two files are the same
    if (file_content_1 == file_content_2) == True:
        return 0
    else:
        return 1


def compare_images (file_name_1, file_name_2):
    """
    compares the content of two images
    when the sum of the difference of the two images is zero, the two images are identical
    """
    
    # read ground truth and corresponding current image
    img_1 = sitk.ReadImage(file_name_1)
    img_2 = sitk.ReadImage(file_name_1)
    # subtract
    difference = img_1 - img_2
    # convert to numpy
    difference = sitk.GetArrayFromImage(difference)
    # check if the difference is zero
    if sum(sum(sum(difference))) == 0:
        return 0
    else:
        return 1
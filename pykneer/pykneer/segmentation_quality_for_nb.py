# Serena Bonaretti, 2018

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import SimpleITK as sitk


# pyKNEER imports 
# ugly way to use relative vs. absolute imports when developing vs. when using package - cannot find a better way
if __package__ is None or __package__ == '':
    # uses current directory visibility
    import sitk_functions  as sitkf

else:
    # uses current package visibility
    from . import sitk_functions  as sitkf

# ---------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO CALCULATE VOLUME OVERLAP -------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------


def compute_overlap(all_image_data):

    dice_coeff = []
    jacc_coeff = []
    vol_simil  = []

    for i in range(0, len(all_image_data)):

        # get file names
        segmented_file_name    = all_image_data[i]["segmented_folder"]    + all_image_data[i]["segmented_name"]
        ground_truth_file_name = all_image_data[i]["ground_truth_folder"] + all_image_data[i]["ground_truth_name"]

        # read images
        segmented_mask    = sitk.ReadImage(segmented_file_name)
        ground_truth_mask = sitk.ReadImage(ground_truth_file_name)

        # measure overlap
        dice, jacc, vols = sitkf.overlap_measures(segmented_mask, ground_truth_mask)
        dice_coeff.append(dice)
        jacc_coeff.append(jacc)
        vol_simil.append(vols)

    return dice_coeff, jacc_coeff, vol_simil


def overlap_coeff_graph(all_image_data, dice_coeff, jacc_coeff, vol_simil):

    # figure size
    figure_width = 18
    figure_length   = 8
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks

    # create figure
    f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)

    # plot data
    x = np.arange(1, len(dice_coeff)+1, 1)
    l1, = ax1.plot(x,dice_coeff, "bo" )
    l2, = ax2.plot(x,jacc_coeff, "ro")
    l3, = ax3.plot(x,vol_simil,  "go")

    # set ticks and labels
    plt.xticks(x)
    image_names= []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["segmented_name"])
        image_names.append(image_root)
    ax3.set_xticklabels(image_names, rotation='vertical')

    ax1.set_ylabel('dice coefficient')
    ax2.set_ylabel('jaccard coefficient')
    ax3.set_ylabel('volume similarity')

    # annotate points
    for i in range(0, len(all_image_data)):
        ax1.annotate(round(dice_coeff[i],3), xy =(x[i], dice_coeff[i]), xytext=(x[i]+0.1, dice_coeff[i]))
    for i in range(0, len(all_image_data)):
        ax2.annotate(round(jacc_coeff[i],3), xy =(x[i], jacc_coeff[i]), xytext=(x[i]+0.1, jacc_coeff[i]))
    for i in range(0, len(all_image_data)):
        ax3.annotate(round(vol_simil[i],3),  xy =(x[i], vol_simil[i]),  xytext=(x[i]+0.1, vol_simil[i]))


    # title and legend
    ax1.set_title("Overlap coefficients")
    plt.legend([l1, l2, l3],["Dice coefficient", "Jaccard Coefficient", "Volume similarity"], loc="lower right")

    # show
    plt.show()


def overlap_coeff_table(all_image_data, dice_coeff, jacc_coeff, vol_simil, output_file_name):

    # extract image names
    image_names = []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["segmented_name"])
        image_names.append(image_root)
    #print (image_names)

    # create table
    table = pd.DataFrame(
        {
            "subjects"          : image_names,
            "dice_coeff"        : dice_coeff,
            "jaccard_coeff"     : jacc_coeff,
            "volume_similarity" : vol_simil
        }
    )

    # format table
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table = table.round(2) #show 2 decimals
    # show all the lines of the table
    data_dimension = table.shape # get number of rows
    pd.set_option("display.max_rows",data_dimension[0]) # show all the rows

    # save table as csv
    table.to_csv(output_file_name,  index = False)
    print("Table saved as: " + output_file_name)

    return table



# ---------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO CALCULATE SURFACE DISTANCE -----------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def compute_surface_distance(all_image_data):

    mean_distances   = [] # average surface distance
    stddev_distances = [] # standard deviation of surface distances

    for i in range(0, len(all_image_data)):
    
        # get file names
        segmented_file_name    = all_image_data[i]["segmented_folder"]    + all_image_data[i]["segmented_name"]
        ground_truth_file_name = all_image_data[i]["ground_truth_folder"] + all_image_data[i]["ground_truth_name"]

        # read images
        segmented_mask    = sitk.ReadImage(segmented_file_name, sitk.sitkUInt8)
        ground_truth_mask = sitk.ReadImage(ground_truth_file_name, sitk.sitkUInt8)
                
        # in some cases spacing of coupled images can be different at a late digits because of approximations in the pipeline
        # if this happens, round to the fourth digit
        if (segmented_mask.GetSpacing()[0] != ground_truth_mask.GetSpacing()[0] or \
            segmented_mask.GetSpacing()[1] != ground_truth_mask.GetSpacing()[1] or \
            segmented_mask.GetSpacing()[2] != ground_truth_mask.GetSpacing()[2] ):
            spacing    = []
            spacing.append(round(segmented_mask.GetSpacing()[0], 4))
            spacing.append(round(segmented_mask.GetSpacing()[1], 4))
            spacing.append(round(segmented_mask.GetSpacing()[2], 4))
            segmented_mask.SetSpacing(spacing)
            spacing    = []
            spacing.append(round(ground_truth_mask.GetSpacing()[0], 4))
            spacing.append(round(ground_truth_mask.GetSpacing()[1], 4))
            spacing.append(round(ground_truth_mask.GetSpacing()[2], 4))
            ground_truth_mask.SetSpacing(spacing)
                        
        # measure average and standard deviation of surface distances
        mean_distance, stddev_distance = sitkf.mask_euclidean_distance(segmented_mask, ground_truth_mask)
        mean_distances.append(mean_distance)
        stddev_distances.append(stddev_distance)
        
    return mean_distances,stddev_distances


def surface_distance_graph(all_image_data, mean_distances, stddev_distances):

    # figure size
    figure_width = 18
    figure_length   = 8
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks

    # create figure
    f, (ax1) = plt.subplots(1, sharex=True)
    
    # plot data
    x = np.arange(1, len(mean_distances)+1, 1)
    ax1.errorbar(x, mean_distances, stddev_distances, linestyle='None', marker='o' )


    # set ticks and labels
    plt.xticks(x)
    image_names= []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["segmented_name"])
        image_names.append(image_root)
    ax1.set_xticklabels(image_names, rotation='vertical')

    ax1.set_ylabel('average surface distance')

    # annotate points
    for i in range(0, len(all_image_data)):
        ax1.annotate(round(mean_distances[i],3), xy =(x[i], mean_distances[i]), xytext=(x[i]+0.1, mean_distances[i]))
    
    # title 
    ax1.set_title("Surface Distance")

    # show
    plt.show()
    
    
def surface_distance_table(all_image_data, mean_distances, stddev_distances, output_file_name):

    # extract image names
    image_names = []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["segmented_name"])
        image_names.append(image_root)
    #print (image_names)

    # create table
    table = pd.DataFrame(
        {
            "subjects"          : image_names,
            "mean_distances"    : mean_distances,
            "stddev_distances"  : stddev_distances,
        }
    )

    # format table
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table = table.round(2) #show 2 decimals
    # show all the lines of the table
    data_dimension = table.shape # get number of rows
    pd.set_option("display.max_rows",data_dimension[0]) # show all the rows

    # save table as csv
    table.to_csv(output_file_name,  index = False)
    print("Table saved as: " + output_file_name)

    return table

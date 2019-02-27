# Serena Bonaretti, 2018

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import SimpleITK     as sitk

from . import sitk_functions as sitkf


def compute_overlap(allImageData):

    diceCoeff = []
    jaccCoeff = []
    volSimil  = []

    for i in range(0, len(allImageData)):

        # get file names
        segmentedFileName   = allImageData[i]["segmentedFolder"]   + allImageData[i]["segmentedName"]
        groundTruthFileName = allImageData[i]["groundTruthFolder"] + allImageData[i]["groundTruthName"]

        # read images
        segmentedMask   = sitk.ReadImage(segmentedFileName)
        groundTruthMask = sitk.ReadImage(groundTruthFileName)

        # measure overlap
        dice, jacc, vols = sitkf.overlap_measures(segmentedMask, groundTruthMask)
        diceCoeff.append(dice)
        jaccCoeff.append(jacc)
        volSimil.append(vols)

    return diceCoeff, jaccCoeff, volSimil


def overlap_coeff_graph(allImageData, diceCoeff, jaccCoeff, volSimil):

    # figure size
    figureWidth = 18
    figLength   = 8
    plt.rcParams['figure.figsize'] = [figureWidth, figLength] # figsize=() seems to be ineffective on notebooks

    # create figure
    f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)

    # plot data
    x = np.arange(1, len(diceCoeff)+1, 1)
    l1, = ax1.plot(x,diceCoeff, "bo" )
    l2, = ax2.plot(x,jaccCoeff, "ro")
    l3, = ax3.plot(x,volSimil,  "go")

    # set ticks and labels
    plt.xticks(x)
    imageNames= []
    for i in range(0, len(allImageData)):
        imageRoot, imageExt = os.path.splitext(allImageData[i]["segmentedName"])
        imageNames.append(imageRoot)
    ax3.set_xticklabels(imageNames, rotation='vertical')

    ax1.set_ylabel('dice coefficient')
    ax2.set_ylabel('jaccard coefficient')
    ax3.set_ylabel('volume similarity')

    # annotate points
    for i in range(0, len(allImageData)):
        ax1.annotate(round(diceCoeff[i],3), xy =(x[i], diceCoeff[i]), xytext=(x[i], diceCoeff[i]))
    for i in range(0, len(allImageData)):
        ax2.annotate(round(jaccCoeff[i],3), xy =(x[i], jaccCoeff[i]), xytext=(x[i], jaccCoeff[i]))
    for i in range(0, len(allImageData)):
        ax3.annotate(round(volSimil[i],3),  xy =(x[i], volSimil[i]),  xytext=(x[i], volSimil[i]))


    # title and legend
    ax1.set_title("Overlap coefficients")
    plt.legend([l1, l2, l3],["Dice coefficient", "Jaccard Coefficient", "Volume similarity"], loc="lower right")

    # show
    plt.show()

def overlap_coeff_table(allImageData,diceCoeff, jaccCoeff, volSimil, outputFileName):

    # extract image names
    imageNames = []
    for i in range(0, len(allImageData)):
        imageRoot, imageExt = os.path.splitext(allImageData[i]["segmentedName"])
        imageNames.append(imageRoot)
    #print (imageNames)

    # create table
    table = pd.DataFrame(
        {
            "Subjects"         : imageNames,
            "DiceCoeff"        : diceCoeff,
            "JaccardCoeff"     : jaccCoeff,
            "VolumeSimilarity" : volSimil
        }
    )

    # format table
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table = table.round(2) #show 2 decimals
    # show all the lines of the table
    dataDimension = table.shape # get number of rows
    pd.set_option("display.max_rows",dataDimension[0]) # show all the rows

    # save table as csv
    table.to_csv(outputFileName,  index = False)
    print("Table saved as: " + outputFileName)

    return table

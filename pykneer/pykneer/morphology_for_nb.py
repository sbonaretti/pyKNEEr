# Serena Bonaretti, 2018

import matplotlib as mpl
import matplotlib.pyplot as plt
import multiprocessing
from functools import partial
import numpy as np
import os
import pandas as pd
import SimpleITK as sitk
import time
import math

from . import pykneer_io as io
from . import morphology_functions as mf
#import vtk_pts_functions as vtkf # Installation of VTK downgrades some python packages causing issues - not used for now


# ---------------------------------------------------------------------------------------------------------------
# SURFACE

def separate_cartilage_surfaces_s(imageData):

    print (imageData["maskName"])

    # read image
    mask = sitk.ReadImage(imageData["inputFolder"] + imageData["maskName"])

    # get contour points and separate them in bone cartilage and articular cartilage
    artiCart_mm, boneCart_mm  = mf.separate_cartilage(mask)

    # flatten surfaces for visualization
    boneCartFlet, bonePhi = mf.fletten_point_cloud(boneCart_mm);
    artiCartFlet, artiPhi = mf.fletten_point_cloud(artiCart_mm);

    # write curved surfaces, flattened surfaces, and flatten angles
    io.write_np_array_to_txt(boneCart_mm,  imageData["morphologyFolder"] + imageData["boneCartName"])
    io.write_np_array_to_txt(artiCart_mm,  imageData["morphologyFolder"] + imageData["artiCartName"])
    io.write_np_array_to_txt(boneCartFlet, imageData["morphologyFolder"] + imageData["boneCartFletName"])
    io.write_np_array_to_txt(artiCartFlet, imageData["morphologyFolder"] + imageData["artiCartFletName"])
    io.write_np_array_to_txt(bonePhi,      imageData["morphologyFolder"] + imageData["bonePhiName"])
    io.write_np_array_to_txt(artiPhi,      imageData["morphologyFolder"] + imageData["artiPhiName"])

def separate_cartilage_surfaces(allImageData, nOfProcesses):

    #start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(separate_cartilage_surfaces_s, allImageData)
    print ("-> Subcondral and articular cartilage separated")
    #print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))


def show_cartilage_surfaces(allImageData):

    # subplots' n. of columns and rows
    nOfColumns = 3
    nOfRows = math.ceil(len(allImageData) / nOfColumns)

    # figure size
    figureWidth = 11
    figLength   = 8 * nOfRows
    fig=plt.figure(figsize=(figureWidth, figLength), dpi= 80, facecolor='w', edgecolor='k')

    # plot
    for i in range(0, len(allImageData)):

        # load the data
        boneCart = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["boneCartFletName"])
        artiCart = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["artiCartFletName"])
        print (allImageData[i]["maskName"])

        # scatter plot
        ax = fig.add_subplot(nOfRows,nOfColumns,i+1)
        ax.scatter(boneCart[0,:],    -boneCart[1,:], vmin=0, vmax=5, color = 'gold')
        ax.scatter(artiCart[0,:], -4.5-artiCart[1,:], vmin=0, vmax=5, color = 'deepskyblue') # shift the articular cartilage of a constant value along x to make it visible

        # axis labels
        ax.set_xlabel('cartilage width [mm]', fontsize=11)
        #ax.set_ylabel('angle [deg]',          fontsize=11)
        plt.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            right=False,         # ticks along the top edge are off
            labelleft=False) # labels along the bottom edge are off

        # axis limits
        plt.axis([-5, +95, -7.5, 2.5])
        ax.text( 0,  -2.5, "M", fontsize=12)
        ax.text( 88, -2.5, "L", fontsize=12)

        # title
        ax.set_title(str(i+1) + ". " + allImageData[i]["maskName"], fontsize=12)

    # show
    fig.tight_layout() # avoids subplots overlap
    plt.show()


# ---------------------------------------------------------------------------------------------------------------
# THICKNESS

def algorithm(allImageData, algoID):

    # add the used algorithm to the image information
    for i in range (0,len(allImageData)):
        allImageData[i]["algorithm"] = algoID
        maskNameRoot, maskNameExt  = os.path.splitext( allImageData[i]["maskName"])
        allImageData[i]["thicknessName"]     =  maskNameRoot + "_thickness_" + str( allImageData[i]["algorithm"]) + ".txt"
        allImageData[i]["thicknessFlatName"] =  maskNameRoot + "_thickness_flat_" + str( allImageData[i]["algorithm"]) + ".txt"


def calculate_thickness_s(imageData):

    print (imageData["maskName"])

    # load the data
    boneCart_mm = io.read_txt_to_np_array(imageData["morphologyFolder"] + imageData["boneCartName"])
    artiCart_mm = io.read_txt_to_np_array(imageData["morphologyFolder"] + imageData["artiCartName"])

    if imageData["algorithm"] == 1:
        # calculate NN distance at the bone surface
        thickness_mm = mf.nearest_neighbor_thickness (boneCart_mm, artiCart_mm)
    elif imageData["algorithm"] == 2:
        # calculate NN distance at the articular cartilage surface
        thickness_mm = mf.nearest_neighbor_thickness (artiCart_mm, boneCart_mm)
    elif imageData["algorithm"] == 3:
        # calculate using potential lines
        print ("coming soon")
    else:
        print ("Use a number between 1 and 3")
        return

    # save thickness
    io.write_np_array_to_txt(thickness_mm, imageData["morphologyFolder"] + imageData["thicknessName"])

    # redistribute thickness for flat surfaces for visualization
    # load the angles phi
    phi = io.read_txt_to_np_array(imageData["morphologyFolder"] + imageData["bonePhiName"])
    # rearrange thicknesses for flattened surfaces for visualization
    thickness_flat = mf.flatten_thickness(thickness_mm, phi)
    # save thickness_flat
    io.write_np_array_to_txt(thickness_flat, imageData["morphologyFolder"] + imageData["thicknessFlatName"])

def calculate_thickness(allImageData, nOfProcesses):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=nOfProcesses)
    pool.map(calculate_thickness_s, allImageData)
    print ("-> Thickness computed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))


def show_thickness_maps(allImageData):

    # subplots' n. of columns and rows
    nOfColumns = 3
    nOfRows = math.ceil(len(allImageData) / nOfColumns)

    # figure size
    figureWidth = 13.5
    figLength   = 4.5 * nOfRows
    fig=plt.figure(figsize=(figureWidth, figLength), dpi= 80, facecolor='w', edgecolor='k')

    # plot
    for i in range(0, len(allImageData)):

        # load the data
        if allImageData[i]["algorithm"] == 1:
            surface   = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["boneCartFletName"])
            thickness = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["thicknessFlatName"])
            thickness = np.extract(thickness==thickness, thickness) # from array of arrays to array of numbers

        print (allImageData[i]["maskName"])

        # scatter plot
        ax = fig.add_subplot(nOfRows,nOfColumns,i+1)
        colormap = plt.cm.get_cmap("jet")
        scatterPlot = ax.scatter(surface[0,:], -surface[1,:], c=thickness, cmap = colormap, vmin=0, vmax=5)

        # axis labels
        ax.set_xlabel('cartilage width [mm]', fontsize=11)
        #ax.set_ylabel('angle [deg]',          fontsize=11)
        plt.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            right=False,         # ticks along the top edge are off
            labelleft=False) # labels along the bottom edge are off


        # axis limits
        plt.axis([-5, +95, -2.5, 2.5])
        ax.text( 0,  1, "M", fontsize=12)
        ax.text( 88, 1, "L", fontsize=12)

        # title
        ax.set_title(str(i+1) + ". " + allImageData[i]["maskName"], fontsize=12)

        # set colorbar
        clb = plt.colorbar(scatterPlot, orientation='vertical', shrink=0.60, ticks=[0, 1, 2, 3, 4, 5])
        clb.ax.set_title('[mm]')

    # show
    fig.tight_layout() # avoids subplots overlap
    plt.show()


def show_thickness_graph(allImageData):

    # calculate average and standard deviation
    average = []
    stdDev  = []
    for i in range(0, len(allImageData)):
        thickness = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["thicknessName"])
        average.append(np.average(thickness))
        stdDev.append(np.std(thickness))

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
        imageRoot, imageExt = os.path.splitext(allImageData[i]["maskName"])
        imageNames.append(imageRoot)
    ax.set_xticklabels(imageNames, rotation='vertical')
    ax.set_ylabel('thickness [mm]')

    # show
    plt.show()


def show_thickness_table(allImageData, outputFileName):

    # read and calculate values for table
    imageNames = []
    average = []
    stdDev  = []

    for i in range(0, len(allImageData)):
        # extract file names
        imageRoot, imageExt = os.path.splitext(allImageData[i]["thicknessName"])
        imageNames.append(imageRoot)
        # read thickness file
        thickness = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["thicknessName"])
        # calculate thickness and standard deviation
        average.append(np.average(thickness))
        stdDev.append(np.std(thickness))

    # create table
    table = pd.DataFrame(
        {
            "Subjects"         : imageNames,
            "averageThickness" : average,
            "std.dev"          : stdDev
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
# VOLUME

def calculate_volume(allImageData):

    volume_mm = []

    for i in range (0, len(allImageData)):

        print (allImageData[i]["maskName"])

        # read image
        mask = sitk.ReadImage(allImageData[i]["inputFolder"] + allImageData[i]["maskName"])
        # sitk to numpy
        mask_py = sitk.GetArrayFromImage(mask)

        # get number of white voxels
        nOfVoxels = np.count_nonzero(mask_py)

        # calculate volume in mm
        volume_mm = nOfVoxels * mask.GetSpacing()[0] * mask.GetSpacing()[1] * mask.GetSpacing()[2]

        # save to file
        file = open(allImageData[i]["morphologyFolder"] + allImageData[i]["volumeName"], "w")
        file.write("%0.2f " % volume_mm )
        file.close()

    print ("-> Volume computed")


def show_volume_graph (allImageData):

    # figure size
    figureWidth = 18
    figLength   = 8
    plt.rcParams['figure.figsize'] = [figureWidth, figLength] # figsize=() seems to be ineffective on notebooks

    # read volumes
    volumes = np.full((len(allImageData),1),0)
    for i in range (0, len(allImageData)):
        volumes[i] = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["volumeName"])

    # plot
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (nOfImages can be larger)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    x = np.arange(len(allImageData))
    ax.plot(x, volumes, linestyle='None', marker='o')

    # set ticks and labels
    plt.xticks(x)
    imageNames= []
    for i in range(0, len(allImageData)):
        imageRoot, imageExt = os.path.splitext(allImageData[i]["maskName"])
        imageNames.append(imageRoot)
    ax.set_xticklabels(imageNames, rotation='vertical')
    ax.set_ylabel('volume [mm^3]')

    # show
    plt.show()


def show_volume_table(allImageData, outputFileName):

    # extract image names
    imageNames = []
    for i in range(0, len(allImageData)):
        imageRoot, imageExt = os.path.splitext(allImageData[i]["maskName"])
        imageNames.append(imageRoot)

    # read volumes
    volumes = np.full((len(allImageData),1),0)
    for i in range (0, len(allImageData)):
        volumes[i] = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["volumeName"])
    volumes = np.extract(volumes==volumes, volumes)

    # create table
    table = pd.DataFrame(
        {
            "Subjects" : imageNames,
            "Volume"   : volumes
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



# ---------------------------------------------------------------------------------------------------------------
# VTK FUNCTIONS
# Installation of VTK downgrades some python packages causing issues - not used for now

# SHOW CARTILAGE SURFACES
#def show_cartilage_surfaces_interactive(allImageData, i):
#
#    # when VTK will be enbedded in jupyterLab, the visualization will be done for all images.
#    # For now, the user selects the subject to check (index i starting from 0)
#    #for i in range(0,len(allImageData)):
#
#    # make sure user enters valid ID
#    if i < 1 or i > len(allImageData):
#        print("Enter an ID between 1 and " + str(len(allImageData)))
#        return
#    else:
#        # user inputs from 1 to n (python counts from 0 to n)
#        i = i-1
#
#    # load the files
#    boneCart = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["boneCartName"])
#    artiCart = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["artiCartName"])
#
#    # from numpy to vtk
#    boneCart_vtk = vtkf.numpy_points_to_vtk_points(boneCart)
#    artiCart_vtk = vtkf.numpy_points_to_vtk_points(artiCart)
#
#    # render
#    vtkf.render_2_point_clouds(boneCart_vtk, artiCart_vtk)

# SHOW CARTILAGE THICKNESS
# Noteboook command: morph.show_cartilage_thickness_interactive(imageData, 2)
#def show_cartilage_thickness_interactive(allImageData, i):
#
#    # when VTK will be enbedded in jupyterLab, the visualization will be done for all images.
#    # For now, the user selects the subject to check (index i starting from 0)
#    #for i in range(0,len(allImageData)):
#
#        # make sure user enters valid ID
#        if i < 1 or i > len(allImageData):
#            print("Enter an ID between 1 and " + str(len(allImageData)))
#            return
#        else:
#            # user inputs from 1 to n (python counts from 0 to n)
#            i = i-1
#
#        # load the data
#        if allImageData[i]["algorithm"] == 1:
#            surface  = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["boneCartName"])
#            print("Surface is sucondral bone")
#        elif allImageData[i]["algorithm"] == 2:
#            surface  = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["artiCartName"])
#            print("Surface is articular cartilage")
#        thickness = io.read_txt_to_np_array(allImageData[i]["morphologyFolder"] + allImageData[i]["thicknessName"])
#
#        # from numpy to vtk
#        surface_vtk  = vtkf.numpy_points_to_vtk_points(surface)
#        thickness_vtk = vtkf.numpy_color_to_vtk_color(thickness)
#
#        # render
#        vtkf.render_points_with_colormap(surface_vtk, thickness_vtk, 1)

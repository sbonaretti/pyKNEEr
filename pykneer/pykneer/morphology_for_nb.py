# Serena Bonaretti, 2018

"""
Module with the functions called by the notebook segmentation.ipynb

There are two morphology measurements:
    - thickness: it is divided in two steps:
        - separation of articular and subcondral cartilage surfaces
        - thickness measurement: so far only the nearest neigbor algorithm is implemented
    - volume: calculated as the number of voxels == 1 multiplied by the image resolution

For each measurements there are:
    - calculation
    - visualization as graph 
    - visualization as table
Cartilage thickness is also visualized as flattened map
    
Functions are in pairs for parallelization. Example:
separate_cartilage_surfaces launches separate_cartilage_surfaces_s as many times as the length of all_image_data (subtituting a for loop).
pool.map() takes care of sending one single element of the list all_image_data (all_image_data[i]) to separate_cartilage_surfaces_s, as if it was a for loop.

"""

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

# pyKNEER imports 
# ugly way to use relative vs. absolute imports when developing vs. when using package - cannot find a better way
if __package__ is None or __package__ == '':
    # uses current directory visibility
    import pykneer_io as io
    import morphology_functions as mf

else:
    # uses current package visibility
    from . import pykneer_io as io
    from . import morphology_functions as mf





#import vtk_pts_functions as vtkf # Installation of VTK downgrades some python packages causing issues - not used for now


# ---------------------------------------------------------------------------------------------------------------------------
# CARTILAGE THICKNESS -------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

# --- SEPARATING AND VISUALIZING ARTICULAR AND SUBCHONDRAL SURFACES ---------------------------------------------------------

def separate_cartilage_surfaces_s(image_data):

    print (image_data["mask_name"])

    # read image
    mask = sitk.ReadImage(image_data["input_folder"] + image_data["mask_name"])

    # get contour points and separate them in bone cartilage and articular cartilage
    arti_cart_mm, bone_cart_mm = mf.separate_cartilage(mask)

    # flatten surfaces for visualization
    bone_cart_flat, bone_phi = mf.flatten_point_cloud(bone_cart_mm);
    arti_cart_flat, arti_phi = mf.flatten_point_cloud(arti_cart_mm);

    # write curved surfaces, flattened surfaces, and flatten angles
    io.write_np_array_to_txt(bone_cart_mm,   image_data["morphology_folder"] + image_data["bone_cart_name"])
    io.write_np_array_to_txt(arti_cart_mm,   image_data["morphology_folder"] + image_data["arti_cart_name"])
    io.write_np_array_to_txt(bone_cart_flat, image_data["morphology_folder"] + image_data["bone_cart_flat_name"])
    io.write_np_array_to_txt(arti_cart_flat, image_data["morphology_folder"] + image_data["arti_cart_flat_name"])
    io.write_np_array_to_txt(bone_phi,       image_data["morphology_folder"] + image_data["bone_phi_name"])
    io.write_np_array_to_txt(arti_phi,       image_data["morphology_folder"] + image_data["arti_phi_name"])

def separate_cartilage_surfaces(all_image_data, n_of_processes):

    #start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(separate_cartilage_surfaces_s, all_image_data)
    print ("-> Subcondral and articular cartilage separated")
    #print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))


def show_cartilage_surfaces(all_image_data):

    # subplots' n. of columns and rows
    n_of_columns = 3
    n_of_rows    = math.ceil(len(all_image_data) / n_of_columns)

    # figure size
    figure_width  = 11
    figure_length = 8 * n_of_rows
    fig           = plt.figure(figsize=(figure_width, figure_length), dpi=80, facecolor='w', edgecolor='k')

    # plot
    for i in range(0, len(all_image_data)):

        # load the data
        bone_cart = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["bone_cart_flat_name"])
        arti_cart = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["arti_cart_flat_name"])
        print (all_image_data[i]["mask_name"])

        # scatter plot
        ax = fig.add_subplot(n_of_rows,n_of_columns,i+1)
        ax.scatter(bone_cart[0,:],     -bone_cart[1,:], vmin=0, vmax=5, color='gold')
        ax.scatter(arti_cart[0,:], -4.5-arti_cart[1,:], vmin=0, vmax=5, color='deepskyblue') # shift the articular cartilage of a constant value along x to make it visible

        # axis labels
        ax.set_xlabel('cartilage width [mm]', fontsize=11)
        #ax.set_ylabel('angle [deg]',          fontsize=11)
        plt.tick_params(
            axis      = 'y',    # changes apply to the x-axis
            which     = 'both', # both major and minor ticks are affected
            left      = False,  # ticks along the bottom edge are off
            right     = False,  # ticks along the top edge are off
            labelleft = False)  # labels along the bottom edge are off

        # axis limits
        plt.axis([-5, +95, -7.5, 2.5])
        ax.text( 0,  -2.5, "M", fontsize=12)
        ax.text( 88, -2.5, "L", fontsize=12)

        # title
        ax.set_title(str(i+1) + ". " + all_image_data[i]["mask_name"], fontsize=12)

    # show
    fig.tight_layout() # avoids subplots overlap
    plt.show()


# --- CALCULATING AND VISUALIZING THICKNESS ---------------------------------------------------------------------------------

def algorithm(all_image_data, algo_ID):

    # add the used algorithm to the image information
    for i in range (0,len(all_image_data)):
        all_image_data[i]["algorithm"] = algo_ID
        mask_name_root, mask_name_ext  = os.path.splitext( all_image_data[i]["mask_name"])
        all_image_data[i]["thickness_name"]      =  mask_name_root + "_thickness_"      + str( all_image_data[i]["algorithm"]) + ".txt"
        all_image_data[i]["thickness_flat_name"] =  mask_name_root + "_thickness_flat_" + str( all_image_data[i]["algorithm"]) + ".txt"


def calculate_thickness_s(image_data):

    print (image_data["mask_name"])

    # load the data
    bone_cart_mm = io.read_txt_to_np_array(image_data["morphology_folder"] + image_data["bone_cart_name"])
    arti_cart_mm = io.read_txt_to_np_array(image_data["morphology_folder"] + image_data["arti_cart_name"])

    if image_data["algorithm"] == 1:
        # calculate NN distance at the bone surface
        thickness_mm = mf.nearest_neighbor_thickness (bone_cart_mm, arti_cart_mm)
    elif image_data["algorithm"] == 2:
        # calculate NN distance at the articular cartilage surface
        thickness_mm = mf.nearest_neighbor_thickness (arti_cart_mm, bone_cart_mm)
    elif image_data["algorithm"] == 3:
        # calculate using potential lines
        print ("coming soon")
    else:
        print ("Use a number between 1 and 3")
        return

    # save thickness
    io.write_np_array_to_txt(thickness_mm, image_data["morphology_folder"] + image_data["thickness_name"])

    # redistribute thickness for flat surfaces for visualization
    # load the angles phi
    phi = io.read_txt_to_np_array(image_data["morphology_folder"] + image_data["bone_phi_name"])
    # rearrange thicknesses for flattened surfaces for visualization
    thickness_flat = mf.flatten_thickness(thickness_mm, phi)
    # save thickness_flat
    io.write_np_array_to_txt(thickness_flat, image_data["morphology_folder"] + image_data["thickness_flat_name"])

def calculate_thickness(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(calculate_thickness_s, all_image_data)
    print ("-> Thickness computed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))


def show_thickness_maps(all_image_data):

    # subplots' n. of columns and rows
    n_of_columns = 3
    n_of_rows    = math.ceil(len(all_image_data) / n_of_columns)

    # figure size
    figure_width  = 13.5
    figure_length = 4.5 * n_of_rows
    fig           = plt.figure(figsize=(figure_width, figure_length), dpi=80, facecolor='w', edgecolor='k')

    # plot
    for i in range(0, len(all_image_data)):

        # load the data
        if all_image_data[i]["algorithm"] == 1:
            surface   = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["bone_cart_flat_name"])
            thickness = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["thickness_flat_name"])
            thickness = np.extract(thickness==thickness, thickness) # from array of arrays to array of numbers

        print (all_image_data[i]["mask_name"])

        # scatter plot
        ax           = fig.add_subplot(n_of_rows,n_of_columns,i+1)
        colormap     = plt.cm.get_cmap("jet")
        scatter_plot = ax.scatter(surface[0,:], -surface[1,:], c=thickness, cmap=colormap, vmin=0, vmax=5)

        # axis labels
        ax.set_xlabel('cartilage width [mm]', fontsize=11)
        #ax.set_ylabel('angle [deg]',          fontsize=11)
        plt.tick_params(
            axis      = 'y',    # changes apply to the x-axis
            which     = 'both', # both major and minor ticks are affected
            left      = False,  # ticks along the bottom edge are off
            right     = False,  # ticks along the top edge are off
            labelleft = False)  # labels along the bottom edge are off


        # axis limits
        plt.axis([-5, +95, -2.5, 2.5])
        ax.text( 0,  1, "M", fontsize=12)
        ax.text( 88, 1, "L", fontsize=12)

        # title
        ax.set_title(str(i+1) + ". " + all_image_data[i]["mask_name"], fontsize=12)

        # set colorbar
        clb = plt.colorbar(scatter_plot, orientation='vertical', shrink=0.60, ticks=[0, 1, 2, 3, 4, 5])
        clb.ax.set_title('[mm]')

    # show
    fig.tight_layout() # avoids subplots overlap
    plt.show()


def show_thickness_graph(all_image_data):

    # calculate average and standard deviation
    average = []
    std_dev = []
    for i in range(0, len(all_image_data)):
        thickness = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["thickness_name"])
        average.append(np.average(thickness))
        std_dev.append(np.std(thickness))

    average = np.asarray(average)
    std_dev = np.asarray(std_dev)
    x = np.arange(len(all_image_data))

    # figure size
    figure_width  = 18
    figure_length = 8
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks

    # error bar
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (nOfImages can be larger)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.errorbar(x, average, yerr=std_dev, linestyle='None', marker='o')

    # set ticks and labels
    plt.xticks(x)
    image_names = []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["mask_name"])
        image_names.append(image_root)
    ax.set_xticklabels(image_names, rotation='vertical')
    ax.set_ylabel('thickness [mm]')

    # show
    plt.show()


def show_thickness_table(all_image_data, output_file_name):

    # read and calculate values for table
    image_names = []
    average     = []
    std_dev     = []

    for i in range(0, len(all_image_data)):
        # extract file names
        image_root, image_ext = os.path.splitext(all_image_data[i]["thickness_name"])
        image_names.append(image_root)
        # read thickness file
        thickness = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["thickness_name"])
        # calculate thickness and standard deviation
        average.append(np.average(thickness))
        std_dev.append(np.std(thickness))

    # create table
    table = pd.DataFrame(
        {
            "subjects"          : image_names,
            "average_thickness" : average,
            "std_dev"           : std_dev
        }
    )
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table       = table.round(2) #show 2 decimals

    # show all the lines of the table
    data_dimension = table.shape # get number of rows
    pd.set_option("display.max_rows", data_dimension[0]) # show all the rows

    # save table as csv
    table.to_csv(output_file_name,  index=False)
    print("Table saved as: " + output_file_name)

    return table


# ---------------------------------------------------------------------------------------------------------------------------
# CARTILAGE VOLUME ----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------


def calculate_volume(all_image_data):

    volume_mm = []

    for i in range (0, len(all_image_data)):

        print (all_image_data[i]["mask_name"])

        # read image
        mask = sitk.ReadImage(all_image_data[i]["input_folder"] + all_image_data[i]["mask_name"])
        # sitk to numpy
        mask_py = sitk.GetArrayFromImage(mask)

        # get number of white voxels
        n_of_voxels = np.count_nonzero(mask_py)

        # calculate volume in mm
        volume_mm = n_of_voxels * mask.GetSpacing()[0] * mask.GetSpacing()[1] * mask.GetSpacing()[2]

        # save to file
        file = open(all_image_data[i]["morphology_folder"] + all_image_data[i]["volume_name"], "w")
        file.write("%0.2f " % volume_mm )
        file.close()

    print ("-> Volume computed")


def show_volume_graph (all_image_data):

    # figure size
    figure_width  = 18
    figure_length = 8
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks

    # read volumes
    volumes = np.full((len(all_image_data),1),0)
    for i in range (0, len(all_image_data)):
        volumes[i] = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["volume_name"])

    # plot
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (nOfImages can be larger)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    x       = np.arange(len(all_image_data))
    ax.plot(x, volumes, linestyle='None', marker='o')

    # set ticks and labels
    plt.xticks(x)
    image_names = []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["mask_name"])
        image_names.append(image_root)
    ax.set_xticklabels(image_names, rotation='vertical')
    ax.set_ylabel('volume [mm^3]')

    # show
    plt.show()


def show_volume_table(all_image_data, output_file_name):

    # extract image names
    image_names = []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["mask_name"])
        image_names.append(image_root)

    # read volumes
    volumes = np.full((len(all_image_data),1),0)
    for i in range (0, len(all_image_data)):
        volumes[i] = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["volume_name"])
    volumes = np.extract(volumes==volumes, volumes)

    # create table
    table = pd.DataFrame(
        {
            "subjects" : image_names,
            "volume"   : volumes
        }
    )

    # format table
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table       = table.round(2) #show 2 decimals

    # show all the lines of the table
    data_dimension = table.shape # get number of rows
    pd.set_option("display.max_rows",data_dimension[0]) # show all the rows

    # save table as csv
    table.to_csv(output_file_name,  index=False)
    print("Table saved as: " + output_file_name)


    return table



# ---------------------------------------------------------------------------------------------------------------
# VTK FUNCTIONS
# Installation of VTK downgrades some python packages causing issues - not used for now

# SHOW CARTILAGE SURFACES
#def show_cartilage_surfaces_interactive(all_image_data, i):
#
#    # when VTK will be enbedded in jupyterLab, the visualization will be done for all images.
#    # For now, the user selects the subject to check (index i starting from 0)
#    #for i in range(0,len(all_image_data)):
#
#    # make sure user enters valid ID
#    if i < 1 or i > len(all_image_data):
#        print("Enter an ID between 1 and " + str(len(all_image_data)))
#        return
#    else:
#        # user inputs from 1 to n (python counts from 0 to n)
#        i = i-1
#
#    # load the files
#    bone_cart = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["bone_cart_name"])
#    arti_cart = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["arti_cart_name"])
#
#    # from numpy to vtk
#    bone_cart_vtk = vtkf.numpy_points_to_vtk_points(bone_cart)
#    arti_cart_vtk = vtkf.numpy_points_to_vtk_points(arti_cart)
#
#    # render
#    vtkf.render_2_point_clouds(bone_cart_vtk, arti_cart_vtk)

# SHOW CARTILAGE THICKNESS
# Noteboook command: morph.show_cartilage_thickness_interactive(image_data, 2)
#def show_cartilage_thickness_interactive(all_image_data, i):
#
#    # when VTK will be enbedded in jupyterLab, the visualization will be done for all images.
#    # For now, the user selects the subject to check (index i starting from 0)
#    #for i in range(0,len(all_image_data)):
#
#        # make sure user enters valid ID
#        if i < 1 or i > len(all_image_data):
#            print("Enter an ID between 1 and " + str(len(all_image_data)))
#            return
#        else:
#            # user inputs from 1 to n (python counts from 0 to n)
#            i = i-1
#
#        # load the data
#        if all_image_data[i]["algorithm"] == 1:
#            surface  = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["bone_cart_name"])
#            print("Surface is sucondral bone")
#        elif all_image_data[i]["algorithm"] == 2:
#            surface  = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["arti_cart_name"])
#            print("Surface is articular cartilage")
#        thickness = io.read_txt_to_np_array(all_image_data[i]["morphology_folder"] + all_image_data[i]["thickness_name"])
#
#        # from numpy to vtk
#        surface_vtk  = vtkf.numpy_points_to_vtk_points(surface)
#        thickness_vtk = vtkf.numpy_color_to_vtk_color(thickness)
#
#        # render
#        vtkf.render_points_with_colormap(surface_vtk, thickness_vtk, 1)

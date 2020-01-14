# Serena Bonaretti, 2018

"""
Module with the functions called by the notebooks relaxometry_EPG.ipynb and relaxometry_fitting.ipynb

There are two group of functions to:
    - Calculate exponential and linear fitting
    - Calculate T2 using EPG modeling from DESS acquisitions 
For each group there are functions to:
    - calculate fitting
    - show map, graph, and table of values
For exponential and linear fitting, there is the option to rigidly register images acquired at different echo times 
    
Functions are in pairs for parallelization. Example:
align_acquisitions launches align_acquisitions_s as many times as the length of all_image_data (subtituting a for loop).
pool.map() takes care of sending one single element of the list all_image_data (all_image_data[i]) to align_acquisitions_s, as if it was a for loop.

"""

from datetime import datetime
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import os
import pandas as pd
import platform
import SimpleITK as sitk
import shutil
import time

from ipywidgets import * # for display
from ipywidgets import HBox, VBox
from ipywidgets import interactive
from ipywidgets import Layout
from ipywidgets import widgets as widgets


# pyKNEER imports 
# ugly way to use relative vs. absolute imports when developing vs. when using package - cannot find a better way
if __package__ is None or __package__ == '':
    # uses current directory visibility
    import relaxometry_functions as rf
    import elastix_transformix

else:
    # uses current package visibility
    from . import relaxometry_functions as rf
    from . import elastix_transformix


# ---------------------------------------------------------------------------------------------------------------------------
# EXPONENTIAL AND LINEAR FITTING MAPS ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

# --- OPTIONAL ALIGNMENT ----------------------------------------------------------------------------------------------------

def align_acquisitions_s(image_data):
    """
    Function for images acquired subsequently, at different echo times.
    Alignment of following acquisitions to image 1 using rigid registration. This is done because images are acquired one after the other, and the subject can move among acquisitions
    The alignment consists in the rigid registration implemented in the class elastix_transformix
    This function mainly moves files to the t1rhoMap folder and creates dictionaries of filenames as requested by the class elastix_transformix
    """

    # get folder_div
    sys = platform.system()
    if sys == "Linux":
        folder_div = "/"
    elif sys == "Darwin":
        folder_div = "/"
    elif sys == "windows":
        folder_div = "\\"

    # get image names for current subject
    acquisition_file_names    = image_data["acquisition_file_names"]

    # create folder named after the first image in the folder "relaxometry" for registration (the first image is the reference for the rigid registration)
    map_folder                = image_data["relaxometry_folder"]
    reference_root, image_ext = os.path.splitext(acquisition_file_names[0])
    registered_folder         = map_folder + reference_root + folder_div
    if not os.path.isdir(registered_folder):
        os.mkdir(registered_folder)

    print ("-> " + acquisition_file_names[0])


    # --- REFERENCE -----------------------------------------------------------------------------------------------------------------

    # create the reference folder
    reference_folder = registered_folder + "reference" + folder_div
    if not os.path.isdir(reference_folder):
        os.mkdir(reference_folder)

    # move the reference (first image) to the reference folder and rename it
    reference_root = "reference"
    reference_name = reference_root + ".mha"
    shutil.copyfile(image_data["preprocessed_folder"] + acquisition_file_names[0],
                    reference_folder + reference_name)

    # move the femur and femoral cartilage masks to the reference folder and rename them
    bone_mask_file_name = reference_root + "_f.mha"
    shutil.copyfile(image_data["segmented_folder"] + image_data["bone_mask_file_name"],
                    reference_folder + bone_mask_file_name)
    cart_mask_file_name = reference_root + "_fc.mha" # not needed but the function 'prepare_reference' of the class 'elastix_transformix' will look for it
    shutil.copyfile(image_data["segmented_folder"] + image_data["cart_mask_file_name"],
                    reference_folder + cart_mask_file_name)

    # create new dictionary specifically for the elastix_transformix class (trick)
    reference = {}
    reference["current_anatomy"]  = image_data["bone"]
    reference["reference_folder"] = reference_folder
    reference[reference["current_anatomy"] + "mask_file_name"]          = bone_mask_file_name
    reference[reference["current_anatomy"] + "dil_mask_file_name"]      = reference_root + "_" + reference["current_anatomy"] + "_" + str(image_data["dilate_radius"]) + ".mha"
    reference[reference["current_anatomy"] + "levelset_mask_file_name"] = reference_root + "_" + reference["current_anatomy"] + "_" + "levelSet.mha"
    reference["dilate_radius"]    = image_data["dilate_radius"]

    # instanciate bone class and prepare reference
    bone = elastix_transformix.bone()
    bone.prepare_reference (reference)


    # --- MOVING IMAGES -----------------------------------------------------------------------------------------------------------------

    # image file names will contain "align"
    acquisition_file_names_new = []

    # move and rename image 1 (reference) to the folder preprocessing to calculate the fitting in the function calculate_t1rho_maps
    file_name_root, file_ext   = os.path.splitext(acquisition_file_names[0])
    acquisition_file_names_new.append(file_name_root + "_aligned.mha")
    shutil.copyfile(image_data["preprocessed_folder"] + acquisition_file_names[0],
                    image_data["preprocessed_folder"] + acquisition_file_names_new[0])

    # move all prep images 2,3,4 (1 is the reference) to the registration folder
    for a in range (1, len(acquisition_file_names)):
        shutil.copyfile(image_data["preprocessed_folder"] + acquisition_file_names[a],
                        registered_folder  + acquisition_file_names[a])

    # rigid registration
    for a in range(1,len(acquisition_file_names)):

        # create new dictionary for current image for the elastix_transformix class (trick)
        img = {}
        img["moving_name"]           = acquisition_file_names[a]
        img["moving_folder"]         = registered_folder
        img["current_anatomy"]       = image_data["bone"]
        img["reference_folder"]      = reference_folder
        img["reference_name"]        = reference_name
        img[img["current_anatomy"] + "dil_mask_file_name"] = reference_root + "_" + reference["current_anatomy"] + "_" + str(image_data["dilate_radius"]) + ".mha"
        img["param_file_rigid"]      = image_data["parameter_folder"] + image_data["param_file_rigid"]
        img["elastix_folder"]        = image_data["elastix_folder"]
        img["complete_elastix_path"] = image_data["complete_elastix_path"]
        img["registered_sub_folder"] = registered_folder
        img[img["current_anatomy"] + "rigid_name"]       = "rigid_2.mha"
        img[img["current_anatomy"] + "rigid_transf_name"] = "transf_2.txt"

        # register
        #print ("   registering " + acquisition_file_names[a])
        bone.rigid (img)
        # copy aligned image to the folder preprocessing
        file_name_root, file_ext = os.path.splitext(acquisition_file_names[a])
        acquisition_file_names_new.append(file_name_root + "_aligned.mha")
        shutil.copyfile(img["registered_sub_folder"] + img[img["current_anatomy"] + "rigid_name"],
                        image_data["preprocessed_folder"]  + acquisition_file_names_new[-1])

    # assign new file names to the main dictionary for the function calculate_fitting_maps
    image_data["acquisition_file_names"] = acquisition_file_names_new

def align_acquisitions(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(align_acquisitions_s, all_image_data)
    print ("-> Acquisitions aligned")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



# --- CALCULATE FITTING -----------------------------------------------------------------------------------------------------
def calculate_fitting_maps_s(image_data):


    # define the kind of fitting to compute (linear or exponential)
    method_flag = image_data["method_flag"] # get info from the first image

    # get fileNames
    preprocessed_folder    = image_data["preprocessed_folder"]
    acquisition_file_names = image_data["acquisition_file_names"]
    info_file_names        = image_data["info_file_names"]
    # mask
    segmented_folder       = image_data["segmented_folder"]
    mask_file_name         = image_data["cart_mask_file_name"] #mask_file_name
    # output maps
    map_folder             = image_data["relaxometry_folder"]
    map_file_name          = image_data["map_file_name"]

    print(acquisition_file_names[0])

    # read info files and get spin lock time (saved as echo time) (x-values for fitting)
    tsl = []
    for current_info in info_file_names:
        for line in open(preprocessed_folder + current_info):
            if "0018|0081" in line:
                tsl.append(float(line[10:len(line)]))

    # read the mask
    mask = sitk.ReadImage(segmented_folder + mask_file_name)
    # from SimpleITK to numpy
    mask_py = sitk.GetArrayFromImage(mask)
    # rotate mask to be compatible with flat bone surface for visualization later
    mask_py = np.rot90(mask_py)
    mask_py = np.flip(mask_py,0)

    # from 3D matrix to array
    mask_py_array = np.reshape(mask_py, np.size(mask_py,0)*np.size(mask_py,1)*np.size(mask_py,2))
    # get only non zero values (= masked cartilage) to speed up computation
    index = np.where(mask_py_array != 0)

    # get values from images (y-values of fitting)
    array_of_masked_images = []

    for a in range(0, len(acquisition_file_names)):
        # read image
        img = sitk.ReadImage(preprocessed_folder + acquisition_file_names[a])
        # from SimpleITK to numpy
        img_py = sitk.GetArrayFromImage(img)
        # rotate images to be compatible with flat bone surface for visualization later
        img_py = np.rot90(img_py)
        img_py = np.flip(img_py,0)
        # from 3D matrix to array
        img_py_array = np.reshape(img_py, np.size(img_py,0)*np.size(img_py,1)*np.size(img_py,2))
        # get only non zero values (= masked cartilage) to speed up computation
        array = img_py_array[index]
        # add array to array of images for current subject
        array_of_masked_images.append(array)

    # calculate fitting
    if method_flag == 0: # linear fitting
        map_py_v = rf.calculate_fitting_maps_lin(tsl, array_of_masked_images)
    elif method_flag == 1: # exponential fitting
        map_py_v = rf.calculate_fitting_maps_exp(tsl, array_of_masked_images)

    # assign map to image-long vector
    map_vector = np.full((np.size(mask_py,0)*np.size(mask_py,1)*np.size(mask_py,2)), 0.00)
    map_vector[index] = map_py_v

    # resize vector to matrix
    map_py = np.reshape(map_vector,(np.size(mask_py,0),np.size(mask_py,1),np.size(mask_py,2)))
    # rotate it back to be consistent with image
    map_py = np.flip(map_py,0)
    map_py = np.rot90(map_py, k=-1)


    # back to SimpleITK
    fitting_map = sitk.GetImageFromArray(map_py)
    fitting_map.SetSpacing  (mask.GetSpacing())
    fitting_map.SetOrigin   (mask.GetOrigin())
    fitting_map.SetDirection(mask.GetDirection())
    fitting_map = sitk.Cast(fitting_map,sitk.sitkInt16)

    # write map
    sitk.WriteImage(fitting_map, (map_folder + map_file_name))

def calculate_fitting_maps(all_image_data, n_of_processes):

    method_flag = all_image_data[0]["method_flag"]
    if method_flag == 0: # linear fitting
        print ('-> using linear fitting ')
    elif method_flag == 1: # exponential fitting
        print ('-> using exponential fitting ')

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(calculate_fitting_maps_s, all_image_data)
    print ("-> Fitting maps calculated")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



# --- VISUALIZE FITTING -----------------------------------------------------------------------------------------------------
def show_fitting_maps (image_data, view_modality):
    
    if view_modality == 0:
        show_fitting_maps_static(image_data)
        trick = 'Figure'
        return trick  # need a return for the interactive function when view_modality == 1. Done to avoid if/else on notebook 
    elif view_modality == 1:
        fig = show_fitting_maps_interactive(image_data)
        return fig
    else:
        print("view_modality has to be 0 for static visualization or 1 for interactive visualization")
        

def show_fitting_maps_static(all_image_data):

    n_of_images  = len(all_image_data)
    img_LW       = 6
    figure_width = img_LW * 3
    figure_length   = img_LW * n_of_images
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (n_of_images can be larger)
    fig.tight_layout() # avoids subplots overlap
    # subplots characteristics
    n_of_columns = 3
    n_of_rows    = n_of_images
    axis_index   = 1;

    for i in range(0, n_of_images):

        # get paths and file names of the current image
        preprocessed_folder = all_image_data[i]["preprocessed_folder"]
        i1_file_name        = all_image_data[i]["acquisition_file_names"][0]
        map_folder          = all_image_data[i]["relaxometry_folder"]
        map_file_name       = all_image_data[i]["map_file_name"]
        image_name_root, image_ext = os.path.splitext(i1_file_name)

        # read images
        img  = sitk.ReadImage(preprocessed_folder + i1_file_name)
        map_ = sitk.ReadImage(map_folder + map_file_name)

        # images from simpleitk to numpy
        img_py = sitk.GetArrayFromImage(img)
        map_py = sitk.GetArrayFromImage(map_)


        # extract slices at 2/5, 3/5 and 4/3 of the image size
        size = np.size(map_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                first_value = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                last_value = b
                break
        slice_step = int ((last_value-first_value)/4)
        slice_ID   = (first_value + slice_step, first_value + 2*slice_step, first_value + 3*slice_step)

        # show slices with maps
        for a in range (0,len(slice_ID)):

            # create subplot
            ax1 = fig.add_subplot(n_of_rows,n_of_columns,axis_index)

            # get slices
            slice_img_py = img_py[:,:,slice_ID[a]]
            slice_map_py = map_py[:,:,slice_ID[a]]
            slice_map_masked = np.ma.masked_where(slice_map_py == 0, slice_map_py)

            # show image
            ren1 = ax1.imshow(slice_img_py    , 'gray', interpolation=None, origin='lower')
            ren2 = ax1.imshow(slice_map_masked, 'jet' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            clb = plt.colorbar(ren2, orientation='vertical', shrink=0.60, ticks=[0, 20, 40, 60, 80, 100])
            clb.ax.set_title('[ms]')
            ax1.set_title(str(i+1) + ". " + image_name_root + " - Slice: " + str(slice_ID[a]))
            ax1.axis('off')

            axis_index = axis_index + 1



def browse_images(moving_py, mask_py, ax_i, fig, moving_root, last_value, sliceID):
    
    # The code in this function has to be separate. If code directly into show_segmented_images, when using widgets, they update the last image
    
    # function for slider
    def view_image(slider):
                
        # get slice of moving image
        slice_moving_py   = moving_py[:,:,slider]
        # get slice in mask
        slice_mask_py     = mask_py[:,:,slider]
        slice_mask_masked = np.ma.masked_where(slice_mask_py == 0, slice_mask_py)
        # show both
        ax_i.imshow(slice_moving_py, cmap=plt.cm.gray, origin='lower',interpolation=None) 
        ren = ax_i.imshow(slice_mask_masked, 'jet' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
        ax_i.set_title(moving_root)
        ax_i.axis('off')
        # colorbar        
        cbar_ax = fig.add_axes([0.08, 0.4, 0.01, 0.2]) #[left, bottom, width, height] 
        fig.colorbar(ren, cax=cbar_ax, orientation='vertical', shrink=0.60, ticks=[0, 20, 40, 60, 80, 100])
        cbar_ax.set_title('[ms]')
        # The following two lines are to avoid this warning in the notebook: 
        # Adding an axes using the same arguments as a previous axes currently reuses the earlier instance.  In a future version, a new instance will always be created and returned.  Meanwhile, this warning can be suppressed, and the future behavior ensured, by passing a unique label to each axes instance.
        # To be fixed in following releases 
        import warnings
        warnings.filterwarnings("ignore")
        
        # display
        display(fig)
        
    # link sliders and its function
    slider_image = interactive(view_image, 
                         slider = widgets.IntSlider(min=0, 
                                                      max=last_value, 
                                                      value=sliceID[1],
                                                      step=1,
                                                      continuous_update=False, # avoids intermediate image display
                                                      readout=False,
                                                      layout=Layout(width='250px'),
                                                      description='Slice n.'))        
    # show figures before start interacting
    slider_image.update()  
    
    # slice number scrolling
    text = widgets.BoundedIntText(description="", # BoundedIntText to avoid that displayed text goes outside of the range
                           min=0, 
                           max=last_value, 
                           value=sliceID[1],
                           step=1,
                           continuous_update=False,
                           layout=Layout(width='50px'))
    
    
    
    # link slider and text 
    widgets.jslink((slider_image.children[:-1][0], 'value'), (text, 'value'))
    
    # layout
    slider_box   = HBox(slider_image.children[:-1])
    widget_box   = HBox([slider_box, text])
    whole_box    = VBox([widget_box, slider_image.children[-1] ]) 
        
    return whole_box

def show_fitting_maps_interactive(all_image_data):

    for i in range(0, len(all_image_data)):

        # get paths and file names of the current image
        preprocessed_folder = all_image_data[i]["preprocessed_folder"]
        i1_file_name        = all_image_data[i]["acquisition_file_names"][0]
        map_folder          = all_image_data[i]["relaxometry_folder"]
        map_file_name       = all_image_data[i]["map_file_name"]
        image_name_root, image_ext = os.path.splitext(i1_file_name)

        # read images
        img  = sitk.ReadImage(preprocessed_folder + i1_file_name)
        map_ = sitk.ReadImage(map_folder + map_file_name)

        # images from simpleitk to numpy
        img_py = sitk.GetArrayFromImage(img)
        map_py = sitk.GetArrayFromImage(map_)


        # extract slices at 2/5, 3/5 and 4/3 of the image size
        size = np.size(map_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                first_value = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                last_value = b
                break
        slice_step = int ((last_value-first_value)/4)
        slice_ID   = (first_value + slice_step, first_value + 2*slice_step, first_value + 3*slice_step)

        # create figure
        plt.rcParams['figure.figsize'] = [20, 15]  
        fig, ax = plt.subplots(nrows=1, ncols=4) 
        
        # static images
        for a in range (0,len(slice_ID)):

            # create subplot
            ax1 = ax[a+1]

            # get slices
            slice_img_py = img_py[:,:,slice_ID[a]]
            slice_map_py = map_py[:,:,slice_ID[a]]
            slice_map_masked = np.ma.masked_where(slice_map_py == 0, slice_map_py)

            # show image
            ax1.imshow(slice_img_py    , 'gray', interpolation=None, origin='lower')
            ax1.imshow(slice_map_masked, 'jet' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            ax1.set_title("Slice: " + str(slice_ID[a]))
            ax1.axis('off')
            plt.close(fig) # avoid to show them several times in notebook
            
        # interactive image
        ax_i = ax[0]
        if i == 0:
            final_box = browse_images(img_py, map_py, ax_i, fig, image_name_root, last_value, slice_ID)
        else:
            new_box = browse_images(img_py, map_py, ax_i, fig, image_name_root, last_value, slice_ID)
            final_box = VBox([final_box,new_box]);   
            
    return final_box



def show_fitting_graph(all_image_data):

    # calculate average and standard deviation
    average = []
    std_dev  = []
    for i in range(0, len(all_image_data)):
        # file name
        map_folder    = all_image_data[i]["relaxometry_folder"]
        map_file_name = all_image_data[i]["map_file_name"]
        # read image
        map_image = sitk.ReadImage(map_folder + map_file_name)
        # from SimpleITK to numpy
        map_py = sitk.GetArrayFromImage(map_image)
        # from 3D matrix to array
        map_py_array = np.reshape(map_py, np.size(map_py,0)*np.size(map_py,1)*np.size(map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(map_py_array != 0)
        map_vector = map_py_array[index]
        # calculate average and std_dev
        average.append(np.average(map_vector))
        std_dev.append(np.std(map_vector))

    average = np.asarray(average)
    std_dev = np.asarray(std_dev)
    x       = np.arange(len(all_image_data))

    # figure size
    figure_width  = 18
    figure_length = 8
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks

    # error bar
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (n_of_images can be larger)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.errorbar(x, average, yerr=std_dev, linestyle='None', marker='o')

    # set ticks and labels
    plt.xticks(x)
    image_names= []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["map_file_name"])
        image_names.append(image_root)
    ax.set_xticklabels(image_names, rotation='vertical')
    ax.set_ylabel('t1rho [ms]')

    # show
    plt.show()


def show_fitting_table(all_image_data, output_file_name):

    # read and calculate values for table
    image_names = []
    average     = []
    std_dev     = []

    for i in range(0, len(all_image_data)):
        # file name
        map_folder    = all_image_data[i]["relaxometry_folder"]
        map_file_name = all_image_data[i]["map_file_name"]
        image_root, image_ext = os.path.splitext(all_image_data[i]["map_file_name"])
        image_names.append(image_root)
        # read image
        image_map = sitk.ReadImage(map_folder + map_file_name)
        # from SimpleITK to numpy
        map_py = sitk.GetArrayFromImage(image_map)
        # from 3D matrix to array
        map_py_array = np.reshape(map_py, np.size(map_py,0)*np.size(map_py,1)*np.size(map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(map_py_array != 0)
        map_vector = map_py_array[index]
        # calculate average and std_dev
        average.append(np.average(map_vector))
        std_dev.append(np.std(map_vector))

    # create table
    table = pd.DataFrame(
        {
            "subjects"      : map_file_name,
            "average"       : average,
            "std_dev"       : std_dev
        }
    )
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
# T2 USING EPG MODELING FROM DESS ACQUISITIONS ------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def calculate_t2_maps_s(image_data):


    # get fileNames
    # images
    preprocessed_folder   = image_data["preprocessed_folder"]
    info_file_name        = image_data["info_file_name"]
    i1_file_name          = image_data["i1_file_name"]
    i2_file_name          = image_data["i2_file_name"]
    # mask
    segmented_folder      = image_data["segmented_folder"]
    mask_file_name        = image_data["mask_file_name"]
    # t2 maps
    relaxometry_folder    = image_data["relaxometry_folder"]
    t2_map_file_name      = image_data["t2_map_file_name"]
    t2_map_mask_file_name = image_data["t2_map_mask_file_name"]
    image_name_root       = image_data["image_name_root"]

    print (image_name_root)

    # read txt file and get acquisition parameters
    for line in open(preprocessed_folder + info_file_name):
        if "0018|0080" in line:
            repetition_time = float(line[10:len(line)])
        if "0018|0081" in line:
            echo_time       = float(line[10:len(line)])
        if "0018|1314" in line:
            alpha_deg_L     = float(line[10:len(line)]) #alpha_deg_L = flipAngle

    # read images
    img_1L = sitk.ReadImage(preprocessed_folder + i1_file_name)
    img_2L = sitk.ReadImage(preprocessed_folder + i2_file_name)
    mask   = sitk.ReadImage(segmented_folder    + mask_file_name)

    # compute T2 map
    t2_map = rf.calculate_t2_maps_from_dess(img_1L, img_2L, repetition_time, echo_time, alpha_deg_L)

    # write T2 map
    sitk.WriteImage(t2_map, relaxometry_folder + t2_map_file_name)

    # mask T2 map
    masked_map = rf.mask_map(t2_map, mask)

    # write masked T2 map
    sitk.WriteImage(masked_map, relaxometry_folder + t2_map_mask_file_name)

def calculate_t2_maps(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(calculate_t2_maps_s, all_image_data)
    print ("-> T2 maps calculated")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def show_t2_maps (image_data, view_modality):
    
    if view_modality == 0:
        show_t2_maps_static(image_data)
        trick = 'Figure'
        return trick  # need a return for the interactive function when view_modality == 1. Done to avoid if/else on notebook 
    elif view_modality == 1:
        fig = show_t2_maps_interactive(image_data)
        return fig
    else:
        print("view_modality has to be 0 for static visualization or 1 for interactive visualization")
        
        

def show_t2_maps_static(all_image_data):

    n_of_images   = len(all_image_data)
    img_LW        = 6
    figure_width  = img_LW * 3
    figure_length = img_LW * n_of_images
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (n_of_images can be larger)
    fig.tight_layout() # avoids subplots overlap
    # subplots characteristics
    n_of_columns = 3
    n_of_rows    = n_of_images
    axis_index   = 1


    for i in range(0, n_of_images):

        # get paths and file names of the current image
        preprocessed_folder   = all_image_data[i]["preprocessed_folder"]
        i1_file_name          = all_image_data[i]["i1_file_name"]
        relaxometry_folder    = all_image_data[i]["relaxometry_folder"]
        t2_map_mask_file_name = all_image_data[i]["t2_map_mask_file_name"]
        image_name_root       = all_image_data[i]["image_name_root"]

        # read images
        img = sitk.ReadImage(preprocessed_folder + i1_file_name)
        map = sitk.ReadImage(relaxometry_folder  + t2_map_mask_file_name)

        # images from simpleitk to numpy
        img_py = sitk.GetArrayFromImage(img)
        map_py = sitk.GetArrayFromImage(map)


        # extract slices at 2/5, 3/5, and 4/5 of the image size
        size = np.size(map_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                first_value = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                last_value = b
                break

        slice_step = int ((last_value-first_value)/4)
        slice_ID   = (first_value + slice_step, first_value + 2*slice_step, first_value + 3*slice_step)

        for a in range (0,len(slice_ID)):

            # create subplot
            ax1 = fig.add_subplot(n_of_rows,n_of_columns,axis_index)

            # get slices
            slice_img_py = img_py[:,:,slice_ID[a]]
            slice_map_py = map_py[:,:,slice_ID[a]]
            slice_map_masked = np.ma.masked_where(slice_map_py == 0, slice_map_py)

            # show image
            ren1 = ax1.imshow(slice_img_py    , 'gray', interpolation=None, origin='lower')
            ren2 = ax1.imshow(slice_map_masked, 'jet' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            clb = plt.colorbar(ren2, orientation='vertical', shrink=0.60, ticks=[0, 20, 40, 60, 80, 100])
            clb.ax.set_title('[ms]')
            ax1.set_title(str(i+1) + ". " + image_name_root + " - Slice: " + str(slice_ID[a]))
            ax1.axis('off')

            axis_index = axis_index + 1



def show_t2_maps_interactive(all_image_data):

    for i in range(0, len(all_image_data)):

        # get paths and file names of the current image
        preprocessed_folder   = all_image_data[i]["preprocessed_folder"]
        i1_file_name          = all_image_data[i]["i1_file_name"]
        relaxometry_folder    = all_image_data[i]["relaxometry_folder"]
        t2_map_mask_file_name = all_image_data[i]["t2_map_mask_file_name"]
        image_name_root       = all_image_data[i]["image_name_root"]

        # read images
        img = sitk.ReadImage(preprocessed_folder + i1_file_name)
        map = sitk.ReadImage(relaxometry_folder  + t2_map_mask_file_name)

        # images from simpleitk to numpy
        img_py = sitk.GetArrayFromImage(img)
        map_py = sitk.GetArrayFromImage(map)


        # extract slices at 2/5, 3/5, and 4/5 of the image size
        size = np.size(map_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                first_value = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = map_py[:,:,b]
            if np.sum(slice) != 0:
                last_value = b
                break

        slice_step = int ((last_value-first_value)/4)
        slice_ID   = (first_value + slice_step, first_value + 2*slice_step, first_value + 3*slice_step)

        # create figure
        plt.rcParams['figure.figsize'] = [20, 15]  
        fig, ax = plt.subplots(nrows=1, ncols=4) 
        
        # static images
        for a in range (0,len(slice_ID)):

            # create subplot
            ax1 = ax[a+1]

            # get slices
            slice_img_py = img_py[:,:,slice_ID[a]]
            slice_map_py = map_py[:,:,slice_ID[a]]
            slice_map_masked = np.ma.masked_where(slice_map_py == 0, slice_map_py)

            # show image
            ax1.imshow(slice_img_py    , 'gray', interpolation=None, origin='lower')
            ax1.imshow(slice_map_masked, 'jet' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            ax1.set_title("Slice: " + str(slice_ID[a]))
            ax1.axis('off')
            plt.close(fig) # avoid to show them several times in notebook
            
        # interactive image
        ax_i = ax[0]
        if i == 0:
            final_box = browse_images(img_py, map_py, ax_i, fig, image_name_root, last_value, slice_ID)
        else:
            new_box = browse_images(img_py, map_py, ax_i, fig, image_name_root, last_value, slice_ID)
            final_box = VBox([final_box,new_box]);   
            
    return final_box


def show_t2_graph(all_image_data):

    # calculate average and standard deviation
    average = []
    std_dev  = []
    for i in range(0, len(all_image_data)):
        # file name
        relaxometry_folder = all_image_data[i]["relaxometry_folder"]
        t2_map_file_name     = all_image_data[i]["t2_map_file_name"]
        # read image
        t2_map = sitk.ReadImage(relaxometry_folder + t2_map_file_name)
        # from SimpleITK to numpy
        t2_map_py = sitk.GetArrayFromImage(t2_map)
        # from 3D matrix to array
        t2_map_py_array = np.reshape(t2_map_py, np.size(t2_map_py,0)*np.size(t2_map_py,1)*np.size(t2_map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(t2_map_py_array != 0)
        t1_rho_vector = t2_map_py_array[index]
        # calculate average and std_dev
        average.append(np.average(t1_rho_vector))
        std_dev.append(np.std(t1_rho_vector))

    average = np.asarray(average)
    std_dev = np.asarray(std_dev)
    x       = np.arange(len(all_image_data))

    # figure size
    figure_width  = 18
    figure_length = 8
    plt.rcParams['figure.figsize'] = [figure_width, figure_length] # figsize=() seems to be ineffective on notebooks

    # error bar
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (n_of_images can be larger)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.errorbar(x, average, yerr=std_dev, linestyle='None', marker='o')

    # set ticks and labels
    plt.xticks(x)
    image_names= []
    for i in range(0, len(all_image_data)):
        image_root, image_ext = os.path.splitext(all_image_data[i]["t2_map_file_name"])
        image_names.append(image_root)
    ax.set_xticklabels(image_names, rotation='vertical')
    ax.set_ylabel('t2 [ms]')

    # show
    plt.show()


def show_t2_table(all_image_data, output_file_name):

    # read and calculate values for table
    image_names = []
    average     = []
    std_dev     = []

    for i in range(0, len(all_image_data)):
        # file name
        relaxometry_folder    = all_image_data[i]["relaxometry_folder"]
        t2_map_file_name      = all_image_data[i]["t2_map_file_name"]
        image_root, image_ext = os.path.splitext(all_image_data[i]["t2_map_file_name"])
        image_names.append(image_root)
        # read image
        t2_map = sitk.ReadImage(relaxometry_folder + t2_map_file_name)
        # from SimpleITK to numpy
        t2_map_py = sitk.GetArrayFromImage(t2_map)
        # from 3D matrix to array
        t2_map_py_array = np.reshape(t2_map_py, np.size(t2_map_py,0)*np.size(t2_map_py,1)*np.size(t2_map_py,2))
        # get only non zero values (= masked cartilage)
        index = np.where(t2_map_py_array != 0)
        t2_vector = t2_map_py_array[index]
        # calculate average and std_dev
        average.append(np.average(t2_vector))
        std_dev.append(np.std(t2_vector))

    # create table
    table = pd.DataFrame(
        {
            "subjects" : t2_map_file_name,
            "average"  : average,
            "std_dev"  : std_dev
        }
    )
    table.index = np.arange(1,len(table)+1) # First ID column starting from 1
    table = table.round(2) #show 2 decimals

    # show all the lines of the table
    data_dimension = table.shape # get number of rows
    pd.set_option("display.max_rows",data_dimension[0]) # show all the rows

    # save table as csv
    #now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    #csvFileName = all_image_data[0]["relaxometry_folder"] + now + "_t2.csv"
    #table.to_csv(csvFileName,  index = False)
    table.to_csv(output_file_name,  index = False)
    print("Table saved as: " + output_file_name)

    return table





    

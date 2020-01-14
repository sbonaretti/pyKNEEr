# Serena Bonaretti, 2018-

"""
Module with the functions called by the notebook segmentation.ipynb

There are three steps: 
    - preparing reference: reference image is dilated and tranformed to a levelset image for continuous intensities
    - segmenting bone
    - segmenting cartilage
The last two steps have three inner steps:
    - register bone to reference
    - invert transformation
    - warp reference mask to moving image using inverted transformation. The bone warping is not needed for cartilage segmentation. It is executed just for check in case of segmentation failure.
    
The atlas-based segmentation is based on elastix and transformix, called in the file elastix_transformix.py 
There is a function

Functions are in pairs for parallelization. Example:
register_bone_to_reference launches register_bone_to_reference_s as many times as the length of all_image_data (subtituting a for loop).
pool.map() takes care of sending one single element of the list all_image_data (all_image_data[i]) to register_bone_to_reference_s, as if it was a for loop.

"""

import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import SimpleITK      as sitk
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
    import elastix_transformix
    import sitk_functions  as sitkf

else:
    # uses current package visibility
    from . import elastix_transformix
    from . import sitk_functions  as sitkf


# ---------------------------------------------------------------------------------------------------------------------------
# PREPARING REFERENCE -------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def prepare_reference(all_image_data):

    """
    The reference image is dilated and transformed to level set (see the function prepare_reference in elastix_transformix.py)
    
    """
    image_data  = all_image_data[0]

    # in "newsubject" there is only one reference
    if image_data["registration_type"] == "newsubject":

        # get paths and file names of the first image
        image_data  = all_image_data[0]
        print (image_data["reference_name"])

        # instanciate bone class and prepare reference
        image_data["current_anatomy"] = image_data["bone"]
        bone = elastix_transformix.bone()
        bone.prepare_reference (image_data)

        # instanciate cartilage class and prepare reference
        image_data["current_anatomy"] = image_data["cartilage"]
        cartilage = elastix_transformix.cartilage()
        cartilage.prepare_reference (image_data)

    # in "longitudinal" and "multimodal" there are several references
    elif image_data["registration_type"] == "longitudinal" or image_data["registration_type"] == "multimodal":

        for i in range(0,len(all_image_data)):

            # get paths and file names of the first image
            image_data  = all_image_data[i]
            print (image_data["reference_name"])

            # instanciate bone class and prepare reference
            image_data["current_anatomy"] = image_data["bone"]
            bone = elastix_transformix.bone()
            bone.prepare_reference (image_data)

            # instanciate cartilage class and prepare reference
            image_data["current_anatomy"] = image_data["cartilage"]
            cartilage = elastix_transformix.cartilage()
            cartilage.prepare_reference (image_data)


    print ("-> Reference preparation completed")



# ---------------------------------------------------------------------------------------------------------------------------
# SEGMENTING BONE -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def register_bone_to_reference_s(image_data):

#    print ("-> Registering " + image_data["moving_root"])

    # instantiate bone class and provide bone to segment
    image_data["current_anatomy"] = image_data["bone"]
    bone = elastix_transformix.bone()

    # register
    if image_data["registration_type"] == "newsubject":
        bone.rigid     (image_data)
        bone.similarity(image_data)
        bone.spline    (image_data)
    elif image_data["registration_type"] == "longitudinal":
        bone.rigid     (image_data)

        bone.spline(image_data)
    elif image_data["registration_type"] == "multimodal":
        bone.rigid     (image_data)


def register_bone_to_reference(all_image_data, n_of_processes):

    # print
    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(register_bone_to_reference_s, all_image_data)
    print ("-> Registration completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def invert_bone_transformations_s(image_data):

#    print ("-> Inverting transformation of " + image_data["moving_root"])

    # instantiate bone class and provide bone to segment
    image_data["current_anatomy"] = image_data["bone"]
    bone = elastix_transformix.bone()

    # invert transformations
    if image_data["registration_type"] == "newsubject":
        bone.i_rigid     (image_data)
        bone.i_similarity(image_data)
        bone.i_spline    (image_data)
    elif image_data["registration_type"] == "longitudinal":
        bone.i_rigid     (image_data)
        bone.i_spline    (image_data)
    elif image_data["registration_type"] == "multimodal":
        bone.i_rigid     (image_data)

def invert_bone_transformations(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(invert_bone_transformations_s, all_image_data)
    print ("-> Inversion completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def warp_bone_mask_s(image_data):

#    print ("-> Warping bone mask of " + image_data["moving_root"])

    # instantiate bone class and provide bone to segment
    image_data["current_anatomy"] = image_data["bone"]
    bone = elastix_transformix.bone()

    # get moving image properties (size and spacing for modify_transformation(rigid) and transformix)
    moving_name  = image_data["moving_folder"] + image_data["moving_name"]
    moving_image = sitk.ReadImage(moving_name)
    image_data["image_size"]      = moving_image.GetSize()
    image_data["image_spacing"]   = moving_image.GetSpacing()

    # modify transformations for mask warping
    if image_data["registration_type"] == "newsubject":
        bone.modify_transformation(image_data,"rigid")
        bone.modify_transformation(image_data,"similarity")
        bone.modify_transformation(image_data,"spline")
    elif image_data["registration_type"] == "longitudinal":
        bone.modify_transformation(image_data,"rigid")
        bone.modify_transformation(image_data,"spline")
    elif image_data["registration_type"] == "multimodal":
        #change filename of something
        bone.modify_transformation(image_data,"rigid")

    # warp mask
    if image_data["registration_type"]   == "newsubject":
        bone.t_spline    (image_data)
        bone.t_similarity(image_data)
        bone.t_rigid     (image_data)
    elif image_data["registration_type"] == "longitudinal":
        bone.t_spline    (image_data)
        # change filename of something
        bone.t_rigid     (image_data)
    elif image_data["registration_type"] == "multimodal":
        # change filename of something
        bone.t_rigid     (image_data)

    # levelsets to binary
    anatomy          = image_data["current_anatomy"]
    input_file_name  = image_data["i_registered_sub_folder"] + image_data[anatomy + "m_rigid_name"]
    output_file_name = image_data["segmented_folder"]        + image_data[anatomy + "mask"]
    mask = sitk.ReadImage(input_file_name)
    mask = sitkf.levelset2binary(mask)
    mask = sitk.Cast(mask,sitk.sitkInt16) # cast to int16 to reduce file size
    sitk.WriteImage(mask, output_file_name)

def warp_bone_mask(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(warp_bone_mask_s, all_image_data)
    print ("-> Warping completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



# ---------------------------------------------------------------------------------------------------------------------------
# SEGMENTING CARTILAGE ------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
def register_cartilage_to_reference_s(image_data):

#    print ("-> Registering " + image_data["moving_root"])

    if image_data["registration_type"] == "newsubject" or image_data["registration_type"] == "longitudinal":
        # instantiate cartilage class and provide cartilage to segment
        image_data["current_anatomy"] = image_data["cartilage"]
        cartilage = elastix_transformix.cartilage()

        # register
        cartilage.spline(image_data)
    else:
        print ("-> Step skipped")

def register_cartilage_to_reference(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(register_cartilage_to_reference_s, all_image_data)
    print ("-> Registration completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def invert_cartilage_transformations_s(image_data):

#    print ("-> Inverting transformation of " + image_data["moving_root"])

    if image_data["registration_type"] == "newsubject" or image_data["registration_type"] == "longitudinal":

        # instantiate cartilage class and provide cartilage to segment
        image_data["current_anatomy"] = image_data["cartilage"]
        cartilage = elastix_transformix.cartilage()

        # invert transformations
        cartilage.i_spline (image_data)

    elif image_data["registration_type"] == "multimodal":
        print ("-> Step skipped")

def invert_cartilage_transformations(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(invert_cartilage_transformations_s, all_image_data)
    print ("-> Inversion completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



def warp_cartilage_mask_s(image_data):

#    print ("-> Warping cartilage mask of " + image_data["moving_root"])

    # instantiate cartilage class and provide cartilage to segment
    image_data["current_anatomy"] = image_data["cartilage"]
    cartilage = elastix_transformix.cartilage()

    # get moving image properties (size and spacing for transformix)
    moving_name  = image_data["moving_folder"] + image_data["moving_name"]
    moving_image = sitk.ReadImage(moving_name)
    image_data["image_size"]      = moving_image.GetSize()
    image_data["image_spacing"]   = moving_image.GetSpacing()

    if image_data["registration_type"] == "newsubject":

        # modify transformations for mask warping
        cartilage.modify_transformation(image_data,"spline")

        # warp mask
        cartilage.t_spline    (image_data)
        cartilage.t_similarity(image_data)
        cartilage.t_rigid     (image_data)

    elif image_data["registration_type"] == "longitudinal":

        # modify transformations for mask warping
        cartilage.modify_transformation(image_data,"spline")

        # warp mask
        cartilage.t_spline    (image_data)
        # change some filename here
        cartilage.t_rigid     (image_data)

    elif image_data["registration_type"] == "multimodal":
        cartilage.t_rigid     (image_data)


    # levelsets to binary
    anatomy          = image_data["current_anatomy"]
    input_file_name  = image_data["i_registered_sub_folder"] + image_data[anatomy + "m_rigid_name"]
    output_file_name = image_data["segmented_folder"]        + image_data[anatomy + "mask"]
    mask = sitk.ReadImage(input_file_name)
    mask = sitkf.levelset2binary(mask)
    mask = sitk.Cast(mask,sitk.sitkInt16) # cast to int16 to reduce file size
    sitk.WriteImage(mask, output_file_name)

def warp_cartilage_mask(all_image_data, n_of_processes):

    start_time = time.time()
    pool = multiprocessing.Pool(processes=n_of_processes)
    pool.map(warp_cartilage_mask_s, all_image_data)
    print ("-> Warping completed")
    print ("-> The total time was %.2f seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))



# ---------------------------------------------------------------------------------------------------------------------------
# VISUALIZING SEGMENTED CARTILAGE -------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def show_segmented_images (image_data, view_modality):
    
    if view_modality == 0:
        show_segmented_images_static(image_data)
        trick = 'Figure'
        return trick  # need a return for the interactive function when view_modality == 1. Done to avoid if/else on notebook 
    elif view_modality == 1:
        fig = show_segmented_images_interactive(image_data)
        return fig
    else:
        print("view_modality has to be 0 for static visualization or 1 for interactive visualization")
        


def show_segmented_images_static(all_image_data): 

    n_of_images  = len(all_image_data)
    img_LW       = 4
    figure_width = img_LW * 3
    fig_length   = img_LW * n_of_images
    plt.rcParams['figure.figsize'] = [figure_width, fig_length] # figsize=() seems to be ineffective on notebooks
    fig     = plt.figure() # cannot call figures inside the for loop because python has a max of 20 figures (n_of_images can be larger)
    fig.tight_layout() # avoids subplots overlap
    # subplots characteristics
    n_of_columns = 3
    n_of_rows    = n_of_images
    axis_index   = 1

    for i in range(0, n_of_images):

        # get paths and file names of the current image
        image_data                    = all_image_data[i]
        image_data["current_anatomy"] = image_data["cartilage"]
        anatomy                       = image_data["current_anatomy"]
        moving_file_name              = image_data["moving_folder"]    + image_data["moving_name"]
        mask_file_name                = image_data["segmented_folder"] + image_data[anatomy + "mask"]
        moving_root                   = image_data["moving_root"]

        # read the images
        moving = sitk.ReadImage(moving_file_name)
        mask   = sitk.ReadImage(mask_file_name)

        # images from simpleitk to numpy
        moving_py = sitk.GetArrayFromImage(moving)
        mask_py   = sitk.GetArrayFromImage(mask)

        # extract slices at 2/5, 3/5, and 4/5 of the image size
        size = np.size(mask_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = mask_py[:,:,b]
            if np.sum(slice) != 0:
                first_value = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = mask_py[:,:,b]
            if np.sum(slice) != 0:
                last_value = b
                break

        slice_step = int ((last_value-first_value)/4)
        sliceID = (first_value + slice_step, first_value + 2*slice_step, first_value + 3*slice_step)

        for a in range (0,len(sliceID)):

            # create subplot
            ax1 = fig.add_subplot(n_of_rows,n_of_columns,axis_index)

            # get slices
            slice_moving_py   = moving_py[:,:,sliceID[a]]
            slice_mask_py     = mask_py[:,:,sliceID[a]]
            slice_mask_masked = np.ma.masked_where(slice_mask_py == 0, slice_mask_py)

            # show image
            ax1.imshow(slice_moving_py,   'gray', interpolation=None, origin='lower')
            ax1.imshow(slice_mask_masked, 'hsv' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            ax1.set_title(moving_root + " - Slice: " + str(sliceID[a]))
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
        ax_i.imshow(slice_mask_masked, 'hsv' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
        ax_i.set_title(moving_root)
        ax_i.axis('off')
        display(fig)
        
    # link sliders and its function
    slider_image = interactive(view_image, 
                         slider = widgets.IntSlider(min=0, 
                                                      max=last_value, 
                                                      value=sliceID[1],
                                                      step=1,
                                                      continuous_update=False, # avoids intermediate image display
                                                      readout=False,
                                                      layout=Layout(width='180px'),
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

def show_segmented_images_interactive(all_image_data):
    
    # for each image
    for i in range(0, len(all_image_data)):

        # get paths and file names of the current image
        image_data                    = all_image_data[i]
        image_data["current_anatomy"] = image_data["cartilage"]
        anatomy                       = image_data["current_anatomy"]
        moving_file_name              = image_data["moving_folder"]    + image_data["moving_name"]
        mask_file_name                = image_data["segmented_folder"] + image_data[anatomy + "mask"]
        moving_root                   = image_data["moving_root"]

        # read the images
        moving = sitk.ReadImage(moving_file_name)
        mask   = sitk.ReadImage(mask_file_name)

        # images from simpleitk to numpy
        moving_py = sitk.GetArrayFromImage(moving)
        mask_py   = sitk.GetArrayFromImage(mask)

        # extract slices at 2/5, 3/5, and 4/5 of the image size
        size = np.size(mask_py,2)
        # get the first slice of the mask in the sagittal direction
        for b in range(0,int(size/2)):
            slice = mask_py[:,:,b]
            if np.sum(slice) != 0:
                first_value = b
                break
        # get the last slice of the mask in the sagittal direction
        for b in range(size-1,int(size/2),-1):
            slice = mask_py[:,:,b]
            if np.sum(slice) != 0:
                last_value = b
                break

        slice_step = int ((last_value-first_value)/4)
        sliceID = (first_value + slice_step, first_value + 2*slice_step, first_value + 3*slice_step)

        # create figure
        plt.rcParams['figure.figsize'] = [20, 15]  
        fig, ax = plt.subplots(nrows=1, ncols=4) 
        
        
         # static images
        for a in range (0,len(sliceID)):

            # create subplot
            ax1 = ax[a+1]

            # get slices
            slice_moving_py   = moving_py[:,:,sliceID[a]]
            slice_mask_py     = mask_py[:,:,sliceID[a]]
            slice_mask_masked = np.ma.masked_where(slice_mask_py == 0, slice_mask_py)

            # show image
            ax1.imshow(slice_moving_py,   'gray', interpolation=None, origin='lower')
            ax1.imshow(slice_mask_masked, 'hsv' , interpolation=None, origin='lower', alpha=1, vmin=0, vmax=100)
            ax1.set_title("Slice: " + str(sliceID[a]))
            ax1.axis('off')
            plt.close(fig) # avoid to show them several times in notebook
            
        # interactive image
        ax_i = ax[0]
        if i == 0:
            final_box = browse_images(moving_py, mask_py, ax_i, fig, moving_root, last_value, sliceID)
        else:
            new_box = browse_images(moving_py, mask_py, ax_i, fig, moving_root, last_value, sliceID)
            final_box = VBox([final_box,new_box]);   
            
    return final_box
        
        


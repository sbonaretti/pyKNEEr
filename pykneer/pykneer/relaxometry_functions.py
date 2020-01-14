# Serena Bonaretti, 2018

""" 
Functions to calculate cartilage relaxometry. 
They are separeted in: 
    - Functions to calculate linear fitting
    - Functions to calculate exponential fitting
    - Functions to calculate T2 using EPG modeling
"""

import math
import numpy     as np
import scipy as sp
import scipy.optimize
import SimpleITK as sitk


#    #small example for testing
#    # linear fitting
#    y       = np.array([349, 208, 134, 44]) # these are the intensities of one single voxel (same coordinates) in the four different images
#    y_log   = np.log(y)
#    tsl     = np.array([1, 10, 30, 60])
#    param   = np.polyfit(tsl, y_log, 1)
#    t1rho = - 1 / param[0]
#    t1rho
#    # exponential fitting
#    https://stackoverflow.com/questions/3938042/fitting-exponential-decay-with-no-initial-guessing


# ---------------------------------------------------------------------------------------------------------------------------
#  LINEAR FITTING -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def calculate_fitting_maps_lin(tsl, list_of_arrays):

    '''
    function to calculate fitting - same as in Osirix
    tsl is a numpy array
    list_of_arrays is a list of n arrays, where each array contains an image (transformed from matrix to array)
    voxel-wise exponential fitting is calculated as linear fitting after tranforming values to log, like in the paper:
    Borthakur A. et al., In Vivo Measurement of T1rho Dispersion in the Human Brain at 1.5 Tesla. 2004
    '''

    # clean up and log
    for a in range(0, len(list_of_arrays)):
        # make sure they are all the same type
        current_array = np.float32(list_of_arrays[a])
        # avoid 0.0s to avoid issues with log
        current_array[current_array == 0] = 0.001
        # transform voxels to log to calculate the linear fitting
        current_array = np.log(current_array)
        # reassign to list_of_arrays
        list_of_arrays[a] = current_array

    # calculate the fitting
    param = np.polyfit(tsl, list_of_arrays, 1)

    # slopes are the first parameter
    slopes = param[0]

    # avoid dividing by 0 when calculating t1rho
    slopes[slopes == 0] = 0.001

    # calculate the relaxometry time
    map_py_v = -1 / slopes

    # uniform to output of Osirix plugin (Select 4 images -> 4D Viewer -> Plugins -> Image Filters -> T2 Fit Map)
    map_py_v = np.round(map_py_v,0)  # values are integers
    map_py_v[map_py_v < 0]    = 0    # values less than 0 are 0
    map_py_v[map_py_v > 2000] = 2000 # values larger than 2000 are 2000
                                     # (when voxel-wise values are not in descending order, the fitting slopes are "wrong"

    return map_py_v


# ---------------------------------------------------------------------------------------------------------------------------
#  EXPONENTIAL FITTING ------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def exp_func(x, A_0, K_0):

    '''
    exponential function for the optimizer in calculate_fitting_maps_exp
    A_0 * np.exp(- K_0 * x) can go in overflow
    To avoid overflow: np.exp(np.log(A_0) - K_0 * x) (the optimization behaves in the same way)
    '''

    # it can happen that for 1 or 2 voxels I get error (A_0 < 0). This might happen when bone voxels are included in the cartilage mask by mistake
    # the error does not affect the computation because in the next optimization loop the optimization algorithm goes back to positive values of A_O
    # the following command just avoids print the warning to screen
    np.seterr(invalid='ignore', over='ignore') # to be improved in the next releases

    # calculate fitting
    output = np.exp(np.log(A_0) - K_0 * x)
    return output

def calculate_fitting_maps_exp(tsl, list_of_arrays):

    '''
    function to calculate voxel-wise exponential fitting
    tsl is a numpy array
    list_of_arrays is a list of n arrays, where each array contains an image (transformed from matrix to array)
    '''

    # initialize the parameters for the function exp_func
    A_0 = 10  # parameters used in exp_func
    K_0 = 0.1 # parameters used in exp_func

    # initialize relaxation time
    map_py_v = np.full(np.size(list_of_arrays[0],0), 0)

    # for each voxel
    for i in range (0,np.size(map_py_v,0)):

        exception_flag = 0

        # extract the intensities from the 4 arrays for this index position
        #y = np.array([array1[i], array2[i], array3[i], array4[i]])
        y = []
        for a in range(0,len(list_of_arrays)):
            y.append(list_of_arrays[a][i])
        y = np.array(y, dtype=float) # to avoid in overflow in following fitting

        # extract the fitting parameters
        try:
            # the exponential curve must be in the first quadrant. This constrain can be set by adding bounds. However,
            # the computational time increases from 30s to 9min, and the method must change, from ml to dogbox ()
            # bounds: A_0 must be positive, K_0 can be anything
            #param_bounds = ((0.00001, -np.inf),(np.inf, np.inf)) # ((lower_bound_A_0, lower_bound_K_0), (upper_bound_A_0, upper_bound_K_0))
            #param_exp, param_cov = sp.optimize.curve_fit(exp_func, tsl, y, bounds=param_bounds, method = 'dogbox')
            # it is
            param_exp, param_cov = sp.optimize.curve_fit(exp_func, tsl, y)

        except RuntimeError:
            #print("Error - curve_fit failed for values: " +  str(array1[i]) + " " +  str(array2[i]) + " " + str(array3[i]) + " " + str(array4[i]) +
            #      " at index " + str(i) + "of masked vector " " - 0 was assigned")
            exception_flag = 1

        # calculate relaxation time
        if exception_flag == 0:
            #A = param_exp[0]
            K = param_exp[1]
            map_voxel =  1 / K
            map_py_v[i] = map_voxel

    # uniform to output of Osirix plugin (Select 4 images -> 4D Viewer -> Plugins -> Image Filters -> T2 Fit Map)
    map_py_v = np.round(map_py_v,0)  # values are integers
    map_py_v[map_py_v < 0]    = 0    # values less than 0 are 0
    map_py_v[map_py_v > 2000] = 2000 # values larger than 2000 are 2000


    return map_py_v



# ---------------------------------------------------------------------------------------------------------------------------
# EPG MODELING (T2 FROM DESS - Bragi's) -------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def calculate_t2_maps_from_dess(echo_1L, echo_2L, repetition_time, echo_time, alpha_deg_L):

    '''
    function courtesy of Bragi Sveinsson (translated from Matlab to Python)
    Paper: A Simple Analytic Method for Estimating T2 in the Knee from DESS
           B Sveinsson, AS Chaudhari, GE Gold, and BA Hargreaves
           Magn Reson Imaging. 2017 May;38:63-70
    '''

    # images echo_1L and echo_2L are in sitk

    # constant values
    assumed_T1 = 1.2
    map_min    = 0
    map_max    = 100
    map_mult   = 1000

    # calculate TR and TE
    TR = repetition_time / 1000
    TE = echo_time       / 1000

    # convert echos to np
    echo_1L_py = sitk.GetArrayFromImage(echo_1L)
    echo_2L_py = sitk.GetArrayFromImage(echo_2L)

    # allocate T2 map
    map_py = np.zeros((echo_1L_py.shape[0], echo_1L_py.shape[1], echo_1L_py.shape[2]), dtype=int)

    # compute map
    for i in range(0, echo_1L.GetSize()[0]):

        # get slice
        echo_1L_slice = echo_1L_py[:,:,i]
        echo_2L_slice = echo_2L_py[:,:,i]

        # convert to float and change 0s into nonZeros for division
        echo_1L_slice = echo_1L_slice.astype(float)
        echo_2L_slice = echo_2L_slice.astype(float)
        echo_1L_slice[echo_1L_slice == 0.0] = 0.0001
        echo_2L_slice[echo_2L_slice == 0.0] = 0.0001

        # compute fit
        map_slice = -2*(TR-TE)/ np.log(echo_2L_slice/  (echo_1L_slice * (math.sin(math.radians(alpha_deg_L/2))) **2 * (1 + math.exp(-TR/assumed_T1))/ (1 - math.cos(math.radians(alpha_deg_L)) * math.exp(-TR/assumed_T1))  )  )

        # mask out noise
        M = np.ones(echo_1L_slice.shape)
        M[echo_1L_slice < 0.15 * np.amax(abs(echo_1L_slice))] = 0
        map_slice = map_slice * M

        # adjust map for visualization
        map_slice = map_slice * map_mult
        map_slice[map_slice<map_min] = map_min
        map_slice[map_slice>map_max] = map_max

        # put map slice into map matrix
        map_py[:,:,i] = map_slice

    # transform map_py to map (SimpleITK)
    T2_map = sitk.GetImageFromArray(map_py)
    T2_map.SetSpacing  (echo_1L.GetSpacing())
    T2_map.SetOrigin   (echo_1L.GetOrigin())
    T2_map.SetDirection(echo_1L.GetDirection())
    T2_map = sitk.Cast(T2_map,sitk.sitkInt16)

    return T2_map


def mask_map(T2_map, mask):

    '''
    function to mask an image
    '''

    # from SimpleITK to np
    T2_map_py = sitk.GetArrayFromImage(T2_map)
    mask_py = sitk.GetArrayFromImage(mask)

    # mask map
    masked_map_py = np.where(mask_py==1, T2_map_py, 0)

    # transform masked_map_py to masked_map (SimpleITK)
    masked_map = sitk.GetImageFromArray(masked_map_py)
    masked_map.SetSpacing  (T2_map.GetSpacing())
    masked_map.SetOrigin   (T2_map.GetOrigin())
    masked_map.SetDirection(T2_map.GetDirection())
    masked_map = sitk.Cast(masked_map,sitk.sitkInt16)

    return masked_map

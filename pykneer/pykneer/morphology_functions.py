# Serena Bonaretti, 2018

""" 
Functions to calculate cartilage thickness. 
They are separeted in three groups: 
    - Functions to separate cartilage sufaces:
        - separate_cartilage calls separate_cartilage_slice
    - Functions to flatten cartilage for 2D visualization:
        flatten_point_cloud calls rotate_to_x and flatten_surface
    - Function to associate thickness to 2D surface after flattening: 
        flatten_thickness
    - Functions to calculate cartilage thickness:
        - nearest_neighbor_thickness calls find_closest_point
"""

import numpy     as np
import SimpleITK as sitk
import skimage   as ski
from skimage.measure import find_contours

from scipy import optimize
from scipy import ndimage as ndi

import time


# pyKNEER imports 
# ugly way to use relative vs. absolute imports when developing vs. when using package - cannot find a better way
if __package__ is None or __package__ == '':
    # uses current directory visibility
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    #cyl_fitting_dir = os.path.dirname(os.path.realpath(__file__)) + "cylinder_fitting"
    from cylinder_fitting import fit

else:
    # uses current package visibility
    from .cylinder_fitting import fit




# ---------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO SEPARATE CARTILAGE SURFACES ----------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

# Functions to calculate circle center and radius. From: https://gist.github.com/lorenzoriano/6799568
def calc_R(x,y, x_c, y_c):
    # calculate the distance of each 2D points from the center (x_c, y_c)
    return np.sqrt((x-x_c)**2 + (y-y_c)**2)

def f(c, x, y):
    # calculate the algebraic distance between the data points and the mean circle centered at c=(x_c, y_c)
    Ri = calc_R(x, y, *c)
    return Ri - Ri.mean()

def leastsq_circle(x,y): # from: https://gist.github.com/lorenzoriano/6799568
    # coordinates of the barycenter
    x_m = np.mean(x)
    y_m = np.mean(y)
    center_estimate = x_m, y_m
    center, ier = optimize.leastsq(f, center_estimate, args=(x,y))
    x_c, y_c = center
    Ri       = calc_R(x, y, *center)
    R        = Ri.mean()
    return x_c, y_c, R


# Functions to calculate segment intersections. From: https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
class Point: #
	def __init__(self,x,y):
		self.x = x
		self.y = y

def ccw(A,B,C):
	return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

def intersect(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

# ---------------------------------------------------------------------------------------------------------------------------


def separate_cartilage_slice(x_c, y_c, x, y):

    # check if radius connecting center and countour points intersects contour segments.
    # if yes, it's bone cartilage, if not, it is articular cartilage

    bone_cart_x = []
    bone_cart_y = []
    point_index = []

    # for each point of the contour
    for j in range(0, len(x)):

        # get the center and the current contour point
        center        = Point(x_c, y_c)
        contour_point = Point(x[j],y[j])

        # in the contour coordinates, delete the current contour_point and copy the first point to the end of the array
        x_temp = x
        x_temp = np.delete(x_temp,j)
        x_temp = np.append(x_temp, x[0])
        y_temp = y
        y_temp = np.delete(y_temp,j)
        y_temp = np.append(y_temp, x[0])

        # look for the intersection
        for k in range(0, len(x)-1):
            contour_point_A = Point(x[k]  ,y[k])
            contour_point_B = Point(x[k+1],y[k+1])
            intersection = intersect(center,contour_point,contour_point_A,contour_point_B)

            # if there is intersection, it is bone cartilage
            if intersection == True:
                bone_cart_x.append(x[j])
                bone_cart_y.append(y[j])
                point_index.append(j)
                break

    # convert bone cartilage to numpy
    bone_cart_x = np.asarray(bone_cart_x)
    bone_cart_y = np.asarray(bone_cart_y)
    bone_cart   = np.array((bone_cart_x, bone_cart_y)).T

    # get articular cartilage
    point_index = np.asarray(point_index)
    arti_cart_x = x
    arti_cart_x = np.delete(arti_cart_x,point_index)
    arti_cart_y = y
    arti_cart_y = np.delete(arti_cart_y,point_index)
    arti_cart   = np.array((arti_cart_x, arti_cart_y)).T

    return bone_cart, arti_cart



def separate_cartilage (mask):

    min_area             = 15
    slice_with_contour_S = []
    bone_cart            = []
    arti_cart            = []

    # mask from SimpleITK to python
    mask_py = sitk.GetArrayFromImage(mask)

    # get contours
    for i in range(0, mask_py.shape[2]): # to be //ized? check how long it takes
#    for i in range(0, 30):

        # get slice
        slice = mask_py[:,:,i]

        # if slice contains the label (i.e. 1 in binary image)
        if sum(sum(slice)) != 0:

            # contours containers
            contour_S = []                # list:    each cell of the list contains a contour (for the slices with several regions)
                                          #          used to separate bone and articular cartilage (small regions are not considered)
            contour_A = np.ndarray((1,2)) # nparray: contains the the contour of all the regions of the  slice
                                          #          used to calculate the circle center (small regions are considered)

            # find number of labelled regions (at the edges cartilage can be broken in pieces)
            regions, n_of_regions = ndi.label(slice)
            regions = np.asarray(regions)

            for w in range (0,n_of_regions):

                # get binary region
                temp_slice = np.full((slice.shape[0], slice.shape[1]), 0)
                temp_slice [regions == w+1] = 1

                # consider only regions with area > min_area
                if sum(sum(temp_slice)) < min_area:
                    continue

                else:
                    # get region contour
                    contour = ski.measure.find_contours(temp_slice, 0.5)

                    # add region contour separately for region (to discriminate bone and articular cartilage)
                    contour_S.append(contour)

                    # put all (A) contours together (to find the circle center)
                    contour   = contour[0]
                    contour_A = np.vstack((contour_A,contour))


                # if the areas is < min_area, do not consider the contour
                if len(contour_S) == 0:
#                    print(str(len(contour_S)))
                    continue

                else:

                    # save slice number
                    slice_with_contour_S.append(i)

                    # get the center of the interpolation circle
                    contour_A = np.delete(contour_A,0,0) # delete first row, which was needed for allocation
                    x = contour_A[:, 1]
                    y = contour_A[:, 0]
                    x_c, y_c, R = leastsq_circle(x,y)

                    # get bone and articular cartilage
                    bone_cart_slice = []
                    arti_cart_slice = []

                    # for each region
                    for w in range (0,len(contour_S)):

                        # convert contour_S from list to np.array
                        temp = contour_S[w]
                        temp = np.array(temp)
                        temp = temp[0]
                        x_S  = temp[:,1]
                        y_S  = temp[:,0]

                        # get bone and articular cartilage
                        bone_C, arti_C = separate_cartilage_slice(x_c,y_c,x_S,y_S)
                        bone_cart_slice.append(bone_C)
                        arti_cart_slice.append(arti_C)

                    # assign contour_S
                    # the points of each region go to a cell of the list bone_cart/arti_cart
                    # if the slice contains two regions, the cell of bone_cart/arti_cart contains two separate contour array_S, one per region
                    # e.g. bone_cart is [1][2][1][1][1]... ;
                    #      bone_cart[0] = [xyzArrayOfRegion1]
                    #      bone_cart[1] = [xyzArrayOfRegion1][xyzArrayOfRegion2]
                    #      ...
                    bone_cart.append(bone_cart_slice)
                    arti_cart.append(arti_cart_slice)

    # combine bone contour_S and articular contour_S across slices
    # allocate np array_S
    bone_cart_all = np.ndarray((1,3))
    arti_cart_all = np.ndarray((1,3))

    for i in range(0, len(slice_with_contour_S)):

        # get contours of the current slice
        bone_C = bone_cart[i]
        arti_C = arti_cart[i]

        # extract contours from all regions
        for a in range (0,len(bone_C)):

            # bone
            temp          = np.array (bone_C[a])
            z             = np.full  ((temp.shape[0],1), slice_with_contour_S[i])
            temp          = np.hstack((temp,z))
            bone_cart_all = np.vstack((bone_cart_all,temp))

            # cartilage
            temp          = np.array (arti_C[a])
            z             = np.full  ((temp.shape[0],1), slice_with_contour_S[i])
            temp          = np.hstack((temp,z))
            arti_cart_all = np.vstack((arti_cart_all,temp))

    # delete first row, which was needed for allocation
    bone_cart_all = np.delete(bone_cart_all,0,0)
    arti_cart_all = np.delete(arti_cart_all,0,0)

    # multiply by image spacing
    bone_cart_all_mm = np.copy(bone_cart_all)
    bone_cart_all_mm[:,0] = bone_cart_all[:,0] * mask.GetSpacing()[1]
    bone_cart_all_mm[:,1] = bone_cart_all[:,1] * mask.GetSpacing()[2]
    bone_cart_all_mm[:,2] = bone_cart_all[:,2] * mask.GetSpacing()[0]
    arti_cart_all_mm = np.copy(arti_cart_all)
    arti_cart_all_mm[:,0] = arti_cart_all[:,0] * mask.GetSpacing()[1]
    arti_cart_all_mm[:,1] = arti_cart_all[:,1] * mask.GetSpacing()[2]
    arti_cart_all_mm[:,2] = arti_cart_all[:,2] * mask.GetSpacing()[0]

    return bone_cart_all_mm, arti_cart_all_mm


# ---------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO FLATTEN CARTILAGE FOR 2D VISUALIZATION -----------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

## Functions to fit cylinder and rotate along axis and angle.
#  Cylinder fitting from https://github.com/xingjiepan/cylinder_fitting
def rotation_matrix(phi, theta, psi):
    '''
    From: https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions#Euler_angles_(z-y%E2%80%B2-x%E2%80%B3_intrinsic)_%E2%86%92_rotation_matrix
    '''
    A11 =  np.cos(theta) * np.cos(psi)
    A21 =  np.cos(theta) * np.sin(psi)
    A31 = -np.sin(theta)

    A12 = -np.cos(phi)*np.sin(psi) + np.sin(phi)*np.sin(theta)*np.cos(psi)
    A22 =  np.cos(phi)*np.cos(psi) + np.sin(phi)*np.sin(theta)*np.sin(psi)
    A32 =  np.sin(phi)*np.cos(theta)

    A13 =  np.sin(phi)*np.sin(psi) + np.cos(phi)*np.sin(theta)*np.cos(psi)
    A23 = -np.sin(phi)*np.cos(psi) + np.cos(phi)*np.sin(theta)*np.sin(psi)
    A33 =  np.cos(phi)*np.cos(theta)

    A = np.array([[A11, A12, A13],
                  [A21, A22, A23],
                  [A31, A32, A33]])
    return A


def rotate_to_x(point_cloud):

    
    # fit to a cylinder
    step = 10
    w_fit, C_fit, r_fit, fit_err = fit(point_cloud[1:np.size(point_cloud,0):step,:])

    # cyl-axis has to be positive for homogeneity
    w_fit = np.abs(w_fit)

    # translate point cloud to origin
    point_cloud = point_cloud - C_fit # do this before the following step, where C_fit becomes the origin

    # translate cyl-axis to origin
    C_fit = C_fit - C_fit
    w_fit = w_fit - C_fit

    # rotatate cyl-axis and point cloud to the x-axis
    # -- vectors
    vector = np.copy(w_fit)    # vector I want to rotate to the x-axis
    versor = np.array([1,0,0]) # x-axis
    # vectors already at the origing

    # -- first rotation
    # angles
    phi   = 0
    theta = 0
    psi   = - np.arccos( np.dot([vector[0], vector[1]], [versor[0], versor[1]]) /
                         np.linalg.norm([vector[0], vector[1]]) * np.linalg.norm([versor[0], versor[1]]))
    # Rotation matrix
    M1 = rotation_matrix(phi, theta, psi)
    # Apply rotation cyl-axis
    vector_out_1 = np.dot(M1,vector)
    # Apply rotation to point_cloud
    point_cloud_out_1 = np.copy(point_cloud)
    for i in range(np.size(point_cloud,0)):
        point_cloud_out_1[i,:] = np.dot(M1,point_cloud[i,:])

    # -- second rotation
    # angles
    phi   = 0
    theta = np.arccos( np.dot([vector_out_1[0], vector_out_1[2]], [versor[0], versor[2]]) /
                       np.linalg.norm([vector_out_1[0], vector_out_1[2]]) * np.linalg.norm([versor[0], versor[2]]))
    psi   = 0
    # Rotation matrix
    M2 = rotation_matrix(phi, theta, psi)
    # Apply rotation cyl-axis
    #vector_out_2 = np.dot(M2,vector_out_1)
    # Apply rotation to point_cloud
    point_cloud_out_2 = np.copy(point_cloud_out_1)
    for i in range(np.size(point_cloud_out_1,0)):
        point_cloud_out_2[i,:] = np.dot(M2,point_cloud_out_2[i,:])

    return point_cloud_out_2


def flatten_surface(pts):

    '''
    Assumption: The axis of the surface (femoral cartilage) is the x-axis
    Input:
    pts    : It is an np.array with dimensions nOfPoints x 3
    Steps:
    1. Calculate the angles on the sagittal plane (i.e. the yz-plane) as arctang2 of the y- and z- components of the points
       The x-component is not used as it is like the cartilage is smeshed to the yz-plane
       This can be thought as that there is an angle phi associated to each "stripe" of points in the x-direction (y and z are fixed)
    2. To avoid eccessive discretization, create angle ranges by rounding the angle to the closest 2-digit value
    3. Cartilage flattening must start from the bottom of the cartilage, not from the middle,
       otherwise the cartilage will result "split" in two parts in the flattened representation
    4. For each angle bin, extract the x-coordinates of the points that belong to that bin
       In the flattened plot, the x-coordinates will be the actual x=coordinates of the cartilage, the y-coordinates will be the angle bins
    '''

    # calculate the angles on the sagittal plane
    phi = np.arctan2(pts[:,2], pts[:,1])
    # bin the angles to their closest 2.decimal
    phi = np.round(phi,2)
    # extract the bins
    phi_unique = np.unique(phi)

    # allocate flattened point cloud
    x = np.full((1,1),1)
    x = np.extract(x==x, x)
    y = np.full((1,1),1)
    y = np.extract(y==y, y)

    # extract the coordinates in x and z
    for a in range (0, len(phi_unique)):
        x_bin = np.extract(phi == phi_unique[a], pts[:,0])
        y_bin = np.full((len(x_bin),1), phi_unique[a])
        y_bin = np.extract(y_bin==y_bin, y_bin)
        x = np.hstack((x,x_bin))
        y = np.hstack((y,y_bin))
    x = np.delete(x,0,0)
    y = np.delete(y,0,0)

    # make cartilage continuous (it can be cut in half in the flattening)
    # calculate difference between current point and following one (derivative) to get where the cartilage is broken in two
#    gr = np.gradient(np.abs(y))
#    threshold = np.where(np.abs(gr) == np.max(np.abs(gr))) # threshold it's a tuple
#    threshold = threshold[0]
#    t_temp = threshold[len(threshold)-1]
#    # for some reasons, the threshold sometimes is the lower element, sometimes the upper element,
#    # so calculate the difference and get the largest
#    y_0 = y[t_temp - 1]
#    y_1 = y[t_temp]
#    y_2 = y[t_temp + 1]
#    diff1 = np.abs(np.abs(y_1) - np.abs(y_0))
#    diff2 = np.abs(np.abs(y_1) - np.abs(y_2))
#    if diff1 > diff2:
#        t = t_temp
#    else:
#        t = t_temp + 1
#    y[0:t] = y[0:t]+2*np.pi

    # make cartilage continuous (it can be cut in half in the flattening)
    # get the histogram of y
    #counts, bins, patches = plt.hist(y, 100, density=True, facecolor='g', alpha=0.5)
    counts, bins = np.histogram(y, 100, density=True)
    # get where there are emtpy
    zero_counts = np.where(counts == 0) # tuple
    zero_counts = zero_counts[0] # np array
    # find the central bin among the empty ones
    middle_zero = zero_counts[round(len(zero_counts)/2)]
    # get the corresponding value
    t = int(bins[middle_zero])
    # add 360degrees to the values below the threshold
    y[y<t] = y[y<t] + 2*np.pi

    # center x and y on zero
    x = x - np.min(x)
    y = y - np.mean(y)

    pts_out = np.vstack((x,y))

    return pts_out, phi #, color_out


def flatten_point_cloud(pts_in):

    # rotate point cloud so that the axis of the cloud coincides with the x-axis
    pts_rot = rotate_to_x(pts_in)

    # flatten the surface around the x-axis
    pts_out, phi = flatten_surface(pts_rot)
    
    return pts_out, phi


def flatten_thickness(thickness_in, phi):

    # extract the bins
    phi_unique = np.unique(phi)

    thickness_out = np.full((1,1),1)
    thickness_out = np.extract(thickness_out==thickness_out, thickness_out)

    # resample the thickness
    for a in range (0, len(phi_unique)):
        thickness_bin = np.extract(phi == phi_unique[a], thickness_in)
        thickness_out = np.hstack((thickness_out,thickness_bin))

    thickness_out = np.delete(thickness_out,0,0)

    return thickness_out



# ---------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO CALCULATE CARTILAGE THICKNESS --------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

def find_closest_point(pt, pt_cloud):
    
    """
    Calculates the minumum distance between a point and a point clould (euclidean pt-to-pt distance)
    pt is a (dim x 1) numpy array (dim is the point dimention, usually 2(i.e. x,y) or 3(i.e. x,y,z) )
    pt_cloud is a (dim x n) numpu array (n is the number of points)
    """

    pt_array     = np.tile(pt, (pt_cloud.shape[0],1))
    distances    = np.sqrt(np.sum((pt_array - pt_cloud)**2, axis=1))
    min_distance = np.min(distances)

    return min_distance


def nearest_neighbor_thickness (bone_cart, arti_cart):

    bone_cart_thickness = np.full((bone_cart.shape[0],1), 0.0)

    for i in range (0, bone_cart.shape[0]):
        bone_cart_thickness[i] = find_closest_point(bone_cart[i,:], arti_cart)

    return bone_cart_thickness

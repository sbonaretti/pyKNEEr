# Serena Bonaretti, 2018

# python modules
import numpy     as np
import SimpleITK as sitk
import skimage   as ski
from skimage.measure import find_contours

from scipy import optimize
from scipy import ndimage as ndi

from .cylinder_fitting import fit
import time


# ---------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO SEPARATE CARTILAGE SURFACES

# Functions to calculate circle center and radius. From: https://gist.github.com/lorenzoriano/6799568
def calc_R(x,y, xc, yc):
    # calculate the distance of each 2D points from the center (xc, yc)
    return np.sqrt((x-xc)**2 + (y-yc)**2)

def f(c, x, y):
    # calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc)
    Ri = calc_R(x, y, *c)
    return Ri - Ri.mean()

def leastsq_circle(x,y): # from: https://gist.github.com/lorenzoriano/6799568
    # coordinates of the barycenter
    x_m = np.mean(x)
    y_m = np.mean(y)
    center_estimate = x_m, y_m
    center, ier = optimize.leastsq(f, center_estimate, args=(x,y))
    xc, yc = center
    Ri       = calc_R(x, y, *center)
    R        = Ri.mean()
    return xc, yc, R


# Functions to calculate segment intersections. From: https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
class Point: #
	def __init__(self,x,y):
		self.x = x
		self.y = y

def ccw(A,B,C):
	return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

def intersect(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def separate_cartilage_slice(xc, yc, x, y):

    # check if radius connecting center and countour points intersects contour segments.
    # if yes, it's bone cartilage, if not, it is articular cartilage

    boneCart_x = []
    boneCart_y = []
    pointIndex = []

    # for each point of the contour
    for j in range(0, len(x)):

        # get the center and the current contour point
        center       = Point(xc, yc)
        contourPoint = Point(x[j],y[j])

        # in the contour coordinates, delete the current contourPoint and copy the first point to the end of the array
        x_temp = x
        x_temp = np.delete(x_temp,j)
        x_temp = np.append(x_temp, x[0])
        y_temp = y
        y_temp = np.delete(y_temp,j)
        y_temp = np.append(y_temp, x[0])

        # look for the intersection
        for k in range(0, len(x)-1):
            contourPointA = Point(x[k]  ,y[k])
            contourPointB = Point(x[k+1],y[k+1])
            intersection = intersect(center,contourPoint,contourPointA,contourPointB)

            # if there is intersection, it is bone cartilage
            if intersection == True:
                boneCart_x.append(x[j])
                boneCart_y.append(y[j])
                pointIndex.append(j)
                break

    # convert bone cartilage to numpy
    boneCart_x = np.asarray(boneCart_x)
    boneCart_y = np.asarray(boneCart_y)
    boneCart   = np.array((boneCart_x, boneCart_y)).T

    # get articular cartilage
    pointIndex = np.asarray(pointIndex)
    artiCart_x = x
    artiCart_x = np.delete(artiCart_x,pointIndex)
    artiCart_y = y
    artiCart_y = np.delete(artiCart_y,pointIndex)
    artiCart   = np.array((artiCart_x, artiCart_y)).T

    return boneCart, artiCart



def separate_cartilage (mask):

    minArea           = 15
    sliceWithContours = []
    boneCart          = []
    artiCart          = []

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
            contourS = []                # list:    each cell of the list contains a contour (for the slices with several regions)
                                         #          used to separate bone and articular cartilage (small regions are not considered)
            contourA = np.ndarray((1,2)) # nparray: contains the the contour of all the regions of the  slice
                                         #          used to calculate the circle center (small regions are considered)

            # find number of labelled regions (at the edges cartilage can be broken in pieces)
            regions, nOfRegions = ndi.label(slice)
            regions = np.asarray(regions)

            for w in range (0,nOfRegions):

                # get binary region
                temp_slice = np.full((slice.shape[0], slice.shape[1]), 0)
                temp_slice [regions == w+1] = 1

                # consider only regions with area > minArea
                if sum(sum(temp_slice)) < minArea:
                    continue

                else:
                    # get region contour
                    contour = ski.measure.find_contours(temp_slice, 0.5)

                    # add region contour separately for region (to discriminate bone and articular cartilage)
                    contourS.append(contour)

                    # put all (A) contours together (to find the circle center)
                    contour = contour[0]
                    contourA = np.vstack((contourA,contour))


                # if the areas is < minArea, do not consider the contour
                if len(contourS) == 0:
#                    print(str(len(contourS)))
                    continue

                else:

                    # save slice number
                    sliceWithContours.append(i)

                    # get the center of the interpolation circle
                    contourA = np.delete(contourA,0,0) # delete first row, which was needed for allocation
                    x = contourA[:, 1]
                    y = contourA[:, 0]
                    xc, yc, R = leastsq_circle(x,y)

                    # get bone and articular cartilage
                    boneCartSlice = []
                    artiCartSlice = []

                    # for each region
                    for w in range (0,len(contourS)):

                        # convert contours from list to np.array
                        temp = contourS[w]
                        temp = np.array(temp)
                        temp = temp[0]
                        xS   = temp[:,1]
                        yS   = temp[:,0]

                        # get bone and articular cartilage
                        boneC, artiC = separate_cartilage_slice(xc,yc,xS,yS)
                        boneCartSlice.append(boneC)
                        artiCartSlice.append(artiC)

                    # assign contours
                    # the points of each region go to a cell of the list boneCart/artiCart
                    # if the slice contains two regions, the cell of boneCart/artiCart contains two separate contour arrays, one per region
                    # e.g. boneCart is [1][2][1][1][1]... ;
                    #      boneCart[0] = [xyzArrayOfRegion1]
                    #      boneCart[1] = [xyzArrayOfRegion1][xyzArrayOfRegion2]
                    #      ...
                    boneCart.append(boneCartSlice)
                    artiCart.append(artiCartSlice)

    # combine bone contours and articular contours across slices
    # allocate np arrays
    boneCartAll = np.ndarray((1,3))
    artiCartAll = np.ndarray((1,3))

    for i in range(0, len(sliceWithContours)):

        # get contours of the current slice
        boneC = boneCart[i]
        artiC = artiCart[i]

        # extract contours from all regions
        for a in range (0,len(boneC)):

            # bone
            temp = np.array (boneC[a])
            z    = np.full  ((temp.shape[0],1), sliceWithContours[i])
            temp = np.hstack((temp,z))
            boneCartAll   = np.vstack((boneCartAll,temp))

            # cartilage
            temp = np.array (artiC[a])
            z    = np.full  ((temp.shape[0],1), sliceWithContours[i])
            temp = np.hstack((temp,z))
            artiCartAll   = np.vstack((artiCartAll,temp))

    # delete first row, which was needed for allocation
    boneCartAll = np.delete(boneCartAll,0,0)
    artiCartAll = np.delete(artiCartAll,0,0)

    # multiply by image spacing
    boneCartAll_mm = np.copy(boneCartAll)
    boneCartAll_mm[:,0] = boneCartAll[:,0] * mask.GetSpacing()[1]
    boneCartAll_mm[:,1] = boneCartAll[:,1] * mask.GetSpacing()[2]
    boneCartAll_mm[:,2] = boneCartAll[:,2] * mask.GetSpacing()[0]
    artiCartAll_mm = np.copy(artiCartAll)
    artiCartAll_mm[:,0] = artiCartAll[:,0] * mask.GetSpacing()[1]
    artiCartAll_mm[:,1] = artiCartAll[:,1] * mask.GetSpacing()[2]
    artiCartAll_mm[:,2] = artiCartAll[:,2] * mask.GetSpacing()[0]

    return boneCartAll_mm, artiCartAll_mm



# ---------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO FLATTEN CARTILAGE

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


def rotate_to_x(pointCloud):

    # fit to a cylinder
    step = 10
    start_time = time.time()
    w_fit, C_fit, r_fit, fit_err = fit(pointCloud[1:np.size(pointCloud,0):step,:])

    # cyl-axis has to be positive for homogeneity
    w_fit = np.abs(w_fit)

    # translate point cloud to origin
    pointCloud = pointCloud - C_fit # do this before the following step, where C_fit becomes the origin

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
    vector_out1 = np.dot(M1,vector)
    # Apply rotation to pointCloud
    pointCloud_out1 = np.copy(pointCloud)
    for i in range(np.size(pointCloud,0)):
        pointCloud_out1[i,:] = np.dot(M1,pointCloud[i,:])

    # -- second rotation
    # angles
    phi   = 0
    theta = np.arccos( np.dot([vector_out1[0], vector_out1[2]], [versor[0], versor[2]]) /
                       np.linalg.norm([vector_out1[0], vector_out1[2]]) * np.linalg.norm([versor[0], versor[2]]))
    psi   = 0
    # Rotation matrix
    M2 = rotation_matrix(phi, theta, psi)
    # Apply rotation cyl-axis
    vector_out2 = np.dot(M2,vector_out1)
    # Apply rotation to pointCloud
    pointCloud_out2 = np.copy(pointCloud_out1)
    for i in range(np.size(pointCloud_out1,0)):
        pointCloud_out2[i,:] = np.dot(M2,pointCloud_out2[i,:])

    return pointCloud_out2


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
        x_bin   = np.extract(phi == phi_unique[a], pts[:,0])
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


def fletten_point_cloud(pts_in):

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



# ---------------------------------------------------------------------------------------------------------------
# FUNCTIONS TO CALCULATE THICKNESS

def find_closest_point(pt, ptCloud):

    ptArray     = np.tile(pt, (ptCloud.shape[0],1))
    distances   = np.sqrt(np.sum((ptArray - ptCloud)**2, axis=1))
    minDistance = np.min(distances)

    return minDistance


def nearest_neighbor_thickness (boneCart, artiCart):

    boneCartThickness = np.full((boneCart.shape[0],1), 0.0)

    for i in range (0, boneCart.shape[0]):
        boneCartThickness[i] = find_closest_point(boneCart[i,:], artiCart)

    return boneCartThickness

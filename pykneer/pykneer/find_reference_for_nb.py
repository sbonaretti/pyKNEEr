# Serena Bonaretti, 2018

import matplotlib.pyplot as plt
import numpy as np
import time

from . import find_reference_functions as frf


def find_reference(allImageData, nOfProcesses):

    # initialize for the while loop
    iterationNo       = 1
    maxIterationNo    = 10
    referenceNames    = (maxIterationNo + 1) * [None]
    referenceNames[1] = allImageData[0]["referenceName"]
    minDistances      = (maxIterationNo + 1) * [None]

    # look for best reference
    while (referenceNames[iterationNo] != referenceNames[iterationNo-1] and iterationNo < maxIterationNo):

        start_time = time.time()

        print ("-> Iteration: " + str(iterationNo))

        # 1. prepare reference bone
        print ("   1. Preparing reference " + referenceNames[iterationNo])
        allImageData = frf.prepare_reference(allImageData, referenceNames, iterationNo)

        # 2. calculate the vector fields
        print ("   2. Registering images to current reference")
        frf.calculate_vector_fields(allImageData, nOfProcesses)

        # 3. calculate average vector field and pick the closest to the average
        print ("   3. Computing new reference")
        referenceNames, minDistances = frf.find_reference_as_minimum_distance_to_average(allImageData, referenceNames, minDistances, iterationNo)

        print ("-> The total time for iteration " + str(iterationNo) +  " was %d seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))

        iterationNo = iterationNo + 1

    # print ("\n")
    # print ("THE REFERENCE FOR THIS DATASET IS " + str(referenceNames[iterationNo]))

    return referenceNames, minDistances


def plot_convergence(referenceNames, minDistances):

    # delete elements with "None" (allocation in "findReference")
    referenceNames = list(filter(None.__ne__, referenceNames))
    minDistances   = list(filter(None.__ne__, minDistances))

    # delete unwanted elements (the first value of referenceNames and minDistances is empty for the while loop, and the last value of referenceNames is the same as the second last)
    referenceNames = np.delete(referenceNames, [len(referenceNames)-1])

    # x-axis
    iterations     = np.arange(1, len(minDistances)+1, 1)

    # plot
    plt.plot(iterations, minDistances, 'ro')
    plt.plot(iterations, minDistances, 'r-')
    plt.xlabel('iterations')
    plt.ylabel('distances')
    for i in range(0, len(referenceNames)):
        plt.annotate(referenceNames[i], xy =(iterations[i], minDistances[i]),  xytext=(iterations[i], minDistances[i]))
    plt.xticks(iterations)
    plt.xlim(0.8,len(iterations)+2)
    plt.show()

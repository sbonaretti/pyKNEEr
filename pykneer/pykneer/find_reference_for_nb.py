# Serena Bonaretti, 2018

import matplotlib.pyplot as plt
import numpy as np
import time

from . import find_reference_functions as frf


def find_reference(all_image_data, n_of_processes):

    # initialize for the while loop
    iteration_no       = 1
    max_iteration_no   = 10
    reference_names    = (max_iteration_no + 1) * [None]
    reference_names[1] = all_image_data[0]["reference_name"]
    min_distances      = (max_iteration_no + 1) * [None]

    # look for best reference
    while (reference_names[iteration_no] != reference_names[iteration_no-1] and iteration_no < max_iteration_no):

        start_time = time.time()

        print ("-> Iteration: " + str(iteration_no))

        # 1. prepare reference bone
        print ("   1. Preparing reference " + reference_names[iteration_no])
        all_image_data = frf.prepare_reference(all_image_data, reference_names, iteration_no)

        # 2. calculate the vector fields
        print ("   2. Registering images to current reference")
        frf.calculate_vector_fields(all_image_data, n_of_processes)

        # 3. calculate average vector field and pick the closest to the average
        print ("   3. Computing new reference")
        reference_names, min_distances = frf.find_reference_as_minimum_distance_to_average(all_image_data, reference_names, min_distances, iteration_no)

        print ("-> The total time for iteration " + str(iteration_no) +  " was %d seconds (about %d min)" % ((time.time() - start_time), (time.time() - start_time)/60))

        iteration_no = iteration_no + 1

    # print ("\n")
    # print ("THE REFERENCE FOR THIS DATASET IS " + str(reference_names[iteration_no]))

    return reference_names, min_distances


def plot_convergence(reference_names, min_distances):

    # delete elements with "None" (allocation in "findReference")
    reference_names = list(filter(None.__ne__, reference_names))
    min_distances   = list(filter(None.__ne__, min_distances))

    # delete unwanted elements (the first value of reference_names and min_distances is empty for the while loop, and the last value of reference_names is the same as the second last)
    reference_names = np.delete(reference_names, [len(reference_names)-1])

    # x-axis
    iterations      = np.arange(1, len(min_distances)+1, 1)

    # plot
    plt.plot(iterations, min_distances, 'ro')
    plt.plot(iterations, min_distances, 'r-')
    plt.xlabel('iterations')
    plt.ylabel('distances')
    for i in range(0, len(reference_names)):
        plt.annotate(reference_names[i], xy = (iterations[i], min_distances[i]),  xytext=(iterations[i], min_distances[i]))
    plt.xticks(iterations)
    plt.xlim(0.8,len(iterations)+2)
    plt.show()

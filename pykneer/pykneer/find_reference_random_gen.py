# Serena Bonaretti, 2018

import random

def pick_seed_images(seed, min_ID, max_ID, n_of_images):
    
    """
    Random pick of the images used as starting reference in the convergence experiment to find the reference bone
    Inputs:
        seed: random seed generator (chosen randomly)
        min_ID: minimum ID of the dataset (For a dataset with 10 images, min_ID = 1)
        max_ID: maximum ID of the dataset (For a dataset with 10 images, max_ID = 10)
        n_of_images: number of images to be used as reference
        
    Ouput: random seeds 
    
    Example: image_IDs = pick_seed_images(4, 1, 19, 5)
    """
    
    # Seed used for reproduciblity
    random.seed(seed)

    # Extract random numbers from the dataset IDs
    image_IDs = []
    for i in range (0, n_of_images):
        image_IDs.append(random.randint(min_ID,max_ID))
    
    print ("seeds IDs are: " + str(image_IDs))
    
    return image_IDs


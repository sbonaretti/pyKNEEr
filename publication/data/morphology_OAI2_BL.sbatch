#!/bin/bash

#SBATCH --job-name=morphology_OAI2_BL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=24:00:00
#SBATCH --partition=normal


## load python module
module load python/3.6.1
## activate the virtual environment
source $HOME/pykneer/pykneer_env/bin/activate


## launch jobs
jupyter nbconvert --execute --allow-errors --ExecutePreprocessor.timeout=86400 --to notebook morphology_OAI2_BL.ipynb
mv morphology_OAI2_BL.nbconvert.ipynb output_morphology_OAI2_BL.ipynb
##mv morphology_OAI2_BL.nbconvert.ipynb $(date +"%m_%d_%Y-%H_%M")_morphology_OAI2_BL.ipynb

## 86400=24h

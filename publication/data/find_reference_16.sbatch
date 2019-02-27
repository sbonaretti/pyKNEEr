#!/bin/bash

#SBATCH --job-name=find_reference_16
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
jupyter nbconvert --execute --allow-errors --ExecutePreprocessor.timeout=86400 --to notebook find_reference_16.ipynb
mv find_reference_16.nbconvert.ipynb output_find_reference_16.ipynb
##mv find_reference_16.nbconvert.ipynb $(date +"%m_%d_%Y-%H_%M")_find_reference_16.ipynb

## 86400=24h

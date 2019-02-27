#!/bin/bash

#SBATCH --job-name=preprocessing_OAI1_T2_0
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
jupyter nbconvert --execute --allow-errors --ExecutePreprocessor.timeout=86400 --to notebook preprocessing_OAI1_T2_0.ipynb
mv preprocessing_OAI1_T2_0.nbconvert.ipynb output_preprocessing_OAI1_T2_0.ipynb
##mv preprocessing_OAI1_T2_0.nbconvert.ipynb $(date +"%m_%d_%Y-%H_%M")_preprocessing_OAI1_T2_0.ipynb

## 86400=24h

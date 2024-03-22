#!/bin/sh
#SBATCH --time=5:00:00
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks=1 --cpus-per-task=10
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=xgph6

srun ./bandwidthchain -ch xpgh5 -sh xgph6 -sport 6855 -auto
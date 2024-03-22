#!/bin/sh
#SBATCH --time=5:00:00
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks=1 --cpus-per-task=10
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=xgpe4

srun ./bandwidthchain -ch xgpe5 -sh xgpe4 -sport 6855 -auto
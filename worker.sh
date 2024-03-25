#!/bin/sh
#SBATCH --time=5:00:00
#SBATCH --partition=medium
#SBATCH --nodes=4
#SBATCH --ntasks=4 --cpus-per-task=10
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=xgpf3,xgpf4,xgpf5,xgpf6

srun ./bandwidthchain -n 200 -start 0 -end 50 -za xgpe5 -zport 6855
srun ./bandwidthchain -n 200 -start 50 -end 100 -za xgpe5 -zport 6855
srun ./bandwidthchain -n 200 -start 100 -end 150 -za xgpe5 -zport 6855
srun ./bandwidthchain -n 200 -start 150 -end 200 -za xgpe5 -zport 6855

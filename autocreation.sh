#!/bin/bash

# List of worker names
workers=("xgpf4" "xgpf5" "xgpf6" "xgpf7")
# #!/bin/sh
# #SBATCH --time=5:00:00
# #SBATCH --partition=medium
# #SBATCH --nodes=4
# #SBATCH --ntasks=4 --cpus-per-task=10
# #SBATCH --ntasks-per-node=1
# #SBATCH --nodelist=xgpf3,xgpf4,xgpf5,xgpf6

# srun ./bandwidthchain -n 200 -start 0 -end 50 -za xgpe5 -zport 6855
# Iterate through each worker
start=0
total=200
for worker in "${workers[@]}"; do
    # Create a script file for each worker
    script_file="${worker}_script.sh"
    
    # Echo the worker's name into the script file
    echo "#!/bin/bash" > "$script_file"
    echo "#SBATCH --time=5:00:00" >> "$script_file"
    echo "#SBATCH --partition=medium" >> "$script_file"
    echo "#SBATCH --ntasks=1 --cpus-per-task=10" >> "$script_file"
    echo "#SBATCH --ntasks-per-node=1" >> "$script_file"
    echo "#SBATCH --nodelist=$worker" >> "$script_file"
    echo "srun ./bandwidthchain -n $total -start $start -end $((start+50)) -za xgpe5 -zport 6855" >> "$script_file"
    start=$((start+50))
    # Make the script executable
    chmod +x "$script_file"
done

for worker in "${workers[@]}"; do
    # Create a script file for each worker
    sbatch "${worker}_script.sh"
done

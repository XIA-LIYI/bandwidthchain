#!/bin/bash

# List of worker names
mapfile -t workers < machines.txt
controller="xgpe5"

# Iterate through each worker
start=0
total=200
gap=5

script_file="./controller/controller.sh"
echo "#!/bin/sh" > "$script_file"
echo "#SBATCH --time=5:00:00" >> "$script_file"
echo "#SBATCH --partition=medium" >> "$script_file"
echo "#SBATCH --nodes=1" >> "$script_file"
echo "#SBATCH --ntasks=1 --cpus-per-task=10" >> "$script_file"
echo "#SBATCH --ntasks-per-node=1" >> "$script_file"
echo "#SBATCH --nodelist=$controller" >> "$script_file"
echo "srun ./zookeeper" >> "$script_file"

for worker in "${workers[@]}"; do
    # Create a script file for each worker
    script_file="./workers/${worker}_script.sh"
    
    # Echo the worker's name into the script file
    echo "#!/bin/bash" > "$script_file"
    echo "#SBATCH --time=5:00:00" >> "$script_file"
    echo "#SBATCH --partition=medium" >> "$script_file"
    echo "#SBATCH --ntasks=10 --cpus-per-task=1" >> "$script_file"
    echo "#SBATCH --ntasks-per-node=10" >> "$script_file"
    echo "#SBATCH --nodelist=$worker" >> "$script_file"
    for i in {1..10}; do
        if [ "$i" -eq 10 ];
        then
            echo "srun --ntasks=1 ./bandwidthchain -start $start -end $((start+gap)) -za 192.168.51.57 -zport 6855 &" >> "$script_file"
        else
            echo "srun --ntasks=1 ./bandwidthchain -start $start -end $((start+gap)) -za 192.168.51.57 -zport 6855" >> "$script_file"
        fi
        start=$((start+gap))
    done
    echo "wait" >> "$script_file"
    # Make the script executable
    chmod +x "$script_file"
done

chmod 777 *
cd ./controller
chmod 777 *
sbatch ./controller.sh
sleep 5
cd ../workers
chmod 777 *
for worker in "${workers[@]}"; do
    # Create a script file for each worker
    sbatch ./${worker}_script.sh
done

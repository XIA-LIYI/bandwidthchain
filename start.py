#!/usr/bin/python3
import subprocess
import sys
import argparse
import os
import time

def get_idle_nodes(partition):
    command = f'sinfo --Node --format="%8N %10P %5T %5c %8O" -p {partition}'
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        lines = output.strip().split('\n')[1:]  # Skip header line
        nodes = []
        for line in lines:
            node_info = line.split()
            if len(node_info) == 5:
                node_name, partition, state, _, _ = node_info
                if node_name[:4] != 'xcne' and node_name[1] != 'g':
                    continue
                if state.strip() == 'idle':
                    nodes.append(node_name)
        return nodes
    except subprocess.CalledProcessError:
        print("Error executing command.")
        return []

def write_to_file(nodes, filename):
    with open(filename, 'w') as f:
        for node in nodes:
            f.write(node + '\n')

def create_controller_script(controller, partition, time):
    directory = "controller"
    script_name = f"controller_script.sh"
    if not os.path.exists(directory):
        os.makedirs(directory)

    script_content = f"""#!/bin/bash

#SBATCH --time={time}
#SBATCH --partition={partition}
#SBATCH --nodes=1
#SBATCH --ntasks=1 --cpus-per-task=10
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist={controller}

srun ./controller/zookeeper
"""
    script_path = os.path.join(directory, script_name)
    with open(script_path, "w") as file:
        file.write(script_content)

    # Make the script executable
    os.chmod(script_path, 0o777)
    subprocess.run(['sbatch', script_path])

    print(f"Created {script_name}")

def create_worker_script(controller, num_scripts, nodes, partition, step, cpu, time):
    # Ensure directory exists
    directory = "workers"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate and save shell scripts
    start = 0
    for i in range(num_scripts):
        script_name = f"{nodes[i]}_script.sh"
        
        script_content = f"""#!/bin/bash

#SBATCH --time={time}
#SBATCH --partition={partition}
#SBATCH --nodes=1
#SBATCH --ntasks=1 --cpus-per-task={cpu}
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist={nodes[i]}

srun --ntasks=1 ./workers/bandwidthchain -start {start} -end {start + step} -za {controller} -zport 6855
"""
        start += step
        script_path = os.path.join(directory, script_name)
        with open(script_path, "w") as file:
            file.write(script_content)

        # Make the script executable
        os.chmod(script_path, 0o777)
        subprocess.run(['sbatch', script_path])

        print(f"Created {script_name}")

if __name__ == "__main__":
    # Parse input
    parser = argparse.ArgumentParser(description='Retrieve idle nodes based on partition.')
    parser.add_argument('--partition', '-p', help='Partition to filter by') # default is medium
    parser.add_argument('--number', '-n', help='Number of machines needed') # default is 4
    parser.add_argument('--cpu', '-c', help='Number of cpus per machine') # default is 4
    parser.add_argument('--step', '-s', help='Number of nodes in one machines') # default is 50
    parser.add_argument('--time', '-t', help='Maximum experiment time') # default is 5:00:00
    args = parser.parse_args()
    if args.number == None:
        args.number = 4
    else:
        args.number = int(args.number)

    if args.partition == None:
        args.partition = 'medium'

    if args.step == None:
        args.step = 50
    else:
        args.step = int(args.step)

    if args.cpu == None:
        args.cpu = 10
    else:
        args.cpu = int(args.cpu)

    if args.time == None:
        args.time = '5:00:00'

    # Find nodes
    idle_nodes = get_idle_nodes(args.partition)
    if len(idle_nodes) < args.number + 1:
        print("No enough idle nodes now")
    else:
        print(f"Zookeeper runs on {idle_nodes[0]}")
        print(f"Bandwidthchain runs on '{args.partition}' partition:")
        for node in idle_nodes[1: args.number + 1]:
            print(node, end=" ")
        print("\n")

        # Run scripts
        print("Start running zookeeper")
        try:
            os.chmod('./controller/zookeeper', 0o777)
        except Exception:
            print("No zookeeper")
        
        create_controller_script(idle_nodes[0], args.partition, args.time)
        
        time.sleep(2)

        print("Start running bandwidthchain")
        try:
            os.chmod('./workers/bandwidthchain', 0o777)
        except Exception:
            print("No bandwidthchain")
        create_worker_script(idle_nodes[0], args.number, idle_nodes[1: args.number + 1], args.partition, args.step, args.cpu, args.time)
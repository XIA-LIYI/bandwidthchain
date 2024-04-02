#!/usr/bin/python3
import subprocess
import sys
import argparse
import os
import time

use_prefix = ['xgpc', 'xgpd', 'xgpe', 'xgpf', 'xgph', 'xgpg', 'xcne', 'amdg']
exclusion_list = ['xgpe10', 'xgpe11', 'xgpf10', 'xgpf11']

def get_nodes(partition):
    standard_nodes = get_nodes_with_partition("standard")
    medium_nodes = get_nodes_with_partition("medium")
    long_nodes = get_nodes_with_partition("long")
    selected_nodes = []
    results = []
    for node in long_nodes:
        selected_nodes.append(node)
        results.append([node, "long"])
    if partition == "long":
        return results
    print(results)
    for node in medium_nodes:
        if node in selected_nodes:
            continue
        selected_nodes.append(node)
        results.append([node, "medium"])
    if partition == "medium":
        return results
    for node in standard_nodes:
        if node in selected_nodes:
            continue
        selected_nodes.append(node)
        results.append([node, "standard"])
    if partition == "standard":
        return results

def get_nodes_with_partition(partition):
    command = f'sinfo --Node --format="%8N %10P %5T %5c %8O" -p {partition}'
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        lines = output.strip().split('\n')[1:]  # Skip header line
        nodes = []
        for line in lines:
            node_info = line.split()
            if len(node_info) == 5:
                node_name, partition, state, _, _ = node_info
                if node_name[:4] not in use_prefix:
                    continue
                if node_name in exclusion_list:
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

def create_controller_script(controller, time):
    directory = "controller"
    script_name = f"controller_script.sh"
    if not os.path.exists(directory):
        os.makedirs(directory)

    script_content = f"""#!/bin/bash

#SBATCH --time={time}
#SBATCH --partition={controller[1]}
#SBATCH --nodes=1
#SBATCH --ntasks=1 --cpus-per-task=10
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist={controller[0]}

srun ./controller/zookeeper
"""
    script_path = os.path.join(directory, script_name)
    with open(script_path, "w") as file:
        file.write(script_content)

    # Make the script executable
    os.chmod(script_path, 0o777)
    subprocess.run(['sbatch', script_path])

    print(f"Created {script_name}")
def create_worker_script_in_one_file(controller, num_scripts, nodes, start, step, cpu, time):
    # Ensure directory exists
    directory = "workers"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate and save shell scripts
    
    nodes_by_partition = {}
    for i in nodes:
        if i[1] in nodes_by_partition:
            nodes_by_partition[i[1]]['count'] += 1
            nodes_by_partition[i[1]]['list'] = nodes_by_partition[i[1]]['list'] + i[0] + ','
        else:
            nodes_by_partition[i[1]] = {'count': 1, 'list':i[0] + ','}
    
    for partition, nodes_info in nodes_by_partition.items():
        script_name = f"{partition}_script.sh"
        sruns = f""
        for i in range(nodes_info['count']):
            sruns += f"srun --ntasks=1 ./workers/bandwidthchain -start {start} -end {start + step} -za {controller} -zport 6855 &\n"
            start += step
        script_content = f"""#!/bin/bash
#SBATCH --time={time}
#SBATCH --partition={partition}
#SBATCH --nodes={nodes_info['count']}
#SBATCH --ntasks={nodes_info['count']} --cpus-per-task={cpu}
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist={nodes_info['list'][: len(nodes_info['list']) - 1]}

{sruns}
wait
"""
        
        script_path = os.path.join(directory, script_name)
        with open(script_path, "w") as file:
            file.write(script_content)

        # Make the script executable
        os.chmod(script_path, 0o777)
        subprocess.run(['sbatch', script_path])

        print(f"Created {script_name}")    
def create_worker_script(controller, num_scripts, nodes, start, step, cpu, time):
    # Ensure directory exists
    directory = "workers"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate and save shell scripts
    for i in nodes:
        script_name = f"{i[0]}_script.sh"
        
        script_content = f"""#!/bin/bash

#SBATCH --time={time}
#SBATCH --partition={i[1]}
#SBATCH --nodes=1
#SBATCH --ntasks=1 --cpus-per-task={cpu}
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist={i[0]}

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
    idle_nodes = get_nodes(args.partition)
    idle_nodes.reverse()
    if len(idle_nodes) < args.number + 1:
        print("No enough idle nodes now")
    else:
        print(f"Zookeeper runs on {idle_nodes[0]}")
        print(f"Bandwidthchain runs on:")
        for node in idle_nodes[1: args.number + 1]:
            print(node, end=" ")
        print("\n")

        # Run scripts
        print("Start running zookeeper")
        try:
            os.chmod('./controller/zookeeper', 0o777)
        except Exception:
            print("No zookeeper")
        
        create_controller_script(idle_nodes[0], args.time)
        
        time.sleep(5)

        print("Start running bandwidthchain")
        try:
            os.chmod('./workers/bandwidthchain', 0o777)
        except Exception:
            print("No bandwidthchain")
        if args.number >= 10:
            create_worker_script(idle_nodes[0][0], args.number, idle_nodes[1: 11], 0, args.step, args.cpu, args.time)
            create_worker_script_in_one_file(idle_nodes[0][0], args.number, idle_nodes[11: (args.number + 1)], 10 * args.step, args.step, args.cpu, args.time)
        else:
            create_worker_script(idle_nodes[0][0], args.number, idle_nodes[1: (args.number + 1)], args.partition, args.step, args.cpu, args.time)

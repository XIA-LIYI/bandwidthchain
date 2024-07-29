#!/usr/bin/python3
import random
import subprocess
import sys
import argparse
import os
import time

use_prefix = ['xcnf', 'xcne']
exclusion_list = []
# use_prefix = ['xcnf', 'xgpc', 'xgpd', 'xgpe', 'xgpf', 'xgph', 'xgpg', 'xcne', 'amdg']
# exclusion_list = ['xcng', 'xgpe10', 'xgpe11', 'xgpf10', 'xgpf11']
randomStamp = int(random.random() * 1000)

def get_nodes(partition, cpu_required):
    normal_nodes = get_nodes_with_partition("normal", cpu_required)
    # gpu_nodes = get_nodes_with_partition("gpu", cpu_required)
    long_nodes = get_nodes_with_partition("long", cpu_required)
    # gpu_long_nodes = get_nodes_with_partition("gpu-long", cpu_required)
    result_idle_nodes = []
    record_idle_nodes = []
    result_mix_nodes = []
    record_mix_nodes = []
    for node in long_nodes[0]:
        if node in record_idle_nodes:
            continue
        record_idle_nodes.append(node)
        result_idle_nodes.append([node, "long"])
    for node in long_nodes[1]:
        if node in record_mix_nodes:
            continue
        record_mix_nodes.append(node)
        result_mix_nodes.append([node, "long"])
    # for node in gpu_long_nodes[0]:
    #     if node in record_idle_nodes:
    #         continue
    #     record_idle_nodes.append(node)
    #     result_idle_nodes.append([node, "gpu_long"])
    # for node in gpu_long_nodes[1]:
    #     if node in record_mix_nodes:
    #         continue
    #     record_mix_nodes.append(node)
    #     result_mix_nodes.append([node, "gpu_long"])                
    if partition == "long":
        return [result_idle_nodes, result_mix_nodes]
    for node in normal_nodes[0]:
        if node in record_idle_nodes:
            continue
        record_idle_nodes.append(node)
        result_idle_nodes.append([node, "normal"])
    for node in normal_nodes[1]:
        if node in record_mix_nodes:
            continue
        record_mix_nodes.append(node)
        result_mix_nodes.append([node, "normal"])
    # for node in gpu_nodes[0]:
    #     if node in record_idle_nodes:
    #         continue
    #     record_idle_nodes.append(node)
    #     result_idle_nodes.append([node, "gpu"])
    # for node in gpu_nodes[1]:
    #     if node in record_mix_nodes:
    #         continue
    #     record_mix_nodes.append(node)
    #     result_mix_nodes.append([node, "gpu"])
    if partition == "normal":
        return [result_idle_nodes, result_mix_nodes]

def get_nodes_with_partition(partition, cpu_required):
    command = f'sinfo --Node --format="%8N %10P %5T %5c %8O %20C" -p {partition}'
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        lines = output.strip().split('\n')[1:]  # Skip header line
        idle_nodes = []
        mix_nodes = []
        for line in lines:
            node_info = line.split()
            if len(node_info) == 6:
                node_name, partition, state, _, _, cpus = node_info
                if node_name[:4] not in use_prefix:
                    continue
                if node_name in exclusion_list:
                    continue
                if state.strip() == 'idle':
                    idle_nodes.append(node_name)
                    continue
                _, idle_cpus, _, _ = cpus.split('/')
                if int(idle_cpus) >= 2 * cpu_required:
                    mix_nodes.append(node_name) 
        return [idle_nodes, mix_nodes]
    except subprocess.CalledProcessError:
        print("Error executing command.")
        return []

def write_to_file(nodes, filename):
    with open(filename, 'w') as f:
        for node in nodes:
            f.write(node + '\n')

def create_controller_script(controller, time, numOfNode):
    directory = "controller"
    script_name = f"controller_script_100.sh"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open("controller_template.txt", "r") as f:
        tmp = f.read()

    script_content = tmp.format(**{"time" : time, "partition": controller[1], "node": controller[0], "n": numOfNode})
    script_path = os.path.join(directory, script_name)
    with open(script_path, "w") as file:
        file.write(script_content)

    # Make the script executable
    os.chmod(script_path, 0o777)
    subprocess.run(['sbatch', script_path])

    print(f"Created {script_name}")
    return script_name + "\n"

def create_worker_script_in_one_file(controller, num_scripts, nodes, start, step, cpu, time, total):
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
    jobname = ""
    for partition, nodes_info in nodes_by_partition.items():
        script_name = f"{partition}_script_{randomStamp}.sh"
        
        sruns = f""
        for i in range(nodes_info['count']):
            sruns += f"srun --ntasks=1 ./workers/betterpob -n {total} -start {start} -end {start + step} -za {controller} -zport 6855 &\n"
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
        jobname += script_name + "\n"
        # Make the script executable
        os.chmod(script_path, 0o777)
        subprocess.run(['sbatch', script_path])

        print(f"Created {script_name}")
    return jobname
def create_worker_script(controller, num_scripts, nodes, start, step, cpu, time, total):
    # Ensure directory exists
    
    directory = "workers"
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    jobname = ""
    # Generate and save shell scripts
    for i in nodes:
        script_name = f"{i[0]}_script_{randomStamp}.sh"
        with open("worker_template.txt", "r") as f:
            tmp = f.read()
        fillIn = {
            "time": time, 
            "partition": i[1], 
            "cpu": cpu, 
            "node": i[0], 
            "total": total, 
            "start": start, 
            "end": start + step, 
            "controller": controller
        }
        script_content = tmp.format(**fillIn)
        start += step
        script_path = os.path.join(directory, script_name)
        with open(script_path, "w") as file:
            file.write(script_content)
        jobname += script_name + "\n"
        # Make the script executable
        os.chmod(script_path, 0o777)
        subprocess.run(['sbatch', script_path])

        print(f"Created {script_name}")
    return jobname

if __name__ == "__main__":
    # Parse input
    parser = argparse.ArgumentParser(description='Retrieve idle nodes based on partition.')
    parser.add_argument('--partition', '-p', help='Partition to filter by') # default is medium
    parser.add_argument('--number', '-n', help='Number of machines needed') # default is 4
    parser.add_argument('--cpu', '-c', help='Number of cpus per machine') # default is 4
    parser.add_argument('--step', '-s', help='Number of nodes in one machines') # default is 50
    parser.add_argument('--time', '-t', help='Maximum experiment time') # default is 3:00:00
    parser.add_argument('--zookeeper', '-z', help='Node that runs zookeeper') # default is None
    args = parser.parse_args()
    if args.number == None:
        args.number = 4
    else:
        args.number = int(args.number)

    if args.partition == None:
        args.partition = 'normal'

    if args.step == None:
        args.step = 50
    else:
        args.step = int(args.step)

    if args.cpu == None:
        args.cpu = 10
    else:
        args.cpu = int(args.cpu)

    if args.time == None:
        args.time = '3:00:00'

    # Find nodes
    idle_nodes, mix_nodes = get_nodes(args.partition, args.cpu)
    idle_nodes.reverse()
    mix_nodes.reverse()
    if len(idle_nodes) + len(mix_nodes) < args.number + 1:
        print("No enough idle nodes now")
    else:
        idle_nodes.extend(mix_nodes)
        if args.zookeeper == None:
            print(f"Zookeeper runs on {idle_nodes[0]}")
        print(f"Bandwidthchain runs on:")
        for node in idle_nodes[1: args.number + 1]:
            print(node, end=" ")
        print("\n")

        with open("./jobs.txt", "w") as file:
        # Run scripts
            print("Start running zookeeper")
            try:
                os.chmod('./controller/zookeeper', 0o777)
            except Exception:
                print("No zookeeper")
            if args.zookeeper == None:
                jobname = create_controller_script(idle_nodes[0], args.time, args.number * args.step)
                file.write(jobname)
                controller = idle_nodes[0][0]
                time.sleep(10)
            else:
                controller = args.zookeeper

            print("Start running betterpob")
            try:
                os.chmod('./workers/betterpob', 0o777)
            except Exception:
                print("No betterpob")
            if args.number >= 10:
                jobname = create_worker_script(controller, args.number, idle_nodes[1: 11], 0, args.step, args.cpu, args.time, str(args.step * args.number))
                file.write(jobname)
                jobname = create_worker_script_in_one_file(controller, args.number, idle_nodes[11: (args.number + 1)], 10 * args.step, args.step, args.cpu, args.time, str(args.step * args.number))
                file.write(jobname)
            else:
                print(args.step * args.number)
                jobname = create_worker_script(controller, args.number, idle_nodes[1: (args.number + 1)], 0, args.step, args.cpu, args.time, str(args.step * args.number))
                file.write(jobname)
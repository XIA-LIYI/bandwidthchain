# bandwidthchain

1. Before start, run **./delete.sh** to delete all out and log files and run **./cancel.sh** to cancel all of running jobs.
2. To start, run **python3 start.py** with optional flags:
    * --number, -n: number of machines needed, default value is 4
    * --partition, -p: partition to filter by, default partition is medium
    * --cpu, -c: number of cpus per machine, default value is 10
    * --step, -s: number of nodes per machine, default value is 50
    * --time, -t: maximum experiment time
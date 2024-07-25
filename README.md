# SoC computing cluster automation script

## Basic Usage
1. `git clone` the project into `~/cluster_tool`, and then `cd ~/cluster_tool`
2. upload the `zookeeper` file into `./controller/zookeeper`
3. upload the executable file into `./workers/betterpob`
4. `chmod +x start.py`
5. `./start.py`
6. use `./delete.sh` to delete the log files, and `./cancel.sh` to cancel the running experiments

## Advanced options
`./start.py` can be run with the following options:
* `--number`, `-n`: number of machines needed, default value is `4`
* `--partition`, `-p`: partition to filter by, default partition is `medium`
* `--cpu`, `-c`: number of cpus per machine, default value is `10`
* `--step`, `-s`: number of nodes per machine, default value is `50`
* `--time`, `-t`: maximum experiment time, default time is `5:00:00`. Note that format of time is DD-HH:MM:SS.

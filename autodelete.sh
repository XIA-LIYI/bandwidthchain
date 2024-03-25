#!/bin/bash

# mapfile -t workers < machines.txt

# for worker in "${workers[@]}"; do
#     script_file="${worker}_script.sh"
#     rm "./workers/$script_file"
# done

rm ./workers/*.sh
rm ./workers/*.out
rm ./workers/*.log
rm *.out
rm ./controller/*.sh
rm ./controller/*.out
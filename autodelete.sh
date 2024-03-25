#!/bin/bash

mapfile -t workers < machines.txt

for worker in "${workers[@]}"; do
    script_file="${worker}_script.sh"
    rm "$script_file"
done
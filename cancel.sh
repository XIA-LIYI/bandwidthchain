#!/bin/bash

# Check if jobs.txt exists
if [ ! -f "jobs.txt" ]; then
    echo "jobs.txt not found!"
    exit 1
fi

# Read names from jobs.txt and cancel each job
while IFS= read -r name; do
    if [ -n "$name" ]; then
        scancel --name "$name"
        echo "Canceled job $name"
    fi
done < "jobs.txt"

echo "All jobs canceled."
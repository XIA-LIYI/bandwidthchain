#!/bin/bash

# Specify the folder where you want to find files
folder="./controller/"

# Check if the folder exists
if [ ! -d "$folder" ]; then
    echo "Folder '$folder' not found."
    exit 1
fi

# Find all files in the specified folder
files=$(find "$folder" -type f)

# Iterate over each file and run scancel
for file in $files; do
    filename=$(basename "$file")
    # Run scancel with the filename
    scancel --name "$filename"
done

echo "scancel command executed for all files in $folder"

# Specify the folder where you want to find files
folder="./workers/"

# Check if the folder exists
if [ ! -d "$folder" ]; then
    echo "Folder '$folder' not found."
    exit 1
fi

# Find all files in the specified folder
files=$(find "$folder" -type f)

# Iterate over each file and run scancel
for file in $files; do
    filename=$(basename "$file")
    # Run scancel with the filename
    scancel --name "$filename"
done

echo "scancel command executed for all files in $folder"
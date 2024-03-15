#!/bin/bash

# Check if a year was provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 year"
    exit 1
fi

# Define the base directory
BASE_DIR="../data/$1"

# Define subdirectories
SUBDIRS=("generated_data" "kaggle_data" "silver_data" "gold_data")

# Create the base directory if it doesn't exist
if [ ! -d "$BASE_DIR" ]; then
    mkdir -p "$BASE_DIR"
    echo "Creating new directory: $BASE_DIR"
else
    echo "Directory already exists: $BASE_DIR"
fi

# Create subdirectories if they don't exist
for SUBDIR in "${SUBDIRS[@]}"; do
    if [ ! -d "${BASE_DIR}/${SUBDIR}" ]; then
        mkdir "${BASE_DIR}/${SUBDIR}"
        echo "Creating new directory: ${BASE_DIR}/${SUBDIR}"
    fi
done
#!/bin/bash

# Directory to start the traversal
directory="$1"

find "$directory" -type f -name "*.json" -exec rm -v {} \;

#!/bin/bash

# Directory to start the traversal
directory="$1"

# Traverse through the directory subtree
find "$directory" -type f | while read -r file; do
    # Check if the file does not already end with '-edited'
    if [[ "$file" != *"-edited"* ]]; then
        # Construct the name of the corresponding edited file
        edited_file="${file%.*}-edited.${file##*.}"
	#
        # Check if the edited version of the file exists
        if [ -f "$edited_file" ]; then
            # Remove the original file since the edited one exists
            echo "Removing $file because $edited_file exists"
            rm "$file"
        fi
    fi
done

#!/bin/bash

directory="$1"

if [[ -z "$directory" ]]; then
        echo "work dir - first arg - missing "
        exit 1
else
        echo "converting dir $directory to h.256"
fi


for filename in "$directory"/*.mkv; do
        echo "Re-coding -$filename- to h.256"
        ffmpeg -i "$filename" -c:v libx265 -vtag hvc1 "$filename.mp4"
done

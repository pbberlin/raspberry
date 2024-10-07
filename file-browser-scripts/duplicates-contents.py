import os
import argparse

import hashlib
from collections import defaultdict

import json
from datetime import datetime


def fileContentHash(filePth, chunkSize=1024*1024):
    md5 = hashlib.md5()
    with open(filePth, 'rb') as f:
        while chunk := f.read(chunkSize):
            md5.update(chunk)
    return md5.hexdigest()


# Function to find files based on extensions and size
def traverse(rootDir, extensions, minSize):
    matching = []
    for dirpath, _, filenames in os.walk(rootDir):
        for filename in filenames:
            hasExt = False
            for ext in extensions:
                if filename.endswith(ext):
                    hasExt = True
            if hasExt:
                filePth = os.path.join(dirpath, filename)
                fileSiz = os.path.getsize(filePth)
                if fileSiz > minSize:
                    print(f"    {filePth} satisfies size and extension")
                    matching.append(filePth)
    return matching


def findDuplicates(rootDir, exts, minSize):

   # Dictionary to store file hash -> list of files
    hashToFiles = defaultdict(list)

    upperCased = []
    for ext in exts:
        upperCased.append(ext.upper())

    origExts = exts.copy()
    exts.extend(upperCased)
    print(f"extensions - upper and lower: {exts}")

    timestampSuffix = f"{datetime.now():%Y-%m-%d-%H-%M-%S}"
    extsStr = "-".join(origExts).replace(".", "")
    fnDupes = f"./duplicates-content-{extsStr}-{timestampSuffix}.json"
    fnSings = f"./singularis-content-{extsStr}-{timestampSuffix}.json"




    print(f"traversing {rootDir}")
    files = traverse(rootDir, exts, minSize)
    print(f"{len(files)} files found")


    print(f"computing hashes may take a while")
    for idx, file in enumerate(files):
        file_hash = fileContentHash(file)
        hashToFiles[file_hash].append(file)
        if (idx % 50) == 0:
            print(f"    computing {idx:3} ... ")
    print(f"hashes computed")


    print(f"selecting hashes with multiple files")
    duplicates = {}
    singularis = {}
    for hashKey, fileList in hashToFiles.items():
        if len(fileList) > 1:
            duplicates[hashKey] = fileList
        elif len(fileList) == 1:
            singularis[hashKey] = fileList


    if duplicates:
        for hashKey, fileList in duplicates.items():
            print(f"hash dupe: {hashKey}")
            for file in fileList:
                print(f"    {file}")

            if len(fileList) == 2:
                if "./Photos/2021/" in fileList[0] and "./Photos/fuer_katrin/" in fileList[1] :
                    pass
                    # os.remove( fileList[0] )
                    # print(f"      deleted {fileList[0]}")
    else:
        print("No duplicate files found.")


    # dump a as JSON
    with open(fnDupes, "w", encoding='utf-8') as outFile:
        json.dump(duplicates, outFile, ensure_ascii=False, indent=4)
        print(f"saving JSON file 'duplicates' {len(duplicates):4} entries")

    with open(fnSings, "w", encoding='utf-8') as outFile:
        json.dump(singularis, outFile, ensure_ascii=False, indent=4)
        print(f"saving JSON file 'singularis' {len(singularis):4} entries")




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="script takes one param type=[images,videos]")    
    parser.add_argument("type", help="[image,video]")
    args = parser.parse_args()
    
    rootDir = "."

    extensions = []
    if args.type == "images":
        extensions = [".jpg", ".jpeg", ".gif", ".png"]

    if args.type == "videos":
        extensions = [".mp4", ".mpg", ".mkv" ]


    if len(extensions) < 1:
        print("first param 'type' must be 'images' or 'videos'")
        quit()

    # (  60 * 1024  => 100KB)
    minFileSize = 60 * 1024

    findDuplicates(rootDir, extensions, minFileSize)

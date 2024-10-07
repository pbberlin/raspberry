import os
import argparse


import json
from datetime import datetime




# Function to find files based on extensions and size
def traverse(rootDir, extensions):

    matchingFN = {}
    mkvCounter = 0

    for dirpath, _, filenames in os.walk(rootDir):
        for filename in filenames:
            hasExt = False
            for ext in extensions:
                if filename.endswith(ext):
                    hasExt = True
            if hasExt:
                filePth = os.path.join(dirpath, filename)
                fileSiz = os.path.getsize(filePth)


                # nm = Path(imgPth).name

                # print(f"    {filename} satisfies extension")

                fnNormalized = filename.replace(".mkv.mp4", ".mp4")

                if filename.endswith(".mkv"):
                    fnNormalized = filename.replace(".mkv", ".mp4")
                    mkvCounter += 1
                    # print(f"        {filename} - {mkvCounter}")

                if fnNormalized not in matchingFN:
                    matchingFN[fnNormalized] = []

                matchingFN[fnNormalized].append( [filePth, fileSiz] )
                # print(f"      {filenameMP4} appended - {fileSiz} bytes")

    return matchingFN


def findSimilarFilenames(rootDir, exts):

    upperCased = []
    for ext in exts:
        upperCased.append(ext.upper())

    origExts = exts.copy()
    exts.extend(upperCased)
    print(f"extensions - upper and lower: {exts}")

    timestampSuffix = f"{datetime.now():%Y-%m-%d-%H-%M-%S}"
    extsStr = "-".join(origExts).replace(".", "")
    fnDupes = f"./duplicates-names-{extsStr}-{timestampSuffix}.json"
    fnSings = f"./singularis-names-{extsStr}-{timestampSuffix}.json"



    print(f"traversing {rootDir}")
    filesDict = traverse(rootDir, exts)
    print(f"{len(filesDict)} files found")


    print(f"selecting hashes with multiple files")
    duplicates = {}
    singularis = {}
    for idx, fileName in enumerate(filesDict):
        occurrences = filesDict[fileName]
        if len(occurrences) == 1:
            singularis[fileName] = occurrences
        elif len(occurrences) > 1:
            duplicates[fileName] = occurrences
        else:
            print(f"filename {fileName}: occurrences {occurrences}")


    # dump as JSON
    if len(singularis) > 0:
        with open(fnSings, "w", encoding='utf-8') as outFile:
            json.dump(singularis, outFile, ensure_ascii=False, indent=4)
            print(f"saving JSON file 'singularis' {len(singularis):4} entries")

    if len(duplicates) > 0:
        with open(fnDupes, "w", encoding='utf-8') as outFile:
            json.dump(duplicates, outFile, ensure_ascii=False, indent=4)
            print(f"saving JSON file 'duplicates' {len(duplicates):4} entries")





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


    findSimilarFilenames(rootDir, extensions)

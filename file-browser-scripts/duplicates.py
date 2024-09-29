import os
import hashlib
from collections import defaultdict


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


def findDuplicates(rootDir, extensions, minSize):
 
   # Dictionary to store file hash -> list of files
    hashToFiles = defaultdict(list)

    uppered = []
    for ext in extensions:
        uppered.append(ext.upper())
    extensions.extend(uppered)
    print(f"extensions - upper and lower: {extensions}")


    print(f"traversing {rootDir}")
    files = traverse(rootDir, extensions, minSize)
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
    for hashVal, fileList in hashToFiles.items():
        if len(fileList) > 1:
            duplicates[hashVal] = fileList


    if duplicates:
        for hashVal, fileList in duplicates.items():
            print(f"hash dupe: {hashVal}")
            for file in fileList:
                print(f"    {file}")
            
            if len(fileList) == 2:
                if "./Photos/2021/" in fileList[0] and "./Photos/fuer_katrin/" in fileList[1] :
                    os.remove( fileList[0] )
                    print(f"      deleted {fileList[0]}")

                if "./Photos/2020a/" in fileList[0] and "./Photos/2020/" in fileList[1] :
                    os.remove( fileList[0] )
                    print(f"      deleted {fileList[0]}")

    else:
        print("No duplicate files found.")



if __name__ == "__main__":
    rootDir = "./Photos"

    extensions = [".mp4", ".mpg" ]
    extensions = [".jpg", "jpeg", ".gif", ".png"]


    # (  100 * 1024  => 100KB)
    minFileSize = 100 * 1024  
    
    findDuplicates(rootDir, extensions, minFileSize)
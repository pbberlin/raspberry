import os
import time
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS




# extract "photo taken" timestamp from EXIF data
def photoTakenTime(imgPth):
    try:
        img = Image.open(imgPth)
        
        # extract EXIF data
        exif_data = img._getexif()
        
        if exif_data is None:
            print(f"\t no EXIF data found in {imgPth}.")
            return None
        
        for tag, val in exif_data.items():
            tagName = TAGS.get(tag, tag)
            if tagName == "DateTimeOriginal":
                # EXIF DateTimeOriginal format: "YYYY:MM:DD HH:MM:SS"
                return val
        
        print(f"\t tag 'DateTimeOriginal' not found in {imgPth}.")
        return None
    
    except Exception as e:
        print(f"\t error reading EXIF data from {imgPth}: {e}")
        return None


def exifToTimestamp(exif_time):
    try:
        # Convert EXIF time format to datetime object
        dt = datetime.strptime(exif_time, "%Y:%m:%d %H:%M:%S")        
        # Convert datetime object to Unix timestamp
        return int(time.mktime(dt.timetuple()))
    except Exception as e:
        print(f"\t error converting EXIF time to timestamp: {e}")
        return None


def updateFileTimestamp(imgPth, ts):
    try:
        # set access and modification time
        os.utime(imgPth, (ts, ts))
        print(f"\t timestamp updated")
    except Exception as e:
        print(f"\t error updating timestamp for {imgPth}: {e}")



def singleImg(imgPth):
    exifTime = photoTakenTime(imgPth)
    if exifTime:
        print(f"\t taken time (EXIF): {exifTime}")        
        ts = exifToTimestamp(exifTime)
        if ts:
            print(f"\t Unix timestamp:    {ts}")            
            updateFileTimestamp(imgPth, ts)



def globJsons(srcDir):
    counter = -1
    print(f" globbing in {srcDir}... ")
    for fnImg in Path(srcDir).rglob('*.jpg'):
        counter += 1
        print(f"  {counter:3}: {fnImg}")        
        singleImg(fnImg)
        if counter > 4:
            pass
            # return            


imgDir = './Photos/2024'
globJsons(imgDir)

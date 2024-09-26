import os
import json
import time
from pathlib import Path
import traceback

from PIL import Image
import piexif


# Directory containing the JSON files
srcDirJson = './2024'
dstDir = '../Photos/2024'


def jpgDescSet(imgPth, desc, imgPthOut=None):

    try:
        img = Image.open(imgPth)
    except Exception as e:
        print(f"Error opening img file for desc change {imgPth}: {e}")

    try:
        # Get existing EXIF data (if any) from the image
        exifDct = piexif.load(img.info.get('exif', b''))
    except Exception as e:
        strE = f"{e}"
        if "No such file or directory: b''" in strE:
            print(f"        piexif.load failed for {Path(imgPth).name}")
        else:
            print(f"Error piexif.load() for {imgPth}: {e}")
        return


    try:
        # Convert description to bytes and add to the ImageDescription field
        exifDct["0th"][piexif.ImageIFD.ImageDescription] = desc.encode('utf-8')

        # Generate the updated EXIF bytes
        exifBts = piexif.dump(exifDct)

        # Save the image with the updated EXIF data
        if imgPthOut is None:
            imgPthOut = imgPth  # Overwrite the original image
        img.save(imgPthOut, exif=exifBts)

        print(f'        desc added to {Path(imgPth).name} - {desc[:64]}')

    except Exception as e:
        print(f"Error adding desc to {imgPth}: {e}")


updateTimestampCounter = 0
# Function to update the file's last modified time
def updateTimestamp(imgPth, timestamp):
    global updateTimestampCounter
    updateTimestampCounter += 1
    try:
        # Convert timestamp (Unix format) to appropriate format for os.utime
        mod_time = time.gmtime(int(timestamp))
        # Update the file's modification and access time
        os.utime(imgPth, (time.mktime(mod_time), time.mktime(mod_time)))
        if updateTimestampCounter % 20 == 0:
            print(f"        {updateTimestampCounter:3} timestamp update {Path(imgPth).name}")
    except Exception as e:
        print(f"Error updating timestamp for {imgPth}: {e}")

# Function to process JSON files
def globJsons(srcDir, dstDirRel):

    dstDirAbs = Path(dstDirRel).resolve()
    print(f"dest dir is {dstDirAbs}")

    for fnJson in Path(srcDir).rglob('*.json'):

        try:
            with open(fnJson, 'r') as f:
                dta = json.load(f)


            desc = dta.get('description', '')
            desc = desc.replace('\r\n', ' ')
            desc = desc.replace('\n', ' ')
            desc = desc.replace('%', ' percent ')
            if desc.strip() != "":
                pass
                # print(f"\tdesc:  {desc}")
                # print(f"\t{fnJson}")


            ts = dta.get('photoTakenTime', {}).get('timestamp')
            fnImg = dta.get('title')
            url = dta.get('url')
            fnShort = f"{fnImg[:16]}...{fnImg[-6:]}"
            if not ts or not fnImg:
                print(f"{fnJson} - missing title or photoTakenTime in {fnShort:28}")
            else:
                pass
                # print(f"img {fnShort:28} - new ts {ts}")


            #  path of the image file (assuming the image file is in the same directory as the JSON)
            pthImg = Path(fnJson).parent / fnImg
            pthImg = dstDirAbs / fnImg

            if not pthImg.exists():
                pthImg3 = dstDirAbs / Path(Path(fnImg).stem + "-edited" + Path(fnImg).suffix)
                if pthImg3.exists():
                    # print("   using suffix '-edited' ")
                    pthImg = pthImg3


            if not pthImg.exists():
                print(f"        no corresponding file in {dstDirAbs}")
                print(f"                      {Path(pthImg).stem} ")
                print(f"          for json fn {Path(fnJson).stem} ")
                # print(f"                 url  {url} ")

                # print(f"                 mask  {mask} ")
                '''
                    There might be several alternatives
                    original_35fa151c-b63b-49e3-a706-b106c2887d37_P.jpg
                    original_35fa151c-b63b-49e3-a706-b106c2887d37_P(1).jpg
                    original_8ab58009-8cb5-461c-9d70-ba3a5a4311dd_P.jpg
                    original_8ab58009-8cb5-461c-9d70-ba3a5a4311dd_P(1).jpg
                '''
                jsonStem = Path(fnJson).stem
                imgSuffix = Path(pthImg).suffix
                mask = f'{jsonStem}*{imgSuffix}'
                alts = []
                for alt in dstDirAbs.rglob(mask):
                    # print(f"                 alt {alt} ")
                    alts.append(alt)

                if len(alts) == 0:
                    print(f"                     no alternatives found  {dstDirAbs} {mask} ")
                    continue


                alts.sort()
                latestAlt = Path(alts[0]).name
                # print(f"                 lastet {latestAlt} ")

                # pthImgAlt = Path(fnJson).parent / latestAlt
                pthImgAlt = dstDirAbs / latestAlt

                if pthImgAlt.exists():
                    print(f"                     found an alt  {pthImgAlt} ")
                    pthImg = pthImgAlt
                else:
                    print(f"                     still not found  {pthImgAlt} ")
                    continue


            if pthImg.exists():
                if desc.strip() != "":
                    jpgDescSet(pthImg, desc )
                updateTimestamp(pthImg, ts)  # after changing meta data
                pass



        except Exception as e:
            print(f"Error processing {fnJson}: {e}")
            traceback.print_exc()
            os._exit(0)

# Run the function
globJsons(srcDirJson, dstDir)

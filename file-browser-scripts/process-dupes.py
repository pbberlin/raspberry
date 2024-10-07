import os
import json

fn = "./duplicates-names-mp4-mpg-mkv-2024-10-06-13-45-37.json"

def main():

    try:
        with open(fn) as f:
            dupes = json.load(f)

            for idx1, hashKey in enumerate(dupes):
                print(f"{idx1:3} hash key: {hashKey}")
                fileList = dupes[hashKey]
                for idx2, file in enumerate(fileList):
                    pass
                    print(f"    {idx2:3}     {file}")

                if len(fileList) == 2:
                    fn1 = fileList[0]
                    fn2 = fileList[1]
                    if type(fn1) is list:
                        fn1 = fn1[0]
                    if type(fn2) is list:
                        fn2 = fn2[0]
                        
                    if "./recordings-2022-08/" in fn1 and "./recordings-2024-02/" in fn2 :
                        
                        if fn2.endswith(".mkv.mp4") or fn2.endswith(".mp4"):
                            try:
                                pass
                                # os.remove( fn1 )
                                # print(f"\t deleted  {fn1}")
                            except Exception as error:
                                pass
                                print(f"\t removing file '{fn1}' caused error:\n\t {str(error)}")
                    else:
                        print("other case")


    except Exception as error:
        print(f"loading dupes file '{fn}' caused error: {str(error)}")


main()
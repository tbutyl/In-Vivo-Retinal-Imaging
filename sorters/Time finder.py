import os
import sys
import shutil
import math
from tkinter.filedialog import askdirectory

def sorting(source):
        file_list = os.listdir(source)
        print (source)
        for file in file_list:
                if os.path.isdir(source + '\\' + file) is True:
                        new_source = source + '\\' + file
                        if "fluorescence" in new_source and len(os.listdir(new_source))>2: #NOT the same file list as above, after and is needed because sometimes fluroescence fodlers got nested inside a folder named fluorescence.
                                fileList = os.listdir(new_source) 
                                first, last = fileList[0], fileList[len(fileList)-1] #get file names for time
                                firstSec, firstHr, firstM, firstS = formatter(first)
                                lastSec, lastHr, lastM, lastS = formatter(last)

                                imagingTime = lastSec-firstSec
                                #print(firstSec, lastSec)
                                print(imagingTime)

                                with open(source + '\\' + 'Imaging time.txt', 'w') as f:
                                        f.write(str(imagingTime)+' seconds elapsed')
                                        f.write('\n\nStarted imaging at: ' + str(firstHr) + ':' + str(firstM) + ':' + str(firstS))
                                        f.write('\nFinished imaging at: ' + str(lastHr) + ':' + str(lastM) + ':' + str(lastS))

                        elif "reflectance" in new_source or "noise" in new_source:
                                continue
                        else:
                                sorting(new_source)
                elif os.path.isfile(source + '\\' + file) is True:
                        continue


def formatter(name):
        nameStrip = name.strip("0123456789-0123456789-0123456789.abcdefghijklmnopqrstuvwxyz")
        nameList = nameStrip.split('_')
        nameHMS = int(nameList[1]) #has hours, min, sec as xx-xx-xx without '-'
        namems = float(nameList[2])*(10**-3)  #milisecond value
        #print(nameHMS, namems)
        nameH = math.floor(nameHMS*(10**-4)) #makes the 6 digit nuber have a decimal after the hours, floors it to the interger to get the hour images were taken
        nameM = math.floor((nameHMS - (nameH*(10**4)))*(10**-2)) # subtracts the hours from the min and sec component of the time then does similar to above to get minutes
        nameS = nameHMS - nameH*(10**4) - nameM*(10**2)
        totalSec = nameH*(60**2) + nameM*60 + nameS + namems #should compute total seconds
        
        if nameH > 12:
                nameHr = nameH - 12
        else:
                nameHr = nameH

        return totalSec, nameHr, nameM, nameS

def main():
    #source = input("Source Path: ")
    source = askdirectory()
    sorting(source)
    print("Completed")
main()



#sometimes the first image of the APD1/reflectance stack is not correctly sorted,
#could making the folders throw off something about file_list?

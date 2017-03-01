#Seems to work as of 09-13-2016 10:45 AM
from tkinter.filedialog import askdirectory
import os
import sys
import shutil

def sorting(source):
        file_list = os.listdir(source)
        # print(file_list)
        print (source)
        destination_apd1 = source + "/reflectance" #\\ is needed because \ causes a unicode escape
        destination_apd2 = source + "/fluorescence"

        if not os.path.exists(destination_apd1) or not os.path.exists(destination_apd2):
                if not os.path.exists(destination_apd1):
                        os.makedirs(destination_apd1)
                if not os.path.exists(destination_apd2):
                        os.makedirs(destination_apd2)

        for each_file in file_list:
                if os.path.isfile(source + '/' + each_file) is True:
                        if "APD1" in each_file:
                                shutil.move(source + '/' + each_file, destination_apd1)       
                        elif "APD2" in each_file:
                                shutil.move(source + '/' + each_file, destination_apd2)
                elif os.path.isdir(source + '/' + each_file) is True:
                        new_source = source + '/' + each_file
                        sorting(new_source)

def cleanup(source):
    file_list = os.listdir(source)
    for each_file in file_list:
        new_source = source+'/'+each_file
        if os.path.isdir(new_source) is True:
            if ("reflectance" in new_source or "fluorescence" in new_source) and (len(os.listdir(new_source))==0):
                print("\t [-] deleting "+ new_source)
                os.rmdir(new_source)
            else:
                cleanup(new_source)
        else:
            continue

def main():
    # old: source = input("Source Path: ")
    source = askdirectory()
    sorting(source)
    cleanup(source)
    print("Completed")
main()



#sometimes the first image of the APD1reflectance stack is not correctly sorted,
#could making the folders throw off something about file_list?

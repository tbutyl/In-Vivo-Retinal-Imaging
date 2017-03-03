from tkinter.filedialog import askdirectory
import os
import sys
import shutil

def sorting(source):
        file_list = os.listdir(source)
        print (source)
        destination_apd1 = source + "/reflectance/" #the trailing / is very important to allow the try/except statements to work. without it, files are sequentially overwritten
        destination_apd2 = source + "/fluorescence/"

        for each_file in file_list:
                if os.path.isfile(source + '/' + each_file) is True:
                        if "APD1" in each_file:
                                try:
                                    shutil.move(source + '/' + each_file, destination_apd1)       
                                except:
                                    os.makedirs(destination_apd1)
                                    shutil.move(source + '/' + each_file, destination_apd1)       
                        elif "APD2" in each_file:
                                try:
                                    shutil.move(source + '/' + each_file, destination_apd2)
                                except:
                                    os.makedirs(destination_apd2)
                                    shutil.move(source + '/' + each_file, destination_apd2)
                elif os.path.isdir(source + '/' + each_file) is True:
                        if source+'/'+each_file == source+'/fluorescence' or source+'/'+each_file == source+'/reflectance':
                                continue
                        else:
                                new_source = source + '/' + each_file
                                sorting(new_source)

def main():
    source = askdirectory()
    sorting(source)
    print("Completed")
main()

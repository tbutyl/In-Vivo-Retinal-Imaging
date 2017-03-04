from tkinter.filedialog import askdirectory
import os
import sys
import shutil

sp = os.sep

def sorting(source):
        file_list = os.listdir(source)
        print (source)
        destination_apd1 = os.join(source, 'reflectance')+sp #the trailing / is very important to allow the try/except statements to work. without it, files are sequentially overwritten
        destination_apd2 = os.join(source,'fluorescence')+sp

        for each_file in file_list:
                file_path = os.join(source,each_file)
                if os.path.isfile(file_path) is True:
                        if 'APD1' in each_file:
                                try:
                                    shutil.move(file_path, destination_apd1)       
                                except:
                                    os.makedirs(destination_apd1)
                                    shutil.move(file_path, destination_apd1)       
                        elif 'APD2' in each_file:
                                try:
                                    shutil.move(file_path, destination_apd2)
                                except:
                                    os.makedirs(destination_apd2)
                                    shutil.move(file_path, destination_apd2)
                elif os.path.isdir(file_path) is True:
                        if file_path == os.join(source,'fluorescence') or file_path == os.join(source,'reflectance'):
                                continue
                        else:
                                new_source = os.join(source,each_file)
                                sorting(new_source)

def main():
    source = os.path.abspath(askdirectory()) #the abspath should clean up the mixed file separators
    sorting(source)
    print('Completed')
main()

from tkinter.filedialog import askdirectory
import os
import sys
import shutil

sp = os.sep

def sorting(source):
        file_list = os.listdir(source)
        print (source)
        destination_apd1 = source + sp + "reflectance"# + sp #the trailing / is very important to allow the try/except statements to work. without it, files are sequentially overwritten
        destination_apd2 = source + sp + "fluorescence"# +sp

        for each_file in file_list:
                if os.path.isfile(source + sp + each_file) is True:
                        if "APD1" in each_file:
                                try:
                                    shutil.move(source + sp + each_file+sp, destination_apd1)       
                                except:
                                    os.makedirs(destination_apd1)
                                    shutil.move(source + sp + each_file, destination_apd1)       
                        elif "APD2" in each_file:
                                try:
                                    shutil.move(source + sp + each_file+sp, destination_apd2)
                                except:
                                    os.makedirs(destination_apd2)
                                    shutil.move(source + sp + each_file, destination_apd2)
                elif os.path.isdir(source + sp + each_file) is True:
                        if source+sp+each_file == source+sp+"fluorescence" or source+sp+each_file == source+sp+"reflectance":
                                continue
                        else:
                                new_source = source + sp + each_file
                                sorting(new_source)

def main():
    source = os.path.abspath(askdirectory()) #the abspath should clean up the mixed file separators
    sorting(source)
    print("Completed")
main()

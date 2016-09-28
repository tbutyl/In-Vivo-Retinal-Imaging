import os
import sys
import shutil

def sorting(source):
        file_list = os.listdir(source)
        print (source)
        destination_apd1 = source + "\\reflectance" #\\ is needed because \ causes a unicode escape
        destination_apd2 = source + "\\fluorescence"

        if not os.path.exists(destination_apd1) or not os.path.exists(destination_apd2):
                if not os.path.exists(destination_apd1):
                        os.makedirs(destination_apd1)
                if not os.path.exists(destination_apd2):
                        os.makedirs(destination_apd2)
                if os.path.exists(destination_apd1) and os.path.exists(destination_apd2):
                        sorting(source)
        for file in file_list:
                if os.path.isfile(source + '\\' + file) is True:
                        if "APD1" in file:
                                shutil.move(source + '\\' + file, destination_apd1)       
                        elif "APD2" in file:
                                shutil.move(source + '\\' + file, destination_apd2)
                elif os.path.isdir(source + '\\' + file) is True:
                        new_source = source + '\\' + file
                        if "reflectance" in new_source or "fluorescence" in new_source:
                                check = os.listdir(source+"\\"+file)
                                if len(check) == 0:
                                        os.rmdir(source+"\\"+file)
                                else:
                                        continue
                        else:
                                sorting(new_source)


def main():
    source = input("Source Path: ")
    sorting(source)
    print("Completed")
main()



#sometimes the first image of the APD1/reflectance stack is not correctly sorted,
#could making the folders throw off something about file_list?

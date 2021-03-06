from tkinter.filedialog import askdirectory
import os
import sys
import shutil
import re
import numpy as np
from skimage import io as io
import operator
import glob
import math

#CAN ONLY BE RUN AFTER SORTING!! 






#~~~~~~~~~~~~~~~~~~~~~~~~~~~NEVER TESTED!!!!!!

previous_stack_count = None
previous_path = None
img_stack = None

def sorting(source):
        file_list = os.listdir(source)
        print (source)


        for each_file in file_list:

                file_path = os.path.join(source,each_file)
                if os.path.isdir(file_path) is True:
                        if file_path == os.path.join(source,'fluorescence'):
                                process_stack(file_path,previous_stack_count,previous_path, img_stack)
                        elif file_path == os.path.join(source, "OCT") or file_path == os.path.join(source,'reflectance'):
                                continue
                        else:
                                new_source = os.path.join(source,each_file)
                                sorting(new_source)
                else:
                        continue

def process_stack(path, previous_stack_count, previous_path, img_stack):

        new_file_list = os.listdir(path)
        new_stack_count = len(new_file_list)
        eye_path = get_parent_path(get_parent_path(path))
        previous_eye_path = get_parent_path(get_parent_path(previous_path))

        if previous_stack_count == None:
                #make new stack
                img_stack = load_stack(new_file_list)
        elif previous_eye_path != eye_path:
                save_stack(previous_eye_path, img_stack)
                img_stack= load_stack(new_file_list)
        else:
                if new_stack_count == previous_stack_count:
                        new_stack = load_stack(new_file_list)
                        img_stack = np.concatenate((img_stack, new_stack))
                else:
                        save_stack(previous_eye_path, img_stack)
                        img_stack= load_stack(new_file_list)


        previous_stack_count = new_stack_count
        previous_path = path

def get_parent_path(note_path):
        
        parent_path = str.rsplit(note_path, os.sep, 1)[0]

        return parent_path

def load_stack(image_list):

        img_collection = io.ImageCollection(image_list)
        img_stack = io.concatenate_images(img_collection)

        return img_stack

def save_stack(eye_path, img_stack):
        
        stack_names = glob.glob(os.path.join(eye_path,"stack*"))
        message = "\n[+]\tStack Saved:\n\t\t"

        try:
                last_stack_name = str.rsplit(stack_names[-1],os.sep,1)[1] # 1 should be same index as -1. hopefully the except only happens here and not from the next line... but that shouldn't happen as long as the only stack name iis from this program and even the the spplit may work but int would throw a TypeError
                stack_index = int((str.rsplit(last_stack_name, "_")[1]).rstrip(".tif"))
                io.imsave(os.path.join(eye_path,"stack_"+str(stack_index+1)+".tif"), img_stack)
                print(message+os.path.join(eye_path,"stack_"+str(stack_index+1)+".tif"))

        except IndexError:
                io.imsave(os.path.join(eye_path,"stack_0.tif"), img_stack)
                print(message+os.path.join(eye_path,"stack_0.tif"))

def main():
        source =askdirectory()
        if source == '':
                sys.exit("\n\nExited: No file path selected\n\n")
        sorting(os.path.abspath(source))
        save_stack(get_parent_path(get_parent_path(previous_path, img_stack))) #covers case of very last stack that wouldnt be saved otherwise.
        print('\n\n\n\t\t\t\t---------\n\t\t\t\tCompleted\n\t\t\t\t---------')
main()

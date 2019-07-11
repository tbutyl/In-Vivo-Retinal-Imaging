#This program was developed to put the OCT volumes from a superaveraging experiment into a single stack in order to decrease the time it takes to transfer data from computer -> external HD


import numpy as np
import skimage.io as io
import sys.exit as exit
import os
from tkinter.filedialog import askdirectory


def sort_key(path):
	file_end = path.rsplit(os.sep,1)[1]
	file_number = file_end.rstrip('.tif')
	return int(file_number)


def files2stack(amp_folder):
	files=sorted(glob.glob('{}{}*'.format(amp_folder,os.sep)),key=sort_key)
	raw_stack = io.imread_collection(files)
	stack = io.collection.concatenate_images(raw_stack).astype('int32')

	return stack

def find_stacks(top_path):
	
	path = '{}{}**{}OCT**{}*.tif'.format(top_path, os.sep, os.sep, os.sep)
	ic = io.ImageCollection(path, conserve_memory=True)
	stack = ic.concatenate()
	io.imsave('{}{}all_oct.tif'.format(top_path, os.sep))

	#step 1 save files to stacks in top path -> this is going to ballon storage space required. BAD
	#amp_folders = glob.iglob(path, recursive=True)
	#for folder in amp_folders:
	#	stack = files2stack(folder)
	#	io.imsave('{}{}{}.tif'.format(top_path, os.sep, folder), stack.astype('int32'))


def main():
	#TOP PATH MUST CONTAIN ONLY OCT FILES FOR SUPERAVERAGING!!!
	top_path = askdirectory()
	if top_path=='':
		exit('\nExited: No directory was selected.')
	elif os.path.isfile(top_path):
		exit('\nExited: File Selected. Please select top-level directory.')
	find_stacks(top_path)

if __name__ == '__main__':
	main()

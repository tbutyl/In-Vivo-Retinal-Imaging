from tkinter.filedialog import askdirectory
import os
import sys
import shutil
import skimage.io as io

def sorting(source):
	file_list = os.listdir(source)
	
	for each_file in file_list:
		file_path = os.path.join(source, each_file)
		if os.path.isdir(file_path) and "DepthStack" in file_path:
			#split images
		elif os.path.isdir(file_path):
			sorting(file_path)
		else:
			continue



def split_image(image):
	
	#open
	
	#loop and split into two sets, every other
	#save each


def main():
#run stuff

import numpy as np
import skimage.io as io
import os,glob,sys
from skimage.transform import warp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search_function

@glob_dec()
def test(file_name,full_path=None):
	print(path)

def main():
	test(file_name='stack_1.tif')

if __name__=='__main__':
	main()
	

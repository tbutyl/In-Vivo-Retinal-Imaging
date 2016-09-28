import numpy as np
from scipy import ndimage
from libtiff import TIFF, TIFFfile, TIFFimage
import sys, argparse

def importStack(pathName='/Users/emiller/Downloads/registered.tif'):
	"Imports a Multipage tiff using PyLibTiff - could alternatively use skimage.extensions.tifffile"
	img = TIFFfile(pathName)
	samples, names = img.get_samples()
	img.close()
	samples = np.asarray(samples).squeeze()

	return samples


def filterImg(imgArr, size):
	"Does the 3D median filter in time with window size set by var size"
	filtered = ndimage.filters.median_filter(imgArr,footprint=np.ones((size,1,1)))

	return filtered

def saveStack(procImg,path='/Users/emiller/Downloads/output.tif'):
	"Saves the multipage tiff"
	img = TIFFimage(procImg)
	img.write_file(path)
	del img

def main():

	parser=argparse.ArgumentParser(description='Temporal Filter for Tiffs')
	parser.add_argument('--filter', dest='filterType', required=False)
	parser.add_argument('--size', dest='filterSize', required=False)
	parser.add_argument('--path', dest='filePath', required=False)
	parser.add_argument('--nameIn', dest='inputFile', require=False)
	parser.add_argument('--nameOut', dest='fileName', required=False)
	args = parser.parse_args()
	filePath = '/Users/emiller/Downloads/'
	inputFile = 'registered.tif'
	fileName = 'output.tif'
	filterSize=5
	filterType = 'median'
	imgArr = importStack()
	filtered = filterImg(imgArr)
	saveStack(filtered)

if __name__=='__main__':
	main()

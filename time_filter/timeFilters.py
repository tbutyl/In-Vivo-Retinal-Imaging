import numpy as np
from scipy import ndimage
from libtiff import TIFF, TIFFfile, TIFFimage
import sys, argparse
from skimage.filters import rank


def importStack(path, inputFile):
	"Imports a Multipage tiff using PyLibTiff - could alternatively use skimage.extensions.tifffile"
	print("Importing", path+inputFile)
	pathName = path+inputFile
	img = TIFFfile(pathName)
	samples, names = img.get_samples()
	img.close()
	samples = np.asarray(samples).squeeze()
	print("Done")

	return samples


def modeFilter(imgArr, size):
	"Does the mode filter"
	#currently not very effective - maybe a gaussian blur first on the reslice would help?
	reslice = np.swapaxes(imgArr,0,1)
	processed = []
	for frame in reslice:
		processed.append(rank.modal(frame, np.ones((size,1))))
	processed = np.asarray(processed)
	filtered = np.swapaxes(processed,0,1)

	return filtered

def bilatFilter(imgArr, size):
	"Does the bilateral mean filter"
	reslice = np.swapaxes(imgArr,0,1)
	processed = []
	for frame in reslice:
		# including a low and high set of filters doens't work -- seems that if pixels aren't in range it floors the central px?
		processed.append(rank.mean_bilateral(frame, np.ones((size,1)),s0=10,s1=75))
		# has a lot of 0 pixels - why?!?!
		# processed.append(rank.mean_bilateral(frame, np.ones((size,1)),s0=0,s1=100))
	processed = np.asarray(processed)
	filtered = np.swapaxes(processed,0,1)

	return filtered

def medFilter(imgArr, size):
	"Does the 3D median filter in time with window size set by var size"
	filtered = ndimage.filters.median_filter(imgArr,footprint=np.ones((size,1,1)))

	return filtered

def saveStack(procImg,path,fileName):
	"Saves the multipage tiff"
	pathName = path+fileName
	img = TIFFimage(procImg)
	img.write_file(pathName)
	del img

def main():

	parser=argparse.ArgumentParser(description='Temporal Filter for Tiffs')
	parser.add_argument('--filter', dest='filterType', required=False,type=str, action='store')
	parser.add_argument('--size', dest='filterSize', required=False,type=int, action='store')
	parser.add_argument('--path', dest='filePath', required=False, type=str, action='store')
	parser.add_argument('--nameIn', dest='inputFile', required=False, type=str, action='store')
	parser.add_argument('--nameOut', dest='fileName', required=False, type=str, action='store')
	args = parser.parse_args()
	filePath = '/Users/emiller/Downloads/'
	inputFile = 'registered.tif'
	fileName = 'output.tif'
	size=5
	filterType = 'median'
	if args.filterSize:
		size=int(args.filterSize)
	if args.filePath:
		filePath=str(args.filePath)
	if args.inputFile:
		inputFile=str(args.inputFile)
	if args.fileName:
		fileName=str(args.fileName)

	imgArr = importStack(filePath, inputFile)

	if args.filterType:
		if args.filterType=='mode':
			#run modal
			print('mode filter of size ',size)
			filtered = modeFilter(imgArr, size)
		elif args.filterType=='bilateral':
			#run bilinear
			print('bilateral filter of size ',size)
			filtered = bilatFilter(imgArr,size)
		else:
			print('You did not enter a valid filter type, bye felica')
			sys.exit()
	else:
		# run median
		print('median filter of size ',size)
		filtered = medFilter(imgArr, size)

	saveStack(filtered, filePath, fileName)

if __name__=='__main__':
	main()

import numpy as np
from scipy import ndimage
from libtiff import TIFF, TIFFfile, TIFFimage
from itertools import zip_longest

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def importStack(pathName='/Users/emiller/Downloads/registered.tif'):
	"Imports a Multipage tiff using PyLibTiff - could alternatively use skimage.extensions.tifffile"
	img = TIFFfile(pathName)
	samples, names = img.get_samples()
	img.close()
	# samples = np.asarray(samples).squeeze()

	return samples

def correlator(imgArr):

	out = [] 
	for slice in imgArr:
		for lineIndex, line in enumerate(slice):
			lineNorm = line-np.average(line)
			lineStd = np.std(line)
			if lineIndex == 0:
				prevNorm = slice[1]-np.average(slice[1])
				prevStd = np.std(slice[1])
			else:
				prevNorm = slice[lineIndex-1]-np.average(slice[lineIndex-1])
				prevStd = np.std(slice[lineIndex-1])
			corr = np.dot(lineNorm,prevNorm)/(lineStd*prevStd*(len(line)))
			out.append(corr)
	organized = list(grouper(out,400))

	truthTable = []
	for img in organized:
		for corVal in img:
			if corVal <0.5:
				truthTable.append(1)
			else:
				truthTable.append(0)
	truthTable = list(grouper(truthTable,400))
	
	return truthTable

def filterImg(imgArr, truthTable, truthFlag=None, size=5):

	filterList = []
	for slice in imgArr:
		filterList.append(ndimage.filters.median_filter(slice,footprint=np.ones((size,1))))
	# ALTERNATIVE SINGAL LINE
	# filtered = ndimage.filters.median_filter(imgArr,footprint=np.ones((size,1,1)))


	if truthFlag!=None:
		out = np.empty_like(imgArr)
		for imgIndex,img in enumerate(truthTable):
			for lineIndex,line in enumerate(img):
				if line==1:
					out[imgIndex][lineIndex] = filterList[imgIndex][lineIndex]
					# out[imgIndex][lineIndex] = np.zeros((1,256))
				else:
					out[imgIndex][lineIndex] = imgArr[imgIndex][lineIndex]

		filtered = np.swapaxes(out,0,1)
	else:
		filtered = np.swapaxes(filterList,0,1)

	return filtered

def saveStack(procImg,path='/Users/emiller/Downloads/output2.tif'):

	img = TIFFimage(procImg)
	img.write_file(path)
	del img

def main():

	#truthTable set this way currently so correlator isn't run becuase it really doesn't fix anything. Should set up flags for cmd line usage.
	truthTable = None
	imgArr = importStack()
	reslice = np.swapaxes(np.asarray(imgArr).squeeze(),0,1)
	# truthTable = correlator(reslice)
	filtered = filterImg(reslice, truthTable)
	saveStack(filtered)

main()

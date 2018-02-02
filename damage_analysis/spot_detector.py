from tkinter.filedialog import askdirectory
import numpy as np
import scipy.ndimage as nd
import matplotlib.pyplot as plt
import skimage.io as io
import glob, os,sys
from scipy.signal import argrelextrema as locmax
import _pickle as pickle

def findRPE(stack):
	#get the average A-scan
	profile = np.mean(stack, axis=(0,2))
	#find the maxima using a spacing of 7 pixels; taken from arrestin analysis program
	maxLoc = locmax(profile, np.greater, order=7)[0]
	#arrange the peak depth locations and intensity values in a matrix
	peaks = np.array([item for item in zip(maxLoc, profile[maxLoc])])
	#get the indices to sort the peaks based on intensity and just take the intensity sorting indices
	ind = np.argsort(peaks, axis=0)[:,1]
	#sort the peaks using the indices and take the top two intensity values, which should be the rpe and bruch's
	ref_peaks = peaks[ind][-2:]
	other_peaks = peaks[ind][:-2]
	#if the rpe and bruch's were detected, they should be close in intensity
	peak_ratio=ref_peaks[1,1]/ref_peaks[0,1]

	#check to make sure rpe and bruch's were detected
	#ref_peaks[1,1] is highest intensity, and probably bruchs, so usually ref_peaks[0,0]>ref_peaks[1,0]
	if np.all(ref_peaks[1,1]>other_peaks[:,1]) and np.all(ref_peaks[0,1]>other_peaks[:,1]) and peak_ratio<1.1 and ref_peaks[0,1]<ref_peaks[1,1]:
		#if the brightest peak is bruch's, pick the rpe
		if ref_peaks[0,0]>ref_peaks[1,0]:
			rpe = ref_peaks[1,0]
		#if the brightest peak is the rpe, pick the rpe
		else:
			rpe = ref_peaks[0,0]
	else:
		#This likely means there was only one peak for brcuhs/rpe and something is definitely wrong
		print("Error: Brightest Peaks are not Bruch's and RPE")
		rpe = ref_peaks[1,0]

	return rpe

def cutBscan(stack):
	
	rpe = findRPE(stack)
	#cut the stack to just get the photoreceptors (and a little extra)
	cutStack = stack[:,rpe+31:rpe+171,:]
	
	return cutStack

def var_filt(img, z,y,x):
	fimg = img.astype('f8') #This is float64, cannot save it this way and use with imagej!!!
	mean = nd.uniform_filter(fimg, (y,z,x))
	sqr_mean = nd.uniform_filter(fimg**2, (y,z,x))
	var = sqr_mean-mean**2
	enface = np.mean(var,axis=1)

	return enface


def detect_spot(cutStack, save_path):

	var_img = var_filt(cutStack, 3,3,16)
	#try to filter out regions of varying intensity to accentuate damage
	bsub = var_img - nd.uniform_filter(var_img, (75,300))
	enface_detector = nd.gaussian_filter(bsub,3)
	point = np.where(enface_detector==np.max(enface_detector))
	enface = np.mean(cutStack,axis=1)
	dmgBscan = np.mean(cutStack[point[0]-5:point[0]+5,:,:],axis=0)

	try:
		with open(os.path.join(save_path, 'onh_info.pkl'), 'rb') as f:
			info = pickle.load(f)
	except FileNotFoundError:
		print('No ONH was found at {}'.format(save_path))
		onh=-1
	else:
		onh = info.centroid

	f, ax = plt.subplots(3,1,sharex=True)
	ax[0].imshow(enface,cmap='gray')
	ax[0].scatter(point[1],point[0], c='r')
	if onh!=-1:
		ax[0].scatter(onh[1],onh[0],c='g')
	ax[1].imshow(bsub, cmap='gray')
	ax[2].imshow(dmgBscan, cmap='gray')
	path_info = save_path.split(os.sep)[4:8]
	file_name=''
	for each in path_info:
		file_name = file_name+each+'_'
	plt.savefig('{}{}{}bsub_var.tif'.format(save_path,os.sep,file_name))
	plt.close()

def find_bscans(path):

	seek = path + os.sep + '**' + os.sep + 'flat_Bscans.tif'
	Bscans = glob.iglob(seek, recursive=True)

	for scan in Bscans:
		scan = scan.replace('/',os.sep)
		stack = io.imread(scan)
		print('\nCutting Bscans for {}\n'.format(scan))
		cutStack = cutBscan(stack)
		del stack
		save_path = scan.rsplit(os.sep,1)[0] 
		io.imsave('{}{}Cut Bscans.tif'.format(save_path, os.sep), cutStack.astype('uint16'))
		print('Detecting Damage for {}\n'.format(scan))
		detect_spot(cutStack,save_path)

def main():
	     
    top_path = askdirectory()
    if top_path=='':
            sys.exit('\nExited: No directory was selected')
    elif os.path.isfile(top_path):
            sys.exit('Exited: File selected. Please select top directory')
    find_bscans(top_path)
    print('\n--------\nComplete\n--------')


if __name__ == '__main__':
        main()

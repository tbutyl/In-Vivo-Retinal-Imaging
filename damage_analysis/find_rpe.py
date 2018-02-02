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
	rpe = ref_peaks[0,1]

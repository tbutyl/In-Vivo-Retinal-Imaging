#This code is used for pre damage OCT cut bscans to measure a baseline annular profile. It combines processing from spot_detector and offset_linear_fit
#However, it computes the background as the average of rings of 30-60 pixel radii as well as the fit offset and saves both.
#The data needs to be aggregated after this program is run.
from tkinter.filedialog import askdirectory
import numpy as np
import scipy.ndimage as nd
import matplotlib.pyplot as plt
from skimage.morphology import rectangle,remove_small_objects
import skimage.io as io
import glob, os,sys
from scipy.signal import argrelextrema as locmax
import _pickle as pickle
from skimage.filters import threshold_yen
from skimage.measure import label, regionprops
from skimage.exposure import rescale_intensity
from skimage.draw import circle_perimeter
from skimage.transform import resize
from scipy import optimize as op

#for fitting a gaussian
#from https://scipy-cookbook.readthedocs.io/items/FittingData.html
class Parameter:
    
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def __call__(self):
        return self.value

def fit(function, parameters, y, x= None):

    def fit2(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)
    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]

    return op.leastsq(fit2,p)


def analyze_damage(cutStack, dmg_point):

    """This does the concentric ring analysis"""

    num_rings=60

    #initialize data containers
    analysis_mat = np.empty((140,num_rings))

    #make image 256x256 for analysis
    restack = resize(np.swapaxes(cutStack,0,1), (140,256,256), preserve_range=True)

    #outer loop each frame in depth
    for depth, frame in enumerate(restack): 
    #loop drawing a ring at point with increasing radius up to $$$$$
        for r in range(0,num_rings):
            #set up background anew for each loop
            null_img = np.zeros((256,256))
            rr,cc = circle_perimeter(int(dmg_point[0]),int(dmg_point[1]/4),r, method='andres')
            #these remove indices of the ring that are off the side of the image
            if np.any(rr>255):
                ind = np.where(rr<256)
                rr=rr[ind]
                cc=cc[ind]
            if np.any(cc>255):
                ind = np.where(cc<256)
                rr=rr[ind]
                cc=cc[ind]
            if np.any(rr<0):
                ind = np.where(rr>=0)
                rr=rr[ind]
                cc=cc[ind]
            if np.any(cc<0):
                ind = np.where(cc>=0)
                rr=rr[ind]
                cc=cc[ind]
            null_img[rr,cc]=1
            #average intensity at each ring
            analysis_mat[depth,r]=np.sum(frame*null_img)/np.sum(null_img)

    return analysis_mat

#This finds the background by averaging rings of 30-60 pixel radii
#OR uses a fit gaussian to find the offset level as background. They are the same,
#but the offset was previously used for convience because the code was in place.
def background(anal_mat):

    def offset_gauss(x): return a()

    profile_fits = np.empty((140,1))
    depth=0
    for row in anal_mat:
        a = Parameter(10000)
        param_vals = fit(offset_gauss, [a], row[30:61])
        profile_fits[depth] = np.abs(param_vals[0][0])
        depth+=1
    #makes a big mat with measurements and linearly fit offset
    combo = np.concatenate((anal_mat, profile_fits), axis=1)
    bkg = np.reshape(np.mean(anal_mat[:,30:61], axis=1), (140,1))
    #print(profile_fits-bkg)
    return combo,bkg
        


def find_dmg(path):

    seek = path + os.sep + '**' + os.sep + 'post_damage_location.npy'
    dmg_spots = glob.iglob(seek, recursive=True)

    for scan in dmg_spots:
        scan = scan.replace('/',os.sep)
        save_path = scan.rsplit(os.sep,1)[0] 
        print('Detecting Damage for {}\n'.format(scan))
        #y, x
        dmg_loc = np.load(scan)
        cut_bscan = io.imread('{}{}Cut Bscans.tif'.format(save_path,os.sep))
        anal_mat = analyze_damage(cut_bscan, dmg_loc)
        np.save('{}{}analysis_matrix.npy'.format(save_path, os.sep),anal_mat)
        lin_fit, bkg = background(anal_mat)
        np.save('{}{}linear_parameter.npy'.format(save_path,os.sep), lin_fit)
        np.save('{}{}mean_background.npy'.format(save_path, os.sep), bkg)
        bkg_rep = np.repeat(bkg, 60, axis=1)
        lin_rep = np.repeat(np.reshape(lin_fit[:,60],(140,1)),60,axis=1)
        anal_bkg = anal_mat-bkg_rep
        anal_fit = anal_mat-lin_rep
        np.save('{}{}background_subtracted_matrix.npy'.format(save_path, os.sep), anal_bkg)
        np.save('{}{}linear_fit_subtracted_matrix.npy'.format(save_path, os.sep), anal_fit)


def main():
         
    top_path = askdirectory()
    if top_path=='':
            sys.exit('\nExited: No directory was selected')
    elif os.path.isfile(top_path):
            sys.exit('Exited: File selected. Please select top directory')
    find_dmg(top_path)
    print('\n--------\nComplete\n--------')


if __name__ == '__main__':
        main()

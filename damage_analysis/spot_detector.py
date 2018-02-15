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


def max_area(props):
    """
    Finds the largest "particle" detected, excluding any that are on the sides of the image.
    """
    i_max=-1
    max_area = -1
    for i, prop in enumerate(props):
        bbx = np.array(prop.bbox)
        #gets rid of any region touching the sides - fufils "exlude on side" function of imagej Analyze particles
        if (bbx[0]==0 or bbx[2]==51) or (bbx[1]==0 or bbx[3]==251):
            continue
        #if np.any(bbx==0) or np.any(bbx==256):
        #    continue
        else:
            #find max area
            if prop.area > max_area:
                max_area = prop.area
                i_max = i
    return i_max

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
        #This likely means there was only one peak for brcuhs/rpe and something is definitely wrong - edit: often happens 
        #when onh wasn't detected
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

def measure_damage(cutStack, enface, point, save_path):
    """
    This function takes the stack that is cut to the photoreceptor layer and the detected damage spot then finds the centroid
    of the damage spot and does a concentric ring analysis at each location in depth.
    -------
    Inputs:
    
    cutStack - the OCT stack that has been cut to 140 frames in depth based on the location of the RPE.

    enface - the mean cut stack image for segmenting the damage spot.
    
    point - the damage location that was detected using the variance enface image.

    save_path - the cleaned path for saving the analysis.

    --------
    Outputs:

    adjusted_point - the corrected damage centroid location

    analysis - this is a matrix when the rows are depth and columns are radius of the concentric rings. The value at each point is the average
    intensity along the respective ring. This is saved for analysis, which will likely be done in a jupyter notebook.
    """
    
    y_dist = 51
    x_dist = 201
    if point[0]<((y_dist-1)/2):
        #top side
        y=0
    elif point[0]>256-((y_dist-1)/2):
        #bottom
        y=206
    else:
        y=point[0]-25
    if point[1]<((x_dist-1)/2):
        #left
        x=0
    elif point[1]>1024-((x_dist-1)/2):
        #right
        x=824
    else:
        x=point[1]-100
    left_corner = (int(y),int(x))
    damage_area = enface[left_corner[0]:left_corner[0]+y_dist,left_corner[1]:left_corner[1]+x_dist]

    #g_img = rescale_intensity(nd.gaussian_filter(damage_area-np.mean(damage_area),(1,4)), out_range=(0,256))
    g_img = rescale_intensity(nd.gaussian_filter(damage_area,(1,4)), out_range=(0,256))
    thresh = threshold_yen(g_img)
    classified_img = remove_small_objects(g_img>thresh)

    labels=label(classified_img, connectivity=2)
    props=regionprops(labels)

    #io.imsave('{}{}damage_binary.tif'.format(save_path,os.sep), (classified_img.astype('uint8'))*256)
    #io.imsave('{}{}damage_spot.tif'.format(save_path,os.sep), (damage_area).astype('uint16'))
    #This checks if the thresholding has failed and the background was thought to be part fo signal.
    #often happens when a vessel is in the area. 40% may be too high and is arbitrary.
    if np.sum(classified_img)/10251<0.3:
        try:
            #if there is mroe than one prop, throw an exception
            assert len(props)==1
        except:
            #hopefully the prop we want will have the biggest area....
            prop_ind = max_area(props)
            if prop_ind==-1:
                return None, classified_img, damage_area
            adj_point = props[prop_ind].centroid
            new_point = (adj_point[0]+y,adj_point[1]+x)
            return new_point, classified_img, damage_area
        else:
            adj_point = props[0].centroid
            new_point = (adj_point[0]+y,adj_point[1]+x)
            return new_point, classified_img, damage_area

    return None, classified_img, damage_area


def analyze_damage(cutStack, dmg_point):

    """This does the concentric ring analysis"""

    num_rings=60

    #initialize data containers
    analysis_mat = np.empty((140,num_rings))
    profile_fits = np.empty((140,3))

    #offset gaussian forced to have peak at x=0
    def offset_gauss(x): return a()+(b()-a())*np.exp(-(x/(2*sigma()))**2)

    #make image 256x256 for analysis
    restack = resize(np.swapaxes(cutStack,0,1), (140,256,256), preserve_range=True)

    #outer loop each frame in depth
    for depth, frame in enumerate(restack): 
        #set up parameters for fitting
        sigma = Parameter(10)
        a=Parameter(10000)
        b=Parameter(25000)
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

        #fit an offset gaussian
        param_vals = fit(offset_gauss,[sigma,a,b],analysis_mat[depth,:])
        profile_fits[depth,0] = param_vals[0][0]
        profile_fits[depth,1] = param_vals[0][1]
        profile_fits[depth,2] = param_vals[0][2]


    return analysis_mat, profile_fits
    

def detect_spot(cutStack, save_path):

    try:
        with open(os.path.join(save_path, 'onh_info.pkl'), 'rb') as f:
            info = pickle.load(f)
    except FileNotFoundError:
        print('No ONH was found at {}'.format(save_path))
        onh=-1
    else:
        onh = info.centroid

    var_img = var_filt(cutStack, 3,3,16)
    #try to filter out regions of varying intensity to accentuate damage
    bsub = var_img - nd.uniform_filter(var_img, (20,80))
    #########
    enface_detector = nd.gaussian_filter(bsub,(3,9))
    if onh!=-1:
        mock_img = rectangle(256,1024)
        #Use the center point to compute where the upper left corner of the rectangle should be
        #left_corner = (int(onh[0]-50),int(onh[1]-200)) @18
        #the if-elses are to make sure the left corner isn't out of the frame, or else it does not get drawn.
        #Don't need to worry if the box goes off the image bounds, it is silently ignored.
        y_dist = 161
        x_dist = 401
        if onh[0]<80:
            y=0
            #shift the size of the onh mask to make it smaller by the amount that is over the image bounds.
            y_dist += (onh[0]-80) 
        else:
            y=onh[0]-80
        if onh[1]<200:
            x=0
            x_dist += (onh[1]-200)
        else:
            x=onh[1]-200
        left_corner = (int(y),int(x))
        mock_img[left_corner[0]:left_corner[0]+y_dist,left_corner[1]:left_corner[1]+x_dist] = 0
        enface_detector*=mock_img
    point = np.where(enface_detector==np.max(enface_detector))

    enface = np.mean(cutStack,axis=1)
    dmgBscan = np.mean(cutStack[point[0]-5:point[0]+5,:,:],axis=0)
    adj_point,bin_img, dmg_img = measure_damage(cutStack, enface, point, save_path)
    if adj_point==None:
        analysis_mat, parameter_fits = analyze_damage(cutStack, point)
    else:
        analysis_mat, parameter_fits = analyze_damage(cutStack, adj_point)
    np.save('{}{}analysis_matrix.npy'.format(save_path, os.sep),analysis_mat)
    np.save('{}{}parameters.npy'.format(save_path, os.sep),parameter_fits)

    ax1 = plt.subplot2grid((3,2),(0,0), colspan=2)
    ax2 = plt.subplot2grid((3,2),(2,1))
    ax3 = plt.subplot2grid((3,2),(1,0))
    ax4 = plt.subplot2grid((3,2),(1,1))
    ax5 = plt.subplot2grid((3,2),(2,0))
    ax1.imshow(enface,cmap='gray')
    ax1.scatter(point[1],point[0], c='r', marker='+')
    if adj_point!=None:
        ax1.scatter(adj_point[1],adj_point[0],c='b',marker='x')
    if onh!=-1:
        ax1.scatter(onh[1],onh[0],c='g')
    ax3.imshow(bsub, cmap='gray')
    ax5.imshow(dmgBscan, cmap='gray')
    ax2.imshow(bin_img, cmap='gray')
    ax4.imshow(dmg_img, cmap='gray')
    #f, ax = plt.subplots(3,2)#,sharex=True)
    #ax[0,0].imshow(enface,cmap='gray')
    #ax[0,0].scatter(point[1],point[0], c='r', marker='+')
    #if adj_point!=None:
    #   ax[0,0].scatter(adj_point[1],adj_point[0],c='b',marker='x')
    #if onh!=-1:
    #   ax[0,0].scatter(onh[1],onh[0],c='g')
    #ax[1,0].imshow(bsub, cmap='gray')
    #ax[2,0].imshow(dmgBscan, cmap='gray')
    #ax[0,1].imshow(bin_img, cmap='gray')
    #ax[1,1].imshow(dmg_img, cmap='gray')
    path_info = save_path.split(os.sep)[4:8]
    file_name=''
    for each in path_info:
        file_name = file_name+each+'_'
    plt.subplots_adjust(left=0.05, right=0.95,top=0.95, bottom=0.05, hspace=0.05)
    plt.savefig('{}{}{}bsub_var.tif'.format(save_path,os.sep,file_name))
    plt.close()

def find_bscans(path):

    seek = path + os.sep + '**' + os.sep + 'flat_Bscans.tif'
    Bscans = glob.iglob(seek, recursive=True)

    for scan in Bscans:
        scan = scan.replace('/',os.sep)
        stack = io.imread(scan)
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

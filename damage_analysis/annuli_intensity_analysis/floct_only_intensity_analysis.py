import numpy as np
import skimage.io as io
import os,sys,glob
from skimage.transform import warp
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search_function as sf 
import matplotlib.pyplot as plt
from skimage.draw import circle_perimeter
from scipy import optimize as op
from skimage.transform import resize


def im_open(path):

    """Imports a folder containing a stack of images using scikit image collections"""

    try:
        assert os.path.isdir(path)
        files=glob.glob('{}{}*'.format(path,os.sep))
        raw_stack = io.imread_collection(files)
        stack = io.collection.concatenate_images(raw_stack)
        
        return stack

    except AssertionError:
        sys.exit("A non-directory object was given to the __open__ function")

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

def analyze_cluster(img, point, OCT=True):

    num_rings=60

    analysis_arr = np.empty((num_rings))
    vid = np.empty((num_rings,256,256))

    def line(x): return a()

    if OCT==True:
        y = int(point[0])
        x = int(point[1]/4)
    else:
        y = int(point[0])
        x = int(point[1])

    for r in range(0,num_rings):
        null_img = np.zeros((256,256))
        rr,cc = circle_perimeter(y,x,r, method='andres')
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
        analysis_arr[r]=np.sum(img*null_img)/np.sum(null_img)
        vid[r,:,:]=img*null_img

    a=Parameter(5000)
    param_vals = fit(line,[a],analysis_arr[30:61])
    #do the subtraction here
    adjusted_arr = analysis_arr-param_vals[0][0]

    return adjusted_arr,vid

def root(path):
    root = path.rsplit(os.sep,1)[0]
    return root

@sf.glob_dec()
def load_info(file_name, full_path):
    full_path = full_path.replace('/',os.sep)
    print('\nProcessing:  {}'.format(full_path))
    try:
        dmg_loc = np.load(full_path) - np.array([[5],[32]])
        assert dmg_loc.size==2
    except:
        print('ERROR')
    else:
        print('\n{}'.format(dmg_loc))
        root_path = full_path
        for i in range(4):
            #find flo path)
            root_path=root(root_path)
        flo_path = '{}{}fluorescence'.format(root_path, os.sep)
        print(flo_path)
        flo_img = resize(np.median(im_open(flo_path),axis=0), (256,256), order=3, preserve_range=True)
        analyze_arr, vid =analyze_cluster(flo_img, dmg_loc)
        fig, ax = plt.subplots(2,1)
        ax[0].imshow(flo_img)
        ax[0].scatter(dmg_loc[1]/4,dmg_loc[0],c='y')
        ax[1].plot(analyze_arr)
        root_path = root(root_path)
        print(root_path)
        fig.savefig('{}{}transform_check.tif'.format(root_path,os.sep))
        plt.close()
        np.save('{}{}cluster_intensity_annuli.npy'.format(root_path,os.sep), analyze_arr)
        io.imsave('{}{}ring_vid.tif'.format(root_path, os.sep), np.mean(vid, axis=0).astype('float32'))

def main():
    load_info(file_name='damage_location.npy')
    print('\n--------\nComplete\n--------\n')

if __name__=='__main__':
    main()

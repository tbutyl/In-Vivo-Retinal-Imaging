import numpy as np
import skimage.io as io
from skimage.draw import circle
from tkinter.filedialog import askdirectory
import glob, os, sys
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


def root(path):
    root = path.rsplit(os.sep,1)[0]
    return root

def index_check(rr,cc):
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
    
    return rr,cc

def make_histogram(img, point):
    
    #equivalent circle area to annuli is about 54 pixel diameter
    cluster_ring = 12 #the cluster size is about 200 um diameter, or about 23 pixels wide, 12 for radius
    response_field_ring = 29 #response field is about 500 um, or 58
    y = int(point[0])
    x = int(point[1]/4)

    null_outer = np.zeros((256,256))
    r1,c1 = circle(y,x,response_field_ring)
    r1,c1 = index_check(r1,c1)
    null_outer[r1,c1] = 1
    null_inner = np.zeros((256,256))
    r2,c2 = circle(y,x,cluster_ring)
    r2,c2 = index_check(r2,c2)
    null_inner[r2,c2] = 1
    mask = null_outer-null_inner
    mask = 2*mask - 1
    result_img = img*mask
    results_arr = np.ravel(result_img)
    results_arr = results_arr[np.where(results_arr>=0)]

    return result_img, results_arr

def load_info(full_path):
    #full_path = full_path.replace('/',os.sep)
    print('\nProcessing:  {}'.format(full_path))
    try:
        dmg_loc = np.load(full_path) - np.array([[5],[32]])
        assert dmg_loc.size==2
    except:
        print('Damage Location ERROR')
    else:
        print('\n{}'.format(dmg_loc))
        root_path = full_path
        for i in range(4):
            #takes a new root each iteration.
            #find flo path)
            root_path=root(root_path)
        flo_path = '{}{}fluorescence'.format(root_path, os.sep)
        print(flo_path)
        flo_img = resize(np.median(im_open(flo_path),axis=0), (256,256), order=3, preserve_range=True)
        results_img,intensity_values_in_annuli = make_histogram(flo_img, dmg_loc)
        histo, bins = np.histogram(intensity_values_in_annuli, bins=256, range=(0,2**16))
        save_path = root(root_path)
        np.save('{}{}annuli_intensity_values.npy'.format(save_path,os.sep), intensity_values_in_annuli)
        np.save('{}{}histogram_annuli.npy'.format(save_path, os.sep), np.squeeze(np.dstack((bins[:-1],histo))))
        io.imsave('{}{}masked_annulus_image.tif'.format(save_path,os.sep), results_img.astype('float32'))

def main():
    top_path = askdirectory()
    if top_path=='':
        sys.exit('\n\nExited: No directory was selected.\n\n')
    elif os.path.isfile(top_path):
        sys.exit('\n\nExited: File selected. Please select directory.\n\n')
    paths = glob.iglob('{}{}**{}damage_location.npy'.format(top_path, os.sep,os.sep,os.sep),recursive=True)
    for full_path in paths:
        load_info(full_path)
    print('\n--------\nComplete\n--------\n')

if __name__=='__main__':
    main()

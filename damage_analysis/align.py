from tkinter.filedialog import askdirectory
import numpy as np
import skimage.feature
import skimage.io as io
import skimage.filters
import matplotlib.pyplot as plt
import skimage.transform as tf
import skimage.util as ut
from skimage.feature import (match_descriptors, corner_harris,
                                     corner_peaks, ORB, plot_matches, register_translation)
from skimage.measure import ransac
from skimage.feature import BRIEF
from skimage.feature import CENSURE
import os, glob, sys

#Some work better with STAR filter, some Octagon

censure = CENSURE(mode='STAR')
#censure = CENSURE(mode='Octagon')

extractor = BRIEF()


def reg(flo,floct):

    """
    Registers two images. For registering two slo fluorescence images from pure slo and slo/oct.
    Uses CENSURE to detect the keypoints in the images and BRIEF to detect descriptors. 
    Outliers are then detected using RANSAC.

    Look at scikit-image examples for help.
    
    Inputs:
    -------
    Two images of the same size. At this point, only SLO fluorescence images work!

    Returned:
    ---------
    The warped SLO image.
    The transformation matrix for going slo->oct.
    """

    censure.detect(flo)
    flo_key = censure.keypoints
    censure.detect(floct)
    floct_key = censure.keypoints

    extractor.extract(flo, flo_key)
    flo_key = flo_key[extractor.mask]
    flo_descriptors = extractor.descriptors

    extractor.extract(floct, floct_key)
    floct_key = floct_key[extractor.mask]
    floct_descriptors = extractor.descriptors

    #print('Flo keys len: {}\nFloct Keys len: {}'.format(flo_key, floct_key))
    matches12 = match_descriptors(flo_descriptors,floct_descriptors,cross_check=True, metric='hamming')
    #print('Matches: {}'.format(matches12))
    flo_keys = floct_key[matches12[:, 1]][:, ::-1]
    floct_keys = flo_key[matches12[:, 0]][:, ::-1]

    model_robust, inliers = ransac((flo_keys, floct_keys), tf.SimilarityTransform,min_samples=4, residual_threshold=2)
    #print("flo key len: {}\nfloct key len: {}".format(len(flo_keys[inliers]),len(floct_keys[inliers])))

    tform = tf.estimate_transform("Similarity", flo_keys[inliers], floct_keys[inliers])
    flo_warped = tf.warp(flo, tform, output_shape=(256, 256))
    #floct_warped = tf.warp(floct,tform.inverse,output_shape=(256,256))

    return flo_warped, tform.params

def rgb_add(im1, im2):
    flat = np.ravel
    ebit = skimage.util.img_as_ubyte
    new = []
    im1 = ebit(im1)
    im2 = ebit(im2)
    print('Floct: {}'.format(np.sum(im1)))
    print('Flo: {}'.format(np.sum(im2)))
    for each in zip(flat(im1),flat(flat(im2)), np.zeros(len(flat(im1)))):
        new.append(each)
    arr = np.array(new).reshape((256,256,3))

    return arr

def recurse(top_path):

    flo=None
    floct=None 

    for path, dirnames, filenames in os.walk(top_path):
        #print('Searching: {}'.format(path))
        files = glob.glob(os.path.join(path,'median_*'))

        if len(files)>0:
            pass
        else:
            continue
        #print('Found files: \n{}\n'.format(files))

        check=False
        for im_file in files:
            if 'median_registered_stack_0.tif' in im_file and '8bit' not in im_file:
                check=True
                print("Found Flo: {}".format(im_file))
                flo = io.imread(im_file)
            elif '8bit' not in im_file:
                check=True
                temp = io.imread(im_file)
                if temp.shape == (256,1024):
                    print("Found Floct: {}\n".format(im_file))
                    floct = temp
                    del temp
                else:
                    del temp
                    pass
        if check==True:
                print('\n{}'.format(path))
                for file in files:
                    print('\n\t{}'.format(file))
            
        else:
            pass

        try:
            #make sure images were loaded, otherwise just skip
            assert flo is not None
            assert np.sum(flo)!=0
            assert floct is not None
        except AssertionError:
            if flo==None:
                print('\tDid not find flo at {}\n'.format(path))
            elif floct==None:
                print('\tDid not find floct at {}\n'.format(path))
            else:
                print('???\n')
            pass
        else:
        
            #automatic locale contrast
            flo = skimage.exposure.equalize_adapthist(flo)
            #automatic local contrast and brightening. Brightening necessary for keypoint detection.
            floct = skimage.exposure.rescale_intensity(skimage.exposure.equalize_adapthist(floct), (0,0.3)) #0.6
            #resize using bicubic interpolation
            floct = skimage.transform.resize(floct,(256,256), order=3) #NO PRESERVE RANGE?????
            try:
                warped_slo, mat = reg(flo,floct)
                mixed_img = rgb_add(floct, warped_slo)
                io.imsave(os.path.join(path, 'py_reg_overlay.tif'), mixed_img.astype('uint8'))
                np.save(os.path.join(path,'similarity_transformation_matrix.npy'),mat)
            except:
                print('Transform failure at {}'.format(path))
                pass

def main():
    top_path = askdirectory()
    sys.stdout = open('{}{}out.txt'.format(top_path,os.sep), 'w')
    if top_path == '':
        sys.exit('\nNo folder was selected.\n')
    recurse(top_path)
    print('\n--------\nComplete\n--------')

if __name__ == '__main__':
    main()


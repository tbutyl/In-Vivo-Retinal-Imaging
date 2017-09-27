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

censure = CENSURE(mode='STAR')
extractor = BRIEF()


def reg(flo,floct):

    """
    Registers two images. For registering two slo fluorescence images from pure slo and slo/oct.
    Uses CENSURE to detect the keypoints in the images and BRIEF to detect descriptors. 
    Outliers are then detected using RANSAC.
    
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
    floct_key = flo_key[extractor.mask]
    flo_descriptors = extractor.descriptors

    extractor.extract(floct, floct_key)
    floct_key = floct_key[extractor.mask]
    floct_descriptors = extractor.descriptors

    matches12 = match_descriptors(flo_descriptors,floct_descriptors,cross_check=True, metric='hamming')
    flo_keys = keypoints2[matches12[:, 1]][:, ::-1]
    floct_keys = keypoints1[matches12[:, 0]][:, ::-1]

    model_robust, inliers = ransac((flo_keys, floct_keys), tf.SimilarityTransform,min_samples=4, residual_threshold=2)

    tform = tf.estimate_transform("Similarity", flo[inliers], floct[inliers])
    flo_warped = tf.warp(flo, tform, output_shape=(256, 256))
    #floct_warped = tf.warp(floct,tform.inverse,output_shape=(256,256))

    return flo_warped, tform.params

def rgb_add(im1, im2):
    flat = np.ravel
    ebit = skimage.util.img_as_ubyte
    new = []
    im1 = ebit(im1)
    im2 = ebit(im2)
    for each in zip(flat(im1),flat(flat(im2)), np.zeros(len(flat(im1)))):
        new.append(each)
    arr = np.array(new).reshape((256,256,3))

    return arr

def recurse(top)
    for path, dirnames, filenames in os.walk(top_path):
        files = glob.glob(os.path.join(path,'median_*'))
        for file in files:
            if 'median_registered_stack_0.tif' in file:
                flo = io.imread(file)
        else:
            temp = io.imread(file)
            if temp.shape == (256,1024):
                floct = temp
                del temp
            else:
                del temp
                pass

    #automatic locale contrast
    flo = skimage.exposure.equalize_adapthist(flo)
    #automatic local contrast and brightening. Brightening necessary for keypoint detection.
    floct = skimage.exposure.rescale_intensity(skimage.exposure.equalize_adapthist(floct), (0,0.6))
    warped_slo, mat = reg(flo,floct)
    mixed_img = rgb_add(floct, warped_slo)
    io.imsave(os.path.join(path, 'py_reg_overlay.tif'), mixed_img)
    np.save(os.path.join(path,'similarity_transformation_matrix.npy'),mat)

def main():
    top_path = askdirectory()
    if top_path = '':
        sys.exit('\nNo folder was selected.\n')
    recurse(top_path)
    print('\n--------\nComplete\n--------')

if __name__ == '__main__':
    main()


import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import blob_log
from skimage.morphology import white_tophat, disk
from skimage.exposure import equalize_adapthist
import skimage.io as io
from tkinter.filedialog import askdirectory
matplotlib.style.use('ggplot')
import os, sys, glob, csv


def find_cells(img, tmat):
    filt_img = white_tophat(img, selem=disk(3))
    #contrast_filt_img = equalize_adapthist(filt_img)
    contrast_filt_img = filt_img
    cell_locations = blob_log(contrast_filt_img, min_sigma=1.5, max_sigma=3, num_sigma=10, threshold=0.025, overlap=0.7)
    #switch x and y to transform coordinates
    cells = np.array([cell_locations.T[1], cell_locations.T[0], np.ones(cell_locations.T[1].shape)])
    #dot product
    transformed_cell_loc = np.linalg.inv(tmat)@cells

    #both should be [[x],[y]] an 2xn matrix of cell locations
    return cells[0:2], transformed_cell_loc[0:2]

def summ_image(image, cells):
    fig, ax = plt.subplots(1,1,figsize=(10,10))
    ax.imshow(image, cmap='gray')
    ax.scatter(cells[0], cells[1], s=5, c='r', marker='o', edgecolor='r')
    ax.grid(b=False)
    ax.set_title('Number of cells detected: {}'.format(cells.shape[1]))
    return fig

#could I glob instead of walk?
def recurse(top_path):
    print(top_path)

    for path, dirnames, filenames in os.walk(top_path):

        test_path = os.path.join(path, 'median_registered_stack_0.tif')
        dmg_info_path = os.path.join(path, 'microglia_dmg_info.csv')
        if os.path.isfile(test_path):
            #load image if it exists in the path
            img = io.imread(test_path)
            try:
                #try to load the transformation matrix created by align.py
                #if it doesn't exist, let the user know and keep chuggin'
                mat_path = os.path.join(path, 'similarity_transformation_matrix.npy')
                tmat = np.load(mat_path)
            except:
                print('No transformation matrix found at {}'.format(path))
                continue
            else:
                #find the cell coordinates with a LoG filter and transform them
                cells, transformed_cells = find_cells(img, tmat)
                #make an image to check where cells were detected
                fig = summ_image(img, cells)
                summ_path = os.path.join(path,'cell_locations.tif')
                plt.savefig(summ_path)
                #save the transformed coordinates to do annular density analysis on
                cell_path = os.path.join(path, 'transformed_cell_coordinates.npy')
                np.save(cell_path, transformed_cells)
        elif os.path.isfile(dmg_info_path):
            #will not happen if no damage was detected
            #have to reload the transformation matrix?
            try:
                parent_path = path.rsplit(os.sep,1)[0]
                mat_path = os.path.join(parent_path, 'similarity_transformation_matrix.npy')
                tmat = np.load(mat_path)
            except:
                print('No transformation matrix found for dmg info at {}'.format(parent_path))
                continue
            else:
                #get info from dmg analysis csv in widefield SLO folder
                #I'm making a dict here, which is over kill, but maybe would be more stable to changes in the structure
                #of the csv in the future?
                with open(dmg_info_path, 'r') as f:
                    file_reader = csv.reader(f)
                    dmg_info = np.array([row for row in file_reader])
                dmg_dict = {info[0]:info[1] for info in dmg_info.T}
                x = float(dmg_dict['X'])
                y = float(dmg_dict['Y'])
                dmg_center = np.array([[x],[y],[1]])
                transformed_center = np.linalg.inv(tmat)@dmg_center
                np.save(os.path.join(parent_path, 'transformed_cluster_coordinate.npy'), transformed_center)
        else:
            pass


def main():
    top_path = askdirectory()
    if top_path == '':
        sys.exit('\nNo folder was selected.\n')
    recurse(top_path)
    print('\n--------\nComplete\n--------')

if __name__ == '__main__':
    main()

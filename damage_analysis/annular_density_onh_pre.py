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
import _pickle as pickle

def annular_area(n,r_i=50):
    #convert to millimeters, default arg is 50um
    mm_r_i = r_i/1000
    ring_area = np.pi*mm_r_i**2*(2*n - 1)
    return ring_area
ring_areas = [annular_area(i) for i in range(1,11)]

def ring_counts(cell_locs, dmg_loc):
    #ring_areas is a global var
    intermediate = (cell_locs - dmg_loc)**2
    distances = np.sqrt(intermediate[0]+intermediate[1])
    #pixel dist 500um/8.566 um/px = 58.4
    bin_counts = np.bincount(np.digitize(distances, np.arange(5.837, 64.207, 5.837)))[0:-1]
    ring_densities = [val[0]/val[1] for val in zip(bin_counts, ring_areas)]
   
    return ring_densities

def find_cells(img, tmat):
    filt_img = white_tophat(img, selem=disk(3))
    #contrast_filt_img = equalize_adapthist(filt_img, clip_limit=0.001)
    if np.mean(img)<5000:
        #5000 is an empirically determined threshold to pull up the values
        #CLAHE
        contrast_filt_img = equalize_adapthist(filt_img, clip_limit=0.009)
    else:
        contrast_filt_img = filt_img
    cell_locations = blob_log(contrast_filt_img, min_sigma=1.5, max_sigma=3, num_sigma=10, threshold=0.042, overlap=0.7)
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
    ax.set_xlabel('Intensity Mean: {}'.format(np.mean(image)))
    return fig

def detect_true_damage(onh,dmg,cluster):
    #onh-dmg
    y_od = dmg[1]-onh[0]
    x_od = dmg[0]-onh[1]
    d_od = np.sqrt(y_od**2 + x_od**2)
    #dmg-cluster
    y_dc = dmg[1]-cluster[0]
    x_dc = dmg[0]-cluster[1]
    d_dc = np.sqrt(y_dc**2 + x_dc**2)
    #print('ONH: {}\nDMG: {}\nCLUSTER: {}\n'.format(onh,dmg,cluster))
    #2.5 is a guess; needed because if damage doesn't get detected correctly, it can be farther than false cluster, but still at the onh
    if d_od>d_dc and d_od/d_dc > 2.5:
        #print('ONH - DMG: {}\nCLUSTER - DMG: {}'.format(d_od,d_dc))
        return True
    else:
        return False

def process(top_path):

    imgs = glob.iglob(top_path+os.sep+'**'+os.sep+'median_registered_stack_0.tif', recursive=True)

    for img_path in imgs:
        print(img_path)
        img = io.imread(img_path)
        root = img_path.rsplit(os.sep,1)[0]
        try:
            mat_path = os.path.join(root, 'similarity_transformation_matrix.npy')
            tmat = np.load(mat_path)
        except:
            print('No transformation matrix found at {}'.format(root))
        else:
            ug_info_path = glob.glob(root+os.sep+'**'+os.sep+'microglia_dmg_info.csv')
            onh_info_path = glob.glob(root+os.sep+'**'+os.sep+'onh_info.pkl', recursive=True)
            dmg_info_path = glob.glob(root+os.sep+'**'+os.sep+'dmg_locations.csv', recursive=True)
            try:
                with open(onh_info_path[-1], 'rb') as f:
                    onh_info = pickle.load(f)
            except:
                print('Could not load pickled onh info at {}, skipping'.format(onh_info_path[-1]))
                continue #doesn't continue loop in nested statements
            onh_point = (onh_info.centroid[0],onh_info.centroid[1]/4)
            try:
                #load particle_dmg_info.csv
                with open(dmg_info_path[0], 'r') as df:
                    read_info = csv.reader(df)
                    data = np.array([row for row in read_info])
                    dmg_point = (float(data[1][1]), float(data[1][0]))
            except:
                print('Error loading damage info at {}'.format(dmg_info_path))
                continue #doesn't continue loop in nested statements
            if len(ug_info_path) == 1:
                with open(ug_info_path[0], 'r') as f:
                    file_reader = csv.reader(f)
                    dmg_info = np.array([row for row in file_reader])
                dmg_dict = {info[0]:info[1] for info in dmg_info.T}
                x = float(dmg_dict['X'])
                y = float(dmg_dict['Y'])
                dmg_center = np.array([[x],[y],[1]])
                #use to check if cluster is real - will need onh coordinate transformed too - not currently b/c its detected in OCT
                transformed_center = np.linalg.inv(tmat)@dmg_center
                np.save(os.path.join(root, 'transformed_cluster_coordinate.npy'), transformed_center[0:2])
            else:
                print('No CSV or too many CSVs found for {}'.format(root))
                transformed_center = None
                continue

            if detect_true_damage(onh_point,dmg_point,transformed_center):
                pass
            else:
                print('Damage at {} does not seem to be real.'.format(ug_info_path))
                continue # i think this continue should work.
            cells, transformed_cells = find_cells(img, tmat)
            fig = summ_image(img, cells)
            summ_path = os.path.join(root, 'cell_locations.tif')
            plt.savefig(summ_path)
            plt.close()
            cell_path = os.path.join(root, 'transformed_cell_coordinates.npy')
            np.save(cell_path, transformed_cells)
            #if dmg is real
            #try, except if dmg was found - may change when real detection is implemented
            try:
                ring_densities = ring_counts(transformed_cells, transformed_center[0:2])
            except (UnboundLocalError,TypeError):
                print('Did not find ug damage info CSV, so did not do ring densities')
            else:
                den_path = os.path.join(root, 'annular_densities.npy')
                np.save(den_path, ring_densities)
                fig, ax = plt.subplots(1,1)
                ax.plot(np.arange(50,550,50), ring_densities, marker='o')
                ax.set_title(transformed_center.T[0:2])
                plt.savefig(os.path.join(root, 'ring_dens.tif'))
                plt.close()

def main():
    top_path = askdirectory()
    if top_path == '':
        sys.exit('\nNo folder was selected.\n')
    process(top_path)
    print('\n--------\nComplete\n--------')

if __name__ == '__main__':
    main()

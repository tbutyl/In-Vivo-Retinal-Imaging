import numpy as np
import skimage.io as io
import os,sys,glob
from skimage.transform import warp
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search_function as sf 
import matplotlib.pyplot as plt
from skimage.draw import circle_perimeter
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
	slo = io.imread(full_path)
	root_path = root(full_path)
	spot_seek = '{}{}**{}OCT{}processed_OCT_images{}Amp_FFT2X{}damage_location.npy'.format(root_path, os.sep,os.sep,os.sep,os.sep,os.sep)
	spot_path = glob.glob(spot_seek, recursive=True)
	try:
		dmg_loc = np.load(spot_path[0]) - np.array([[5],[32]])
		print('loaded dmg_loc at {}'.format(spot_path[0]))
		print('OCT location: \n{}'.format(dmg_loc))
	except:
		print('Did not load {}'.format(spot_path)[0])
		pass
	try:
		cluster_coord = np.load('{}{}transformed_cluster_coordinate.npy'.format(root_path,os.sep))[::-1] #reverse array to match the damage spot (y,x)
		print('SLO location: \n{}'.format(cluster_coord))
		tform = np.load('{}{}similarity_transformation_matrix.npy'.format(root_path,os.sep))
	except FileNotFoundError:
		print('->\tMatrix or coordinate not found.')
		pass
	else:
		slo_warp = warp(slo.astype('f8'), tform, output_shape=(256,256), preserve_range=True) 
		del slo
		try:
			analyze_arr, vid = analyze_cluster(slo_warp, dmg_loc)
			print('\n\t\tAnalyzed with OCT dmg')
		except:
			analyze_arr,vid = analyze_cluster(slo_warp,cluster_coord, OCT=False)
			print('\n\t\tAnalyzed with SLO cluster')
		fig,ax=plt.subplots(2,1)
		ax[0].imshow(slo_warp)
		ax[0].scatter(cluster_coord[1],cluster_coord[0],c='r')
		try:
			ax[0].scatter(dmg_loc[1]/4,dmg_loc[0],c='y')
			print('Y loc diff: \n{}\nX loc diff: \n{}'.format(dmg_loc[0]-cluster_coord[1],dmg_loc[1]/4 - cluster_coord[0]))
		except:
			pass
		ax[1].plot(analyze_arr)
		fig.savefig('{}{}transform_check.tif'.format(root_path,os.sep))
		plt.close()
		np.save('{}{}cluster_intensity_annuli.npy'.format(root_path,os.sep), analyze_arr)
		io.imsave('{}{}ring_vid.tif'.format(root_path,os.sep),np.mean(vid,axis=0).astype('float32'))

def main():
	load_info(file_name='median_registered_stack_0.tif')
	print('\n--------\nComplete\n--------\n')

if __name__=='__main__':
	main()
	

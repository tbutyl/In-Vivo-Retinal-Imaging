import numpy as np
import skimage.io as io
import os,sys
from skimage.transform import warp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search_function as sf
import matplotlib.pyplot as plt
from skimage.draw import circle_perimeter
from scipy import optimize as op
import matplotlib.animation as ani
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

def loop(img, point, im):

	for r in range(0,60):
		null_img = np.zeros((256,256))
		rr,cc = circle_perimeter(int(point[0]),int(point[1]),r, method='andres')
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
		#analysis_arr[r]=np.sum(img*null_img)/np.sum(null_img)
		yield im.imshow(img*null_img)

def analyze_cluster(img, point):

	num_rings=60

	analysis_arr = np.empty((num_rings))


	fig = plt.figure()
	im = plt.imshow(img, animated=True)

	swoop = loop(img, point, im)

	test = ani.FuncAnimation(fig, loop(img, point, im), interval=10)
	plt.show()
	#do the subtraction here
	#adjusted_arr = analysis_arr#-param_vals[0][0]

	#return adjusted_arr


def root(path):
	root = path.rsplit(os.sep,1)[0]
	return root

@sf.glob_dec()
def load_info(file_name, full_path):
	full_path = full_path.replace('/',os.sep)
	print('\nProcessing:  {}'.format(full_path))
	slo = io.imread(full_path)
	root_path = root(full_path)
	try:
		cluster_coord = np.load('{}{}transformed_cluster_coordinate.npy'.format(root_path,os.sep))
		tform = np.load('{}{}similarity_transformation_matrix.npy'.format(root_path,os.sep))
	except FileNotFoundError:
		print('->\tMatrix or coordinate not found.')
		pass
	else:
		slo_warp = warp(slo.astype('f8'), tform, output_shape=(256,256), preserve_range=True) 
		del slo
		analyze_arr = analyze_cluster(slo_warp,cluster_coord)
		fig,ax=plt.subplots(2,1)
		ax[0].imshow(slo_warp)
		ax[0].scatter(cluster_coord[0],cluster_coord[1],c='r')
		ax[1].plot(analyze_arr)
		fig.savefig('{}{}transform_check.tif'.format(root_path,os.sep))
		plt.close()
		np.save('{}{}cluster_intensity_annuli.npy'.format(root_path,os.sep), analyze_arr)

def main():
	load_info(file_name='median_registered_stack_0.tif')
	print('\n--------\nComplete\n--------\n')

if __name__=='__main__':
	main()
	

from tkinter.filedialog import askdirectory
import numpy as np
import scipy.ndimage as nd
import glob, os,sys
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

def find_data(top_path):

	def offset_gauss(x): return a()+(b()-a())*np.exp(-(x/(2*sigma()))**2)
	
	seek = '{}{}**{}analysis_matrix.npy'.format(top_path,os.sep,os.sep)
	mat_paths = glob.iglob(seek, recursive=True)

	for path in mat_paths:
		print('\n{}'.format(path))
		profile_fits = np.empty((140,3))
		analysis_mat = np.load(path)
		save_path = path.rsplit(os.sep,1)[0] 
		depth=0
		for row in analysis_mat:
			#set up parameters for fitting
			sigma = Parameter(10)
			a=Parameter(10000)
			b=Parameter(25000)
			param_vals = fit(offset_gauss, [sigma,a,b], row)
			profile_fits[depth,0] = np.abs(param_vals[0][0])
			profile_fits[depth,1] = param_vals[0][1]
			profile_fits[depth,2] = param_vals[0][2]
			depth+=1
		np.save('{}{}parameters.npy'.format(save_path, os.sep), profile_fits)
		del profile_fits
		
def main():
         
    top_path = askdirectory()
    if top_path=='':
            sys.exit('\nExited: No directory was selected')
    elif os.path.isfile(top_path):
            sys.exit('Exited: File selected. Please select top directory')
    find_data(top_path)
    print('\n--------\nComplete\n--------')


if __name__ == '__main__':
        main()

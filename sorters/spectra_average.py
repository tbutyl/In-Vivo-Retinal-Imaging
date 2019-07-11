from pathlib import Path
import numpy as np
import os, sys
from tkinter.filedialog import askdirectory

def avg_spec(pth):
	spectra = list(pth.glob('*Spectra*'))
	num = len(spectra) #finds the number of files in the folder.
	mat = np.empty((num, 1044)) #1044 is number of spectral samples from Pengfei's program. May not work for others!
	for i, path in enumerate(spectra):
		arr = np.loadtxt(str(path), delimiter='\t')
		mat[i] = arr.T[1]
	ind = arr.T[0]
	spec = np.mean(mat, axis=0)

	labeled_spec = np.stack((ind,spec)).T

	save_path = pth / 'avg_spec'
	np.save(str(save_path), labeled_spec)
	np.savetxt(str(pth/'avg_spec.txt'), labeled_spec, delimiter='\t', newline='\n', fmt='%.2f')


def runner(top_path):

	paths = set([f.parent for f in top_path.glob('**/*Spectra*')])
	for pth in paths:
		print('Processing {}'.format(pth))
		avg_spec(pth)

def main():
	top_path = askdirectory()
	if top_path=='':
		sys.exit('\nExited: No directory was selected.')
	elif os.path.isfile(top_path):
		sys.exit('\nExited: File selected. Please select top directory')
	else:
		top_path = Path(top_path)
		runner(top_path)
	print('\n--------\nComplete\n--------')

if __name__ == '__main__':
	main()
	

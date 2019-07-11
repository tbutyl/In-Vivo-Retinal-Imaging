import glob, os, sys
from tkinter.filedialog import askdirectory

def root(path):
	root = path.rsplit(os.sep,1)[0]
	return root

def find_path():

	top_path = askdirectory()
	if top_path=='':
		sys.exit('\n\nExited: No directory was selected.\n\n')
	elif os.path.isfile(top_path):
		sys.exit('\n\nExited: File selected. Please select directory.\n\n')
	return top_path

#decorator and closure
def glob_dec(ig=True,path_str=None):
	def wrap(fcn):
		def wrapper(**kwargs):
			if path_str==None:
				top_path = find_path()
				try:
					seek = '{}{}**{}{}'.format(top_path, os.sep,os.sep,kwargs['file_name'])
				except KeyError:
					sys.exit('\n\nFunction ( {} ) does not have a keyword argument "file_name".\n\n'.format(fcn.__name__))
			else: 
				seek = path_str
			if ig==True:
				g = glob.iglob
			else:
				g = glob.glob
			paths = g(seek, recursive=True)
			for path in paths:
				fcn(full_path=path,**kwargs)
		return wrapper
	return wrap

# EXAMPLE OF USAGE

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#import search_function as sf

#@sf.glob_dec(ig=False,path_str='D:{}24_hour_dmg{}**{}stack_1.tif'.format(os.sep,os.sep,os.sep))
#@sf.glob_dec()
#def test(file_name, full_path):
#	print(full_path)

#def main():
#	test(file_name='stack_1.tif')
#	print('\n--------\nComplete\n--------\n')

#if __name__=='__main__':
#	main()


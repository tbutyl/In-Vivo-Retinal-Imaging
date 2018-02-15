import glob, os, sys
from tkinter.filedialog import askdirectory


def find_path():

	top_path = askdirectory()
	if top_path=='':
		sys.exit('\n\nExited: No directory was selected.\n\n')
	elif os.path.isfile(top_path):
		sys.exit('\n\nExited: File selected. Please select directory.\n\n')
	return top_path

#decorator and closure
def glob_dec(ig=True,path_str=None):

	seek=''
	#if path_str is specified, it must be the complete path WITH file name for globbing
	if path_str==None:
		top_path = find_path()
	else: 
		seek = path_str
	if ig==True:
		ig=glob.iglob
	else:
		ig = glob.glob

	def wrap(fcn):
		def wrapper(**kwargs):
			if seek=='':
				try:
					seek = '{}{}**{}{}'.format(top_path, os.sep,os.sep,kwargs['file_name'])
				except KeyError:
					sys.exit('\n\nYour function does not have a keyword argument "file_name".\n\n')
			paths = ig(seek, recursive=True)
			for path in paths:
				fcn(full_path=path,**kwargs)
		return wrapper
	return wrap


from tkinter.filedialog import askdirectory
import os
import sys
import shutil

def sorting(source):
	#print(source)
	file_list = os.listdir(source)

	for each_file in file_list:
		file_path = os.path.join(source, each_file)
		if os.path.isfile(file_path) is True and "group50" in file_path:
			stack_num = each_file.split("_")[-1]
			stack_num = stack_num.split(".")[0]
			color_file = "registered_STD_timecode_stack_"+stack_num+".tif"
			stack = "stack_"+stack_num+".tif"
			avg_stack = "group50_average_registered_stack_"+stack_num+".tif"

			folder_tree = source.split(":")[-1]
			folder_tree = folder_tree.split(os.sep)[1:]
			folder_tree[0] = "F:\\Python_Moved_Files"+"\\"+folder_tree[0]
			for i in range(1,len(folder_tree)):
				folder_tree[i] = folder_tree[i-1]+"\\"+folder_tree[i]
			for new_folder in folder_tree:
				try:
					os.mkdir(new_folder)
					print("Writing: ", new_folder)
				except OSError:
					continue
			
			shutil.copy2(source+"\\"+color_file, folder_tree[-1])
			print("Copying "+source+"\\"+color_file+" to "+ folder_tree[-1])
			shutil.copy2(source+"\\"+stack, folder_tree[-1])
			print("Copying "+source+"\\"+stack+" to "+ folder_tree[-1])
			shutil.copy2(source+"\\"+avg_stack, folder_tree[-1])
			print("Copying "+source+"\\"+avg_stack+" to "+ folder_tree[-1])
		elif os.path.isdir(file_path) is True:
			if "OCT" in file_path or "fluorescence" in file_path or "reflectance" in file_path:
				continue
			else:
				sorting(file_path)

def main():
	directory = askdirectory()
	if directory  == '':
		sys.exit("\n\nExited: No file path selected\n\n")
	sorting(directory)
	print("\n\n\t\tCompleted\n\n")

try:
	os.mkdir("F:\\Python_Moved_Files")
	main()
except:
	main()

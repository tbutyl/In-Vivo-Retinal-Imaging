import sys, os

def newFiles(parent='/Users/emiller/pyScripts/test/'):

	animals = ['a','b','c','d']
	eyes = ['reye','leye']
	spots = ['dorsal','ventral','anterior','posterior']

	parent=parent+'/Imaging Session'
	os.makedirs(parent)

	for animal in animals:
		print('\t'+animal)
		current_folder_animal = parent+'/'+animal
		os.makedirs(current_folder_animal)
		for eye in eyes:
			print('\t\t'+eye)
			current_folder_eye = current_folder_animal+'/'+eye
			os.makedirs(current_folder_eye)
			for spot in spots:
				print('\t\t\t'+spot)
				current_folder_spot = current_folder_eye+'/'+spot
				os.makedirs(current_folder_spot)
				for i in range(10):
					fileName_apd1 = "APD1_"+str(i+1)
					fileName_apd2 = "APD2_"+str(i+1)
					file = open(current_folder_spot+'/'+fileName_apd1,"w")
					file.close()
					file = open(current_folder_spot+'/'+fileName_apd2,"w")
					file.close()


def main():
    # source = input("Source Path: ")
    newFiles()
    print("Completed")
main()

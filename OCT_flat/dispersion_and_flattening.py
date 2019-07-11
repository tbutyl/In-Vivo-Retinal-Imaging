#### WORKS FOR 3D DISPERSION COMPENSATION
#SAVES CORRESPONDING FILES INTO FOLDER 

#### RUN IN QTPYTHON   %gui tk ---> %run 


###################
#### 7/9/2018 - editing to combine dispersion compensation and flattening programs together

### 7/10/18 - edit to run on batch of files


import matplotlib.pyplot as plt #imports the main graphing library
import matplotlib.image as mpimg #imports another part of the graphing library
import numpy as np #imports Python's numerical computing library
import scipy as sp #imports Python's scientific computing library
from scipy import ndimage, signal #import some specific sub-librarys from Scipy
from skimage.filters import rank
import skimage.io as io #These two lines import sub-libraries from Scikit Image, a great library for image processing and analysis
import sys, os, glob, csv, shutil #Libraries for interacting with the computer
import scipy.fftpack as spfft #A sublibrary from Scipy that does FFTs
import scipy.ndimage as sim #A sublibrary from Scipy that is also for image manipulation
import scipy.signal #A sublibrary from Scipy that is for signal processing and analysis
import skimage.exposure as expo #library to.... rescale image intensities
from tkinter.filedialog import askdirectory, askopenfilename
from skimage import io, transform
import skimage.morphology as morph
from skimage.filters import rank, threshold_minimum
from skimage.filters import gaussian, threshold_isodata
from skimage.measure import label, regionprops
from skimage.morphology import convex_hull_image, remove_small_objects, binary_closing
from skimage.feature import canny
from scipy.interpolate import interp1d
import argparse
import _pickle as pickle



#this is a function that allows you to load files in order
def sort_key(path):

    """When loading files they are named 0-255.tif and are sorted as strings, not as numbers.
       This function returns the number in the file name and is used as the key for Python's
       built-in "sorted" function."""
    
    #Take the file path as a string and remove everything except for the characters after that last file separator
    file_end = path.rsplit(os.sep,1)[1]
    #remove the file extension, which should always be tif
    file_number = file_end.rstrip('.tif')
    #return the number, but make sure to convert it to an interger so the sorting actually works!
    return int(file_number)


#This is a function to load an OCT data set
def im_open(path):

    """Imports a folder containing a stak of images using Scikit Image Collections"""

    try:
        #make sure the path exists and if it doesn't, throw an exception
        assert os.path.isdir(path)
        #get the list of files in the directory supplied to the function
        files = sorted(glob.glob('{}{}*'.format(path,os.sep)), key=sort_key)
        #load the collection into memory
        raw_stack = io.imread_collection(files)
        #Turn the collection of images into a numpy array. Coordinates are: (z,y,x)
        #Also, convert to signed int, 32 bit representation
        stack = io.collection.concatenate_images(raw_stack).astype('int32')
        print(stack.shape)

        return stack
    
    except AssertionError:
        sys.exit("A non-directory object was given to the __im_open__ function")
        
#load a raw oct stack, path will need to be changed



def searchStart(pathImported):
    searchPath = pathImported+os.sep+'**'+os.sep+'OCT'
    ## ^^^ currently only runs with Pengfei's repeated volumetric imaging
    amp_folders = glob.iglob(searchPath, recursive=True) # thisis going to be a list nad you have to iterate through the list and operate on ecah paht - for item in whatever variable is - load image from file paht
    print('hilooo')
    print(amp_folders)
    for folder in amp_folders:
        print(folder)
        print('in folder')
        if os.path.isdir(folder+os.sep+'processed_OCT_images'):
            print('processed_OCT_images folder found - skipping folder path\n')
            continue
        else:
            print('\n*****\nProcessing:\t{}\n*****\n'.format(folder))
            stack = im_open(folder)
            image_to_flat = dispComp(stack)
            flatProg(image_to_flat, folder)






def dispComp(stack):
    """START OF DISPERSION COMPENSATION PROGRAM"""
    
    



    #print(pathImported)

    #select a single Ascan for processing
    Bscan_spectrum = stack[int(stack.shape[0]/2)]

    #Subtract the offset
    Bscan_offset = Bscan_spectrum-(2**15)
    #Average the spectrums in the Bscan spectrum to get just the light source spectrum
    DC = (sim.uniform_filter1d(Bscan_offset.T,size=Bscan_offset.shape[1], axis=1)).T
    #remove the light-source spectrum
    Bscan_backsub = Bscan_offset-DC
    #Take the Ascan to look at the interference spectrum
    Ascan_backsub = Bscan_backsub[int(Bscan_backsub.shape[0]/2)]


    #We have the interference spcetrum, but the light has been sorted by wavelength and in order to do a
    #FFT we need it in frequency space

    #first we set up some knowns about our camera
    #the largest wavelength
    lambdaMin = 954
    #the change in wavelength between each pixel
    dLambda = -0.0805
    #Camera specific correction factor
    secondOrderCorrection = -2.579*(10**-6)
    #Corrected wavelength array
    lambdaRaw = np.array([lambdaMin+(i*dLambda)+((i**2)*secondOrderCorrection) for i in range(Bscan_backsub.shape[1])])
    #convert each wavelength into a frequency
    kRaw = 1/lambdaRaw
    #figure out a linear spacing for the frequencies
    dK = (kRaw[-1] - kRaw[0])/(Bscan_backsub.shape[1]-1)#2047 
    #sets up linearly spaced frequencies
    #Take the first frequency
    kLinearTemporary = [kRaw[0]]

    #Append the nexst frequency to the array
    for j in range(len(kRaw)-1):
        kLinearTemporary.append(kLinearTemporary[0]+(j*dK))
    #We know have a linearly spaced array of the frequencies of light, now we need to interpolate the intensities from
    #wavelength -> frequency to do the FFT

    #A hann window is used to mitigate some of the effects of the FFT. "Understanding Digital Signal Processing" by
    #Lyons is a good reference.
    window = scipy.signal.hann(2048)
    AScan = Bscan_backsub[512]*window
    #interpolate for raw frequencies, then find the values at the linearly spaced frequencies
    interpAScan = scipy.interpolate.interp1d(kRaw, AScan)(kLinearTemporary) 

    #Do a fft to see if we got an A-scan
    fft_sig = np.abs(np.real(np.fft.rfft(interpAScan)))

    #Now we process an entire Bscan
    #window the entire Bscan
    windowed_img = Bscan_backsub*window
    #initialize a list
    bscan = []

    #interpolate each A-scan of the Bscan and do an FFT on it, then add it to an array.
    for row in windowed_img:
        interpAScan_bscan = scipy.interpolate.interp1d(kRaw, row)(kLinearTemporary) 
        bscan.append(np.abs(np.real(np.fft.rfft(interpAScan_bscan))))

    #Covert the list into a numpy array for better graphing/manipulation
    BScan = (np.array(bscan))


    #The goal is to change the phase of different colors of light to do the dispersion compensation.
    #What follows is setting up for equation 7 in Wojtowski et al. 2004.
    #First, we set up an array where each number is the distance from the center frequency of the light source.
    #This is for the 2nd and 3rd order terms in the Taylor Series Expansion of the propagation constant: (f-f_center)
    distanceArray = [-2048/2 + i for i in range(2048)]
    #We then square and cube the distances for the 2nd and 3rd terms, respectively.
    a = np.array(distanceArray)**2
    a3 = a*distanceArray

    #setting boundaries for dispVal values to begin iterative process
    lowBound = -1000
    highBound = 1000
    #variables x1 and holdx compare the pixel max intensity
    x1 = 101
    holdx = 100
    #counter to begin the while loop
    counter = 0
    #inverse sum of average pixel intensity
    holdcheckBool = -1
    checkBool = 1

    while (1.03 < np.abs(checkBool/holdcheckBool) and np.abs(checkBool/holdcheckBool) > 1) or counter<2:

        iterations = np.linspace(lowBound, highBound, num=20)
        buildArray = []
        counter += 1

        for i, dispValIteration in enumerate(iterations):

            #dispVal is the diserpsion Value for the coefficients of the 2nd and 3rd terms. These are what need to be optimized!
            dispVal = dispValIteration * 10**-8
            dispValThird = 0 * 10**-9
            dispPhase = dispVal*a
            dispPhaseThird = dispValThird*a3

            #Now we actually do the diserpsion compensation while going from frequency -> spatial domains
            bscan = []

            for row in windowed_img:
                #Change to frequency from wavelength.
                interpAScan_bscan = scipy.interpolate.interp1d(kRaw, row)(kLinearTemporary)
                #Here we obtain the Analytic Signal. This allows us to use the amplitude and phase information.
                complexScan = scipy.signal.hilbert(interpAScan_bscan)
                #Now we take the phase of the frequencies and add the dispersion compensation terms.
                ph = np.angle(complexScan)+dispPhase+dispPhaseThird
                #Using euler's equation, recombine the amplitude and dispersion compensated phase terms
                ascan4 = np.abs(complexScan)*np.exp(1j*ph)
                #Convert to spatial domain
                fft4 = np.abs((np.fft.fft(np.pad(ascan4,1024,'constant'))))
                bscan.append(fft4)

            BScan2 = np.array(bscan)
            checkBool = np.sum(BScan2.T[100:800, :2048] > np.mean(BScan2.T[100:800, :2048]))
            checkBool = 1/checkBool
            buildArray.append(checkBool)
            
        array = np.array(buildArray)
        dispValIdeal = iterations[np.where(array==np.max(array))[0]]

        #logic checks to prevent the dispVal from changing towards values where
        #the intensity is decreasing
        #forces program to choose only values larger
        if (checkBool<holdcheckBool):
                
            dispValIdeal = x1
            break

        else:

            holdcheckBool=checkBool
            pass

        holdx = x1

        if dispValIdeal.shape[0] > 1:

            if (1.03 < np.abs(checkBool/holdcheckBool) and np.abs(checkBool/holdcheckBool) > 1):
            
                dispValIdeal = dispValIdeal[0]
                break

            else:

                x1 = dispValIdeal[0]
                dispValIdeal = dispValIdeal[0]
        
        else:
        
            x1 = dispValIdeal

        lowBound = x1 + lowBound/10
        highBound = x1 + highBound/10


    #Same as dispVal logic, but now applied to dispValThird

    #The goal is to change the phase of different colors of light to do the dispersion compensation.
    #What follows is setting up for equation 7 in Wojtowski et al. 2004.
    #First, we set up an array where each number is the distance from the center frequency of the light source.
    #This is for the 2nd and 3rd order terms in the Taylor Series Expansion of the propagation constant: (f-f_center)
    distanceArray = [-2048/2 + i for i in range(2048)]
    #We then square and cube the distances for the 2nd and 3rd terms, respectively.
    a = np.array(distanceArray)**2
    a3 = a*distanceArray

    lowBoundt = -10
    highBoundt = 30
    xt = 101
    holdxt = 100
    counter = 0
    holdcheckBoolThird = -1
    checkBoolThird = 1

    while (1.03 < np.abs(checkBoolThird/holdcheckBoolThird) and np.abs(checkBoolThird/holdcheckBoolThird) > 1) or counter < 2:

        thirdIterations = np.linspace(lowBoundt, highBoundt, num=10)
        makeArray = []
        counter += 1
        
        for i, dispValThirdIteration in enumerate(thirdIterations):
            
            #dispVal is the diserpsion Value for the coefficients of the 2nd and 3rd terms. These are what need to be optimized!
            dispVal = dispValIdeal * 10**-8
            dispValThird = dispValThirdIteration * 10**-9
            dispPhase = dispVal*a
            dispPhaseThird = dispValThird*a3

            #Now we actually do the diserpsion compensation while going from frequency -> spatial domains
            bscan = []

            for row in windowed_img:
                #Change to frequency from wavelength.
                interpAScan_bscan = scipy.interpolate.interp1d(kRaw, row)(kLinearTemporary)
                #Here we obtain the Analytic Signal. This allows us to use the amplitude and phase information.
                complexScan = scipy.signal.hilbert(interpAScan_bscan)
                #Now we take the phase of the frequencies and add the dispersion compensation terms.
                ph = np.angle(complexScan)+dispPhase+dispPhaseThird
                #Using euler's equation, recombine the amplitude and dispersion compensated phase terms
                ascan4 = np.abs(complexScan)*np.exp(1j*ph)
                #Convert to spatial domain
                fft4 = np.abs((np.fft.fft(np.pad(ascan4,1024,'constant'))))
                bscan.append(fft4)

            BScan2 = np.array(bscan)
            checkBoolThird = np.sum(BScan2.T[100:800, :2048] > np.mean(BScan2.T[100:800, :2048]))
            checkBoolThird = 1/checkBoolThird
            makeArray.append(checkBoolThird)
            
        array2 = np.array(makeArray)

        dispValThirdIdeal = thirdIterations[np.where(array2==np.max(array2))[0]]

        if (checkBoolThird<holdcheckBoolThird):

            dispValThirdIdeal = xt
            break
        
        else:
        
            holdcheckBoolThird=checkBoolThird
            pass

        holdxt = xt

        if dispValThirdIdeal.shape[0] > 1:
        
            if (1.03 < np.abs(checkBool/holdcheckBool) and np.abs(checkBool/holdcheckBool) > 1):
        
                dispValThirdIdeal = dispValThirdIdeal[0]
                break

            else:

                xt = dispValThirdIdeal[0]
                dispValThirdIdeal = dispValThirdIdeal[0]
        
        else:
        
            xt = dispValThirdIdeal

        lowBoundt = xt + lowBoundt/5
        highBoundt = xt + highBoundt/5



    #Final Dispersion 
    #Applying the dispersion to all files and creating a single .tif file with every frame
    #stackSize = range(len(os.listdir(pathImported))-1)
    stackSize = range(stack.shape[0])
    print('stackszie=' + str(stackSize[-1]))
    
    outputArray = np.empty((stackSize[-1]+1,700,1083))
    print(outputArray.shape)

    for frameThing in stackSize:
        print(frameThing)    
        Bscan_spectrumInput = stack[frameThing]

        #Subtract the offset
        Bscan_offset = Bscan_spectrumInput-(2**15)
        #Average the spectrums in the Bscan spectrum to get just the light source spectrum
        DC = (sim.uniform_filter1d(Bscan_offset.T,size=Bscan_offset.shape[1], axis=1)).T
        #remove the light-source spectrum
        Bscan_backsub = Bscan_offset-DC
        #Take the Ascan to look at the interference spectrum
        Ascan_backsub = Bscan_backsub[int(Bscan_backsub.shape[0]/2)]


        #We have the interference spcetrum, but the light has been sorted by wavelength and in order to do a
        #FFT we need it in frequency space

        #first we set up some knowns about our camera
        #the largest wavelength
        lambdaMin = 954
        #the change in wavelength between each pixel
        dLambda = -0.0805
        #Camera specific correction factor
        secondOrderCorrection = -2.579*(10**-6)
        #Corrected wavelength array
        lambdaRaw = np.array([lambdaMin+(i*dLambda)+((i**2)*secondOrderCorrection) for i in range(Bscan_backsub.shape[1])])
        #convert each wavelength into a frequency
        kRawSave = 1/lambdaRaw
        #figure out a linear spacing for the frequencies
        dK = (kRawSave[-1] - kRawSave[0])/(Bscan_backsub.shape[1]-1)#2047 
        #sets up linearly spaced frequencies
        #Take the first frequency
        kLinearTemporarySave = [kRawSave[0]]
        #Append the nexst frequency to the array
        for j in range(len(kRaw)-1):
            kLinearTemporarySave.append(kLinearTemporarySave[0]+(j*dK))
        #We know have a linearly spaced array of the frequencies of light, now we need to interpolate the intensities from
        #wavelength -> frequency to do the FFT

        #A hann window is used to mitigate some of the effects of the FFT. "Understanding Digital Signal Processing" by
        #Lyons is a good reference.
        window = scipy.signal.hann(2048)
        AScan = Bscan_backsub[512]*window
        #interpolate for raw frequencies, then find the values at the linearly spaced frequencies
        interpAScan = scipy.interpolate.interp1d(kRawSave, AScan)(kLinearTemporarySave) 

        #Do a fft to see if we got an A-scan
        fft_sig = np.abs(np.real(np.fft.rfft(interpAScan)))

        #Now we process an entire Bscan
        #window the entire Bscan
        windowed_img = Bscan_backsub*window
        #initialize a list
        bscan = []
        #interpolate each A-scan of the Bscan and do an FFT on it, then add it to an array.
        for row in windowed_img:

            interpAScan_bscan = scipy.interpolate.interp1d(kRawSave, row)(kLinearTemporarySave) 
            bscan.append(np.abs(np.real(np.fft.rfft(interpAScan_bscan))))

        #Covert the list into a numpy array for better graphing/manipulation
        BScan = (np.array(bscan))

        #dispVal is the diserpsion Value for the coefficients of the 2nd and 3rd terms. These are what need to be optimized!
        dispVal = dispValIdeal * 10**-8
        dispValThird = dispValThirdIdeal * 10**-9
        dispPhase = dispVal*a
        dispPhaseThird = dispValThird*a3

        #Now we actually do the diserpsion compensation while going from frequency -> spatial domains
        bscan = []
        for i, row in enumerate(windowed_img):

            #Change to frequency from wavelength.
            interpAScan_bscan = scipy.interpolate.interp1d(kRawSave, row)(kLinearTemporarySave)
            #Here we obtain the Analytic Signal. This allows us to use the amplitude and phase information.
            complexScan = scipy.signal.hilbert(interpAScan_bscan)
            #Now we take the phase of the frequencies and add the dispersion compensation terms.
            ph = np.angle(complexScan)+dispPhase+dispPhaseThird
            #Using euler's equation, recombine the amplitude and dispersion compensated phase terms
            ascan4 = np.abs(complexScan)*np.exp(1j*ph)
            #Convert to spatial domain
            fft4 = np.abs((np.fft.fft(np.pad(ascan4,1024,'constant'))))
            bscan.append(fft4)

        BScan2 = np.array(bscan)
        outputArray[frameThing] = BScan2.T[100:800, :2048]     


    img = expo.rescale_intensity(outputArray, in_range=(100,10000), out_range='uint16')
    
    image_to_flat = img[:,:,0:1024]
#    fileName = input("Type desired file name: ")
#    saveName = (fileName + ".tif")

    #io.imsave((saveName), image_to_flat.astype('uint16'))
    #image_to_flat = img
    print(image_to_flat.shape)

    return image_to_flat

    ####################
    #######################
    ###################


def flatProg(image_to_flat, pathImported):
    """FLATTENING PROGRAM"""

    parser = argparse.ArgumentParser('Select Extent of Program to run')
    onh_only = parser.add_argument('-onh', action='store_true', help='only find onh')
    overwrite = parser.add_argument('-overwrite', action='store_true', help='overwrite flattened octs')
    multi = parser.add_argument('-multi', action='store_true', help='select more than one directory')
    args = parser.parse_args() ### WHAT'S ARGS??????
     
    if args.multi!=True:
        #top_path = askdirectory()
        #print('asking file name')
        #file_name = askopenfilename()
        #if file_name=='':
        #        sys.exit('\nExited: No file was selected')
        #elif os.path.isfile(top_path):
                #sys.exit('Exited: File selected. Please select top directory')
                # two lines above commented out because we are looking for a file and not a directory anymore
        #else:
        print('args.multi not true')
        find_amp(image_to_flat, pathImported, args)

    else:
        path_list = []
        flag = 1
        counter = 0 ######
        while flag:
            #path = askdirectory()
            counter+=1
            print('while loop' + str(counter))
            nevve = pathImported
            #path_list.append(path)
            #path_list.append(path)
            path_list.append(nevve)
            #if path=='':
            if nevve == '':
                flag = 0
            #flag=0#####?maybe dont need this idk i think im doing something wrong
        if len(path_list) > 0:
            for nevve in path_list:
                print('BLERB')
                find_amp(image_to_flat, nevve, args)
        else:
            sys.exit('\nExited: No directory was selected')


    print('\n--------\nComplete\n--------')


    # img


def sort_key_flat(path):
    """
    When loading files from the dispersion compensation program, they are named 0-255.tif. When globing to get the list of files to load them, they are ordered not numerically, but as strings.
    This function returns the number in that file name and is used as the key function in the built-in "sorted" function.
    """
    
    file_end = path.rsplit(os.sep,1)[1]
    file_number = file_end.rstrip('.tif')
    return int(file_number)


def max_area(props):
    """
    Finds the largest "particle" detected, excluding any that are on the sides of the image.
    """
    i_max=-1
    max_area = -1
    for i, prop in enumerate(props):
        bbx = np.array(prop.bbox)
        #gets rid of any region touching the sides - fufils "exlude on side" function of imagej Analyze particles
        #2/2/2018 - now only excludes corner points so that onhs that touch the sides aren't excluded - this gets rid of non-retina
        if (bbx[0]==0 or bbx[2]==256) and (bbx[1]==0 or bbx[3]==1024):
            continue
        #if np.any(bbx==0) or np.any(bbx==256):
        #    continue
        else:
            #find max area
            if prop.area > max_area:
                max_area = prop.area
                i_max = i
    return i_max

def detect_onh(stack):
    """
    Detects the location of the ONH. Finds the frame with the highest intensity and averages all frames below that to 100 frames above it. This will include all choroid and
    RPE, so the ONH should appear as a dark hole in the retina. The gaussian blurring is to attempt to not detect vessels.
    """
    profile = np.mean(stack, axis=(0,2))
    max_frame_ind = np.where(profile==np.max(profile))[0][0]
    enface = np.mean(stack[:,0:max_frame_ind+100,:], axis=1)
    ref = gaussian(enface, sigma=2)
    thresh_val = threshold_isodata(ref)
    #I don't think remove small objects should ever be a problem, the default is <64 px
    #This is to prevent a small object from tricking the program into thinking it's the onh when the onh is touching the sides.
    classified_img = morph.remove_small_objects(ref<thresh_val, min_size=200)
    #io.imsave("check_raw.tif", (classified_img.astype('uint8'))*256)
    labels = label(classified_img, connectivity=2)
    props = regionprops(labels)
    onh_ind = max_area(props)
    if onh_ind == -1:
        binary_enface = 1-morph.convex_hull_image(morph.remove_small_objects(morph.binary_closing(classified_img!=True)))
        #io.imsave('binary.tif',(binary_enface.astype('uint8'))*256)
        classified_img = sim.filters.maximum_filter(sim.filters.minimum_filter(binary_enface - classified_img, size=(4,6)),size=(4,6))
        #io.imsave("check.tif", (classified_img.astype('uint8'))*256)
        labels = label(classified_img, connectivity=2)
        props = regionprops(labels)
        onh_ind = max_area(props)

    try:
        assert onh_ind!=-1
    except AssertionError:
        return -1
    else:
        return props[onh_ind]

def im_open_flat(path):

    """Imports a folder containing a stack of images using scikit image collections"""

    try:
        assert os.path.isdir(path)
        #get file list in directory -  glob includes full path
        files = sorted(glob.glob('{}{}*'.format(path,os.sep)), key=sort_key_flat) 
        #load the collection
        raw_stack = io.imread_collection(files)
        #turn the collection into a np array and remove extraneous OCT portion from 1025:1083 on x axis. (z,y,x)
        #if .bmp files are open (from pv-oct), the slicing will not affect them, the x-axis is only 540 pixels.
        stack = io.collection.concatenate_images(raw_stack)[:,:,0:1024]
        
        return stack

    except AssertionError:
        sys.exit("A non-directory object was given to the __open__ function")


def extract_tiff(tiff_path):
    
    """Extracts each image saved in the tiff"""
    # saved using append -->
    # bscan.append(fft4)
    # Bscan2 = np.array(bscan)
    # outputArray[frameThing] = Bscan2.T[100:800, :2048]
    # where frameThing is how many images in the stack were imported
    ### somehow undo the np.array???? or just pull each tiff page individually

    tiff_import = io.imread(tiff_path)[:,:,0:1024]
    #print(tiff_import)

    return tiff_import








def save(img, path, file_name):
        
        """Saves the numpy array image as a MultiPage tiff file"""

        name = os.path.join(path,file_name).replace('/', os.sep)

        io.imsave(name,img)

        

def adjustFrame(frame, shifts):
    """
    First, corrects the list of shifts in case there are any negative shifts. Then finds the padding that must be on
    the top of the image. Finally, puts the appropriate padding onto each column (as a row for easy indexing), then
    puts them into an initialized array and transposes for correct orientation.
    
    Parameters:
    -----------
    frame: Takes a single OCT frame to put the columns in the correct place.
    
    shifts: The list of shifts for each column.
    
    Outputs:
    -----------
    newFrame: The finished, flattened frame. 
    
    """

    print(shifts)
    if min(shifts)<0:
        botShifts = [int(colShift)-int(min(shifts)) for colShift in shifts]
    else:
        botShifts = [int(colShift) for colShift in shifts]
    topShifts = [np.max(botShifts)-shift for shift in botShifts]
    newFrame=np.empty([frame.shape[1],frame.shape[0]+np.max(botShifts)])
    for i, col in enumerate(frame.T):
        newCol = np.concatenate((np.zeros(topShifts[i]),col,np.zeros(botShifts[i])))
        newFrame[i]=newCol
    newFrame=newFrame.T
    
    return newFrame

def shiftDetector(frame, onh_info=None):
    """
    Normalizes the frame to the max pixel value and gets the shifts using cross correlation.
    
    Parameters:
    -----------
    frame: takes a single OCT frame and finds the shift of all image columns from the center column of the image using
           cross-correlation. Must also subtract half the image height, but I'm not sure why yet. 
           
    Outputs:
    -----------
    shifts: a list of the shifts for each column
    
    """
    norm = frame/np.max(frame)#(2**16)
    anchorCol = norm[:,int((frame.shape[1])/2)]
    shifts = [np.argmax(signal.correlate(norm[:,i],anchorCol,mode='same'))-int((frame.shape[0])/2) for i in range(frame.shape[1])]
    
    return shifts

def shiftDetectorONH(frame, onh_info, x_onh_bounds):
    """
    Normalizes the frame to the max pixel value and gets the shifts using cross correlation.
    Moves anchor col if inside ONH and uses a qudratic fit to estimate the curveature at the onh.
    
    Parameters:
    -----------
    frame: takes a single OCT frame and finds the shift of all image columns from the center column of the image using
           cross-correlation. Must also subtract half the image height, but I'm not sure why yet. 
           
    Outputs:
    -----------
    shifts: a list of the shifts for each column
    
    """

    x_min = x_onh_bounds[0]-30
    x_max = x_onh_bounds[1]+30
    frame_len = frame.shape[1]
    mid_x = int(frame_len/2)

    norm = frame/np.max(frame)#(2**16)
    #if the frame midpoint is inside the bbox x bounds
    #this section is to avoid using any part of the onh as the a-scan to reference when doing the cross-correlation
    if mid_x>=x_min and mid_x<=x_max:
        d_min = mid_x-x_min
        d_max = x_max-mid_x
        #if mid_x is closer to x_min but not close to the edge of the image -- at least 75 px
        if d_min<d_max and x_min>75:
            acol = int((frame_len/2)-(d_min+1))
        elif x_max<frame_len-75:
            acol = int((frame_len/2)+(d_max+1))
        else:
            acol = int((frame_len/2)-(d_min+1))
        anchorCol = norm[:,acol]
    else:
        anchorCol = norm[:,mid_x]
    shifts = [np.argmax(signal.correlate(norm[:,i],anchorCol,mode='same'))-int((frame.shape[0])/2) for i in range(frame_len)]

    #if onh detection is bad, bbox might be huge. The onh area should be less that 10% of the image (256*1024 pixels)
    if onh_info.area/(2**18) > 0.10:
        return shifts
    #old, changed 1-29-2018 because this is really about location, not size
    #if x_min<100 or x_max>902:
        #return shifts

    #This ensures that clean_shifts and clean_x are the same length and comes into play when the ONH is basically touching the
    #side of the image.
    #if the onh is too far to the right side of the frame, only use the left side info
    #fit a quadratic to get LOCAL curvature
    if x_max>=frame_len-100:
        #this uses the entire bscans to get the curvature, otherwise it will fit very poorly
        clean_x = np.arange(0,x_min,1)
        curve_fit_params = np.polyfit(clean_x, shifts[0:x_min],2)
        curve_fit = lambda x: curve_fit_params[0]*x**2 + curve_fit_params[1]*x + curve_fit_params[2]
        corrected_shifts = np.round(curve_fit(np.arange(x_min,x_max+1,1)))
        clean_shifts = shifts
        clean_shifts[x_min:x_max+1]=corrected_shifts
    #if the onh is too far to the left side, only use right side info
    elif x_min<100:
        clean_x = np.arange(x_max+1,frame_len,1)
        curve_fit_params = np.polyfit(clean_x, shifts[x_max+1:frame_len],2)
        curve_fit = lambda x: curve_fit_params[0]*x**2 + curve_fit_params[1]*x + curve_fit_params[2]
        corrected_shifts = np.round(curve_fit(np.arange(x_min,x_max+1,1)))
        clean_shifts = shifts
        clean_shifts[x_min:x_max+1]=corrected_shifts
    #Everything is normal, everyone is happy.
    else:
        #need to cut out onh, I don't think there is a way to index this to put it
        #directly in polyfit
        clean_shifts = np.array(shifts[0:x_min] + shifts[x_max+1:frame_len])
        clean_x = np.concatenate((np.arange(x_min-100,x_min,1),np.arange(x_max+1,x_max+101,1)))
        curve_fit_params = np.polyfit(clean_x, clean_shifts[x_min-100:x_min+100],3)
        curve_fit = lambda x: curve_fit_params[0]*x**3 + curve_fit_params[1]*x**2 + curve_fit_params[2]*x + curve_fit_params[3]
        corrected_shifts = np.round(curve_fit(np.arange(x_min,x_max+1,1)))
        clean_shifts = np.insert(clean_shifts, x_min+1, corrected_shifts)

    return list(clean_shifts)

def flattenFrames(stack, onh_info):
    """
    Loops through the frames of the image stack. First, the frame undergoes a median filter, which is passed to 
    shiftDetector to get the list of shifts. The shifts are then used to move the columns into the correct position
    for that frame with adjustFrame. The frames (with unequal heights) are then put into a list. The height of the
    largest frame is detcted with maxHeight.
    
    Parameters:
    -----------
    stack: The stack of tifs in ndarray form.
    
    Ouputs:
    -----------
    frameList: The list of frames that have been flattened, but do not have matching heights.
    
    maxHeight: The largest height of the frames in frameList.
    
    """
    
    maxHeight=0
    frameList=[]

    if onh_info!=-1:
        y_min = onh_info.bbox[0]
        #need to subtract one because index?
        y_max = onh_info.bbox[2]
        
        #hull starts at (0,0), add the y and x min to translate to correct indices.
        hull_onh = np.array(np.where(onh_info.convex_image)) + np.array([[y_min], [onh_info.bbox[1]]])
    elif onh_info==-1:
        #should prevent shiftDetectorONH from running since i will always be greater than -1
        #hull_onh has been left undefined.
        y_min, y_max = -1,-1
    
    print('Finding and correcting horizontal shifts start')
    for i, frame in enumerate(stack):
        #medFrame = ndimage.filters.median_filter(frame,size=(1,60)) #Takes 3.5 minutes
        medFrame = ndimage.filters.uniform_filter1d(frame, 60) #Takes 1.0 minutes and has same output as med filter
        if i>=y_min and i<y_max:
            #get the index of x pixels that are part of the onh for each frame
            #these are indices of indices
            x_onh_ind = np.array(np.where(hull_onh[0]==i)) 
            x_onh = hull_onh.T[x_onh_ind][0].T[1]
            #this should be sorted so that its the x_min and max for each frame
            x_onh_bounds = (x_onh[0], x_onh[-1])
            shifts = shiftDetectorONH(medFrame, onh_info, x_onh_bounds)
        else:
            shifts = shiftDetector(medFrame)
        newFrame = adjustFrame(frame, shifts)
        frameList.append(newFrame)
        if newFrame.shape[0] > maxHeight:
            maxHeight = newFrame.shape[0]
            
        #Show percentage of loop completed.
        #print('\rFinding and correcting horizontal shifts: {:.2f}% done'.format((100.0*((i+1)/len(stack)))), end='', flush=True)
        #print('Finding and correcting horizontal shifts: {:.2f}% done'.format((100.0*((i+1)/len(stack)))), end='', flush=True)
        #print(str(i) + 'flattenframes loop\n')
    print('\n')
    print('Finding and correcting horizontal shifts end')
    print('\n')
    del stack    
    flattenedStack = padFrames(frameList, maxHeight)

    return flattenedStack

def padFrames(frameList, maxHeight):
    """
    Finds the height differences between frames in the stack and adds padding to give them identical dimensions.
    
    Parameters:
    -----------
    frameList: the list of flattened frames with different heights.
    
    maxHeight: the largest height of the frames.
    
    Outputs:
    -----------
    stack: Flattened ndarray stack ready for saving. b
    
    """
    
    # writeText('\n')
    print('padding frames start')
    for i, frame in enumerate(frameList):
        extraSpace = maxHeight - frame.shape[0]
        #frameList[i] = np.lib.pad(frame,((int(np.floor(extraSpace/2)),int(np.ceil(extraSpace/2))),(0,0)),'constant', constant_values=(4000,8000))
        frameList[i] = np.lib.pad(frame,((extraSpace,0),(0,0)),'constant', constant_values=0)
        #print('\rPadding Frames: {:.2f} % done'.format((100.0*((i+1)/len(frameList)))),end='',flush=True)
        #print('Padding Frames: {:.2f} % done'.format((100.0*((i+1)/len(frameList)))),end='',flush=True)
    print('\n')
    print('padding frames end')
    print('\n')
    stack = np.stack(frameList, axis=0)
    
    return stack

def correctFrameShift(stack):

    """
    Finds and corrects the differences between frames - this is due in part to the within frame correction and the curvature of the retina and the breathing artifacts
    which are not completely removed with this algorithm.

    Parameters:
    -----------
    stack: this is the stack that has had each frame flattened, but the frames are at different heights.

    Outputs:
    -----------
    shiftedStack: This is the stack that is fully flattened.

    """

    maxHeight=0
    frameList=[]
    midStripsFrame = np.empty((stack.shape[1],stack.shape[0])) #needs to have the number of columns as the depth of the stack!

    #I think this should be powerfule enough that I don't need to worry about onh for the frame adjustments
    midStripsFrame = np.mean(stack, axis=2).T

    shifts = shiftDetector(midStripsFrame)
    minShift = min(shifts)
    allPositiveShifts = [shift-minShift for shift in shifts]
    
    shiftedFrames = []
    i=0
    # writeText('\n')
    print('correcting frame shifts/vertical curvature start')
    for shift, frame in zip(allPositiveShifts, stack):
        newFrame = np.lib.pad(frame, ((0,shift),(0,0)),'constant',constant_values=0)
        shiftedFrames.append(newFrame)
        if newFrame.shape[0] > maxHeight:
            maxHeight = newFrame.shape[0]
        #print('Correcting Frame Shifts/Vertical Curvature: {:.2f} % done'.format((100.0*((i+1)/len(stack)))), end='', flush=True)
        i+=1
    print('\n')
    print('correcting frame shifts/vertical curvature end')
        
    shiftedStack = padFrames(shiftedFrames, maxHeight)
                                                          
    return shiftedStack 
    #return shiftedFrames

def enfaceStack(stack):
    """Turns the Bscans into a 256x256 enface image, and removes all blank frames (the dimensions will not match the Bscans!!)"""
    enface=np.swapaxes(stack,0,1)
    enface_downsize=np.empty((enface.shape[0],256,256))
    # writeText('\n')
    print('resizing start')
    for i, frame in enumerate(enface):
        enface_downsize[i] = transform.resize(frame,(256,256),order=3,mode='reflect')
        #print('Resizing: {:.2f} % done'.format((100.0*((i+1)/enface.shape[0]))), end='', flush=True)
    print('resizing done')
    print('\n')
    mask=np.any(enface_downsize!=0,axis=(1,2))
    enface_cleaned = enface_downsize[mask]

    return enface_cleaned

def runImageProcessProgram(stack, onh_info):
    flattenedStack = flattenFrames(stack, onh_info)
    shiftedStack = correctFrameShift(flattenedStack)
    enfaceStackImages = enfaceStack(shiftedStack)
    
    return shiftedStack, enfaceStackImages

def runner(image_data, path, onh=False):   

    print('runner')

    #parentPath, childDir = str.rsplit(path,os.sep,1)
 
    #savePath = os.path.join(os.path.join(parentPath,"processed_OCT_images"),childDir)
    savePath = os.path.join(path, "processed_OCT_images")
    print('save'+savePath)

    try:
        os.makedirs(savePath)
    except FileExistsError:
        print('processed_OCT_images folder already exists at {},\n use -overwrite if processing is desired at this location'.format(path))
        pass
    else:
        #stackIn = im_open(path) #### OPEN IMAGE NOT DIRECTORY???? <-- have to change im_open function i think???
        #replacing line above with line below
        #stackIn = extract_tiff(full_path)
        stackIn = image_data
        onh_info = detect_onh(stackIn)
        if not onh:

            stackOut, enfaceOut = runImageProcessProgram(stackIn, onh_info)
            
            #if doing pv oct: bmps are already 8bit. using 16bit will get a low contrast warning, but no worries.
            
            save(stackOut.astype('uint16'),savePath,'flat_Bscans.tif')
            print('[+]\tSaved {}{}flat_bscans.tif'.format(savePath, os.sep))
            save(enfaceOut.astype('uint16'),savePath,'enface.tif')
            print('[+]\tSaved {}{}enface.tif\n'.format(savePath, os.sep))
        csv_path = os.path.join(savePath,'onh_location.csv')
        if onh_info!=-1:
            with open(csv_path,'w') as f:
                csv_write = csv.writer(f)
                csv_write.writerow(['Y', 'X'])
                csv_write.writerow((onh_info.centroid[0], onh_info.centroid[1]/4))
            pickle_path = os.path.join(savePath, 'onh_info.pkl')
            with open(pickle_path, 'wb') as p:
                pickle.dump(onh_info, p, -1)
        else:
            print('No ONH was detected at {}'.format(path))
            pass

def runnerOver(path, onh=False):

    print('RUNNEROVER')

    parentPath, childDir = str.rsplit(path,os.sep,1)

    savePath = os.path.join(os.path.join(parentPath,"processed_OCT_images"),childDir)

    try:
        os.makedirs(savePath)
    except FileExistsError:
        print('\nRemoving {}'.format(savePath))
        shutil.rmtree(savePath)
        os.makedirs(savePath)
        #pass
    stackIn = im_open_flat(path) ######## <- 
    onh_info = detect_onh(stackIn)
    if not onh:
        stackOut, enfaceOut = runImageProcessProgram(stackIn, onh_info)
        
        #if doing pv oct: bmps are already 8bit. using 16bit will get a low contrast warning, but no worries.
        
        save(stackOut.astype('uint16'),savePath,'flat_Bscans.tif')
        print('[+]\tSaved {}{}flat_bscans.tif'.format(savePath, os.sep))
        save(enfaceOut.astype('uint16'),savePath,'enface.tif')
        print('[+]\tSaved {}{}enface.tif\n'.format(savePath, os.sep))
    if onh_info != -1:
        csv_path = os.path.join(savePath,'onh_location.csv')
        with open(csv_path,'w') as f:
            csv_write = csv.writer(f)
            csv_write.writerow(['Y', 'X'])
            csv_write.writerow((onh_info.centroid[0], onh_info.centroid[1]/4))
        pickle_path = os.path.join(savePath, 'onh_info.pkl')
        with open(pickle_path, 'wb') as p:
            #open using with open(f_path, 'rb') as f:
            #   onh_info = pickle.load(f)
            pickle.dump(onh_info, p, -1)
    else:
        print('error at {}'.format(parentPath))
        error_path = os.path.join(savePath, 'error.txt')
        with open(error_path, 'w') as e:
            e.write('ONH was not identified.')


##########################
def find_amp(image_data, path, args):

    #path = top_path+os.sep+'**'+os.sep+'OCT'

        #### importing folder from matlab <-- change
    print('find amp')
    
    print('path=' + path)
    amp_folders = glob.iglob(path, recursive=True)    # <-- path processing to save - change path - searches for you
    for folder in amp_folders:
        if 'processed_OCT_images' in folder:
            continue
        else:
            print('\n*****\nProcessing:\t{}\n*****\n'.format(folder))
            if args.overwrite and not args.onh:
                #overwrite
                runnerOver(folder)
            elif not args.overwrite and args.onh:
                #find onh only
                runner(image_data, path, onh=True)
            elif args.overwrite and args.onh:
                #find onh after flattening has occurred
                runnerOver(folder, onh=True)
            else:
                #Run and don't overwrite anything
                print('else - run and dont overwrite anything')
                runner(image_data, path)
    #case sensitivity issues...
    #pv_path = top_path+os.sep+'**'+os.sep+'r'+os.sep+'i'










pathImported = askdirectory() # contais top folder with all the other folders
print('working?')
if pathImported == '':
    sys.exit('\nExited: No directory selected')

else:
    print('starting search')
    searchStart(pathImported)      

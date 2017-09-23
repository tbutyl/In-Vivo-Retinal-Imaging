from tkinter.filedialog import askdirectory, askopenfilename
from skimage import io, transform
import numpy as np
import scipy as sp
import sys, os, glob
from scipy import ndimage, signal
from skimage.filters import rank

def open(path):

        """Imports a folder containing a stack of images using scikit image collections"""

        try:
                assert os.path.isdir(path)
                #get file list in directory - glob includes full path
                files = glob.glob('{}{}*'.format(path,os.sep)) 
                #load the collection
                raw_stack = io.imread_collection(files)
                #turn the collection into a np array and remove extraneous OCT portion from 1025:1083 on x axis. (z,y,x)
                #if .bmp files are open (from pv-oct), the slicing will not affect them, the x-axis is only 540 pixels.
                stack = io.collection.concatenate_images(raw_stack)[:,:,0:1024]
                
                return stack

        except AssertionError:
                sys.exit("A non-directory object was given to the __open__ function")


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
    if min(shifts)<0:
        botShifts = [colShift-min(shifts) for colShift in shifts]
    else:
        botShifts = [colShift for colShift in shifts]
    topShifts = [max(botShifts)-shift for shift in botShifts]
    newFrame=np.empty([frame.shape[1],frame.shape[0]+max(botShifts)])
    for i, col in enumerate(frame.T):
        newCol = np.concatenate((np.zeros(topShifts[i]),col,np.zeros(botShifts[i])))
        newFrame[i]=newCol
    newFrame=newFrame.T
    
    return newFrame

def shiftDetector(frame):
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

def flattenFrames(stack):
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
    
    
    for i, frame in enumerate(stack):
        #medFrame = ndimage.filters.median_filter(frame,size=(1,60)) #Takes 3.5 minutes
        medFrame = ndimage.filters.uniform_filter1d(frame, 60) #Takes 1.0 minutes and has same output as med filter
        shifts = shiftDetector(medFrame)
        newFrame = adjustFrame(frame, shifts)
        frameList.append(newFrame)
        if newFrame.shape[0] > maxHeight:
            maxHeight = newFrame.shape[0]
            
        #Show percentage of loop completed.
        print('\rFinding and correcting horizontal shifts: {:.2f}% done'.format((100.0*((i+1)/len(stack)))), end='', flush=True)
    print('\n')
        
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
    stack: Flattened ndarray stack ready for saving. 
    
    """
    
    # writeText('\n')
    for i, frame in enumerate(frameList):
        extraSpace = maxHeight - frame.shape[0]
        #frameList[i] = np.lib.pad(frame,((int(np.floor(extraSpace/2)),int(np.ceil(extraSpace/2))),(0,0)),'constant', constant_values=(4000,8000))
        frameList[i] = np.lib.pad(frame,((extraSpace,0),(0,0)),'constant', constant_values=0)
        print('\rPadding Frames: {:.2f} % done'.format((100.0*((i+1)/len(frameList)))),end='',flush=True)
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
    # writeText('\n')
    for i, frame in enumerate(stack):
        medFrame = ndimage.filters.uniform_filter1d(frame, 60)
        midStrip = medFrame[:,int(medFrame.shape[1]/2)]
        midStripsFrame[:,i] = midStrip
        print('\rDetecting Frame Shifts/Vertical Curvature: {:.2f} % done'.format((100.0*((i+1)/len(stack)))), end='', flush=True)
    print('\n')

    shifts = shiftDetector(midStripsFrame)
    minShift = min(shifts)
    allPositiveShifts = [shift-minShift for shift in shifts]
    
    shiftedFrames = []
    i=0
    # writeText('\n')
    for shift, frame in zip(allPositiveShifts, stack):
        newFrame = np.lib.pad(frame, ((0,shift),(0,0)),'constant',constant_values=0)
        shiftedFrames.append(newFrame)
        if newFrame.shape[0] > maxHeight:
            maxHeight = newFrame.shape[0]
        print('\rCorrecting Frame Shifts/Vertical Curvature: {:.2f} % done'.format((100.0*((i+1)/len(stack)))), end='', flush=True)
        i+=1
    print('\n')
        
    shiftedStack = padFrames(shiftedFrames, maxHeight)
                                                          
    return shiftedStack 

def enfaceStack(stack):
    """Turns the Bscans into a 256x256 enface image, and removes all blank frames (the dimensions will not match the Bscans!!)"""
    enface=np.swapaxes(stack,0,1)
    enface_downsize=np.empty((enface.shape[0],256,256))
    # writeText('\n')
    for i, frame in enumerate(enface):
        enface_downsize[i] = transform.resize(frame,(256,256),order=3,mode='reflect')
        print('\rResizing: {:.2f} % done'.format((100.0*((i+1)/enface.shape[0]))), end='', flush=True)
    print('\n')
    mask=np.any(enface_downsize!=0,axis=(1,2))
    enface_cleaned = enface_downsize[mask]

    return enface_cleaned

def runImageProcessProgram(stack):
    flattenedStack = flattenFrames(stack)
    shiftedStack = correctFrameShift(flattenedStack)
    enfaceStackImages = enfaceStack(shiftedStack)
    
    return shiftedStack, enfaceStackImages

def runner(path):
        parentPath, childDir = str.rsplit(path,os.sep,1)

        savePath = os.path.join(os.path.join(parentPath,"processed_OCT_images"),childDir)

        try:
                os.makedirs(savePath)
        except FileExistsError:
                print('processed_OCT_images folder already exists at {},\n currently you must delete this folder to rerun'.format(path))
                pass
        else:
                stackIn = open(path)
                stackOut, enfaceOut = runImageProcessProgram(stackIn)
                
                #if doing pv oct: bmps are already 8bit. using 16bit will get a low contrast warning, but no worries.
                
                save(stackOut.astype('uint16'),savePath,'flat_Bscans.tif')
                print('Saved {}{}flat_bscans.tif'.format(savePath, os.sep))
                save(enfaceOut.astype('uint16'),savePath,'enface.tif')
                print('Saved {}{}enface.tif'.format(savePath, os.sep))
                


def walker(top_path):

        for path, direc, files in os.walk(top_path):
                for each in direc:
                        new_path = os.path.join(path,each)
                        if (('Amp_FFT2X' in new_path or os.path.join('r','i') in new_path.lower()) and not "processed_OCT_images" in new_path):
                                print('\nFound {}'.format(new_path))
                                runner(new_path)


def main():
        top_path = askdirectory()
        if top_path=='':
                sys.exit('\nExited: No directory was selected')
        elif os.path.isfile(top_path):
                sys.exit('Exited: File selected. Please select top directory')
        walker(top_path)
        print('\n--------\nComplete\n--------')


if __name__ == '__main__':
        main()

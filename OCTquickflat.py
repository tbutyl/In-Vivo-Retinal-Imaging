from tkinter.filedialog import askopenfilename
from tkinter import *
import numpy as np
import scipy as sp
from scipy import ndimage
from scipy import signal
from libtiff import TIFFfile, TIFFimage, TIFF
from skimage.filters import rank
import sys

def importStack(path, inputFile):
    ##Imports a Multi-page Tiff using pylibtiff"""
    print("Importing",path+inputFile)
    pathName = path+inputFile
    img = TIFFfile(pathName)
    samples, names = img.get_samples()
    img.close()
    samples = np.asarray(samples).squeeze()
    print("Done")
    
    return samples

def saveStack(procImg,path,fileName):
    #"Saves the multipage tiff"
    pathName = path+fileName
    img = TIFFimage(procImg)
    img.write_file(pathName)
    del img

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
    
    
    print('\n')
    for i, frame in enumerate(stack):
        #medFrame = ndimage.filters.median_filter(frame,size=(1,60)) #Takes 3.5 minutes
        medFrame = ndimage.filters.uniform_filter1d(frame, 60) #Takes 1.0 minutes and has same output as med filter
        shifts = shiftDetector(medFrame)
        newFrame = adjustFrame(frame, shifts)
        frameList.append(newFrame)
        if newFrame.shape[0] > maxHeight:
            maxHeight = newFrame.shape[0]
            
        #Show percentage of loop completed.
        print('\rFinding and correcting shifts {:.2f}% done'.format(100.0*((i+1)/len(stack))),end='', flush=True)
        
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
    
    print('\n')
    for i, frame in enumerate(frameList):
        extraSpace = maxHeight - frame.shape[0]
        #frameList[i] = np.lib.pad(frame,((int(np.floor(extraSpace/2)),int(np.ceil(extraSpace/2))),(0,0)),'constant', constant_values=(4000,8000))
        frameList[i] = np.lib.pad(frame,((extraSpace,0),(0,0)),'constant', constant_values=0)
        print('\rPadding Frames {:.2f}% done'.format(100.0*((i+1)/len(frameList))),end='', flush=True)
    stack = np.stack(frameList, axis=0)
    
    return stack

def correctFrameShift(stack):

    """Need Doc info"""

    maxHeight=0
    frameList=[]
    midStripsFrame = np.empty((stack.shape[1],stack.shape[0])) #needs to have the number of columns as the depth of the stack!
    print('\n')
    for i, frame in enumerate(stack):
        medFrame = ndimage.filters.uniform_filter1d(frame, 60)
        midStrip = medFrame[:,int(medFrame.shape[1]/2)]
        midStripsFrame[:,i] = midStrip
        print('\rDetecting Frame Shifts/Vertical Curvature {:.2f}% done'.format(100.0*((i+1)/len(stack))),end='', flush=True)
    
    shifts = shiftDetector(midStripsFrame)
    minShift = min(shifts)
    allPositiveShifts = [shift-minShift for shift in shifts]
    
    shiftedFrames = []
    i=0
    print('\n')
    for shift, frame in zip(allPositiveShifts, stack):
        newFrame = np.lib.pad(frame, ((0,shift),(0,0)),'constant',constant_values=0)
        shiftedFrames.append(newFrame)
        if newFrame.shape[0] > maxHeight:
            maxHeight = newFrame.shape[0]
        print('\rCorrecting Frame Shifts/Vertical Curvature {:.2f}% done'.format(100.0*((i+1)/len(stack))),end='', flush=True)
        i+=1
        
    shiftedStack = padFrames(shiftedFrames, maxHeight)
                                                          
    return shiftedStack 

def runner(stack):
    flattenedStack = flattenFrames(stack)
    shiftedStack = correctFrameShift(flattenedStack)
    print('\nCorrection Finished')
    
    return shiftedStack
    
def main():
    
    Tk().withdraw()
    filename = askopenfilename()
    fileSplit = str.rsplit(filename,'/',1)
    path = fileSplit[0]+'/'
    imageName = fileSplit[1]
    stackIn = importStack(path,imageName)
    stackOut = runner(stackIn)
    saveStack(stackOut.astype('uint16'),path,'flat_'+imageName)
    
main()

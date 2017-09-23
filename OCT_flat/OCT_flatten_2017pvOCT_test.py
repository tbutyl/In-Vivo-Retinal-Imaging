from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from tkinter import *
from libtiff import TIFFfile, TIFFimage, TIFF
import numpy as np
import scipy as sp
from tkinter import *
from tkinter import ttk
import sys
from scipy import ndimage
from scipy import signal
from skimage.filters import rank
from skimage import transform
import os

def writeText(text, location=END, replace=False, loopVar=None):
    if replace==True:
        textOut['state']='normal'
        if loopVar > 0:
            textOut.delete("end-1l", "end")
            textOut.insert(location, '\n'+text)
        else:
            textOut.insert(location, text)
        textOut['state']='disabled'
    else:
        textOut['state']='normal'
        textOut.insert(location, text+'\n')
        textOut['state']='disabled'
    root.update()
    
def saveStack(procImg,path,fileName):
    #"Saves the multipage tiff"
    pathName = path+fileName
    img = TIFFimage(procImg)
    #Set verbose to false on 10-11-2016 because there was an issue with time.time()-start_time was 0 and was a divisor that prevented the enface stack from getting saved. This also prevents output to the command line
    img.write_file(pathName, verbose=False)
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
    
    
    for i, frame in enumerate(stack):
        #medFrame = ndimage.filters.median_filter(frame,size=(1,60)) #Takes 3.5 minutes
        medFrame = ndimage.filters.uniform_filter1d(frame, 60) #Takes 1.0 minutes and has same output as med filter
        shifts = shiftDetector(medFrame)
        newFrame = adjustFrame(frame, shifts)
        frameList.append(newFrame)
        if newFrame.shape[0] > maxHeight:
            maxHeight = newFrame.shape[0]
            
        #Show percentage of loop completed.
        percentDone = '{:.2f} % done'.format((100.0*((i+1)/len(stack))))
        writeText('Finding and correcting horizontal shifts '+percentDone,replace=True, loopVar=i)
        # writeText('Finding and Correcting Horizontal Curvature {:.2f}% done'.format((100.0*((i+1)/len(stack)))))
        
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
        percentDone = '{:.2f} % done'.format((100.0*((i+1)/len(frameList))))
        writeText('Padding Frames '+percentDone,replace=True, loopVar=i)
        # writeText('Padding Frames {:.2f} % done'.format((100.0*((i+1)/len(frameList)))))
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
        percentDone = '{:.2f} % done'.format((100.0*((i+1)/len(stack))))
        writeText('Detecting Frame Shifts/Vertical Curvature '+percentDone,replace=True, loopVar=i)
        # writeText('Detecting Frame Shifts/Vertical Curvature {:.2f} % done'.format((100.0*((i+1)/len(stack)))))
    
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
        percentDone = '{:.2f} % done'.format((100.0*((i+1)/len(stack))))
        writeText('Correcting Frame Shifts/Vertical Curvature '+percentDone,replace=True, loopVar=i)
        i+=1
        # writeText('Correcting Frame Shifts/Vertical Curvature {:.2f} % done'.format((100.0*((i+1)/len(stack)))))
        
    shiftedStack = padFrames(shiftedFrames, maxHeight)
                                                          
    return shiftedStack 

def enfaceStack(stack):
    enface=np.swapaxes(stack,0,1)
    enface_downsize=np.empty((enface.shape[0],256,256))
    # writeText('\n')
    for i, frame in enumerate(enface):
        enface_downsize[i] = transform.resize(frame,(256,256),order=3,mode='reflect')
        percentDone = '{:.2f} % done'.format((100.0*((i+1)/enface.shape[0])))
        writeText('Resizing '+percentDone,replace=True, loopVar=i)
        # writeText('Resizing {:.2f} % done'.format((100.0*((i+1)/enface.shape[0]))))
    mask=np.any(enface_downsize!=0,axis=(1,2))
    enface_cleaned = enface_downsize[mask]

    return enface_cleaned

def runImageProcessProgram(stack):
    flattenedStack = flattenFrames(stack)
    shiftedStack = correctFrameShift(flattenedStack)
    enfaceStackImages = enfaceStack(shiftedStack)
    
    return shiftedStack, enfaceStackImages

def singleImport(path, fileName):
    img = TIFFfile(path+'/'+fileName)
    samples, names = img.get_samples()
    img.close()
    #change on 10-17-16 to try to get the image at the correct size 1083->1024
    #10-17-16 note after test: 0:1023 caused the B-scans to only be 1023 pixels wide. Should be 1024 so changed to 0:1024, though this seems wrong.
    samples = np.asarray(samples).squeeze()
    if len(samples.shape) == 3:
        samples = samples[:,:,0:1024]
    elif len(samples.shape) == 2:
        samples = samples[:,0:1024]
    else:
        writeText("You have an array that is not 2 or 3 dimensions.")

    return samples

def seqImport(path):
    file_list = os.listdir(path)
    file_list.sort(key=lambda x: '{0:0>8}'.format(x))
    stack = []
    for fileName in file_list:
        samples = singleImport(path, fileName)
        stack.append(samples)
    stack=np.asarray(stack)

    return stack

def runner(path, fileName=None):
    if fileName != None:
        stackIn = singleImport(path, fileName) 
    else:
        stackIn = seqImport(path)
    stackOut, enfaceOut = runImageProcessProgram(stackIn)
    parentPath,childDir = str.rsplit(path,'/',1)
    try:
#Kinda weak sauce, but should usually only fail when dir already exists
        try:
            os.mkdir(parentPath +"/processed_OCT_images")
        except:
            pass
        os.mkdir(parentPath +"/processed_OCT_images/"+childDir)
    except:
        pass
    savePath = parentPath +'/'+"processed_OCT_images/"+childDir+'/'
    # overwrites saved images -- shuld fix
    writeText('\n')
    saveStack(stackOut.astype('uint16'),savePath,'flat_Bscans.tif')
    writeText('Saved '+savePath+'flat_Bscans.tif')
    # writeText('\n')
    saveStack(enfaceOut.astype('uint16'),savePath,'enface.tif')
    writeText('Saved '+savePath+'enface.tif')

def loader():
    path = askdirectory()
    bottomFolder = str.rsplit(path,'/',1)[1]
    if (bottomFolder == 'Amp_FFT2X' or bottomFolder=='i'):#before had OCT, fluorescence, and reflectance, but really those probably won't work
        pathList.insert(END, path)
    else:
        path=askopenfilename()
        pathList.insert(END, path)
    if int(pathList.size())>=1:
        processButton['state']='normal'

def removePath():
    try:
        indexOfSelection=pathList.curselection()
        pathList.delete(indexOfSelection)
    except:
        try:
            pathList.delete(END)
        except:
            pass
    if int(pathList.size())==0:
        processButton['state']='disabled'
    

def processList():
    processButton['state']='disabled'
    addButton['state']='disabled'
    removeButton['state']='disabled'
    quitButton['state']='disabled'
    pathListSize=int(pathList.size())-1
    # writeText('Starting')
    images = pathList.get(0, pathListSize)
    for eachPath in images:
        writeText('Processing...'+eachPath)
        try:
            try:
                # should cahnge to os.isfile
                a, b = str.rsplit(eachPath, '.', 1) #test case to see if file is being loaded
                pathName, fileName = str.rsplit(eachPath, '/', 1)
                runner(pathName, fileName)
            except:
                runner(eachPath)
        except:
            writeText("There was an error for "+eachPath)
            continue
            #print the suffix of the file -- probably not a tif. Else? I dunno...
    quitButton['state']='!disabled'
    pathList.delete(0,END)
    addButton['state']='!disabled'
    removeButton['state']='!disabled'

def quit():
    # root.destroy()
    sys.exit()

root = Tk()
root.title("OCT Processor")

mainframe = ttk.Frame(root, padding="12 12 12 12")
mainframe.grid(column=0,row=0,sticky=(N,W,E,S))
mainframe.columnconfigure(0,weight=1)
mainframe.rowconfigure(0,weight=1)

#Box with paths
pathListVar = StringVar()
pathList = Listbox(mainframe, listvariable=pathListVar,width=50,height=30)
# pathListScroll = ttk.Scrollbar(mainframe, orient=VERTICAL, command=pathList.yview)
# pathList.configure(yscrollcommand=pathListScroll.set)
pathList.grid(column=1,row=2,rowspan=10,columnspan=10,sticky=E+W)

#Add/remove buttons
addButton = ttk.Button(mainframe, text='Add', command=loader)
addButton.grid(column=1,row=12,columnspan=2, sticky=E+W)
removeButton = ttk.Button(mainframe, text='Remove',command=removePath)
removeButton.grid(column=3,row=12,columnspan=2, sticky=E+W)

#Ouput Frame
infoFrame = ttk.Frame(mainframe, borderwidth=5, relief="sunken", padding = "5 5 5 5", width=350,height=350)
infoFrame.grid(row=1,column=12, rowspan=12, columnspan=8)
textOut = Text(infoFrame, state=DISABLED)
textOut.grid(column=0,row=0)

#Process button
processButton = ttk.Button(mainframe,text='Process', state=DISABLED, command=processList)
processButton.grid(row=13,column=15,columnspan=4, sticky=E+W)

#quit button
quitButton = ttk.Button(mainframe, text='Quit', command=quit)
quitButton.grid(row=1,column=15,columnspan=4,sticky=E+W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5,pady=5)

root.mainloop()

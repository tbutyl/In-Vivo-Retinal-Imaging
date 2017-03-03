// "StartupMacros"
// The macros and macro tools in this file ("StartupMacros.txt") are
// automatically installed in the Plugins>Macros submenu and
//  in the tool bar when ImageJ starts up.

//  About the drawing tools.
//
//  This is a set of drawing tools similar to the pencil, paintbrush,
//  eraser and flood fill (paint bucket) tools in NIH Image. The
//  pencil and paintbrush draw in the current foreground color
//  and the eraser draws in the current background color. The
//  flood fill tool fills the selected area using the foreground color.
//  Hold down the alt key to have the pencil and paintbrush draw
//  using the background color or to have the flood fill tool fill
//  using the background color. Set the foreground and background
//  colors by double-clicking on the flood fill tool or on the eye
//  dropper tool.  Double-click on the pencil, paintbrush or eraser
//  tool  to set the drawing width for that tool.
//
// Icons contributed by Tony Collins.

// Global variables
var pencilWidth=1,  eraserWidth=10, leftClick=16, alt=8;
var brushWidth = 10; //call("ij.Prefs.get", "startup.brush", "10");
var floodType =  "8-connected"; //call("ij.Prefs.get", "startup.flood", "8-connected");

// The macro named "AutoRunAndHide" runs when ImageJ starts
// and the file containing it is not displayed when ImageJ opens it.

// macro "AutoRunAndHide" {}

function UseHEFT {
	requires("1.38f");
	state = call("ij.io.Opener.getOpenUsingPlugins");
	if (state=="false") {
		setOption("OpenUsingPlugins", true);
		showStatus("TRUE (images opened by HandleExtraFileTypes)");
	} else {
		setOption("OpenUsingPlugins", false);
		showStatus("FALSE (images opened by ImageJ)");
	}
}

UseHEFT();

// The macro named "AutoRun" runs when ImageJ starts.

macro "AutoRun" {
	// run all the .ijm scripts provided in macros/AutoRun/
	autoRunDirectory = getDirectory("imagej") + "/macros/AutoRun/";
	if (File.isDirectory(autoRunDirectory)) {
		list = getFileList(autoRunDirectory);
		// make sure startup order is consistent
		Array.sort(list);
		for (i = 0; i < list.length; i++) {
			if (endsWith(list[i], ".ijm")) {
				runMacro(autoRunDirectory + list[i]);
			}
		}
	}
}

var pmCmds = newMenu("Popup Menu",
	newArray("Help...", "Rename...", "Duplicate...", "Original Scale",
	"Paste Control...", "-", "Record...", "Capture Screen ", "Monitor Memory...",
	"Find Commands...", "Control Panel...", "Startup Macros...", "Search..."));

macro "Popup Menu" {
	cmd = getArgument();
	if (cmd=="Help...")
		showMessage("About Popup Menu",
			"To customize this menu, edit the line that starts with\n\"var pmCmds\" in ImageJ/macros/StartupMacros.txt.");
	else
		run(cmd);
}

macro "Abort Macro or Plugin (or press Esc key) Action Tool - CbooP51b1f5fbbf5f1b15510T5c10X" {
	setKeyDown("Esc");
}

var xx = requires138b(); // check version at install
function requires138b() {requires("1.38b"); return 0; }

var dCmds = newMenu("Developer Menu Tool",
newArray("ImageJ Website","News", "Documentation", "ImageJ Wiki", "Resources", "Macro Language", "Macros",
	"Macro Functions", "Startup Macros...", "Plugins", "Source Code", "Mailing List Archives", "-", "Record...",
	"Capture Screen ", "Monitor Memory...", "List Commands...", "Control Panel...", "Search...", "Debug Mode"));

macro "Developer Menu Tool - C037T0b11DT7b09eTcb09v" {
	cmd = getArgument();
	if (cmd=="ImageJ Website")
		run("URL...", "url=http://rsbweb.nih.gov/ij/");
	else if (cmd=="News")
		run("URL...", "url=http://rsbweb.nih.gov/ij/notes.html");
	else if (cmd=="Documentation")
		run("URL...", "url=http://rsbweb.nih.gov/ij/docs/");
	else if (cmd=="ImageJ Wiki")
		run("URL...", "url=http://imagejdocu.tudor.lu/imagej-documentation-wiki/");
	else if (cmd=="Resources")
		run("URL...", "url=http://rsbweb.nih.gov/ij/developer/");
	else if (cmd=="Macro Language")
		run("URL...", "url=http://rsbweb.nih.gov/ij/developer/macro/macros.html");
	else if (cmd=="Macros")
		run("URL...", "url=http://rsbweb.nih.gov/ij/macros/");
	else if (cmd=="Macro Functions")
		run("URL...", "url=http://rsbweb.nih.gov/ij/developer/macro/functions.html");
	else if (cmd=="Plugins")
		run("URL...", "url=http://rsbweb.nih.gov/ij/plugins/");
	else if (cmd=="Source Code")
		run("URL...", "url=http://rsbweb.nih.gov/ij/developer/source/");
	else if (cmd=="Mailing List Archives")
		run("URL...", "url=https://list.nih.gov/archives/imagej.html");
	else if (cmd=="Debug Mode")
		setOption("DebugMode", true);
	else if (cmd!="-")
		run(cmd);
}

var sCmds = newMenu("Stacks Menu Tool",
	newArray("Add Slice", "Delete Slice", "Next Slice [>]", "Previous Slice [<]", "Set Slice...", "-",
		"Convert Images to Stack", "Convert Stack to Images", "Make Montage...", "Reslice [/]...", "Z Project...",
		"3D Project...", "Plot Z-axis Profile", "-", "Start Animation", "Stop Animation", "Animation Options...",
		"-", "MRI Stack (528K)"));
macro "Stacks Menu Tool - C037T0b11ST8b09tTcb09k" {
	cmd = getArgument();
	if (cmd!="-") run(cmd);
}

var luts = getLutMenu();
var lCmds = newMenu("LUT Menu Tool", luts);
macro "LUT Menu Tool - C037T0b11LT6b09UTcb09T" {
	cmd = getArgument();
	if (cmd!="-") run(cmd);
}
function getLutMenu() {
	list = getLutList();
	menu = newArray(16+list.length);
	menu[0] = "Invert LUT"; menu[1] = "Apply LUT"; menu[2] = "-";
	menu[3] = "Fire"; menu[4] = "Grays"; menu[5] = "Ice";
	menu[6] = "Spectrum"; menu[7] = "3-3-2 RGB"; menu[8] = "Red";
	menu[9] = "Green"; menu[10] = "Blue"; menu[11] = "Cyan";
	menu[12] = "Magenta"; menu[13] = "Yellow"; menu[14] = "Red/Green";
	menu[15] = "-";
	for (i=0; i<list.length; i++)
		menu[i+16] = list[i];
	return menu;
}

function getLutList() {
	lutdir = getDirectory("luts");
	list = newArray("No LUTs in /ImageJ/luts");
	if (!File.exists(lutdir))
		return list;
	rawlist = getFileList(lutdir);
	if (rawlist.length==0)
		return list;
	count = 0;
	for (i=0; i< rawlist.length; i++)
		if (endsWith(rawlist[i], ".lut")) count++;
	if (count==0)
		return list;
	list = newArray(count);
	index = 0;
	for (i=0; i< rawlist.length; i++) {
		if (endsWith(rawlist[i], ".lut"))
			list[index++] = substring(rawlist[i], 0, lengthOf(rawlist[i])-4);
	}
	return list;
}

macro "Pencil Tool - C037L494fL4990L90b0Lc1c3L82a4Lb58bL7c4fDb4L5a5dL6b6cD7b" {
	getCursorLoc(x, y, z, flags);
	if (flags&alt!=0)
		setColorToBackgound();
	draw(pencilWidth);
}

macro "Paintbrush Tool - C037La077Ld098L6859L4a2fL2f4fL3f99L5e9bL9b98L6888L5e8dL888c" {
	getCursorLoc(x, y, z, flags);
	if (flags&alt!=0)
		setColorToBackgound();
	draw(brushWidth);
}

macro "Flood Fill Tool -C037B21P085373b75d0L4d1aL3135L4050L6166D57D77D68La5adLb6bcD09D94" {
	requires("1.34j");
	setupUndo();
	getCursorLoc(x, y, z, flags);
	if (flags&alt!=0) setColorToBackgound();
	floodFill(x, y, floodType);
}

function draw(width) {
	requires("1.32g");
	setupUndo();
	getCursorLoc(x, y, z, flags);
	setLineWidth(width);
	moveTo(x,y);
	x2=-1; y2=-1;
	while (true) {
		getCursorLoc(x, y, z, flags);
		if (flags&leftClick==0) exit();
		if (x!=x2 || y!=y2)
			lineTo(x,y);
		x2=x; y2 =y;
		wait(10);
	}
}

function setColorToBackgound() {
	savep = getPixel(0, 0);
	makeRectangle(0, 0, 1, 1);
	run("Clear");
	background = getPixel(0, 0);
	run("Select None");
	setPixel(0, 0, savep);
	setColor(background);
}

// Runs when the user double-clicks on the pencil tool icon
macro 'Pencil Tool Options...' {
	pencilWidth = getNumber("Pencil Width (pixels):", pencilWidth);
}

// Runs when the user double-clicks on the paint brush tool icon
macro 'Paintbrush Tool Options...' {
	brushWidth = getNumber("Brush Width (pixels):", brushWidth);
	call("ij.Prefs.set", "startup.brush", brushWidth);
}

// Runs when the user double-clicks on the flood fill tool icon
macro 'Flood Fill Tool Options...' {
	Dialog.create("Flood Fill Tool");
	Dialog.addChoice("Flood Type:", newArray("4-connected", "8-connected"), floodType);
	Dialog.show();
	floodType = Dialog.getChoice();
	call("ij.Prefs.set", "startup.flood", floodType);
}

macro "Set Drawing Color..."{
	run("Color Picker...");
}

macro "-" {} //menu divider

macro "About Startup Macros..." {
	title = "About Startup Macros";
	text = "Macros, such as this one, contained in a file named\n"
		+ "'StartupMacros.txt', located in the 'macros' folder inside the\n"
		+ "Fiji folder, are automatically installed in the Plugins>Macros\n"
		+ "menu when Fiji starts.\n"
		+ "\n"
		+ "More information is available at:\n"
		+ "<http://imagej.nih.gov/ij/developer/macro/macros.html>";
	dummy = call("fiji.FijiTools.openEditor", title, text);
}

macro "Save As JPEG... [j]" {
	quality = call("ij.plugin.JpegWriter.getQuality");
	quality = getNumber("JPEG quality (0-100):", quality);
	run("Input/Output...", "jpeg="+quality);
	saveAs("Jpeg");
}

macro "Save Inverted FITS" {
	run("Flip Vertically");
	run("FITS...", "");
	run("Flip Vertically");
}

macro "Convert to AVI" {
	/*
	 * Macro template to process multiple images in a folder
	 */

	input = getDirectory("Input directory");
	output = getDirectory("Output directory");

	Dialog.create("File type");
	Dialog.addString("File suffix: ", ".fits", 5);
	Dialog.show();
	suffix = Dialog.getString();

	processFolder(input);

	function processFolder(input) {
		list = getFileList(input);
		for (i = 0; i < list.length; i++) {
			if(File.isDirectory(list[i]))
				processFolder("" + input + list[i]);
			if(endsWith(list[i], suffix))
				processFile(input, output, list[i]);
		}
	}

	function processFile(input, output, file) {
		//run ("Bio-Formats", "open=[input]");
		open(input + file);
		splitFile = split(file, '.');
		outFile = output + splitFile[0] + ".avi";
		run("AVI... ", "compression=Uncompressed frame=28 save=[" + outFile + "]");
		print("Processing: " + input + file);
		print("Saving to: " + outFile);
		close();
	}
}

macro "Delete Slice [w]" {
	run("Create Shortcut... ", "command=[Delete Slice] shortcut=q");
}

\/*

************* Temporal-Color Coder *******************************
Color code the temporal changes.

Kota Miura (miura@embl.de) +49 6221 387 404 
Centre for Molecular and Cellular Imaging, EMBL Heidelberg, Germany

!!! Please do not distribute. If asked, please tell the person to contact me. !!!
If you publish a paper using this macro, it would be cratedful if you could acknowledge. 

 
---- INSTRUCTION ----

1. Open a stack (8 bit or 16 bit)
2. Run the macro
3. In the dialog choose one of the LUT for time coding.
	select frame range (default is full).
	check if you want to have color scale bar.

History

080212	created ver1 K_TimeRGBcolorcode.ijm
080213	stack slice range option added.
		time color code scale option added.

		future probable addiition: none-linear assigning of gray intensity to color intensity
		--> but this is same as doing contrast enhancement before processing.
*****************************************************************************
*/


var Glut = "Fire";	//default LUT
var Gstartf = 1;
var Gendf = 10;
var GFrameColorScaleCheck=1;

macro "Time-Lapse Color Coder"{
	Gendf = nSlices;
	Glut = ChooseLut();
	run("Duplicate...", "title=listeriacells-1.stk duplicate");
	hh = getHeight();
	ww = getWidth();
	totalslice = nSlices;
	calcslices = Gendf - Gstartf +1;
	run("8-bit");
	imgID = getImageID();

	newImage("colored", "RGB White", ww, hh, calcslices);
	newimgID = getImageID();

	setBatchMode(true);

	newImage("stamp", "8-bit White", 10, 10, 1);
	run(Glut);
	getLut(rA, gA, bA);
	close();
	nrA = newArray(256);
	ngA = newArray(256);
	nbA = newArray(256);

	for (i=0; i<calcslices; i++) {
		colorscale=floor((256/calcslices)*i);
		//print(colorscale);
		for (j=0; j<256; j++) {
			intensityfactor=0;
			if (j!=0) intensityfactor = j/255;
			nrA[j] = round(rA[colorscale] * intensityfactor);
			ngA[j] = round(gA[colorscale] * intensityfactor);
			nbA[j] = round(bA[colorscale] * intensityfactor);
		}
		newImage("temp", "8-bit White", ww, hh, 1);
		tempID = getImageID;

		selectImage(imgID);
		setSlice(i+Gstartf);
		run("Select All");
		run("Copy");

		selectImage(tempID);
		run("Paste");
		setLut(nrA, ngA, nbA);
		run("RGB Color");
		run("Select All");
		run("Copy");
		close();

		selectImage(newimgID);
		setSlice(i+1);
		run("Select All");
		run("Paste");
	}

	selectImage(imgID);
	close();
	selectImage(newimgID);
	op = "start=1 stop="+totalslice+" projection=[Max Intensity]";
	run("Z Project...", op);
	setBatchMode("exit and display");	
	if (GFrameColorScaleCheck) CreatGrayscale256(Glut, Gstartf, Gendf);
}

/*
run("Spectrum");
run("Fire");
run("Ice");
run("3-3-2 RGB");
run("brgbcmyw");
run("Green Fire Blue");
run("royal");
run("thal");
run("smart");
run("Rainbow RGB");
run("unionjack");
10 luts
*/

function ChooseLut() {
	lutA=newArray(10);
	lutA[0] = "Spectrum";
	lutA[1] = "Fire";
	lutA[2] = "Ice";
	lutA[3] = "Rainbow RGB";
	lutA[4] = "brgbcmyw";
	lutA[5] = "Green Fire Blue";
	lutA[6] = "royal";
	lutA[7] = "thal";
	lutA[8] = "smart";
	lutA[9] = "unionjack";

 	Dialog.create("Color Code Settings");
	Dialog.addChoice("LUT", lutA);
	Dialog.addNumber("start frame", Gstartf);
	Dialog.addNumber("end frame", Gendf);
	Dialog.addCheckbox("create Time Color Scale Bar", GFrameColorScaleCheck);
 	Dialog.show();
 	Glut = Dialog.getChoice();
	Gstartf= Dialog.getNumber();
	Gendf= Dialog.getNumber();
	GFrameColorScaleCheck = Dialog.getCheckbox();
	print("selected lut:"+ Glut);
	return Glut;
}

function CreatGrayscale256(lutstr, beginf, endf){
	ww = 256;
	hh=32;
	newImage("color time scale", "8-bit White", ww, hh, 1);
	for (j=0; j<hh; j++) {
		for (i=0; i<ww; i++) {
			setPixel(i, j, i);
		}
	}
	run(lutstr);
	//setLut(nrA, ngA, nbA);
	run("RGB Color");
	op = "width="+ww+" height="+hh+16+" position=Top-Center zero";
	run("Canvas Size...", op);
	setFont("SansSerif", 12, "antiliased");
	run("Colors...", "foreground=white background=black selection=yellow");
	drawString("frame", round(ww/2)-12, hh+16);
	drawString(leftPad(beginf, 3), 0, hh+16);
	drawString(leftPad(endf, 3), ww-24, hh+16);

}

function leftPad(n, width) {
    s =""+n;
    while (lengthOf(s)<width)
        s = "0"+s;
    return s;
}
/*
macro "drawscale"{
	CreatGrayscale256("Fire", 1, 100);
}
*/

macro "512-sizer [7]" {
	run("Size...", "width=512 height=512 "/*depth=5*/+" constrain average interpolation=Bicubic");
}
macro "compiled [f]" {
	run("Grouped Z Project...");
	run("Size...", "width=512 height=512 "/*depth=5*/+" constrain average interpolation=Bicubic");
	run("Brightness/Contrast...");
}

macro "stack draw [d]" {
	Dialog.create('Choose Color for Stack Draw');
	
	Dialog.addNumber('Red', 255);
	Dialog.addNumber('Green', 128);
	Dialog.addNumber('Blue', 0);
	Dialog.show()
	r = Dialog.getNumber();
	g = Dialog.getNumber();
	b = Dialog.getNumber();
	
	setForegroundColor(r,g,b);
	run("Draw", "stack");
}

macro "StackProc [8]" {
	Output = getImageID();
	run("Z Project...", "projection=Median");
	rename("Median Projection of RegStack"); // will want +j when the algorithm becomes iterative.
	
	//end registration function here

	Dialog.create("Set critera for NCCC cut off");
	Dialog.addMessage("This allows the user to modulate the threshold for famres to be cut.\n It is determined by the standard deviation of the NCCC multiplied by the entered factors.")
	Dialog.addNumber("Lower Threshold: ", 0.85);
	Dialog.addNumber("Upper Threshold: ", 0.85);
	Dialog.show();
	lower = Dialog.getNumber();
	upper = Dialog.getNumber();
	
	//Now need to compare the Ouput stack to the Median Projection with NCC
	//run("Z Project...", "projection=Median");
	getRawStatistics(count, mean, min, max, std);
	row = nResults;
   	setResult("Pixels", row, count);
   	setResult("Mean ", row, mean);
   	setResult("Std ", row, std);
   	setResult("Max ", row, max);
   	updateResults();
	pixelMed = getResult("Pixels",row);
	meanMed = getResult("Mean ",row);
   	stdMed = getResult("Std ",row);
    //Subtract median pixel value from median as part of NCC computation
   	run("Duplicate...","title=MedianSubMean");
	run("Macro...", "code=&v=v-("+meanMed+")"); //May want to duplicate in real thing

	
	selectImage(Output); //Select the stack that has been reigstered
	numSlices=nSlices;
	setBatchMode(true);
	for(k=1;k<=numSlices;k++){ //watch the numSlices here, this may change when I implement iteration and break the program.
		selectImage(Output);
		setSlice(k);
		getRawStatistics(count, mean, min, max, std); //Better to implement through List.setMeasurements?
    	row = nResults;
    	setResult("Pixels", row, count);
    	setResult("Mean ", row, mean);
    	setResult("Std ", row, std);
    	setResult("Max ", row, max);
    	updateResults();
    	pixel = getResult("Pixels",row);
    	mean = getResult("Mean ",row);
    	std = getResult("Std ",row);
    	max = getResult("Max ",row);
    	denom = (pixel-1)*std*stdMed; //can use pixel because images should ALWAYS have the same dimensions, issue: 1/n or 1/(n-1)? 1/(n-1) -- ImageJ uses n-1 in STDev computation.	
	
		//NCC loop

		run("Duplicate...", "title=slice"+k);
		run("Macro...", "code=&v=v-("+ mean + ")");
		//ImgCalc Multiply --- run(imgCalc, ??);
		//print("slice"+k+"wooo"); This is an check for the NCCC of every slice
		imageCalculator("Multiply create 32-bit", "slice"+k, "MedianSubMean");
		//Sum by integrated density
		List.setMeasurements;
		sum = List.getValue("RawIntDen");
		close();
		//divide by #pix and stdSlice*stdMed --- equation
		NCC = sum/denom; //Value doesn't match correlationj plugin though. But 1/n > 1 for NCC vals. 
		//print(sum, pixel, std, stdMed, NCC);
		//Build NCC array
		if(k==1) {
			indexArray = newArray(NCC); //This initializes the array that holds the correlation coeficient values. I'M VERY WORRIED THIS IS INITIALIZING WRONG!!!!!! 7/29/15 (week after writing code)
			indexArray = Array.concat(indexArray, NCC); //Fixed on 7/29 -- This fixes it for some reason. The frameTrimmer function does it quite a different way, but this seems a little easier, I guess.	Initial value was missing, but is now in array.	
		} else {
			indexArray = Array.concat(indexArray, NCC);//updating the array
		}
		selectImage("slice"+k);
		close();
	}
	setBatchMode("exit and display");
	//Trim bad frames
	
	//Array.show(indexArray);
	//print(indexArray.length);
	Array.getStatistics(indexArray, min, max, mean, stdDev);
	//print(mean);

	low = mean - lower*stdDev; //Changed from version 6 on 8/4/2015. empiracally these seem slightly better.
	high = mean + upper*stdDev;
	//print(min,max,mean,stdDev,"Low Val: ",low, "High Val: ",high);

	//initialize deletion array For keeping where frames were deleted 
	deleArray = newArray();
	delSli=0;

	selectImage(Output);
	run("Duplicate...", "title=TrimmedOutput duplicate");
	
	setBatchMode(true);
	
	for(l=0;l<indexArray.length;l++) {
		checkVal = indexArray[l];
		if (checkVal < low || checkVal > high) { //compares NCCC value of each slice to distribution; if greater than 1 STDev, slice is deleted.
			//cut
			adjSli = l+1-delSli; //adjusted counter to keep stack in bounds
			setSlice(adjSli);
			//print("Index Value: ", checkVal, "Adjusted Slice Number: ", adjSli, "Real Slice Number: ", l+1);
			run("Delete Slice"); 
			arrValSeq = Array.getSequence(l+2);
			//Array.print(arrValSeq);
			arrVal = Array.slice(arrValSeq, arrValSeq.length-1, arrValSeq.length); //Had to make an an array that goes up to the real slice number in the stack and then remove that 
			//because imageJ doesn't let you make a stack with just one number. I don't know why the start and end indices are not the same, but it seems to work. 
			deleArray = Array.concat(deleArray, arrVal); //concatenate the real slice number into the deletion array so we know where the deleted frames are. 
			delSli+=1;
		} else {
			//doNothing
		}
	}
	
	setBatchMode("exit and display");
	selectWindow("Results");
	run("Close");
	Array.show(deleArray);


}

macro 'Keeper [k]' {
	run("Slice Keeper");
}

macro "Time Stamper" {
	Dialog.create("Time splitter");
	Dialog.addString("Unit of Time", "seconds");
	Dialog.addNumber("Beginning Time", 0);
	Dialog.addNumber("End Time (s)", 100);
	
	Dialog.show();
	time = Dialog.getString();
	start = Dialog.getNumber();
	end = Dialog.getNumber();
	
	realFPS = (nSlices-1)/(end-start) //n-1 because there is the 0 slice

	run("Duplicate...","title=Labeled Stacks duplicate");
	run("Size...", "width=512 height=512 "/*depth=5*/+" constrain average interpolation=Bicubic");
	run("RGB Color");

	setFont("SansSerif" , 32, "antialiased");
	number = start;
	numberLabel = toString(number,1);
	label = numberLabel + ' ' + time;
	x = getStringWidth(label);
	y = 20; //font size
	
	for(k=1;k<=nSlices;k++){
		setSlice(k);
		drawString(label,512-x,512-y);
		number = number + (1/realFPS);
		numberLabel = toString(number,1);
		label = numberLabel+' '+time;
		x = getStringWidth(label);
	}
}

//please send comments to rietdorf@embl.de
// updates and other macros available at www.embl.de/eamnet/html/downloads.html

	requires("1.33n");
function check4pic() {
	if (nImages==0) exit("open an image");
}

function check4stack() {
	if (nSlices==0) exit("open a stack");
}

function pic2stack() {
	if (nSlices==0) run("Convert Images to Stack");
}


function  check4ROItype(mintype,maxtype,notype) {

	if ((selectionType()<mintype)||(selectionType()>maxtype)||(selectionType()==notype)||(selectionType()==-1)){
		if ((mintype==3)&&(maxtype==7)) exit("select a line ROI");
		if ((mintype==0)&&(maxtype==3)) exit("select an area ROI");
		else exit("select a suitable ROI");
	}
}

macro "correct bleach" {

	requires("1.33n");
        check4pic();
        pic2stack();
        if (selectionType()==-1) run("Select All");
        check4ROItype(0,3,-1);
        run("Set Slice...", "slice="+1);
        run("Set Measurements...", "  mean redirect=None decimal=9");
	  run("Select None");
	setBatchMode(true);				
	for(l=0; l<nSlices+1; l++) {
		run("Restore Selection");
		run("Clear Results");
		run("Measure");
		picsum=getResult("Mean",0);
		if(l==0){picsum1=picsum;}
		int_ratio=picsum1/picsum;
                		//print(int_ratio+'  '+picsum1+'  '+picsum);
		run("Select None");
		run("Multiply...", "slice value="+int_ratio);
		run("Next Slice [>]");
	}
	setBatchMode(false);
}

macro "makeNewStack" {
	//For some reason can't have stack in the name, seems to change it to iamge and throws an error?
	Dialog.create("Info for New Stack");
	Dialog.addMessage("Make a stack that has different images - rand, ramp, 0, 1")
	Dialog.addString("Name:  ", "Test");
	Dialog.addString("Type:  ", "random");
	Dialog.addNumber("Width: ", 256);
	Dialog.addNumber("Height: ", 256);
	Dialog.addNumber("Number of Slices: ", 1)
	Dialog.show();
	Name = Dialog.getString();
	Type = Dialog.getString();
	Width = Dialog.getNumber();
	Height = Dialog.getNumber();
	Slices = Dialog.getNumber();

	setBatchMode(true);
	
	for(i=1;i<=Slices;i++) {
		i_s = toString(i);
		sliceName = "slice"+i_s;
		newImage(sliceName, "8-bit "+Type, Width, Height, 1);
		if(i==1) {
			rename(Name);
		} else {
			run("Concatenate...", "stack1="+Name+" stack2="+sliceName+" title="+Name);
		}
	}
	
	setBatchMode("exit and display");
}

macro "rename [r]" {
	name=getTitle;
	Dialog.create("Input New Name");
	Dialog.addMessage("Input New Image Name - Make sure Image to be renamed was selected when you ran this macro!")
	Dialog.addString("Name:  ", name);
	Dialog.show();
	Name = Dialog.getString();
	rename(Name);
}

macro "sequence octProc [T]" {
	input = getDirectory("Input directory");
	list = getFileList(input);
	setBatchMode(true);
	run("Image Sequence...", "open=["+input+list[0]+"] sort");
	run("Reslice [/]...", "output=1.000 start=Top avoid");
	run("Size...", "width=512 height=512 average interpolation=Bicubic");
	output = getDirectory("Output directory");
	saveAs("tiff",output+"enface_stack");
	selectImage("Amp_FFT2X");
	run("Close");
	setBatchMode("exit and display");
}

macro "octProc [t]" {
	input = getDirectory("Input directory");
	setBatchMode(true);
	open(input+"flat_Amp_FFT2X.tif");
	run("Reslice [/]...", "output=1.000 start=Top avoid");
	run("Size...", "width=512 height=512 average interpolation=Bicubic");
	output = getDirectory("Output directory");
	saveAs("tiff",output+"enface_stack");
	run("Close All");
	setBatchMode("exit and display");
}

macro "reflectanceOCTStackMaker" {

	run("Close All");

	input = getDirectory("Input directory");
	output = input; //I'm too lazy to go through an change all the variable names...
	
	Dialog.create("File type");
	Dialog.addString("Match Name: ", "reflectance/", 10); // "/" is for folders, but may be WIN only, File.separator should work, but has not been.
	Dialog.show();
	suffix = Dialog.getString();
	
	//Can't set batch mode because to make the stack need to iterate through open images for concatenation
	//Open the images
	print("Input: "+input);
	processFolder(input);
	
	//Concatenate images from the set(s) of OCT
	list = listImageNames();
	if (lengthOf(list)>1) {
		run("Concatenate...", "title=[Reflectance Stack] image1="+list[0]+" image2="+list[1]+" image3="+list[2]);
	} else {
		rename("Reflectance Stack");
	}

	//Duplicate Stack and put into proper bitdepth and length x width
	run("Duplicate...", "duplicate");
	rename("ForReg");
	run("Size...", "width=512 height=512 depth=15 average interpolation=Bicubic"); //depth 15 only works with 3 sets of oct
	run("8-bit");
	//Get variables for registration - source
	numSlices = nSlices();
	sW = getWidth(); 
	sH = getHeight();

	//Produce the mask for ignoring the internal reflection spot
	selectImage("Reflectance Stack");
	run("16-bit"); //forced confirmation for the following line
	setThreshold(0,41401, "black & white"); //upper bound is set empirically, would be better to use getStatistics(area,mean,min,max,std,histogram); and try to figure out the position that is greater than 99% of the pixel values.  
	run("Convert to Mask", "method=Default background=Default");
	run("Z Project...", "projection=Median");
	run("Size...", "width=512 height=512 depth=15 average interpolation=Bicubic");
	rename("Mask");

	//Get first frame to register to and make the anchor
	selectImage("ForReg");
	run("8-bit");
	run("Slice Keeper", "first=1 last=1 increment=1");
	rename("RegAnchor");
	run("Concatenate...", "title=[RegAnchor] image1=RegAnchor image2=Mask");
	//Get variables for registration - target
	tW = getWidth();
	tH = getHeight();

	//Register 
	//Currently Does Rigid Body
	setBatchMode(true); //This prevents imagej from drawing each image
		for(i=1;i<=numSlices;i++) {
			selectImage("ForReg");
			setSlice(i);
			run("Duplicate...", "title=currentFrame");	
			//currently using an affine but this moght distort motile processes. So: Affine for topological and density analysis, translation for motility! May need to be two different sets of stacks.
			run("TurboReg ", "-align -window currentFrame 0 0 " + (sW-1) + " " + (sH-1) + " -window RegAnchor 0 0 " + (tW-1) + " " + (tH-1) + " -rigidBody " + (sW/2) + " " + (sH/3) + " " + (tW/2) + " " + (tH/3) + " " + (sW/3) + " " + ((2/3)*sH) + " " + (tW/3) + " " + ((2/3)*tH) + " " + ((2/3)*sW) + " " + ((2/3)*sH) + " " + ((2/3)*tW) + " " + ((2/3)*tH) + " -showOutput");
			rename("registeredFrame");
			if(i==1) {
				run("Duplicate...","title=Output");
				selectWindow("registeredFrame");
				close();
			} else {
				run("Duplicate...", "title=datFrame"); //Necessary because the output of Turbo Reg, only want data frame, not mask.
				run("Concatenate...", "stack1=Output stack2=datFrame title=Output");
		//Registered stack title is output
				selectImage("registeredFrame");
				close();
			}
			selectImage("currentFrame");
			close();
		}
	run("Clear Results");
	selectWindow("Refined Landmarks");
	run("Close");
	//Batch mode exited and output is drawn.
	setBatchMode("exit"); 
	run("Z Project...", "projection=Median");
	run("8-bit");
	
	//Save
	saveAs("tiff",output+"Registered_Reflectance_Image");
	run("Close All");
	
	
	function processFolder(input) {
		list = getFileList(input);
		for (i = 0; i < list.length; i++) {
			print(list[i]);
			if(File.isDirectory(input + list[i]) && !matches(list[i], suffix) && !matches(list[i], "OCT/")) { //prob WIN only right now
				processFolder("" + input + list[i]);
			}	
			if(matches(list[i], suffix)) {
				processFile(input, output, list[i]);
			}
		}
	}
	
	function processFile(input, output, folder) {
		print("Processing: " + input + folder);
		list = getFileList(input+folder);
		run("Image Sequence...", "open=["+input+folder+list[0]+"] sort");
		name = substring(input, (lengthOf(input)-7),(lengthOf(input)-2));
		rename(name);
		
	}
	
	function listImageNames() {
		n = nImages;
	    list = newArray(n);
	    for (i=1; i<=n; i++) {
	        selectImage(i);
	        list[i-1] = getTitle;
	    } 
		
	    return list;
	}
}

macro "change to 8-bit and enhance contrast [a]" {
	run("8-bit");
	path = getInfo("image.directory");
	name = split(getTitle(), '.');
	rename(name[0]+"_8bit");
	new_name = getTitle();
	run("Enhance Contrast...", "saturated=0.4");
	saveAs("tiff", path+new_name);
}

macro "reflectanceProcess [p]" {

	img = getImageID();
	//Duplicate Stack and put into proper bitdepth and length x width
	setBatchMode(true); //This prevents imagej from drawing each image
	run("Duplicate...", "duplicate");
	rename("ForReg");
	run("8-bit");
	//Get variables for registration - source
	numSlices = nSlices();
	sW = getWidth(); 
	sH = getHeight();

	//Produce the mask for ignoring the internal reflection spot
	selectImage(img); 
	run("16-bit"); //forced confirmation for the following line
	setThreshold(0,41401, "black & white"); //upper bound is set empirically, would be better to use getStatistics(area,mean,min,max,std,histogram); and try to figure out the position that is greater than 99% of the pixel values.  
	run("Convert to Mask", "method=Default background=Default");
	run("Z Project...", "projection=Median");
	rename("Mask");

	//Get first frame to register to and make the anchor
	selectImage("ForReg");
	run("8-bit");
	run("Slice Keeper", "first=1 last=1 increment=1");
	rename("RegAnchor");
	run("Concatenate...", "title=[RegAnchor] image1=RegAnchor image2=Mask");
	//Get variables for registration - target
	tW = getWidth();
	tH = getHeight();

	//Register 
	//Currently Does Rigid Body
	
	for(i=1;i<=numSlices;i++) {
		showProgress(i/numSlices);
		selectImage("ForReg");
		setSlice(i);
		run("Duplicate...", "title=currentFrame");	
		//Turboreg Function Call
		run("TurboReg ", "-align -window currentFrame 0 0 " + (sW-1) + " " + (sH-1) + " -window RegAnchor 0 0 " + (tW-1) + " " + (tH-1) + " -rigidBody " + (sW/2) + " " + (sH/3) + " " + (tW/2) + " " + (tH/3) + " " + (sW/3) + " " + ((2/3)*sH) + " " + (tW/3) + " " + ((2/3)*tH) + " " + ((2/3)*sW) + " " + ((2/3)*sH) + " " + ((2/3)*tW) + " " + ((2/3)*tH) + " -showOutput");
		rename("registeredFrame");
		if(i==1) {
			run("Duplicate...","title=Output");
			selectWindow("registeredFrame");
			close();
		} else {
			run("Duplicate...", "title=datFrame"); //Necessary because the output of Turbo Reg, only want data frame, not mask.
			run("Concatenate...", "stack1=Output stack2=datFrame title=Output");
	//Registered stack title is output
			selectImage("registeredFrame");
			close();
		}
		//Close the frame that was getting registered
		selectImage("currentFrame");
		close();
		}
	run("Clear Results");
	selectWindow("Refined Landmarks");
	run("Close");
	selectWindow("Log");
	run("Close");
	//Batch mode exited and output is drawn.
	setBatchMode("exit"); 
	run("Z Project...", "projection=Median");
	run("8-bit");
	
}

macro "reslice" {
	run("Reslice [/]...", "output=1.000 start=Top avoid");
	run("Z Project...", "projection=Median");

}

macro "contrast reset oct [c]" {
	run("Clear Results");
	setSlice(1);
	numSlices = nSlices();
	setBatchMode(true);
		mean_old=-1;
		for(i=1;i<=numSlices;i++) {
			setSlice(i);
			run("Measure");
			mean_new = getResult("Mean", i-1);
			if(mean_new>mean_old) {
				mean_old = mean_new;
				max_frame = i;
			} else {
				//continue
			}
			if(max_frame+100<i) {
				//if there is no increase of mean for 100 slices, quit loop
				i = numSlices;
			} else {
				//do nothin
			}
		}
	setBatchMode("exit");
	setSlice(max_frame);
	resetMinAndMax();
}

macro "enface oct avg [v]" {
	resetMinAndMax();
	run("Slice Keeper");
	run("Grouped Z Project...", "projection=[Average Intensity] group=9");
	//copied from rename macro
	name=getTitle;
	Dialog.create("Input New Name");
	Dialog.addMessage("Input New Image Name - Make sure Image to be renamed was selected when you ran this macro!")
	Dialog.addString("Name:  ", name);
	Dialog.show();
	Name = Dialog.getString();
	rename(Name);
	saveAs();
}

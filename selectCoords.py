from Tkinter import *
from time import gmtime, strftime
import cv2
import argparse
import tkFileDialog
from PIL import Image, ImageTk
import tkSimpleDialog
import tkMessageBox
import os
import ttk

rootfilename = None
filename = None
jpgname = None
classdir = None
classjpg = None
prevclassjpg = None
prevcaptionStr = None
root = None
jsonFileExists = False
jsonFile = ""
newImage = False
#labelF = None
textEntry = None
mainmenu = {}
mainmenuvariable = {}
readyState = False
captionStr = []


levelonemenu = []
leveltwomenu = []
levelthreemenu = []
levelfourmenu = []
levelonevariable = []
leveltwovariable = []
levelthreevariable = []
levelfourvariable = []

newcaptionfile = open("test_caption_new.txt", 'w')
newimagefile = open("test_image_new.txt", 'w')

root = Tk()
features = []

gmb = None #Menubutton (root, text="Select features", relief=RAISED)

x=[]
for i in range(150):
    x1=[]
    for j in range(150):
	x1.append(0)
    x.append(x1)

root.geometry("850x500")
root.configure(bg="lightblue")

x0 = 0
y0 = 0

answer = False
ans = False
DoneFeatures = False

selectedFeatures = ""

def open_txt(t_file):
  os.system('pwd')
  f = open(t_file, 'r')
  txt_file = f.readlines()
  return [t.strip() for t in txt_file]

def init_proc():
	global x, x0, y0, answer, ans, DoneFeatures, selectedFeatures, readlines, captionStr
	x0 = 0
	y0 = 0

	x=[]
	for i in range(150):
	    x1=[]
	    for j in range(150):
		x1.append(0)
	    x.append(x1)

	answer = False
	ans = False
	DoneFeatures = False

	selectedFeatures = ""
	readyState = False
	captionStr = []


def check_heatmap(hm_img, i, j, i1 , j1,x):
    print ("i j: ", i,j)
    if(x[i][j]==0):
        x[i][j]=1
        if hm_img[i][j] > 0 and hm_img[i][j]<255:
            if j!=226:
                if hm_img[i][j +1] <1 or hm_img[i][j+1]==255:
                    hm_img[i][j +1]=255
                elif not (i==i1 and j+1==j1):
                    check_heatmap(hm_img, i, j + 1,i,j,x)

            if i!=226:
                if hm_img[i+1][j] <1 or hm_img[i+1][j]==255:
                    hm_img[i+1][j] = 255
                elif not (i+1==i1 and j==j1):
                    check_heatmap(hm_img, i + 1, j,i,j,x)

            if j!=0:
                if hm_img[i][j - 1] <1 or hm_img[i][j-1]==255:
                    hm_img[i][j-1] = 255
                elif not (i==i1 and j-1==j1):
                    check_heatmap(hm_img, i, j-1,i,j,x)

            if i!=0:
                if hm_img[i-1][j] <1 or hm_img[i-1][j]==255:
                    hm_img[i-1][j] = 255
                elif not (i-1==i1 and j==j1):
                    check_heatmap(hm_img, i-1, j,i,j,x)
    return hm_img

def get_heatmap():
	global x, jpgname,classjpg, rootfilename

	#print "path is : ", HEATMAP_PATH+jpgname+"_heatmap.png"
	#l = cv2.imread(HEATMAP_PATH+jpgname+"_heatmap.png", cv2.IMREAD_GRAYSCALE)
        print ("rootfilename: ", rootfilename)
	l = cv2.imread(rootfilename, cv2.IMREAD_GRAYSCALE)

	cv2.imwrite("heatmap_temp.png", l)

def overlay_image():
	global jpgname, classjpg
	output = cv2.imread("heatmap_temp.png")
	overlayimage = cv2.cvtColor(cv2.imread(HEATMAP_PATH+jpgname+"_as_inputted_into_the_dnn.png", cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
	cv2.addWeighted(overlayimage, 0.9, output, 0.9, 0, output)

	cv2.imwrite("heatmap_image_overlay.jpg", output)

def update_caption(eventtype):
	global selectedFeatures, textEntry
	#print selectedFeatures
	if textEntry is not None:
			selectedFeatures = textEntry.get(1.0, END)
	#print selectedFeatures
	#print "selected features: ", selectedFeatures

def create_json(captionString):

	# 'CAPTION' Remove below lines to store captions in single file after close
        global jsonFileExists, filename, classjpg, jsonFile, newimagefile, newcaptionfile, prevclassjpg, prevcaptionStr
	#print "in create json"

	if prevclassjpg == filename:
		prevcaptionStr = captionString
	else:
		newimagefile.close()
		newcaptionfile.close()
		prevclassjpg = classjpg
		prevcaptionStr = captionString
		newcaptionfile = open("test_caption_new.txt", 'a')
		newimagefile = open("test_image_new.txt", 'a')
		newimagefile.write(prevclassjpg+'\n')
		newcaptionfile.write(prevcaptionStr+'\n')


	currentTime = strftime("%Y-%m-%d%H:%M:%S", gmtime())

	captionjsonFile = "captions"+"_"+currentTime+".json"
	imagejsonFile = "images"+"_"+currentTime+".json"

	os.system('cp test_caption_new.txt '+captionjsonFile)
	os.system('cp test_image_new.txt '+imagejsonFile)


def freeze_features():
	global DoneFeatures, textEntry, selectedFeatures

	DoneFeatures = True

	if textEntry is not None:
			root.unbind("<Double-Button-1>")
	create_json(selectedFeatures)

def process_image():

	global jpgname, classdir, classjpg, labelF, newImage, selectedFeatures, textEntry, rootfilename, filename
	global readyState, gmb
	root.unbind("<Button 1>")

	if textEntry is not None:
		create_json(selectedFeatures)
		textEntry.destroy()
		textEntry = None

	init_proc()

	if gmb is not None:
		gmb = None

	rootfilename = tkFileDialog.askopenfilename(parent=root, initialdir=HEATMAP_PATH, title='Select an heatmap image', filetypes=[("heatmap files", "*.*")])
	print(rootfilename)
        filename = rootfilename.split('/')[-1]
	classdir = rootfilename.split('/')[-2]
	classjpg = classdir+"/"+filename

	get_heatmap()

        answer = True
    	if answer == True:
		os.system('cp '+rootfilename+" heatmap.png")

		image = cv2.cvtColor(cv2.imread("./heatmap.png", cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
	else:
		image = cv2.imread("./heatmap_image_overlay.jpg", cv2.IMREAD_COLOR)

	img = cv2.resize(image,(500,500))
	img = Image.fromarray(img)
	img = ImageTk.PhotoImage(img)
	panelA = Label(image=img)
	panelA.image = img
	panelA.place(x=0,y=0)

	labelD = Label(text="                                  Instructions                                   \n", fg="red", bg="lightblue", borderwidth=3, relief='solid', justify="left", font=("Helvetica 10 bold italic"))

	labelD.place(x=500,y=0, anchor='nw')

	labelE = Label(text="1. Double click on region of the object to define features\n2. Press button <Save> to save selected features\n3. Press button <Next> to save and continue with new image\n4. Press button <Close> to save and close application", font=("Helvetica", 10), fg="blue", bg="lightblue", borderwidth=3, relief='solid', justify="left")

	labelE.place(x=500,y=25, anchor='nw')

	labelk = Label(text="Heatmap of "+filename, font=("Helvetica", 10), fg="blue", bg="lightblue", relief='solid', justify="left")

	labelk.place(x=500,y=120, anchor='nw')

	labelG = Label(text="           The ExAI Caption          \n             Edit Tool        ", font=("Helvetica 20 bold italic"), fg="red", bg="lightblue", borderwidth=3, relief='groove')

	labelG.place(x=500,y=400, anchor="nw")


	btn = Button(root, text='Save', font=("Helvetica 10 bold"), command=freeze_features)
	btn.place(x=100, y=450, anchor="ne")

	btn = Button(root, text='Next', font=("Helvetica 10 bold"), command=process_image)
	btn.place(x=100+350, y=450, anchor="ne")


	contbtn = Button(root, text='Close', font=("Helvetica 10 bold"), command=close_proc)
	contbtn.place(x=500+350, y=450, anchor="ne")
	readyState = True

	root.bind("<Double-Button-1>", getorigin)

def close_proc():
	global selectedFeatures

	create_json(selectedFeatures)

	newimagefile.close()
	newcaptionfile.close()

	os.system('python2 number_preprocess.py --splits train')

	currentTime = strftime("%Y-%m-%d%H:%M:%S", gmtime())

	jsonFile = "captions"+"_"+currentTime+".json"
	os.system('cp descriptions.json '+jsonFile)

    	tkMessageBox.showinfo("Information","The captions are saved in "+jsonFile+" \n")
	sys.exit(0)

def define_features():
	global selectedFeatures, textEntry, captionStr, topmenu, mainmenu

	currentFeatures = ""
	print "caption str is : ", captionStr
	for menupath in captionStr:
		if len(menupath) == 2:
			topmenunum = int(menupath[0])
			l1num = int(menupath[1])
			currentFeatures = currentFeatures+' and ' if currentFeatures != "" else ""
			currentFeatures = currentFeatures + \
				mainmenu[topmenunum][0][0].entrycget(l1num+1, "label")
		if len(menupath) == 3:
			topmenunum = int(menupath[0])
			l1num = int(menupath[1])
			l2num = int(menupath[2])
			currentFeatures = currentFeatures+' and ' if currentFeatures != "" else ""
			currentFeatures = currentFeatures + \
				mainmenu[topmenunum][1][l1num].entrycget(l2num+1, "label") \
				+ " " + mainmenu[topmenunum][0][0].entrycget(l1num+1, "label")
		if len(menupath) == 4:
			topmenunum = int(menupath[0])
			l1num = int(menupath[1])
			l2num = int(menupath[2])
			l3num = int(menupath[3])
			currentFeatures = currentFeatures+' and ' if currentFeatures != "" else ""
			currentFeatures = currentFeatures + \
				mainmenu[topmenunum][2][l2num].entrycget(l3num+1, "label") + " " + \
				mainmenu[topmenunum][1][l1num].entrycget(l2num+1, "label") \
				+ " " + mainmenu[topmenunum][0][0].entrycget(l1num+1, "label") \
				+ " " + topmenu.entrycget(topmenunum+1, "label")

	selectedFeatures = "This image has "+currentFeatures+"."

	labelF = Label(text="                              The Caption                                  ", font=("Helvetica bold", 12), fg="yellow", bg="blue")
	#rahul#
	#labelF.place(x=900,y=180)
	labelF.place(x=500,y=180)
	if textEntry is None:
		textEntry = Text(root, width=39, height=5, font=('Helvetica 12 italic'), wrap="word")

	textString = textEntry.get(1.0, END)
	if textString != "":
		textEntry.delete(1.0, END)
	textEntry.insert(INSERT, selectedFeatures)
	textEntry.pack()

	textEntry.place(x=500, y=200)


def update_l1Variable(length, menupath):
	global mainmenu, topmenu, captionStr

	if mainmenuvariable[int(menupath[0])][0][length].get() == 1:
		captionStr.append(menupath)
	else:
		captionStr.remove(menupath)
	define_features()


def update_l2Variable(length, menupath):
	global mainmenu, topmenu, captionStr

	if mainmenuvariable[int(menupath[0])][1][length].get() == 1:
		captionStr.append(menupath)
	else:
		captionStr.remove(menupath)
	define_features()

def update_l3Variable(length, menupath):
	global mainmenu, topmenu, captionStr

	if mainmenuvariable[int(menupath[0])][2][length].get() == 1:
		captionStr.append(menupath)
	else:
		captionStr.remove(menupath)
	define_features()

# Determine the origin by clicking
def getorigin(eventorigin):
    global x0, y0, answer, gmb, selectedFeatures
    global mainmenu, topmenu, levelonemenu, levelonevariable, leveltwomenu, leveltwovariable, \
			levelthreevariable, levelthreemenu, levelfourmenu, levelfourvariable

    if gmb is not None:
	doneButton = Button(root, text="Done", font=("Helvetica 10"), bg="green")
	doneButton.place(x=x0, y=y0, anchor="ne")

    x0 = eventorigin.x
    y0 = eventorigin.y

    if gmb is not None:
    	gmb.place(x=x0, y=y0, anchor="ne")

    mb = gmb
    answer = tkMessageBox.askyesno("Question","Do you want to continue with this region to define feature?\n")
    if answer == True and gmb is None:
	mb=  Menubutton (root, text="Select features", relief=RAISED)
	gmb = mb

	menufile = open('menu.txt', 'r')

	menulist = menufile.readlines()
	menulist = [tbuffer.split('\n')[0] for tbuffer in menulist]


	menuptr = 0
	topmenu = Menu(mb, name="topmenu")

	totallevelonemenus = int(menulist[menuptr])
	if totallevelonemenus == 0:
		return

	menuptr = menuptr + 1
	for l1num_new in range(totallevelonemenus):
		mainmenu.update({l1num_new:[]})
		mainmenuvariable.update({l1num_new:[]})

		l1num = 0
		leveltwocount = 0
		leveltwolength = 0

		levelonemenu = []
		levelonevariable = []
		leveltwomenu = []
		leveltwovariable = []
		levelthreemenu = []
		levelfourmenu = []
		levelthreevariable = []
		levelfourvariable = []
		levelonemenu.append(Menu(topmenu, name=menulist[menuptr]))
		menuptr = menuptr + 1
		totalleveltwomenus = int(menulist[menuptr])
		if totalleveltwomenus == 0:
			print "totalleveltwomenus: ", totalleveltwomenus
			topmenu.add_cascade(label=menulist[menuptr-1], menu=levelonemenu[l1num])
			menuptr = menuptr + 1
			print menulist[menuptr]
			for i in range(int(menulist[menuptr])):
				levelonevariable.append(IntVar())
			for ele in range(int(menulist[menuptr])):
				print "ele: ",ele
				menuptr = menuptr + 1
				print menulist[menuptr]
				length = leveltwolength + ele
				print "length: ", length
				levelonemenu[l1num].add_checkbutton(label=menulist[menuptr], \
					variable=levelonevariable[length], \
					command=lambda length=length, l1num_new=l1num_new, ele=ele: update_l1Variable(length, str(l1num_new)+str(ele)))
			leveltwocount = leveltwocount + 1
			leveltwolength = leveltwocount*len(levelonevariable)
			menuptr = menuptr + 1

			# Chandra
			mainmenu[l1num_new].append(levelonemenu)
			mainmenuvariable[l1num_new].append(levelonevariable)
			continue
		topmenu.add_cascade(label=menulist[menuptr-1], menu=levelonemenu[l1num])
		menuptr = menuptr + 1
		#print menulist[menuptr]
		levelthreecount = 0
		levelthreelength = 0
		for l2num in range(totalleveltwomenus):
			leveltwomenu.append(Menu(levelonemenu[l1num], name=menulist[menuptr]))
			menuptr = menuptr + 1
			totallevelthreemenus = int(menulist[menuptr])
			if totallevelthreemenus == 0:
				levelonemenu[l1num].add_cascade(label=menulist[menuptr-1], \
					menu=leveltwomenu[l2num])
				menuptr = menuptr + 1
				for i in range(int(menulist[menuptr])):
					leveltwovariable.append(IntVar())
				for ele in range(int(menulist[menuptr])):
					menuptr = menuptr + 1
					length = levelthreelength + ele
					leveltwomenu[l2num].add_checkbutton(label=menulist[menuptr], \
						variable=leveltwovariable[length], \
						command=lambda length=length, l1num_new=l1num_new, l2num=l2num, ele=ele: \
						update_l2Variable(length, str(l1num_new)+str(l2num)+str(ele)))
				levelthreecount = levelthreecount + 1
				levelthreelength = levelthreecount*len(leveltwovariable)
				menuptr = menuptr + 1
				mainmenu[l1num_new].append(leveltwomenu)
				mainmenuvariable[l1num_new].append(leveltwovariable)
				continue
			levelonemenu[l1num].add_cascade(label=menulist[menuptr-1], \
				menu=leveltwomenu[l2num])
			menuptr = menuptr + 1
			levelfourcount = 0
			levelfourlength = 0
			for l3num in range(totallevelthreemenus):
				levelthreemenu.append(Menu(leveltwomenu[l2num], name=menulist[menuptr]))
				menuptr = menuptr + 1
				totallevelfourmenus = int(menulist[menuptr])
				if totallevelfourmenus == 0:
					leveltwomenu[l2num].add_cascade(label=menulist[menuptr-1], \
						menu=levelthreemenu[l3num])
					menuptr = menuptr + 1
					for i in range(int(menulist[menuptr])):
						levelthreevariable.append(IntVar())
					for ele in range(int(menulist[menuptr])):
						menuptr = menuptr + 1
						length = levelfourlength + ele
						levelthreemenu[l3num].add_checkbutton(label= menulist[menuptr], \
							variable=levelthreevariable[length], \
							command=lambda l1num_new=l1num_new, l2num=l2num, l3num=l3num, \
							ele=ele, length=length: update_l3Variable(length,  str(l1num_new)+str(l2num)+str(l3num)+str(ele)))
					levelfourcount = levelfourcount + 1
					levelfourlength = levelfourcount*len(levelthreevariable)
					menuptr = menuptr + 1
					mainmenu[l1num_new].append(levelthreemenu)
					mainmenu[l1num_new].append(levelfourmenu)
					mainmenuvariable[l1num_new].append(levelthreevariable)
					mainmenuvariable[l1num_new].append(levelfourvariable)
					continue
				leveltwomenu[l2num].add_cascade(label=menulist[menuptr-1], \
					menu=levelthreemenu[l3num])
				menuptr = menuptr + 1
    mb.pack()
    mb.place_configure(x=x0, y=y0)
    #mb["menu"] =  featuremenu
    mb["menu"] =  topmenu
    root.unbind("<Button 1>")

    gmb = mb

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--heatmap_path", type=str, default=None)
#parser.add_argument("--splits", type=str, default=None)
#parser.add_argument("--generate", type=str, default='gen_json')

    args = parser.parse_args()

    if args.heatmap_path == None:
        print ("Enter the heatmap image dir path as an argument\n")
    else:
        print ("heatmap path: ", args.heatmap_path)
        HEATMAP_PATH = args.heatmap_path

        process_image()

        root.mainloop()

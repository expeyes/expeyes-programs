'''
MicroHOPE IDE program, a tkinter text widget with File I/O, Compile and Upload options  
author : Ajith Kumar B.P., ajith@iuac.res.in  
Licence : GPL version 3
Date: 21-Oct-2013
last edit : 6-Dec-2013
'''

from Tkinter import *
import tkMessageBox
from tkFileDialog import *
import commands, subprocess
   
import gettext
gettext.bindtextdomain('expeyes')
gettext.textdomain('expeyes')
_ = gettext.gettext

# Global variables   
filename = ''  			 # Currently active file
device   = ''            # User should choose this from the list
mcu = 'atmega32'		 # mcu  

file_opt = {'defaultextension':'.c', 'initialdir':'~/microhope',\
		'filetypes': [(_('C files'), '.c'), (_('text files'), '.txt'),(_('All files'), '.*')]}

credentials=_("microHOPE IDE\n\n(c) 2013-2014 Ajith Kumar\n\nThis program is free software, it is available under the license GPL-3; on Debian systems, please see the file /usr/share/common-licenses/GPL-3\n\nTranslations:\n(FR) (c) 2014 Georges Khaznadar")

def show(s, col='blue'):
	Res.config(text =s, fg=col)
	Res.update()
	
def show_status():	
	global filename, device
	f = filename
	d = device
	if filename == '': f = _('Not Selected')
	if device == '': d = _('Not Selected')
	root.title(_('MicroHOPE: File->%s : Device-> %s') %(f, d))
	show(_('File->%s : Device-> %s') %(f, d))

def newFile():
	global filename
	tw.delete(0.0, END)	
	mw.delete(0.0, END)
	filename = ''

def saveAs():
	global filename
	f = asksaveasfile(mode='w', **file_opt)
	if f == None: return
	text = tw.get(0.0, END).rstrip() # contents of the text widget, no trailing whitespaces
	f.write(text + '\n')
	filename = f.name
	show_status()
	
def saveFile():
	global filename
	if filename == '':
		saveAs()
		return
	f = open(filename, 'w')
	text = tw.get(0.0, END).rstrip() # contents of the text widget, no trailing whitespaces
	f.write(text + '\n')
	show(_('File Saved'))

def openFile():
	global filename
	f = askopenfile(mode='r', **file_opt)
	if f == None: return
	data = f.read() 			# Get all the text from file.
	tw.delete(0.0, END)
	tw.insert(0.0, data)    
   	filename = f.name
	show_status()
	mw.delete(0.0, END)
	
def Compile():
	if filename == '' :
		show(_('No file selected'), 'red')
		return
	saveFile()
	fname = filename.split(".")[0]
	cmd = 'avr-gcc -Wall -O2 -mmcu=%s -o %s %s.c' %(mcu,fname,fname)
	res = commands.getstatusoutput(cmd)
	if res[0] != 0:
		show(_('Compilation Error'),'red')
		mw.insert(END, res[1])
		return
	cmd = 'avr-objcopy -j .text -j .data -O ihex %s %s.hex' %(fname,fname)
	res = commands.getstatusoutput(cmd)
	mw.insert(END, res[1])
	show(_('Compilation Done'))

def pulseRTS(dev):
	import serial, time
	fd = serial.Serial(dev, 38400, stopbits=1, timeout = 1.0)
	fd.setRTS(0)
	fd.setRTS(1)
	fd.setRTS(0)
	fd.close()
	
def Upload():
	global device
	if device == None:
		show(_('Hardware device not selected'),'red')
		return
	pulseRTS(device)               # Sending a pulse on RTS pin to reset the uC
	show(_('Starting Upload....'))
	fname = filename.split(".")[0]
	cmd= 'avrdude -b 19200 -P %s -pm32 -c stk500v1 -U flash:w:%s.hex'%(device, fname)
	res = commands.getstatusoutput(cmd)
	mw.insert(END, res[1])
	if res[0] != 0:
		show(_('Upload Error: Try pressing nicroHOPE Reset button just before Uploading'))
		return
	show(_('Upload Completed'))
	   
def upload_usbasp():
	if filename == '' :
		show(_('No file selected'), 'red')
		return
	show(_('Starting Upload via USBASP....'))
	fname = filename.split(".")[0]
	cmd= 'avrdude -c usbasp -patmega32 -U flash:w:%s.hex'%(fname)
	print cmd
	res = commands.getstatusoutput(cmd)
	if res[0] != 0:
		show(_('Upload Error: Make use USBASP programmer is connected'), 'red')
		return
	mw.insert(END, res[1])	
	show(_('Upload Completed'))
	
def set_device(d):
	global device
	device = d
	show_status()
		   
def select_device(event):
	cmd = "ls /dev/ttyUSB*"         # search for MCP2200 type
	res = commands.getstatusoutput(cmd)   # get the device name, mostly on USB0
	devs = []
	if res[0] == 0:
		devs = res[1].split('\n')
	cmd = "ls /dev/ttyACM*"			# search for FT232 type
	res = commands.getstatusoutput(cmd)   # get the device name, mostly on USB0
	if res[0] == 0:
		devs += res[1].split('\n')
	print devs
	if devs == []:
		show(_('microHOPE hardware not found?'), 'red')
		return
	popup = Menu(root, tearoff=0)
	for k in devs:
		popup.add_command(label=k , command= lambda dev=k :set_device(dev))
	# display the popup menu
	try:
		popup.tk_popup(event.x_root,event.y_root, 0)
	finally:
		popup.grab_release()

def about():
	tkMessageBox.showinfo(_("About ..."), credentials)
	return

def documentation():
	docfile="/usr/share/microhope/doc/microhope-en.pdf"
	loc=subprocess.Popen("locale | sed -n 's/LANG=\\(.*\\)$/\\1/ p'", shell=True, stdout=subprocess.PIPE).communicate()[0][:2]
	# assert (loc in ['fr', 'en'])
	# !! here there should be some localization system !!
	loc='en'
	# there is only one locale available now
	subprocess.call("(evince %s)" %docfile, shell=True)
	return

def hints():
	tkMessageBox.showinfo(_("Hints"), _("You may need to build the directory ~/microhope with the command 'create-microhope-env'. See 'man create-microhope-env'."))

root = Tk()
root.minsize(width=500,height=200)
                   
# Set up basic Menu
menubar = Menu(root)

filemenu = Menu(menubar,tearoff=0,font=('Monospace', 12))
filemenu.add_command(label=_("New File"), command=newFile, accelerator="Ctrl+N")
filemenu.add_command(label=_("Open"), command=openFile, accelerator="Ctrl+O")
filemenu.add_command(label=_("Save"), command=saveFile, accelerator="Ctrl+s")
filemenu.add_command(label=_("Save As"), command=saveAs, accelerator="Ctrl+Shift+S")
filemenu.add_separator()
filemenu.add_command(label=_("Upload using USBASP"), command = upload_usbasp)

menubar.add_cascade(label=_("File"), menu=filemenu,font=('Monospace', 12))
root.config(menu=menubar)

menubar.add_command(label=_('Compile'), command=Compile, font=('Monospace', 12))
menubar.add_command(label=_('Upload'),  command=Upload, font=('Monospace', 12))

menubar.add_separator()
helpmenu = Menu(menubar,tearoff=0,font=('Monospace', 12))
helpmenu.add_command(label=_("About ..."), command=about)
helpmenu.add_command(label=_("Documentation"), command=documentation)
helpmenu.add_command(label=_("Hints"), command=hints)
menubar.add_cascade(label=_("Help"), menu=helpmenu,font=('Monospace', 12))

# Top Frame and scrollable editor text widget inside that
top = Frame(root)
top.pack(side=TOP, expand=YES, fill=BOTH)
sb1 = Scrollbar(top)
sb1.pack(side=RIGHT, fill=BOTH)
tw = Text(top, height= 22, font=('Monospace', 11), bg='ivory', yscrollcommand=sb1.set)
tw.pack(expand=YES, fill=BOTH) 
sb1.config(command=tw.yview)
tw.bind("<Button-3>", select_device)

Res = Label(root, fg = 'blue')
Res.pack(side=TOP, expand=NO, fill=X)

bot = Frame(root)
bot.pack(side=TOP, expand=YES, fill=BOTH)
sb2 = Scrollbar(bot)
sb2.pack(side=RIGHT, fill=Y)
mw = Text(bot, height = 7, yscrollcommand=sb2.set, bg='black', fg='white')
mw.pack(side = TOP, expand=YES, fill=BOTH)
sb2.config(command=mw.yview)

show_status()
root.mainloop()


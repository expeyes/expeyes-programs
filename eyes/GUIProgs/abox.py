from tkinter import *
import Image, ImageTk, ImageDraw, sys, math
import phm, time
import phmath
from abdisp import *


WIDTH = 600
HEIGHT = 300
NP = 400
delay = 15
dac = 2000
data = None
fftdata = None
fitted = None
col = 'black'
#col = ['black', 'red', 'green', 'cyan']

def getpar():
    global NP, delay
    NP = int(Npoints.get())
    delay = int(Delay.get())
    p.select_adc(1)

    
def clear():
    global data
    data = None
    mainwin.delete_lines()      

def save():
    global data
    p.save_data(data, 'data.dat')

#------------------------------- Fitting ------------------
def save_fit():
    global fitted
    p.save_data(fitted[0], 'fit.dat')
    
def do_fit():
    global fitted, data
    if data == None : 
        msg.config(text='No Data Present')
        return
    fitted = phmath.fit_sine(data)
    par = fitted[1]
    other = Toplevel()
    other.title('Curve Fitting Window')
    fitwin = disp(other, WIDTH, HEIGHT,'white')
    fitwin.setWorld(0,-5000,data[-1][0],5000)
    f = Frame(other)
    f.pack()
    ss = 'A = %4.1f mV | F = %4.1f Hz |  ph = %4.1f rad | Offset = %4.1f mV'\
        %(par[0], par[1]*1.0e6, par[2], par[3])
    l1 = Label(f,text=ss)
    l1.pack(side=LEFT)
    b1 = Button(f,text = 'Save',command = save_fit)
    b1.pack(side=LEFT)
    
    x = []
    y1 = []
    y2 = []
    for k in fitted[0]:
      y1.append((k[0],k[1]))
      y2.append((k[0],k[2]))
    fitwin.line(y1,'black')
    fitwin.line(y2,'red')

def capture_ch0():
    global data, NP, delay
    getpar()
    p.select_adc(0)
    data = p.read_block(NP, delay, 1)
    if data == None: return
    mainwin.auto_scale(data)
#    mainwin.setWorld(0,-5000, data[-1][0], 5000)
    mainwin.mark_axes(xlab='usecs', ylab='mV')
    y = []
    for k in data:
      y.append((k[0],k[1]))
    mainwin.line(y,'black')

def capture_ch1():
    global data, NP, delay
    getpar()
    p.select_adc(1)
    data = p.read_block(NP, delay, 1)
    if data == None: return
    mainwin.auto_scale(data)
#    mainwin.setWorld(0,-5000,data[-1][0],5000)
    mainwin.mark_axes(xlab='usecs', ylab='mV')
    y = []
    for k in data:
      y.append((k[0],k[1]))
    mainwin.line(y,'black')
        
def capture_both():
    global data, NP, delay
    getpar()
    for k in range(4): p.del_channel(k)
    p.add_channel(0)
    p.add_channel(1)
    data = p.multi_read_block(NP, delay, 1)
    if data == None: return
    mainwin.auto_scale(data)
#    mainwin.setWorld(0,-5000,data[-1][0],5000)
    mainwin.mark_axes(xlab='usecs', ylab='mV', numchans=2)
    y1 = []
    y2 = []
    for k in data:
      y1.append((k[0],k[1]))
      y2.append((k[0],k[2]))
    mainwin.line(y1,'green')
    mainwin.line(y2,'red')

#---------------------------------- FFT ---------------------------
def save_fft():
    global fftdata
    p.save_data(fftdata, 'fft.dat')

fftwin = None    
def zoom_fft():
    global fftwin
    fftwin.zoom()

def reset_fft():
    global fftwin, fftdata
    fftwin.auto_scale(fftdata)
    fftwin.mark_axes(xlab='Hz', ylab='N')

def do_fft():
    global data, fftdata, fftwin
    if data == None : return
    fftdata = phmath.fft(data)
    xmin = fftdata[0][0]
    xmax = fftdata[-1][0]
    ymin = 0.0
    ymax = 0.0
    for k in range(len(fftdata)):
        if fftdata[k][1] > ymax: ymax = fftdata[k][1]
        if fftdata[k][1] < ymin: ymin = fftdata[k][1]

    other = Toplevel()
    other.title('Fourier Transform Window')
    fftwin = disp(other, WIDTH, HEIGHT,'white')
    fftwin.auto_scale(fftdata)
    fftwin.mark_axes(xlab='Hz', ylab='N')
    f = Frame(other)
    f.pack()
    b1 = Button(f,text = 'Save FFT',command = save_fft)
    b1.pack(side=LEFT)
    b1 = Button(f,text = 'Zoom',command = zoom_fft)
    b1.pack(side=LEFT)
    b1 = Button(f,text = 'Reset',command = reset_fft)
    b1.pack(side=LEFT)
    x = []
    y = []
    fftwin.delete_lines()
    for k in fftdata:
      y.append((k[0],k[1]))
    fftwin.line(y,'red')
    
def set_pwg_dac():
    opt = option.get()
    dac = int(DAC.get())
    if opt == 0:
        p.set_frequency(dac)
    else:
        if dac > 5000: dac = 5000
        p.set_voltage(dac)

def pwg_dac():
    options = ['PWG','DAC']
    units = ['Hz', 'mV']
    opt = option.get()
    Option.configure(text = options[opt])
    Unit.configure(text = units[opt])
    
p=phm.phm()
p.set_voltage(1500)
p.set_adc_size(1)

root = Tk()
mainwin = disp(root, WIDTH, HEIGHT,'white')
f = Frame(root)
f.pack(side=TOP)

f1 = Frame(f)
f1.pack(side=TOP)

l = Label(f1, text = 'Number of Samples =')
l.pack(side=LEFT)
Npoints = StringVar()
t=Entry(f1, width=5, bg = 'white', textvariable = Npoints)
t.pack(side=LEFT, anchor = S)
Npoints.set('400')

l = Label(f1, text = 'Delay between samples=')
l.pack(side=LEFT)
Delay = StringVar()
t=Entry(f1, width=5, bg = 'white', textvariable = Delay)
t.pack(side=LEFT, anchor = S)
Delay.set('20')

option = IntVar()
Option=Checkbutton(f1,text='PWG/DAC', underline = 4 , \
      variable = option, command = pwg_dac)
Option.pack(side=LEFT, anchor = S)

DAC = StringVar()
t=Entry(f1, width=5, bg = 'white', textvariable = DAC)
t.pack(side=LEFT, anchor = S)
DAC.set('2000')
Unit = Label(f1, width = 3, text = 'Hz')
Unit.pack(side=LEFT)
Apply = Button(f1,text = 'Set',command = set_pwg_dac)
Apply.pack(side=LEFT)

f2 = Frame(root)
f2.pack(side=TOP)

b1 = Button(f2,text = 'CH0',command = capture_ch0)
b1.pack(side=LEFT)
b2 = Button(f2,text = 'CH1',command = capture_ch1)
b2.pack(side=LEFT)
b3 = Button(f2,text = 'Both',command = capture_both)
b3.pack(side=LEFT)
b3 = Button(f2,text = 'Save',command = save)
b3.pack(side=LEFT)
b4 = Button(f2,text = 'FFT',command = do_fft)
b4.pack(side=LEFT)
b4 = Button(f2,text = 'lsq Fit',command = do_fit)
b4.pack(side=LEFT)
b4 = Button(f2,text = 'Clear',command = clear)
b4.pack(side=LEFT)

msgframe = Frame(root)
msgframe.pack(side=TOP,fill=BOTH)
msg = Label(msgframe, bg='yellow',text = 'Waveform capture and analysis')
msg.pack(side=TOP,fill=BOTH)

root.mainloop()

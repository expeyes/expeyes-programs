'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import time, sys, numpy, shelve, tempfile, subprocess, os
if sys.version_info.major==3:
        from tkinter import *
else:
        from Tkinter import *

sys.path=[".."] + sys.path

import expeyes.eyesj as eyes
import expeyes.eyeplot as eyeplot
import expeyes.eyemath as eyemath


import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext


TIMER = 100
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height

NP = 400
tg = 20
fmin = 2500.0
freq = fmin
fmax = 5000.0
vpeak = 0            # Assume as 0
fpeak = fmin
history = []        # Data store
trial = 0            # trial number
data = [ [], [] ]    # Current & Voltage
index = 0
running = False

def start():
    global running, NP, freq, fmin, data, index
    running = True
    data = [ [], [] ]
    index = 0
    freq = fmin
    ph.set_sqr1(fmin)
    root.after(10,update)

def update():                    # Called periodically by the Tk toolkit
    global running, NP, tg, freq, fmax, fpeak, vpeak, history, data, index, trial
    if running == False:
        return
    fr = ph.set_sqr1(freq)
    freq += 20
    t,v = ph.capture_hr(1, NP, tg)
    rmsv = ph.rms(v)
    data[0].append(fr)
    data[1].append(rmsv)
    if rmsv > vpeak:
        vpeak = rmsv
        fpeak = fr
    if fr > fmax:
        running = False
        history.append(data)
        trial += 1
        g.delete_lines()
        for k in range(len(history)):
            g.line(history[k][0], history[k][1], k)
        vmax = max(data[1])
        R.config(text='Fo = %5.0f Hz'%fpeak)
        ph.set_sqr1(0)
        return

    if index > 1:            # Draw the line
        g.delete_lines()
        g.line(data[0], data[1], trial)
    index += 1
    root.after(TIMER, update)

def plotdata(pref="qtiplot"):        # Send the data to XmGrace or QtiPlot
    """
    sends the data to a plotter/analyser with many features
    @param pref the preferred program, defaults to qtiplot
    """
    global history
    if pref=="qtiplot":
        #print len(history)
        for dat in history:
            tmpfile=tempfile.NamedTemporaryFile(prefix="tmpExpEYES")
            name=tmpfile.name
            tmpfile.close()
            d = shelve.open(name,"c")
            d["title"]=_('Frequency response curve').decode('utf8').encode('latin1')
            d["xlabel"]=_('Frequency').decode('utf8').encode('latin1')
            d["ylabel"]=_('Amplitude').decode('utf8').encode('latin1')
            d["data"]=[dat[0],dat[1]]
            d.close()
            cmd="EXPEYES_SHELVE=%s qtiplot -x /usr/share/expeyes/eyes-junior/expeyes2qtiplot.py &" % name
            subprocess.call(cmd, shell=True)
    else:
        try:
            import pygrace
        except:
            return
            global pg
        pg = pygrace.grace()
        for dat in history:
            pg.plot(dat[0],dat[1])
            pg.hold(1)            # Do not erase the old data
        pg.xlabel(_('Frequency'))
        pg.ylabel(_('Amplitude'))
        pg.title(_('Frequency response curve'))

def save():
    global history, running
    if running == True:
        return
    s = e1.get()
    if s == '':
        return
    f = open(s, 'w')
    for dat in history:
        for k in range(len(dat[0])):
            f.write('%5.3f  %5.3f\n'%(dat[0][k], dat[1][k]))
        f.write('\n')
    f.close()
    msg.config(text = _('Data saved to file ')+s)

def clear():
    global history, trial, running
    if running == True:
        return
    g.delete_lines()
    history = []
    trial = 0

def quit():
    ph.set_sqr1(0)
    sys.exit()


ph = eyes.open()
root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT)    # make plot objects using draw.disp
g.setWorld(fmin, 0, fmax, 5.0,_('Freq'),_('Amp'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b1 = Button(cf, text = _('START'), command = start)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('freq-response.dat')
e1.pack(side = LEFT)
R = Label(cf,text=_('Fmax = '))
R.pack(side=LEFT)
b5 = Button(cf, text = _('QUIT'), command = quit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = RIGHT, anchor = N)
b5 = Button(cf, text = _('Grace'), command = plotdata)
b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msg = Label(mf,text=_('Connect Piezo from SQR1 to GND. Microphone to 16,15 & 31. Wire from 13 to 26'), fg = 'blue')
msg.pack(side=LEFT)

eyeplot.pop_image('pics/sound.png', _('Frequency Response Curve'))
root.title(_('Audio Frequency response Curve'))
root.mainloop()


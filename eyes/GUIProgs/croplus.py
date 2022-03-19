from __future__ import print_function

import phm, time, math
import tkFont
from Tix import *

class disp:
    """
    Class for displaying items in a canvas using a global coordinate system.
    """
    border = 5
    bordcol = '#555555'
    gridcol = '#f0f0f0'
    gridcol2 ='#e0e0e0'
    def __init__(self, parent, width=400., height=300.):
        self.parent = parent
        self.SCX = width
        self.SCY = height
        self.XLIM = width + 2 * self.border
        self.YLIM = height + 2 * self.border
        self.canvas = Canvas(parent, background="white",
                             width = self.XLIM, height = self.YLIM)
        self.canvas.pack()
        b1 = (self.border - 1, self.border-1)
        b2 = (self.XLIM - self.border + 1, self.YLIM - self.border + 1)
        self.canvas.create_rectangle ([b1,b2], outline = self.bordcol)
        self.canvas.pack()
        self.setWorld(-0.5 * width, -0.5*height, 0.5 * width, 0.5* height)
        self.grid(10,100)
        self.canvas.bind("<Button-1>", self.show)
        self.canvas.bind("<Button-3>", self.show)
        self.xydisp = None
        self.marker = None

    def show(self,event):
        if self.xydisp != None:
          self.canvas.delete(self.xydisp)
        ix = self.canvas.canvasx(event.x) - self.border
        iy = self.YLIM - self.canvas.canvasy(event.y) - self.border
        x = float(ix) * self.xscale + self.xmin
        y = float(iy) * self.yscale + self.ymin
        if event.num == 1:
          s = 'x = %6.3f\ny = %6.0f' % (x/1000.,y)
          self.marker = (x,y)
        elif event.num == 3 and self.marker != None:
            s = 'x = %6.3f  dx = %6.3f\ny = %6.0f  dx = %6.0f' %\
                (
                    self.marker[0]/1000,
                    (x-self.marker[0])/1000.,
                    self.marker[1],
                    y - self.marker[1]
                )
        self.xydisp = self.canvas.create_text(self.border+1,self.SCY-1,
                                              anchor = SW, justify = LEFT, text = s)

    def setWorld(self, x1, y1, x2, y2):
      #Calculate the scale factors to be used by functions drawPoint etc.
      self.xmin = x1
      self.ymin = y1
      self.xmax = x2
      self.ymax = y2
      self.xscale = (self.xmax - self.xmin) / (self.SCX)
      self.yscale = (self.ymax - self.ymin) / (self.SCY)

    def w2s(self, p):
        ip = []
        for xy in p:
            ix = self.border + int( (xy[0] - self.xmin) / self.xscale)
            iy = self.border + int( (xy[1] - self.ymin) / self.yscale)
            iy = self.YLIM - iy
            ip.append((ix,iy))
        return ip

    def box(self, x1,  y1,  x2,  y2, col):
        ip = self.w2s([(x1,y1),(x2,y2)])
        self.canvas.create_rectangle(ip, outline=col)

    def line(self, points, col):
        ip = self.w2s(points)
        return self.canvas.create_line(ip, fill=col, smooth = 1)

    def delete_line(self, trace):
        self.canvas.delete(trace)

    def grid(self, major, minor):
        dx = (self.xmax - self.xmin) / major
        dy = (self.ymax - self.ymin) / major
        x = self.xmin + dx
        while x < self.xmax:
            self.line([(x,self.ymin),(x,self.ymax)],self.gridcol)
            x = x +dx
        y = self.ymin + dy
        while y < self.ymax:
            self.line([(self.xmin,y),(self.xmax,y)],self.gridcol)
            y = y +dy

        dx = (self.xmax - self.xmin) / minor
        dy = (self.ymax - self.ymin) / minor
        x = self.xmin + dx
        while x < self.xmax:
            self.line([(x, 0.),(x, dy)],self.gridcol2)
            x = x +dx

        y = self.ymin + dy
        while y < self.ymax:
            self.line([(0., y),(dx,y)],self.gridcol2)
            y = y +dy

func_list = [
    'r2rtime', 'r2ftime', 'f2rtime', 'f2ftime', 'set2rtime', \
    'set2ftime', 'clr2rtime', 'clr2ftime','pulse2rtime', 'pulse2ftime',\
    'multi_r2rtime', 'pendulum_period','CNTR Frequency','ADC Inputs']
src_list = ['D0', 'D1', 'D2', 'D3', 'CMP']
dst_list = ['D0', 'D1', 'D2', 'D3', 'CMP']

class CRO:
    global fd
    NPMAX = 200
    NP = 200                # Number of points to be sampled
    width = 600                # Window X width, MUST be multiple of NP
    height = 512                # height, MUST be multiple of ADC range(256)
    xmin = 0.0
    xmax = 2000.0
    ymin = -5000.0
    ymax =  5000.0
    color = ['black', 'red', 'green', 'blue']

    current_wave = None        # Used by Wave form generator

    MAXCHAN = 4
    numchans = 1
    chmask = 1                        # Channel mask
    val = [10,20,50,100,200,500,1000]
    delay = None                        # delay is IntVar() of set_delay()

    root = None                        # tkinter Widgets

    chan_status = []
    dinButtons  = []
    dout_status = []
    data = []
    traces = None

    def __init__(self, root):
        self.parent = root
        mf = Frame(root)
        mf.pack(side=LEFT)
        self.screen = disp(mf,self.width, self.height)

        help = Balloon(root, bg ='green')

        #Control widgets start from here
        row1 = Frame(mf)
        row1.pack(side=TOP, ipady=5, ipadx= 5,anchor = W)

        self.level_shifted = IntVar()
        self.levelCB = Checkbutton(row1, text='(x+5)/2',\
                                   selectcolor = 'yellow',
                                   variable = self.level_shifted)
        self.levelCB.pack(side = LEFT)
        help.bind_widget(self.levelCB, balloonmsg=
                         'Check this if ADC inputs are connected through the level shifting amplifier')

        self.trigpol = IntVar()
        self.Trigpol = Checkbutton(row1, text='Tr',\
                                   selectcolor = 'yellow',
                                   variable = self.trigpol,
                                   command = self.set_pol)
        self.Trigpol.pack(side = LEFT)
        help.bind_widget(self.Trigpol, balloonmsg=\
                         'Check this for negative edge trigger')

        self.Trig =  Scale(row1, command = self.set_trig, from_ = 5,
                           to=250, orient=HORIZONTAL, length=self.width/8,
                           showvalue=0)
        self.Trig.set(125)
        self.Trig.pack(side=LEFT)

        l = Label(row1,text='CH ')
        l.pack(side=LEFT)
        for k in range(4):
            var = IntVar()
            c = Checkbutton(row1, variable = var, text=str(k+1),
                            fg = self.color[k], selectcolor = self.color[k],
                            command = self.select_channels)
            self.chan_status.append(var)
            c.pack(side=LEFT)
        self.chan_status[0].set(1)

        self.Delay = Scale(row1, command = self.set_delay, from_ =0,
                           to=6, orient=HORIZONTAL, length = self.width/7,
                           showvalue=0)
        self.Delay.pack(side=LEFT)
        self.Delay.set(0)
        help.bind_widget(self.Delay, balloonmsg='Change the CRO Time Base')

        self.timebase = StringVar()
        self.tblab = Label(row1, width = 10, textvariable = self.timebase)
        self.tblab.pack(side=LEFT)

        self.zoom = IntVar()
        self.Zoom = Checkbutton(row1, text='10x', variable = self.zoom,\
                                onvalue = 10, offvalue = 1,\
                                selectcolor = 'yellow', command = self.set_zoom)
        self.Zoom.pack(side = LEFT)

        self.lizajous = IntVar()
        self.Liz = Checkbutton(row1, text='LIZ', variable = self.lizajous,\
                               onvalue = 1, offvalue = 0,
                               selectcolor = 'yellow')
        self.Liz.pack(side = LEFT)
        self.lizajous.set(0)
        help.bind_widget(self.Liz, balloonmsg=\
                         'Select Lissajous figure mode, select only CH0 and CH1')

        # Add Second ROW of widgets
        row2 = Frame(mf)
        row2.pack(side=TOP, ipady=2, ipadx= 5,anchor = W)
        f1 = Frame(row2,relief = GROOVE, borderwidth=4)
        f1.pack(side = LEFT)

        f = Frame(f1)
        f.pack(side=LEFT, anchor = W)
        self.m = Label(f, text = 'AWF-DAC')
        self.m.pack(side=TOP)

        self.plugin_dac = IntVar()
        self.pluginDAC = Checkbutton(f, text='Ext. DAC',
                                     command =self.set_awg_dac,
                                     selectcolor = 'yellow',
                                     variable = self.plugin_dac)
        self.pluginDAC.pack(side = TOP)

        scrollbar = Scrollbar(f1, orient=VERTICAL)
        self.shapes = Listbox(f1, yscrollcommand=scrollbar.set, height=1, width = 10)
        for item in ["Stop","sine", "tria","sawt"]:
            self.shapes.insert(END, item)
        scrollbar.config(command = self.shapes.yview)
        self.shapes.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.pack(side=LEFT, fill = Y)
        self.b = Button(f1, text='Set', command=self.select_wave)
        self.b.pack(side=LEFT)

        f = Frame(f1)
        f.pack(side=LEFT, anchor = W)
        self.awgDisp = Label(f, text = '50 Hz')
        self.awgDisp.pack(side=TOP, anchor = 'nw')
        self.awgScale =  Scale(f, command = self.set_awg_freq, showvalue=0,
                               from_ = 1, to=125, orient=HORIZONTAL,
                               length=self.width/5)
        self.awgScale.set(50.0)
        self.awgScale.pack(side=TOP, anchor = 'sw')

        help.bind_widget(f1, balloonmsg=\
'Arbitrary waveform generation on the DAC output using\n\
 interrupts. Frequency only up to 156 Hz.\n\
 Select Checkbutton for using the External Plug-in DAC\n\
 Select a waveform from the list and press Set to Start. \n\
 Change the waveform frequency using the slider')

        # PWG setup
        f2 = Frame(row2,relief = GROOVE, borderwidth=4)
        f2.pack(side = LEFT)
        f = Frame(f2)
        f.pack(side=LEFT, anchor = W)
        m = Label(f, text = '  Square Wave')
        m.pack(side=TOP)
        m = Label(f, text = '  on PWG')
        m.pack(side=TOP)
        help.bind_widget(f2, balloonmsg=\
                         'Squarewave on PWG Socket. Stop AWF generation of DAC to\n enable this feature. You cannot use PWG and DAC at the same time.')

        f = Frame(f2)
        f.pack(side=LEFT, anchor = W)
        self.pwgDisp = Label(f, text = '1000 Hz')
        self.pwgDisp.pack(side=TOP, anchor = 'nw')
        self.pwgScale =  Scale(f, command = self.set_pwg, from_ = 0,\
                               to=10000, orient=HORIZONTAL,
                               length=self.width/5, showvalue=0)
        self.pwgScale.set(1000)
        self.pwgScale.pack(side=LEFT)

        # Add Third ROW of widgets
        row3 = Frame(mf, relief = FLAT, borderwidth = 1)
        row3.pack(side=TOP, ipady=2, ipadx= 5,anchor = W)

        f = Frame(row3, relief = GROOVE, borderwidth = 5)
        f.pack(side=LEFT)
        u = Frame(f)
        u.pack(side=TOP)
        self.wait4din = IntVar()
        self.WaitCB = Button(u, text='Scan After Detecting',\
                             command = self.wait_enabled_scan)
        self.WaitCB.pack(side = LEFT)
        self.wait4din_pol = IntVar()
        self.Wait_polCB = Checkbutton(u, text='HIGH on', \
                                      variable = self.wait4din_pol,
                                      command=self.wait_text_change)
        self.Wait_polCB.pack(side = LEFT)

        l = Frame(f)
        l.pack(side=TOP)
        self.waitchan = IntVar()
        for k in range(4):
            c = Radiobutton(l, variable = self.waitchan, value = k,\
                            text='D'+str(k), selectcolor = 'green')
            c.pack(side=RIGHT)
        self.waitchan.set(3)
        help.bind_widget(f, balloonmsg=\
 'Digitize and plot the selected ADC channels after detecting\n\
 the chosen LEVEL on the selected Digital Input\n\
 This feature is used for capturing transient waveforms.\n\
 Stops after one scan to allow user to save the result.\n\
 Press C.Scan button for continuous scanning')

        f = Frame(row3, relief = GROOVE, borderwidth = 5)
        f.pack(side=LEFT)
        u = Frame(f)
        u.pack(side=TOP)
        self.set_dout = IntVar()
        self.SetCB = Button(u, text='Scan After Setting', \
                            command = self.set_enabled_scan)
        self.SetCB.pack(side = LEFT)
        self.set_dout_pol = IntVar()
        self.Set_polCB = Checkbutton(u, text='HIGH on', variable = \
                                     self.set_dout_pol,
                                     command=self.set_text_change)
        self.Set_polCB.pack(side = LEFT)

        l = Frame(f)
        l.pack(side=TOP)
        self.setchan = IntVar()
        for k in range(4):
            c = Radiobutton(l, variable = self.setchan, value = k,\
                            text='D'+str(k), selectcolor = 'red')
            c.pack(side=RIGHT)
        self.setchan.set(3)
        help.bind_widget(f, balloonmsg=\
 'Set HIGH or LOW on the selected Digital Output\n\
 just before starting the digitization of the selected ADC channels.\n\
 Studying capacitor discharge is one application of this feature.')
 
        f = Frame(row3, relief = FLAT, borderwidth = 2)
        f.pack(side=LEFT)
        u = Frame(f)
        u.pack(side=TOP)
        self.Loop = Button(u, text='C.Scan',width = 7,command = self.loop)
        self.Loop.pack(side=LEFT)
        self.Save = Button(u, text='Save',width=7,command = self.save)
        self.Save.pack(side=LEFT)
        help.bind_widget(self.Save, balloonmsg=\
'Saves the data in text from to "cro.dat"')

        l = Frame(f)
        l.pack(side=TOP)
        self.Print = Button(l, text='Capture',width=7,command = self.capture)
        self.Print.pack(side=LEFT)
        self.limit = 0.0

        self.Print = Button(l, text='Print',width=7,command = self.eps)
        self.Print.pack(side=LEFT)
        help.bind_widget(self.Print, balloonmsg=\
'CRO screenshot is saved to "cro.eps"')

        # Add Fourth ROW of widgets

        row4 = Frame(mf, relief = FLAT, borderwidth = 1)
        row4.pack(side=TOP,anchor = W)
        self.dacDisp = Label(row4, text = 'DAC= 0', width=12)
        self.dacDisp.pack(side=LEFT, anchor = 'n')
        self.dacScale =  Scale(row4, command = self.set_dac, showvalue=0,
                               from_ = 1, to=5000, orient=HORIZONTAL,
                               length=100)
        self.dacScale.set(0)
        self.dacScale.pack(side=LEFT, anchor = 'n')
        help.bind_widget(self.dacScale, balloonmsg=\
'Set the DAC output, between 0 to 5000 mV.\n\
 DAC outpout is used by AWF. It is also affected by PWG.\n\
 Disable them to maintain a DC on DAC output')

        self.msg = Label(row4, bg = 'green', width = 60, justify =LEFT)
        self.msg.pack(side=LEFT)


        #Time mesurement Widgets & Variables

        rv = Frame(root)
        rv.pack(side=LEFT, anchor = N)

        df = Frame(rv, relief = GROOVE, borderwidth=5)
        df.pack()
        l = Label(df, text = 'Digital Input/Output', bg = 'cyan')
        l.pack(side = TOP, fill = X)
        f = Frame(df)
        f.pack(side=TOP)
        for i in range(4):
            j = Frame(f,borderwidth = 2)
            j.pack(side=RIGHT)
            b = Label(j, width = 5, fg = 'white',text='D'+str(i))
            b.pack(side = RIGHT)
            self.dinButtons.append(b)
        f = Frame(df)
        f.pack(side=TOP)
        for k in range(4):
            var = IntVar()
            c = Checkbutton(f, variable = var, text=str(k),\
                            selectcolor = 'red', command = self.set_digout)
            self.dout_status.append(var)
            c.pack(side=RIGHT)

        self.pulseScale =  Scale(df, command = self.set_pulse, showvalue=1,
                                 from_ = 0.0, to=10.0, resolution = 0.01,
                                 orient=HORIZONTAL, length=100)
        self.pulseScale.set(0.0)
        self.pulseScale.pack(side=LEFT, anchor = 'sw')
        self.pulseDisp = Label(df, text = 'Hz (D0,D1)')
        self.pulseDisp.pack(side=LEFT, anchor='s')

        help.bind_widget(df, balloonmsg=\
'Status of Digital Input Sockets are shown here.\n\
 RED means HIGH and BLACK means LOW.\n\
 Depressing a Checkbutton makes that Digital Output Socket HIGH.\n\
 Any non-zero value on the Slider below will generate a squarewave\n\
 of the selected frequency on Outputs D0 and D1. To stop pulsing\n\
 make the slider zero')

        mf = Frame(rv, relief = GROOVE, borderwidth = 5)
        mf.pack(side=TOP)
        l = Label(mf, text = 'Select Function', bg = 'cyan')
        l.pack(side = TOP, fill = X)
        self.function = StringVar()
        for i in range(len(func_list)):
            c = Radiobutton(mf, variable = self.function, val = i, \
                            text = func_list[i])
            c.pack(side=TOP, anchor = W, fill = Y)
        self.function.set(1)                # R2Ftime is default

        help.bind_widget(mf, balloonmsg=\
'Select any function from the Function List.\n\
 Select the Input/Output Sockets on which\n\
 the measurement is to be done and press GO')
 
        f = Frame(mf)
        f.pack(side=TOP)
        self.ppol = IntVar()
        l = Checkbutton(f, variable = self.ppol, text = '+/-')
        l.pack(side = LEFT, fill = X)
        self.ppol.set(0)
        l = Label(f, text = 'Pulse')
        l.pack(side = LEFT)
        self.pwidthScale =  Scale(f, from_ = 10,\
                                  to=100, orient=HORIZONTAL, length=70,
                                  showvalue=1)
        self.pwidthScale.set(13)
        self.pwidthScale.pack(side=LEFT)

        c = Frame(mf, relief = FLAT, borderwidth = 1)
        c.pack(side=TOP, fill = BOTH)
        l = Label(c, text = 'Select I/O Socket', bg = 'cyan')
        l.pack(side = TOP, fill = X)
        c1 = Frame(c)
        c1.pack(side=LEFT, anchor = N)
        c2 = Frame(c)
        c2.pack(side=RIGHT, anchor = N)

        self.src = IntVar()
        self.dst = IntVar()
        l = Label(c1, text = 'Start')
        l.pack(side = TOP, fill = X, expand = 1)
        l = Label(c2, text = 'Stop')
        l.pack(side = TOP, fill = X, expand = 1)

        for i in range(len(src_list)):
            c = Radiobutton(c1, variable = self.src, val = i, text = src_list[i])
            c.pack(side=TOP, anchor=W)
            self.src.set(0)

        for i in range(len(dst_list)):
            c = Radiobutton(c2, variable = self.dst, val = i, text = dst_list[i])
            c.pack(side=TOP, anchor =W)
        self.dst.set(0)

        f = Frame(mf)
        f.pack(side=TOP)
        self.Start = Button(f, text='GO', width = 3,command = self.time_func)
        self.Start.pack(side=LEFT)
        self.tmResult = Label(f, bg = 'white', width = 15)
        self.tmResult.pack(side=LEFT)

        f = Frame(rv)
        f.pack(side=TOP)
        self.Quit = Button(f, text='Quit',width=7,command = self.bye)
        self.Quit.pack(side=RIGHT)

        fd.disable_wait()
        fd.stop_wave()
        self.update_digins()
        fd.set_frequency(1000)
        fd.set_num_samples(self.NP)
        fd.set_adc_size(1)
        self.select_channels()
        self.looping = True
        self.waiting_capture = False
        self.parent.after(10, self.update)


    def bye(self):
        sys.exit(0)

    def capture(self):
        self.data = fd.multi_read_block\
                    (self.NP,self.delay,self.level_shifted.get())
        self.limit = 0.0
        for val in self.data:
            if abs(val[1]) > self.limit:
                self.limit = abs(val[1])
        self.limit = self.limit + 100
        s = 'Waiting for CH0 input to exceed %4.0f mV'%(self.limit)
        self.msg.config(text=s)
        self.waiting_capture = True
        self.looping = True

    def loop(self):
        self.looping = True
        self.waiting_capture = False

    def set_pulse(self,w):
        val = self.pulseScale.get()
        fd.pulse_d0d1(val)

    def set_dac(self,w):
        val = self.dacScale.get()
        fd.set_frequency(0)
        fd.set_voltage(val)
        s = 'DAC= %4.0f'%(val)
        self.dacDisp.config(text = s)

    def wait_text_change(self):
        wtext = ['HIGH on','LOW on']
        self.Wait_polCB.config(text = wtext[self.wait4din_pol.get()])

    def set_text_change(self):
        wtext = ['HIGH on','LOW on']
        self.Set_polCB.config(text = wtext[self.set_dout_pol.get()])

    def wait_enabled_scan(self):                # Wait Actions on DIN
        pol = self.wait4din_pol.get()
        res = self.waitchan.get()
        if pol == 0:
            fd.enable_rising_wait(res)
        else:
            fd.enable_falling_wait(res)
        self.draw()
        if self.data == None:
            self.msg.config(text='time out')
        else:
            self.msg.config(text='Press C.Scan to continue')
            self.looping = False
        fd.disable_wait()


    def set_enabled_scan(self):                # Set/Clear Actions on DOUT
        pol = self.set_dout_pol.get()
        res = self.setchan.get()
        if pol == 0:
            fd.enable_set_high(res)
        else:
            fd.enable_set_low(res)
        self.draw()
        self.msg.config(text='Press Start to continue')
        self.looping = False
        fd.disable_set()
        self.set_digout()

    def update_digins(self):
        dat = fd.read_inputs()
        for k in range(4):
            if (dat & (1 << k)) != 0:
                self.dinButtons[k].config(bg='red')
            else:
                self.dinButtons[k].config(bg='black')

    def set_digout(self):
        dat = 0
        for k in range(4):
            if self.dout_status[k].get() == 1:
                dat = dat | (1 << k)
        fd.write_outputs(dat)

    def time_func(self):
        global fd, data
        i = int(self.function.get())
        cmd = func_list[i]
        p1 = self.src.get()
        p2 = self.dst.get()
        if cmd == 'r2rtime':
            t  = fd.r2rtime(p1,p2)
        elif cmd == 'r2ftime':
            t  = fd.r2ftime(p1,p2)
        elif cmd == 'f2rtime':
            t  = fd.f2rtime(p1,p2)
        elif cmd == 'f2ftime':
            t  = fd.f2ftime(p1,p2)
        elif cmd == 'set2rtime':
            t  = fd.set2rtime(p1,p2)
        elif cmd == 'set2ftime':
            t  = fd.set2ftime(p1,p2)
        elif cmd == 'clr2rtime':
            t  = fd.clr2rtime(p1,p2)
        elif cmd == 'clr2ftime':
            t  = fd.clr2ftime(p1,p2)
        elif cmd == 'pulse2rtime':
            fd.set_pulse_width(int(self.pwidthScale.get()))
            fd.set_pulse_polarity(int(self.ppol.get()))
            t  = fd.pulse2rtime(p1,p2)
        elif cmd == 'pulse2ftime':
            t  = fd.pulse2ftime(p1,p2, int(self.pwidthScale.get()),\
                                self.ppol.get())
        elif cmd == 'multi_r2rtime':
            t  = fd.multi_r2rtime(p1,0)
        elif cmd == 'pendulum_period':
            t  = fd.pendulum_period(p1)
        elif cmd == 'CNTR Frequency':
            t = fd.measure_frequency()
        elif cmd == 'ADC Inputs':
            s = 'ADC (mV) :'
            fd.set_adc_size(2)        #Do with 10 bit resolution
            for ch in range(4):
                fd.select_adc(ch)
                val = fd.zero_to_5000()[1]
                s = s +' CH%d = %4.0f '%(ch,val)
            self.msg.config(text = s)
            fd.set_adc_size(1)        # Back to 8 bit, for scanning
            return
        else:
            self.tmResult.config(text = s)        # should not happen
            return

        self.set_digout()        # Recover DOUTs, if we have changed them

        if t == -1:
            s = 'time out'
        else:
            s = '%3.1f '%(t)
        self.tmResult.config(text = s)
        return

    def set_awg_dac(self):
        self.set_awg_freq(0)

    def set_awg_freq(self, dummy):        # Arbitrary wave form generator
        if self.current_wave == None:
            return;
        DAC = self.plugin_dac.get()
        fr = float(self.awgScale.get())
        res = fd.start_wave(fr,DAC)

        s = '%3.1f Hz'%(res)
        self.awgDisp.config(text = s)

    def select_wave(self):                # Arbitrary wave form generator
        v = []
        wave = self.shapes.get(ACTIVE)
        if wave == 'Stop':
            fd.stop_wave()
            self.current_wave = None
            self.pwgScale.config(state = ACTIVE)
            self.pwgDisp.config(text='Enabled')
            return
        elif self.current_wave != wave:
            self.load_wave(wave)
            self.current_wave = wave
            self.pwgScale.config(state = DISABLED)
            self.pwgDisp.config(text='Stop AWF to Enable')
            self.set_awg_freq(0)        # argument unused
        return

    def load_wave(self,wave):
        v = []
        if wave == 'sine':
            for i in range(100):
                x = 127.5 + 127.5 * math.sin(2.0*math.pi*i/100)
                x = int(x+0.5)
                v.append(x)
        elif wave == 'tria':
            for i in range(50):
                x = 255.0 * i / 50;
                x = int(x+0.5)
                v.append(x)
            for i in range(50):
                x = 255.0 * i / 50;
                x = 255 - int(x+0.5)
                v.append(x)
        elif wave == 'sawt':
            for i in range(100):
                x = 255.0 * i / 100;
                x = int(x+0.5)
                v.append(x)
        else:
            print ('no match ',wave)
            return None

        fd.load_wavetable(v)
        return wave


    def set_pwg(self, freq):
        f = float(freq)
        fr = fd.set_frequency(f)
        s = '%3.1f Hz'%(fr)
        self.pwgDisp.config(text=s)

    def eps(self):
        self.screen.canvas.postscript(file = 'cro.eps', colormode = 'color')

    def save(self):
        fd.save_data(self.data, 'cro.dat')

    def set_zoom(self):
        z = self.zoom.get()
        self.NP = self.NPMAX / z
        fd.set_num_samples(self.NP)
        self.set_delay(0)

    def set_trig(self, dummy):
        tr = int(self.Trig.get())
        pol = self.trigpol.get()
        if pol == 1:                # -ive edge trigger
            fd.set_adc_trig(tr,tr-5)
        else:
            fd.set_adc_trig(tr,tr+5)

    def set_pol(self):
        self.set_trig(0)

    def set_delay(self,dummy):
        d = self.Delay.get()
        self.delay = self.val[d]
        fd.set_adc_delay(self.delay)
        perdiv = float(self.NP) * self.delay * self.numchans / 10000
        self.timebase.set(str(perdiv) +' ms/div')
        self.xmax = self.NP * self.delay
        self.screen.setWorld(self.xmin, self.ymin,self.xmax, self.ymax)

    def select_channels(self):
        self.chmask = 0
        self.numchans = 0
        for k in range(4):
            if self.chan_status[k].get() == 1:
                self.chmask = self.chmask | (1 << k)
                fd.add_channel(k)
                self.numchans = self.numchans  + 1
            else:
                fd.del_channel(k)
        self.set_delay(0)

    def draw(self):
        try:
            self.data = fd.multi_read_block\
                        (self.NP,self.delay,self.level_shifted.get())
            if self.data == None:
                return
        except:
            return

        if self.traces != None:
            for ch in range(len(self.traces)):
                self.screen.delete_line(self.traces[ch])
        self.traces = []

        mode = self.lizajous.get()
        if (mode == 1) and (self.chmask == 3):        # Lissagous figure
            self.screen.setWorld(self.ymin, self.ymin, self.ymax, self.ymax)
            points = []
            for n in range(self.NP):
                points.append((self.data[n][1], self.data[n][2]))
            t = self.screen.line(points, 'black')
            self.traces.append(t)
        else:
            self.screen.setWorld(self.xmin, self.ymin, self.xmax, self.ymax)
            ch = 0;
            for k in range(self.MAXCHAN):
                if self.chmask & (1 << k):        # Draw if selected channel
                    points = []
                    try:
                        for p in self.data:
                            points.append((p[0],p[ch+1] ))
                            t = self.screen.line(points, self.color[k])
                            self.traces.append(t)
                    except:
                        pass           #ignore errors
                    ch = ch + 1

    def update(self):
        self.update_digins()
        if self.looping == True:
            self.draw()
            if self.waiting_capture:
                for val in self.data:
                    if abs(val[1]) > self.limit:
                        self.looping = False
                        self.waiting_capture = False
                        self.msg.config(text='Captured')
                        break
        self.parent.after(10, self.update)
        return

root = Tk()
fd = phm.phm()
if fd == None:
    root.title('Error')
    Label(root, bg = 'red',text='Phoenix-M Hardware not found').pack()
    root.mainloop()
    sys.exit()

font = tkFont.Font ( family="times", size=12, weight="normal" )
root.option_add ( "*font", font)
root.title('CROplus')
CRO(root)
root.mainloop()

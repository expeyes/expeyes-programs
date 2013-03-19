#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
expEYES Explorer program
© 2010-2012 Ajith Kumar B.P, bpajith@gmail.com
© 2012 Georges Khaznadar, georgesk@ofset.org, for qt4 support
License : GNU GPL version 3
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os, sys, subprocess, math
import expeyes.eyes as eyes

try:        
    import expeyes.eyemath as eyemath        # Will fail if scipy is not installed
    EYEMATH = True
except:
    EYEMATH = False

import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

help = [
_("""For help, click on the Terminal Boxes(1 to 32).<br/>
LIZ : Lissajous figure.<br/>
FT : Fourier Transform power spectrum.<br/>
XM : Xmgrace 2D plotting program<br/>
XmGrace is NOT available under MSWindows"""),
_("""1.Software can read the voltage input level, LOW ( < .8V) or HIGH (>2V).<br/>
If a square wave input is given, click on the Buttons for measuring frequency / duty cycle"""),
_("""2. Can sense input level"""),
_("""3. Digital Output.  Can be set to 0 or 5 volts.<br/>Use the Checkbutton to change the Level"""),
_("""4. Digital Output.  Can be set to 0 or 5 volts.<br/>Use the Checkbutton to change the Level"""),
_("""5. Ground (zero volts)"""),
_("""6. SQR1: Generates Square Wave. Voltage swings between 0 and 5V. Frequency is programmable from Hz to1 MHz. All intermediate values of frequency are not possible."""),
_("""7. SQR2: Generates Square Wave. The frequency range is controlled by software and fine adjustment is done by an external 22 kOhm variable resistor. Frequency range is from 0.7 Hz to 90 kHz."""),
_("""8. 22 kOhm resistor used for frequency adjustment of SQR2."""),
_("""9. 22 kOhm resistor used for frequency adjustment of SQR2."""),
_("""10. Programmable Pulse. Frequency is 488.3 Hz. Duty cycle from 0 to 100% in 255 steps."""),
_("""11. Ground"""),
_("""12. Output of Inverting Amplifier with a gain of 47. (Input at 14)"""),
_("""13. Output of Inverting Amplifier with a gain of 47. (Input at 15)"""),
_("""14. Input of Inverting Amplifier with a gain of 47. (Output at 12)"""),
_("""15. Input of Inverting Amplifier with a gain of 47. (Output at 13). Also acts as a Frequency counter, for a bipolar a signal (amplitude from 100 mV to 5V). If the signal is unipolar feed it via a series capacitor"""),
_("""16. Ground"""),
_("""17. Input of Inverting Amplifier. Default Gain=100. The gain can be reduced by a series resistor at the input. The gain will be given by G = 10000/(100+R), where R is the value of the external series resistor."""),
_("""18. Output of the Inverting Amplifier (Input 17)"""),
_("""19. Ground"""),
_("""20. Gain control resistor for Non-Inverting amplifier, from 20 to Ground. Gain = 1 + 10000/Rg."""),
_("""21. Input of Non-Inverting Amplifier (Output 22)"""),
_("""22. Output of Non-Inverting Amplifier(Input 21)"""),
_("""23. Sensor Input. Connect Photo transistor collector here and emitter to Ground."""),
_("""24. Voltage measurement terminal. Input must be in the 0 to 5V range."""),
_("""25. Voltage measurement terminal. Input must be in the -5V to 5V range."""),
_("""26. Voltage measurement terminal. Input must be in the -5V to 5V range."""),
_("""27. Ground"""),
_("""28. Programmable constant current source. 0.05 to 2 milli ampere range. The load resistor should be chosen to make the product of I and R less than 2 volts."""),
_("""29. Output of 30 through a 1kOhm resistor. Used for doing diode I-V characteristic."""),
_("""30. Programmable voltage between -5V to +5V."""),
_("""31. Programmable voltage between 0 to +5V."""),
_("""32. Sine wave output. Frequency around 90 Hz. Voltage swings between -4V to +4V.""")
]

# stylesheets for backgrounds
bgreen="background:#ddffaa;"
bgray="background:#aaaaaa;"

#-----------------------------main program starts here-----------------------------
class mainWindow(QMainWindow):
    def __init__(self, parent, opts, locale="fr_FR"):
        """
        Le constructeur
        @param parent un QWidget
        @param opts une liste d'options extraite à l'aide de getopts
        @param locale la langue de l'application
        """
        QMainWindow.__init__(self)
        QWidget.__init__(self, parent)
        self.locale=locale
        from Ui_main import Ui_Dialog
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.graphWidget.setWorld(0,-5,1,5)
        # begins with A0 checked
        self.ui.A0Check.setCheckState(Qt.Checked)
        # connects the panel's great button
        self.connect(self.ui.panelButton, SIGNAL("clicked()"), self.panelHelp)
        # clears the text browser
        self.showhelp('')
        # initialize self.tw: table of widgets which are on the panel
        self.NSIG = 1 + 32           # number of signals; zeroth element is unused
        self.tw = [None] * self.NSIG
        # left entry widgets: 6, 7, 10
        self.setTwDisplay(1,self.ui.ID0_display)
        self.setTwDisplay(2,self.ui.ID0_display)
        self.setTwEdit(6,self.ui.SQR1_edit)
        self.setTwEdit(7,self.ui.SQR2_edit)
        self.setTwDisplay(8,self.ui.SQR2_display)
        self.setTwEdit(10,self.ui.PULSE_edit)
        self.setTwDisplay(15,self.ui.FREQ_display)
        self.setTwDisplay(22,self.ui.SEN_display_2)
        self.setTwDisplay(23,self.ui.SEN_display)
        self.setTwDisplay(24,self.ui.A2_display)
        self.setTwDisplay(25,self.ui.A1_display)
        self.setTwDisplay(26,self.ui.A0_display)
        self.setTwDisplay(27,self.ui.CS_display)
        self.setTwEdit(28,self.ui.CS_edit)
        self.setTwEdit(30,self.ui.BPV_edit)
        self.setTwEdit(31,self.ui.UPV_edit)

        self.connect(self.ui.OD0_check, SIGNAL("stateChanged(int)"), self.OD0toggle)
        self.connect(self.ui.OD1_check, SIGNAL("stateChanged(int)"), self.OD1toggle)
        self.connect(self.ui.ID0_button_F, SIGNAL("clicked()"), self.freq_id0)
        self.connect(self.ui.AMPLI_button_F, SIGNAL("clicked()"), self.freq_ampin)
        self.connect(self.ui.SEN_button_F, SIGNAL("clicked()"), self.freq_sen)
        self.connect(self.ui.ID0_button_pcent, SIGNAL("clicked()"), self.pcent_id0)
        self.connect(self.ui.horizontalSlider, SIGNAL("valueChanged(int)"), self.set_timebase)
        self.connect(self.ui.A0Check, SIGNAL("stateChanged(int)"), self.toggleA0)
        self.connect(self.ui.A1Check, SIGNAL("stateChanged(int)"), self.toggleA1)
        self.connect(self.ui.fitCheck, SIGNAL("stateChanged(int)"), self.toggleFit)
        self.connect(self.ui.lisCheck, SIGNAL("stateChanged(int)"), self.toggleLis)
        self.connect(self.ui.saveButton, SIGNAL("clicked()"), self.save)
        self.connect(self.ui.xmButton, SIGNAL("clicked()"), self.xmgrace)
        self.connect(self.ui.ftButton, SIGNAL("clicked()"), self.do_fft)
        self.connect(self.ui.quitButton, SIGNAL("clicked()"), self.close)
        # other intializations
        self.VPERDIV = 1.0      # Volts per division, vertical scale
        self.delay = 10         # Time interval between samples
        self.np = 100           # Number of samples
        self.nc = 1             # Number of channels
        self.lissa = False      # drawing lissajous-type plots
        self.chanmask=1         # byte to store the mask for active analogic channels.
        self.np=100             # number of points to plot (and samples to get)
        self.delay=10           # delay for measurements (µs between two samples)
        self.measure = 0        # boolean to toggle data fitting
        self.NOSQR2 = True      # SQR2 is not set
        self.NOSF = True        # No frequency on SENSOR input
        self.NOAF = True        # No frequency on Amplifier input, T15
        self.NODF = True        # No frequency on Digital input 0
        self.OUTMASK = 0        # Digital outputs to LOW
        # connect to the eyes box
        self.eye=eyes.open()   # Try several times to make a connection
        # starts the timer for refresh loop
        if self.eye == None:
            self.setWindowTitle('EYES Hardware NOT found.')
            self.showhelp('EYES Hardware Not Found.<br/>Re-Connect USB cable and restart the program.', 'red')
        else:
            self.setWindowTitle(('EYES Hardware found on ' + str(self.eye.device)))
            self.eye.write_outputs(0)
            self.eye.disable_actions()
            self.eye.loadall_calib()
            self.timer=QTimer(self)
            self.connect(self.timer, SIGNAL("timeout()"), self.update)
            self.timer.start(500)   # refresh twice per second if possible

    def save(self, filename='measures.dat'):
        """
        save current data to a file
        @param filename the name of the file
        """
        self.eye.save(self.trace,filename)
        self.showhelp('Traces saved to %s' %filename)

    def xmgrace(self):
        """
        opens xmgrage with current data in a plot
        """
        if self.eye.grace(self.trace) == False:
            self.showhelp('Could not find Xmgrace or Pygrace. Install them','red')


    def do_fft(self, filename='measureFFT.dat'):
        """
        opens xmgrage with current data in a FFT plot
        @param filename the name of the file
        """
        if EYEMATH == False:
            self.showhelp('Could not find scipy package. Install it','red')
            return
        if self.trace == None: return
        transform = []
        for xy in self.trace:
            fr,tr = eyemath.fft(xy[1], self.delay * self.nc * 0.001)
            transform.append([fr,tr])
        self.eye.save(transform, filename)
        self.eye.grace(transform, 'freq', 'power')
        self.showhelp('Fourier transform Saved to %s' %filename)

    
    def toggleA0(self, state):
        """
        callback function for the A0 check box
        @param state state of the checkbox
        """
        if state == Qt.Checked:
            self.chanmask = self.chanmask | 1
        else:
            self.chanmask = self.chanmask & 254
        self.adjustChannels()

    def toggleA1(self, state):
        """
        callback function for the A1 check box
        @param state state of the checkbox
        """
        if state == Qt.Checked:
            self.chanmask = self.chanmask | 2
        else:
            self.chanmask = self.chanmask & 253
        self.adjustChannels()

    def adjustChannels(self):
        """
        adjust channel flags when some has been toggled
        """
        if self.chanmask == 3: 
            self.nc = 2
        else:
            self.nc = 1
        if self.chanmask == 0:
            self.ui.graphWidget.delete_lines()
            self.ui.graphWidget.update()

    def toggleFit(self, state):
        """
        callback function for the Fit check box
        @param state state of the checkbox
        """
        if state == Qt.Checked:
            self.measure = 1
        else:
            self.measure = 0
            self.showhelp('') # to erase previous fittings if any

    def toggleLis(self, state):
        """
        callback function for the Lis check box
        @param state state of the checkbox
        """
        if state == Qt.Checked:
            self.lissa = 1
        else:
            self.lissa = 0


    def freq_id0(self):
        """
        force the display of the frequency at ID0
        """
        fr = self.eye.digin_frequency(0)
        if fr < 0:
            self.labset(1, '0 Hz')
        else:
            self.labset(1, '%5.2f Hz'%fr)

    def freq_ampin(self):
        fr = self.eye.ampin_frequency()
        if fr < 0:
            self.labset(15, '0 Hz')
            self.NOAF = True
        else:
            self.labset(15, '%5.2f Hz'%(fr))
            self.NOAF = False

    def freq_sen(self):
        fr = self.eye.sensor_frequency()
        if fr < 0:
            self.labset(22, '0 Hz')
            self.NOSF = True
        else:
            self.labset(22, '%5.2f Hz'%(fr))
            self.NOSF = False

    def pcent_id0(self):
        """
        force the display of the duty cycle at ID0
        """
        hi = self.eye.r2ftime(0,0)
        if hi > 0:
            lo = self.eye.f2rtime(0,0)
            ds = 100*hi/(hi+lo)
            self.labset(1, '%5.2f %%'%(ds))
        else:
            self.labset(1,'0 Hz')

    def set_timebase(self, value):
        """
        callback for the horizontal slider
        @param value: the position of the cursor in range(10)
        """
        assert value in range(10)
        divs = [0.050, 0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
        msperdiv = divs[value]
        self.np = 200
        self.delay = msperdiv * 100
        if self.delay < 10: # for value==0
            # self.delay == 5 is too short; increase the delay, get less measurements
            self.np = 20 * self.delay * self.nc
            self.delay = 10
        elif self.delay > 1000: # for value in [8,9]
            # self.delay in [2000, 5000] is too long; get more measurements, decrease the delay
            self.np = self.delay / 5 / self.nc
            self.delay = 1000
        # don't allow float values
        self.delay=int(self.delay)
        self.np=int(self.np) 
        self.setTimeVoltageWorld()

    def setTimeVoltageWorld(self):
        """
        ensures the right viewport for ordinary oscillogramme
        """
        self.ui.graphWidget.setWorld(0,
                                     -5*self.VPERDIV, 
                                     self.np * self.delay * 0.001, 
                                     5*self.VPERDIV,
                                     xUnit='ms', yUnit='V')

    def OD0toggle(self, state):
        """
        Callback for the check box OD0
        @param state the state of the check box
        """
        if state==Qt.Checked:
            self.ui.OD0_check.setStyleSheet(bgreen)
            self.ui.OD0_check.setText(_("HI"))
            self.OUTMASK |= (1 << 0)
        else:
            self.ui.OD0_check.setStyleSheet(bgray)
            self.ui.OD0_check.setText(_("LO"))
            self.OUTMASK &= ~(1 << 0)
        self.eye.write_outputs(self.OUTMASK & 3)

    def OD1toggle(self, state):
        """
        Callback for the check box OD1
        @param state the state of the check box
        """
        if state==Qt.Checked:
            self.ui.OD1_check.setStyleSheet(bgreen)
            self.ui.OD1_check.setText(_("HI"))
            self.OUTMASK |= (1 << 1)
        else:
            self.ui.OD1_check.setStyleSheet(bgray)
            self.ui.OD1_check.setText(_("LO"))
            self.OUTMASK &= ~(1 << 1)
        self.eye.write_outputs(self.OUTMASK & 3)


    def setTwDisplay(self, i, w):
        """
        affects a widget to the table, when it is used to display values
        @param i the index in the table
        @param w the widget
        """
        self.tw[i]=w
        w.setReadOnly(True)
        return

    def panelHelp(self):
        """
        callback used when one clicks over the panel
        """
        wpos=self.geometry().topLeft()
        pos=QCursor.pos()
        x=pos.x()-wpos.x(); y=pos.y()-wpos.y()
        plug=int(1.0+(y-12)/(550-12)*16)
        if x in range(11,72):
            self.showhelp(help[plug])
        elif x in range(394,455):
            plug=33-plug
            self.showhelp(help[plug])
        else:
            self.showhelp(help[0])
        

    def setTwEdit(self, i, w):
        """
        affects a widget to the table, when it is used to enter values
        @param i the index in the table
        @param w the widget
        """
        self.tw[i]=w
        self.connect(w, SIGNAL("editingFinished ()"), self.make_process(w))
        return


    def make_process(self, w):
        """
        function factory to make callbacks for line editors on the Panel
        @param w a widget which will send a signal
        """
        # begin of definition of a process which will use w as a local variable
        def process():
            """
            callback for line editors on the Panel
            """
            for i in range(self.NSIG):
                if self.tw[i] == w:                # Look for the widget where Enter is pressed            
                    fld = i
                    break
            msg = ''
            try:
                val = float(w.text())                   # Get the value entered by the user
            except:
                return
            if fld == 6:                    # Set SQR1
                freq = self.eye.set_sqr1(val)
                self.twset(fld,'%5.1f'%freq)
            elif fld == 7:                    # Set SQR2
                self.eye.set_sqr2(val)
                freq = self.eye.get_sqr2()
                if freq > 0:
                    self.labset(8,'%5.1f Hz'%freq)
                    self.NOSQR2 = False
                else:
                    self.labset(8, '0 Hz')
                    self.NOSQR2 = True
            elif fld == 10:                    # Set Pulse duty cycle
                ds = self.eye.set_pulse(val)
                self.twset(fld,'%5.1f'%ds)
            elif fld == 28:                    # Set Current
                self.eye.set_current(val)
                self.twset(fld,'%5.3f'%val)
            elif fld == 30:
                self.eye.set_voltage(0,val)
                self.twset(i,'%5.3f'%val)
            elif fld == 31:
                self.eye.set_voltage(1,val)
                self.twset(fld, '%5.3f'%val)
        # end of definition of the process with w as a local variable
        return process

    def update(self, debug=True):
        """
        the routine for the periodic timer;
        reports an error when something goes wrong
        @param debug setting it to True escapes the try/except clause, so errors can be raised
        """
        if debug:
            self.routine_work()
            return
        try:
            self.routine_work()
        except:
            self.showhelp('Transaction Error.','red')

    def routine_work(self):
        """
        sequence of actions to be done at each timer's tick
        """
        self.trace = []  # a pair of vectors which remains local to mainWindow
        g=self.ui.graphWidget
        tt, vv = None, None

        if self.lissa == True:
            t,v,tt,vv = self.eye.capture01(self.np,self.delay)
            g.delete_lines()
            g.setWorld(-5,-5,5,5,xUnit='V',yUnit='V')
            g.polyline(v,vv)
            self.trace.append([v,vv])
        elif self.chanmask == 1 or self.chanmask == 2:                # Waveform display code 
            t, v = self.eye.capture(self.chanmask-1,self.np,self.delay)
            g.delete_lines()
            g.polyline(t,v,self.chanmask-1)
            self.trace.append([t,v])
        elif self.chanmask == 3:
            t,v,tt,vv = self.eye.capture01(self.np,self.delay)
            g.delete_lines()
            g.polyline(t,v)
            g.polyline(tt,vv,1)
            self.trace.append([t,v])
            self.trace.append([tt,vv])

        self.curveFit(t,v,tt,vv)               # fits the curves

        v = self.eye.get_voltage(6)            # CS voltage
        self.labset(27, '%5.3f V'%v)                    
        v = self.eye.get_voltage(0)            # A0
        self.labset(26, '%5.3f V'%v)
        v = self.eye.get_voltage(1)            # A1
        self.labset(25, '%5.3f V'%v)
        v = self.eye.get_voltage(2)            # A2
        self.labset(24, '%5.3f V'%v)
        v = self.eye.get_voltage(4)            # SENSOR
        self.labset(23, '%5.3f V'%v)

        res = self.eye.read_inputs()        # Set the color based on Input Levels
        if res & 1:                                # ID0
            self.ui.ID0_display.setStyleSheet(bgreen)                
        else:
            self.ui.ID0_display.setStyleSheet(bgray) 
        if res & 2:                                # ID1
            self.ui.ID1_display.setStyleSheet(bgreen) 
        else:
            self.ui.ID1_display.setStyleSheet(bgray)
        if res & 4:                                # T15 input
            self.ui.FREQ_display.setStyleSheet(bgreen)
        else:
            self.ui.FREQ_display.setStyleSheet(bgray)
        if res & 8:                                # Sensor Input
            self.ui.SEN_display_2.setStyleSheet(bgreen)
        else:
            self.ui.SEN_display_2.setStyleSheet(bgray)

        if self.NOSQR2 == False:
            freq = self.eye.get_sqr2()
            if freq > 0:
                self.labset(8,'%5.1f Hz'%freq)
            else:
                self.labset(8, '0 Hz')
                self.NOSQR2 = True

        if self.NOSF == False:
            freq = self.eye.sensor_frequency()
            if freq > 0:
                self.labset(22,'%5.1f Hz'%freq)
            else:
                self.labset(22, '0 Hz')
                self.NOSF = True

    def curveFit(self, t, v, tt=None, vv=None):
        """
        Curve fitting routine
        @param t : abscissa vector
        @param v : ordinate vector
        @param tt: abscissa vector
        @param vv: ordinate vector
        """
        if not self.measure:
            return
        if not EYEMATH:
            self.showhelp('python-scipy not installed. Required for data fitting','red')
            return
        s = ''
        if self.chanmask in (1,2):
            fa = eyemath.fit_sine(t, v)
            if fa != None:
                rms = self.eye.rms(v)
                f0 = fa[1][1] * 1000
                s = 'CH%d: %5.2f V, F= %5.2f Hz'%(self.chanmask>>1, rms, f0)
            else:
                s = 'CH%d: nosig '%(self.chanmask>>1)

        elif self.chanmask == 3:    
            fa = eyemath.fit_sine(t,v)
            if fa != None:
                rms = self.eye.rms(v)
                f0 = fa[1][1]*1000
                ph0 = fa[1][2]
                s += 'CH0: %5.2f V, F= %5.2f Hz'%(rms, f0)
            else:
                s += 'CH0: no signal'
            fb = eyemath.fit_sine(tt,vv)
            if fb != None:
                rms = self.eye.rms(vv)
                f1 = fb[1][1]*1000
                ph1 = fb[1][2]
                s = s + '<br/>CH1: %5.2f V, F= %5.2f Hz'%(rms, f1)
                if fa != None and abs(f0-f1) < f0*0.1:
                    s = s + '<br/>dphi= %5.1f'%( (ph1-ph0)*180.0/math.pi)
            else:
                s += '<br/>CH1:no signal'
        self.showhelp(s,'blue')
        return

    def showhelp(self, s, color='black'):
        """
        displays a new text in the text browser
        @param s a plain or html text
        @param color a color to span over it
        """
        self.ui.helpBrowser.clear()
        self.ui.helpBrowser.setAcceptRichText(True)
        t=QTextDocument()
        t.setHtml("<span style='color:%s;font-family:monospace;font-size:11px;'>%s</span>" %(color, s))
        self.ui.helpBrowser.setDocument(t)

    def labset(self,i,s):
        self.tw[i].setText(s)

    def twset(self,i,s):
        self.tw[i].setText(s)


if __name__=="__main__":
    from dbus.mainloop.qt import DBusQtMainLoop
    DBusQtMainLoop(set_as_default=True)
    
    app = QApplication(sys.argv)
    locale = "%s" %QLocale.system().name()
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale, "/usr/share/qt4/translations"):
        # print "OK for qttranslator"
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    for path in ["/usr/share/scolasync","."]:
        langdir=os.path.join(path,"lang",locale+".qm")
        b= appTranslator.load(langdir)
        if b:
            # print "installation du fichier de traduction", langdir
            app.installTranslator(appTranslator)
            break
    opts=[] # sould gather options from the command line
    w=mainWindow(None,opts,locale)
    w.show()

    sys.exit(app.exec_())

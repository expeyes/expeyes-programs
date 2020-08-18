from .uhope import MyFrame
import wx, gettext, os, sys
import wx.stc
from .the_keywords import setEditor, codeStyle, styles
from .examples import add_examples
from subprocess import Popen, PIPE, call

_ = gettext.gettext

class MicrohopeFrame(MyFrame):
    def __init__(self, *args, **kw):
        MyFrame.__init__(self, *args, **kw)
        add_examples(self)
        self.device = None
        self.dirname = os.getcwd()
        self.setFilename(_("unNamed"))
        self.fileType="cpp"
        self.colors="light"
        # pre-check the view->statusbar menu
        self.Microhope_menubar.i_view_statusbar.Check(True)
        self.bindEvents()
        if len(sys.argv) > 1:
            openfile = sys.argv[1]
            self.dirname = os.path.dirname(openfile)
            self.setFilename(os.path.basename(openfile))
            self.file_open_()
        return

    @property
    def path(self):
        return os.path.join(self.dirname, self.filename)

    @property
    def path_noext(self):
        return os.path.join(self.dirname, os.path.splitext(self.filename)[0])

    def bindEvents(self):
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.control.Bind(wx.EVT_CHAR, self.controlEventChar)
        return

    def controlEventChar(self, event):
        if event.ControlDown() and event.GetKeyCode() == 43 :   #Ctrl+Plus
            self.control.ZoomIn()
        elif event.ControlDown() and event.GetKeyCode() == 45:  #Ctrl+Minus
            self.control.ZoomOut()
        else:
            event.Skip()
        return

    def setFilename(self, filename):
        self.filename = filename
        self.title()
        return

    def title(self):
        """
        make the window's title
        """
        fnameWidth = 25
        def shortFilename():
            filename = self.path
            if len(filename) <= fnameWidth:
                return filename
            else:
                return "... " + filename[-(fnameWidth-4):]
        the_title = _("µHOPE :: File --> {filename:25s}\t\tDevice --> {device}")
        the_title = the_title.format(
            filename = shortFilename(),
            device = self.device
        )
        self.SetTitle(the_title)
        return
    
    def file_new(self, event):
        if self.control.IsModified():
            ok = wx.MessageDialog( self, _("Clear the editor - are you sure?"),
                                   _("Unsaved modifications ..."), wx.YES_NO).ShowModal()
            if ok == wx.ID_YES:
                self.setFilename(_("unNamed"))
                self.dirname = os.getcwd()
                self.control.SetValue("")
        else:
            self.control.SetValue("")
        return

    def file_open(self, event):
        dlg = wx.FileDialog(self, _("Choose a file"), self.dirname, "", "*.*")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            self.file_open_()
        dlg.Destroy()
        return

    def file_open_(self):
        self.control.LoadFile(self.path)
        self.fileType = "cpp"
        if self.filename.endswith(".py"):
            self.fileType="py"
        self.highlighting()
        return

    def example_open(self, filename):
        dirname = self.dirname
        self.dirname = "/usr/share/microhope/microhope"
        self.setFilename(filename)
        self.file_open_()
        self.dirname = dirname
        return
    
    def highlighting(self):
        setEditor(self.control, fileType=self.fileType)
        codeStyle(self.control, fileType=self.fileType, style=styles[self.colors])
        self.control.Colourise(0, -1)
        return

    def view_bw(self, event):
        self.colors="light"
        self.highlighting()
        return

    def view_wb(self, event):
        self.colors="dark"
        self.highlighting()
        return

    def file_save_as(self,e):
        dlg = wx.FileDialog(self, _("Choose a file"), self.dirname, "", "*.*", \
                wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.setFilename(dlg.GetFilename())
            self.dirname=dlg.GetDirectory()
            self.control.SaveFile(self.path)
        dlg.Destroy()
        
        return

    def file_save(self,e):
        if _("unNamed") in self.filename:
            self.file_save_as(e)
        else:
            self.control.SaveFile(self.path)
        return

    def file_init(self, event):
        dlg = wx.MessageDialog(None,_("Create microHope environment\nDo you want to create your own microHope environment?\n\nIf you reply \"Yes\", a subdirectory named microHope will be created in your home directory, and a set of files will be copied into it.\n\nIf any previous installation existed, its contents will be overwriten."),_("µHOPE init()"),wx.YES_NO | wx.YES_DEFAULT |  wx.ICON_QUESTION)
        chk = dlg.ShowModal()
        dlg.Destroy()
        if chk == wx.ID_YES:
            os.system("mkdir -p ~/microhope && cp -Rd /usr/share/microhope/microhope/* ~/microhope/")
            self.showMsg(_("Created microhope environment"))
        return

    def showMsg(self, msg):
        wx.LogMessage(msg)
        return
    
    def OnCloseWindow(self, event):
        if not self.control.IsModified():
            self.Destroy()
            return
        # there is something modified
        ok = wx.MessageDialog( self, _("Exit without saving the changes?"),
                        _("The source has been modified ..."), wx.YES_NO).ShowModal()
        if ok == wx.ID_YES:
            self.Destroy()
        return

    def file_exit(self, event):
        self.Close()
        return

    def view_statusbar(self, event):
        if self.Microhope_menubar.i_view_statusbar.IsChecked():
            self.Microhope_statusbar.Show()
        else:
            self.Microhope_statusbar.Hide()
        return

    def device_detect(self, event):
        devc = []
        for dev in ("ttyUSB", "ttyACM"):
            command = f"ls /dev/{dev}* 2>/dev/null"
            process=Popen(command, shell=True, stdout = PIPE, stderr = PIPE)
            out, _err = process.communicate()
            if process.returncode == 0:
                    devc += out.decode("utf-8").strip().split('\n')
        if devc == []:
            self.showMsg(_('microHOPE hardware not found?'))
            self.device = None
            self.title()
            return 
        else:
            self.device = devc[0]
            self.title()
            self.showMsg(_("Device is found at ")+ devc[0])
        return

    def device_set_bootloader(self,event):
        #self.SetTitle(_("Setting up MicroHOPE bootloader via USBASP....."))
        self.showMsg(_("Setting up MicroHOPE bootloader via USBASP.... \nIt will take few seconds"))
        command = 'avrdude -B10 -c usbasp -patmega32 -U flash:w:/usr/share/microhope/firmware/Bootloader_atmega32.hex'
        process=Popen(command, shell=True, stdout = PIPE, stderr = PIPE)
        out, err = process.communicate()
        if process.returncode != 0 :
            self.showMsg(_('Error: Check Connections....'))
            return 
        command = 'avrdude -B10 -c usbasp -patmega32 -U lfuse:w:0xff:m -U hfuse:w:0xda:m'
        process=Popen(command, shell=True, stdout = PIPE, stderr = PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            self.showMsg(_('Error: Setting up fuses'))
            return 
        self.showMsg(_('Upload Completed'))
        return
    
    def build_compile(self,event):
        self.file_save(event)
        fd = self.path
        fn = self.path_noext # the path, without the extension
        command = 'avr-gcc -Wall -O2 -mmcu=atmega32 -o %s  %s' %(fn, fd)
        process=Popen(command, shell=True, stdout = PIPE, stderr = PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            self.showMsg(_('Compilation Error :\n') + err.decode("utf-8"))
            return
        # no compilation error so far
        command = 'avr-objcopy -j .text -j .data -O ihex %s %s.hex' %(fn, fn) 
        call(command, shell=True)
        self.showMsg(_('Compilation Done'))
        return
    
    def build_assemble(self,event):
        self.file_save(event)
        fd = self.path
        fn = self.path_noext # the path, without the extension
        command = 'avr-gcc -Wall -O2 -mmcu=atmega32 -o %s %s' %(fn, fd)
        
        process=Popen(command, shell=True, stdout=PIPE, stderr = PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            self.showMsg(_('Assembler Error :\n') + err)
            return
        # avr-gcc was successful, make the .ext file
        command = 'avr-objcopy -j .text -j .data -O ihex %s %s.hex' %(fn, fn) 
        call(command, shell=True)
        # avr-objcopy was successful, make the .lst file
        command = 'avr-objdump -S %s > %s.lst'%(fn, fn)
        call(command, shell=True)
        self.showMsg(_('Assembing Done'))
        return

    def build_upload(self,event):
        if not self.device:
            self.showMsg(_('Device not selected\nA new detection will be tried'))
            self.device_detect(event)
            if not self.device:
                self.showMsg(_('No hardware was detected\nUpload filed'))
        assert (bool(self.device)) # the hardware should be detected
        fn = self.path_noext
        command= 'avrdude -b 19200 -P %s -pm32 -c stk500v1 -U flash:w:%s.hex'%(self.device, fn)
        process=Popen(command, shell=True, stdout = PIPE, stderr = PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            self.showMsg(_('Upload Error:\n') + err.decode("utf-8") + _('\nTry pressing microHOPE Reset button just before Uploading'))
            return
        else:
            self.showMsg(_('Upload Completed\n') + err.decode("utf-8"))
        return
    
    def build_upload_USBASP(self,event):
        self.showMsg(_("Uploading through USBASP ...."))
        fn = self.path_noext
        command ="avrdude -c usbasp -patmega32 -U flash:w:%s.hex"%(fn,)
        process=Popen(command, shell=True, stdout = PIPE, stderr = PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            self.showMsg(_("Check connections of USBASP"))
            return
        else:
            self.showMsg(_("Uploading via USBASP completed....."))
        return
    
class MicrohopeApp(wx.App):
    def OnInit(self):
        self.Microhope = MicrohopeFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.Microhope)
        self.Microhope.Show()
        return True
    
def run():
    gettext.install("app") # replace with the appropriate catalog name
    app = MicrohopeApp(0)
    app.MainLoop()

from .uhope import MyFrame
import wx, gettext, os, sys
import wx.stc
from .the_keywords import setEditor, codeStyle, styles
from .examples import add_examples

class MicrohopeFrame(MyFrame):
    def __init__(self, *args, **kw):
        MyFrame.__init__(self, *args, **kw)
        add_examples(self)
        self.filename = _("unNamed")
        self.dirname = os.getcwd()
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        if len(sys.argv) > 1:
            openfile = sys.argv[1]
            self.dirname = os.path.dirname(openfile)
            self.filename = os.path.basename(openfile)
            self.file_open_()
        return


    def file_new(self, event):
        if self.control.IsModified():
            ok = wx.MessageDialog( self, _("Clear the editor - are you sure?"),
                                   _("Unsaved modifications ..."), wx.YES_NO).ShowModal()
            if ok == wx.ID_YES:
                self.filename = _("unNamed")
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
        with open(os.path.join(self.dirname, self.filename)) as infile:
            self.control.SetValue(infile.read())
            self.SetTitle("Editing ... "+self.filename)
            self.control.EmptyUndoBuffer()
            self.highlighting()
        return

    def example_open(self, filename):
        dirname = self.dirname
        self.dirname = "/usr/share/microhope/microhope"
        self.filename = filename
        self.file_open_()
        self.dirname = dirname
        return
    
    def highlighting(self, style="cpp"):
        setEditor(self.control, fileType="cpp")
        codeStyle(self.control, fileType="cpp", style=styles["light"])
        self.control.Colourise(0, -1)
        return

    def file_save_as(self,e):
        dlg = wx.FileDialog(self, _("Choose a file"), self.dirname, "", "*.*", \
                wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            with open(os.path.join(self.dirname, self.filename),'w') as outfile:
                outfile.write(self.control.GetValue())
        dlg.Destroy()
        return

    def file_save(self,e):
        with open(os.path.join(self.dirname, self.filename),'w') as outfile:
            outfile.write(self.control.GetValue())
        return

    def file_init(self, event):
        dlg = wx.MessageDialog(None,_("Create microHope environment\nDo you want to create your own microHope environment?\n\nIf you reply \"Yes\", a subdirectory named microHope will be created in your home directory, and a set of files will be copied into it.\n\nIf any previous installation existed, its contents will be overwriten."),_("uHOPE init()"),wx.YES_NO | wx.YES_DEFAULT |  wx.ICON_QUESTION)
        chk = dlg.ShowModal()
        dlg.Destroy()
        if chk == wx.ID_YES:
            os.system("mkdir -p ~/microhope && cp -Rd /usr/share/microhope/microhope/* ~/microhope/")
            wx.LogMessage(_("Created microhope environment"))
        return

    def OnCloseWindow(self, event):
        ok = wx.MessageDialog( self, _("Exit - are you sure?"),
                        _("Closing ..."), wx.YES_NO).ShowModal()
        if ok == wx.ID_YES:
            self.Destroy()
        return
    
    def file_exit(self, event):
        self.Close()
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

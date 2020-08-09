from .uhope import MyFrame
import wx, gettext, os, sys
import wx.stc

class MicrohopeFrame(MyFrame):
    def __init__(self, *args, **kw):
        MyFrame.__init__(self, *args, **kw)
        self.filename = _("unNamed")
        self.dirname = os.getcwd()
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
    
    def highlighting(self, style="cpp"):
        self.control.StyleSetFont(
            wx.stc.STC_STYLE_DEFAULT,
            wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.control.ClearDocumentStyle() 
        #self.control.SetLexerLanguage(style)
        self.control.SetLexer(wx.stc.STC_LEX_CPP)
        self.control.Colourise(0, -1)
        print("tried to set the style", style)
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

    def file_exit(self, event):
        ok = wx.MessageDialog( self, _("Exit - are you sure?"),
                        _("Closing ..."), wx.YES_NO).ShowModal()
        if ok == wx.ID_YES:
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

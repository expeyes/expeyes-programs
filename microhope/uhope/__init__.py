from .uhope import MyFrame
import wx, gettext

class MicrohopeFrame(MyFrame):
    def __init__(self, *args, **kw):
        MyFrame.__init__(self, *args, **kw)
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

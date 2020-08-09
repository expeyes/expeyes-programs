from .uhope import MyFrame
import wx, gettext

class MicrohopeFrame(MyFrame):
    def __init__(self, *args, **kw):
        MyFrame.__init__(self, *args, **kw)
        """
        acceltbl = wx.AcceleratorTable( [
            (wx.ACCEL_CTRL, ord('Q'), self.Microhope_menubar.i_file_exit.GetId())
        ])
        self.SetAcceleratorTable(acceltbl)
        """
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

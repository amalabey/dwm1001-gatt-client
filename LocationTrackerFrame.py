import wx

FLOOR_PLAN_IMAGE = "demo/demo-floor-plan.png"

class LocationTrackerFame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Location Tracker')
        panel = wx.Panel(self)
        self.SetSize((890, 970))
        self.SetTitle('wx.StaticLine')
        self.Centre()

        png = wx.Image(FLOOR_PLAN_IMAGE, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(panel, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
        
        self.Show()
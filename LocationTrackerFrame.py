import wx

FLOOR_PLAN_IMAGE = "demo/demo-floor-plan.png"

class LocationTrackerFame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Location Tracker')
        self.panel = wx.Panel(self)
        self.SetSize((890, 1000))
        self.SetTitle('wx.StaticLine')
        self.Centre()

        bitmap_img = wx.Image(FLOOR_PLAN_IMAGE, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.floor_plan_img = wx.StaticBitmap(self.panel, -1, bitmap_img, (10, 5), (bitmap_img.GetWidth(), bitmap_img.GetHeight()))
        self.floor_plan_img.Bind(wx.EVT_MOTION, self.ImageCtrl_OnMouseMove)

        self.status_bar = wx.StatusBar(self.panel, -1, wx.STB_ELLIPSIZE_END, "defaultstatusbar");
        self.status_bar.SetStatusText("X={0}, Y={1}".format(0,0))
        self.SetStatusBar(self.status_bar)

        self.Show()

    def ImageCtrl_OnMouseMove(self, event):
        # position in control
        ctrl_pos = event.GetPosition()
        pos = self.floor_plan_img.ScreenToClient(ctrl_pos)
        #print("pos relative to screen top left = {0}".format())
        screen_pos = self.panel.GetScreenPosition()
        relative_pos_x = pos[0] + screen_pos[0]
        relative_pos_y = pos[1] + screen_pos[1]
        #print("pos relative to image top left = {0}, {1}".format(relative_pos_x, relative_pos_y))
        self.status_bar.SetStatusText("X={0}, Y={1}".format(relative_pos_x,relative_pos_y))

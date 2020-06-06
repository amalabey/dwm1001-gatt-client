import wx
from MarkerPanel import MarkerPanel
# from MarkerControl import MarkerControl

FLOOR_PLAN_IMAGE = 'demo/demo-floor-plan.png'
ANCHOR_IMAGE = 'demo/anchor.png'
ANCHOR_IMG_WIDTH = 50
ANCHOR_IMAGE_HEIGHT = 50

class LocationTrackerFame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Location Tracker')

        self.SetSize((890, 1000))
        self.SetTitle('wx.StaticLine')
        self.Centre()

        img = wx.Image(FLOOR_PLAN_IMAGE, wx.BITMAP_TYPE_ANY)
        bitmap_img = img.ConvertToBitmap()
        
        self.floor_plan_img = wx.StaticBitmap(self, -1, bitmap_img, (10, 5), (bitmap_img.GetWidth(), bitmap_img.GetHeight()))
        self.floor_plan_img.Bind(wx.EVT_MOTION, self.imgctrl_on_mousemove)

        self.status_bar = wx.StatusBar(self, -1, wx.STB_ELLIPSIZE_END, "defaultstatusbar");
        self.status_bar.SetStatusText("X={0}, Y={1}".format(0,0))
        self.SetStatusBar(self.status_bar)

        self.anchors = dict()
        self.tag = None
        self.overlay = wx.Overlay()

        self.Show()

    def imgctrl_on_mousemove(self, event):
        ctrl_pos = event.GetPosition()
        pos = self.floor_plan_img.ScreenToClient(ctrl_pos)
        screen_pos = self.GetScreenPosition()
        relative_pos_x = pos[0] + screen_pos[0]
        relative_pos_y = pos[1] + screen_pos[1]
        self.status_bar.SetStatusText("X={0}, Y={1}".format(relative_pos_x,relative_pos_y))

        self.draw_tracking_overlay()

    def draw_tracking_overlay(self):
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()

        self._draw_anchor(dc, "Red", 100, 200)
        self._draw_anchor(dc, "Blue", 500, 300)
        self._draw_anchor(dc, "Green", 200, 700)


    def _draw_anchor(self, dc, name, x, y):
        # Draw icon: Anchor image
        icon_img = wx.Image('demo/anchor.png', wx.BITMAP_TYPE_ANY).Scale(ANCHOR_IMG_WIDTH, ANCHOR_IMAGE_HEIGHT, wx.IMAGE_QUALITY_HIGH)
        icon_bitmap = icon_img.ConvertToBitmap()
        #icon_bitmap.SetSize(ANCHOR_IMG_WIDTH,ANCHOR_IMAGE_HEIGHT)
        dc.DrawBitmap(icon_bitmap, x, y)

        # Draw text: Name and position
        label = "{0} (x={1}mm, y={2}mm)".format(name, x, y)
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, x, y+ANCHOR_IMAGE_HEIGHT)
import wx

FLOOR_PLAN_IMAGE = 'demo/demo-floor-plan.png'
WINDOW_WIDTH = 890
WINDOW_HEIGHT = 1000

ANCHOR_IMAGE = 'demo/anchor.png'
TAG_IMAGE = 'demo/tag.png'
ICON_IMG_WIDTH = 32
ICON_IMG_HEIGHT = 32

X_OFFSET = 16
Y_OFFSET = -16

class LocationTrackerFame(wx.Frame):
    def __init__(self, device_manager, anchor_names, tag_name):
        super().__init__(parent=None, title='Location Tracker')
        self.init_location_tracking(device_manager, anchor_names, tag_name)

        self.SetSize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.SetTitle('DWM1001 Location Tracker Demo')
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

        self.add_anchor("Red", 100, 200)
        self.add_anchor("Blue", 500, 300)
        self.add_anchor("Green", 200, 700)
        self.set_tag_position(250, 250)

        self.Show()

    def init_location_tracking(self, device_manager, anchor_names, tag_name):
        self.device_manager = device_manager
        self.mac_address_mapping = {name:None for name in anchor_names}
        self.mac_address_mapping[tag_name] = None

        # We need to find the mac addresses of all anchors and tags
        device_manager.set_discovery_callback(self.dwm_node_discovered)
        device_manager.start_discovery()
        device_manager.run()

        print("completed discovering devices")

    def dwm_node_discovered(self, device_manager, device):
        print("Discovered [%s] %s" % (device.mac_address, device.alias()))
        alias = device.alias()
        if alias in self.mac_address_mapping:
            self.mac_address_mapping[alias] = device.mac_address
        
        # Check if we collected macs for all nodes
        if None not in self.mac_address_mapping.values():
            device_manager.stop()

    def imgctrl_on_mousemove(self, event):
        ctrl_pos = event.GetPosition()
        pos = self.floor_plan_img.ScreenToClient(ctrl_pos)
        screen_pos = self.GetScreenPosition()
        relative_pos_x = pos[0] + screen_pos[0]
        relative_pos_y = pos[1] + screen_pos[1]
        self.status_bar.SetStatusText("X={0}, Y={1}".format(relative_pos_x,relative_pos_y))

        self.draw_tracking_overlay()

    def add_anchor(self, name, x, y):
        self.anchors[name] = (x, y)

    def set_tag_position(self, x, y):
        self.tag = (x, y)

    def draw_tracking_overlay(self):
        dc = wx.ClientDC(self)
        font = wx.Font(pointSize = 9, family = wx.DEFAULT,
               style = wx.NORMAL, weight = wx.NORMAL,
               faceName = 'Consolas')
        dc.SetFont(font)

        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        
        # draw anchors
        if self.anchors != None:
            for name in self.anchors:
                x, y = self.anchors[name]
                self._draw_anchor(dc, name, x, y)

        # draw tag
        if self.tag != None:
            x , y = self.tag
            self._draw_tag(dc, x, y)

    def _draw_tag(self, dc, x, y):
        # Draw icon: tag image
        icon_img = wx.Image(TAG_IMAGE, wx.BITMAP_TYPE_ANY).Scale(ICON_IMG_WIDTH, ICON_IMG_HEIGHT, wx.IMAGE_QUALITY_HIGH)
        icon_bitmap = icon_img.ConvertToBitmap()
        img_x = x-(ICON_IMG_WIDTH/2)
        img_y = y-(ICON_IMG_HEIGHT)
        dc.DrawBitmap(icon_bitmap, img_x, img_y)
        dc.DrawCircle(x, y, 3)

        # Draw text: position
        label = "x={0}mm, y={0}mm".format(x, y)
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, img_x + (ICON_IMG_WIDTH - tw)/2, img_y+ICON_IMG_HEIGHT)

        # Draw lines to all anchors
        dc.SetPen(wx.Pen("gray", 1, style=wx.PENSTYLE_DOT))
        if self.anchors != None:
            for name in self.anchors:
                anchor_x, anchor_y = self.anchors[name]
                dc.DrawLine(x, y, anchor_x, anchor_y)

    def _draw_anchor(self, dc, name, x, y):
        # Draw icon: Anchor image
        icon_img = wx.Image('demo/anchor.png', wx.BITMAP_TYPE_ANY).Scale(ICON_IMG_WIDTH, ICON_IMG_HEIGHT, wx.IMAGE_QUALITY_HIGH)
        icon_bitmap = icon_img.ConvertToBitmap()
        img_x = x-(ICON_IMG_WIDTH/2)
        img_y = y-(ICON_IMG_HEIGHT/2)
        dc.DrawBitmap(icon_bitmap, img_x , img_y)

        # Draw text: Name and position
        label = "{0} (x={1}mm, y={2}mm)".format(name, x, y)
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, img_x, img_y+ICON_IMG_HEIGHT)
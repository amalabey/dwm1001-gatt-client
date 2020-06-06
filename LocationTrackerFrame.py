import wx
from dwm1001 import DwmDevice
import threading

FLOOR_PLAN_IMAGE = 'demo/demo-floor-plan.png'
WINDOW_WIDTH = 890
WINDOW_HEIGHT = 1000

ANCHOR_IMAGE = 'demo/anchor.png'
TAG_IMAGE = 'demo/tag.png'
ICON_IMG_WIDTH = 32
ICON_IMG_HEIGHT = 32


X_UI_RANGE = (16, 875)
Y_UI_RANGE = (-16, 899)

X_PHYSICAL_RANGE = (0, 3000)
Y_PHYSICAL_RANGE = (0, 3220)


LOC_RECEIVED_EVNT_TYPE = wx.NewEventType()
LOC_RECEIVED_EVNT = wx.PyEventBinder(LOC_RECEIVED_EVNT_TYPE, 1)
class LocationReceivedEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, tag_name, x_pos, y_pos):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.tag_name = tag_name
        self.x_pos = x_pos
        self.y_pos = y_pos

    def get_position(self):
        return (self.x_pos, self.y_pos)

class LocationSubscriberThread(threading.Thread):
    def __init__(self, parent, device_manager, mac_address):
        threading.Thread.__init__(self)
        self._parent = parent
        self._device_manager = device_manager
        self._mac_address = mac_address

    def run(self):
        device = DwmDevice(mac_address=self._mac_address, manager=self._device_manager, 
            location_callback=self.dwm_tag_location_received, subscribe=True)
        device.connect()
        self._device_manager.run()

    def dwm_tag_location_received(self, device_manager, device, x_pos, y_pos, quality):
        evt = LocationReceivedEvent(LOC_RECEIVED_EVNT_TYPE, -1, device.alias(), x_pos, y_pos)
        wx.PostEvent(self._parent, evt)

class LocationTrackerFame(wx.Frame):
    def __init__(self, device_manager, anchor_names, tag_name):
        super().__init__(parent=None, title='Location Tracker')

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

        self.init_location_tracking(device_manager, anchor_names, tag_name)
        # self.add_anchor("Red", 100, 200)
        # self.add_anchor("Blue", 500, 300)
        # self.add_anchor("Green", 200, 700)
        #self.set_tag_position(250, 250)

        self.Bind(LOC_RECEIVED_EVNT, self.on_location_received)
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

        # We need to get anchor positions
        device_manager.set_discovery_callback(None)
        for anchor_name in anchor_names:
            print("Finding location of {0}".format(anchor_name))
            mac_address = self.mac_address_mapping[anchor_name]
            device = DwmDevice(mac_address=mac_address, manager=device_manager, 
                location_callback=self.dwm_anchor_location_received, subscribe=False)
            device.connect()
            device_manager.run()

        # Subscribe to tag position so that we can show live view
        mac_address = self.mac_address_mapping[tag_name]
        worker = LocationSubscriberThread(self, device_manager, mac_address)
        worker.start()

    def on_location_received(self, evt):
        x_pos, y_pos = evt.get_position()
        x_pixel, y_pixel = self.convert_to_ui_coordinates(x_pos, y_pos)
        self.set_tag_position(x_pixel, y_pixel)
        self.draw_tracking_overlay()

    def dwm_anchor_location_received(self, device_manager, device, x_pos, y_pos, quality):
        print("X = {0}m , Y = {1}m, Quality= {2}, mac={3}".format(x_pos/1000, y_pos/1000, quality, device.mac_address))
        
        # add anchor with position
        anchor_name = device.alias()
        x_pixel, y_pixel = self.convert_to_ui_coordinates(x_pos, y_pos)
        self.add_anchor(anchor_name, x_pixel, y_pixel)

        if device.subscribe != True:
            device_manager.stop()

    def convert_to_ui_coordinates(self, physical_x, physical_y):
        x_pixel_start, x_pixel_end = X_UI_RANGE
        x_physical_start, x_physical_end = X_PHYSICAL_RANGE
        x_pixels_per_mm = (x_pixel_end - x_pixel_start)/(x_physical_end - x_physical_start)
        x_pixel_coord = int(physical_x * x_pixels_per_mm)

        y_pixel_start, y_pixel_end = Y_UI_RANGE
        y_physical_start, y_physical_end = Y_PHYSICAL_RANGE
        y_pixels_per_mm = (y_pixel_end - y_pixel_start)/(y_physical_end - y_physical_start)
        y_pixel_coord = int(physical_y * y_pixels_per_mm)

        return (x_pixel_coord, y_pixel_coord)
    

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
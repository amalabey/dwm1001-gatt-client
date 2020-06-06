import wx
from dwm1001 import DwmDevice
from LocationTrackerWorker import DeviceType, LocationTrackerWorker, LocationTrackerWorker, LOC_RECEIVED_EVNT
import math
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

QUALITY_THRESHOLD = 50
MIN_UPDATE_DISTANCE = 0
MAX_UPDATE_DISTANCE = 1000

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

        worker = LocationTrackerWorker(self, device_manager, anchor_names, tag_name)
        worker.start()

        # self.add_anchor("Red", 100, 200)
        # self.add_anchor("Blue", 500, 300)
        # self.add_anchor("Green", 200, 700)
        #self.set_tag_position(250, 250)

        self.Bind(LOC_RECEIVED_EVNT, self.on_location_received)
        self.Show()

    def on_location_received(self, evt):
        x_pos, y_pos = evt.get_position()
        x_pixel, y_pixel = self.convert_to_ui_coordinates(x_pos, y_pos)
        device_name = evt.get_alias()
        device_type = evt.get_type()
        quality = evt.get_quality()

        if quality > QUALITY_THRESHOLD:
            if device_type == DeviceType.ANCHOR:
                self.anchors[device_name] = (x_pixel, y_pixel, x_pos, y_pos)
                self.draw_tracking_overlay()
            else:
                if self.tag != None:
                    x,y,curr_x,curr_y = self.tag
                    distance = self.calculate_distance(x_pos, y_pos, curr_x, curr_y)
                    if distance < MIN_UPDATE_DISTANCE or distance > MAX_UPDATE_DISTANCE:
                        print("distance={0} was out of range={1} - {2}".format(distance, MIN_UPDATE_DISTANCE, MAX_UPDATE_DISTANCE))
                        return
                
                self.tag = (x_pixel, y_pixel, x_pos, y_pos)
                self.draw_tracking_overlay()
        else:
            print("Ignored x={0}, y={1}, due to poor quality={2}".format(x_pos, y_pos, quality))

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

    def calculate_distance(self, x1, y1, x2, y2):
        distance = math.sqrt(((x1-x2)**2)+((y1-y2)**2) )
        return distance

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
        font = wx.Font(pointSize = 9, family = wx.DEFAULT,
               style = wx.NORMAL, weight = wx.NORMAL,
               faceName = 'Consolas')
        dc.SetFont(font)

        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        
        # draw anchors
        if self.anchors != None:
            for name in self.anchors:
                x, y, x_mm, y_mm = self.anchors[name]
                self._draw_anchor(dc, name, x, y, x_mm, y_mm)

        # draw tag
        if self.tag != None:
            x , y, x_mm, y_mm = self.tag
            self._draw_tag(dc, x, y, x_mm, y_mm)

    def _draw_tag(self, dc, x, y, x_mm, y_mm):
        # Draw icon: tag image
        icon_img = wx.Image(TAG_IMAGE, wx.BITMAP_TYPE_ANY).Scale(ICON_IMG_WIDTH, ICON_IMG_HEIGHT, wx.IMAGE_QUALITY_HIGH)
        icon_bitmap = icon_img.ConvertToBitmap()
        img_x = x-(ICON_IMG_WIDTH/2)
        img_y = y-(ICON_IMG_HEIGHT)
        dc.DrawBitmap(icon_bitmap, img_x, img_y)
        dc.DrawCircle(x, y, 3)

        # Draw text: position
        label = "x={0} mm, y={0} mm".format(x_mm, y_mm)
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, img_x + (ICON_IMG_WIDTH - tw)/2, img_y+ICON_IMG_HEIGHT)

        # Draw lines to all anchors
        dc.SetPen(wx.Pen("gray", 1, style=wx.PENSTYLE_DOT))
        if self.anchors != None:
            for name in self.anchors:
                anchor_x, anchor_y, x_mm, y_mm = self.anchors[name]
                dc.DrawLine(x, y, anchor_x, anchor_y)

    def _draw_anchor(self, dc, name, x, y, x_mm, y_mm):
        # Draw icon: Anchor image
        icon_img = wx.Image('demo/anchor.png', wx.BITMAP_TYPE_ANY).Scale(ICON_IMG_WIDTH, ICON_IMG_HEIGHT, wx.IMAGE_QUALITY_HIGH)
        icon_bitmap = icon_img.ConvertToBitmap()
        img_x = x-(ICON_IMG_WIDTH/2)
        img_y = y-(ICON_IMG_HEIGHT/2)
        dc.DrawBitmap(icon_bitmap, img_x , img_y)

        # Draw text: Name and position
        label = "{0} (x={1} mm, y={2} mm)".format(name, x_mm, y_mm)
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, img_x, img_y+ICON_IMG_HEIGHT)
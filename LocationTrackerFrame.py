import wx
from dwm1001 import DwmDevice
from LocationTrackerWorker import DeviceType, LocationTrackerWorker, LocationTrackerWorker, LOC_RECEIVED_EVNT
import math
import numpy as np
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

QUALITY_THRESHOLD = 0

MAX_PREVIOUS_LOCATION_UPDATES = 10 # look at previous 'n' updates to calculated avg position
SKIP_LOCATION_UPDATES = 0 # ui updates after every 'n' loc update

class LocationTrackerFame(wx.Frame):
    def __init__(self, device_manager, anchor_names, tag_name):
        super().__init__(parent=None, title='Location Tracker')

        self.SetSize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.SetTitle('DWM1001 Location Tracker Demo')
        self.Centre()

        img = wx.Image(FLOOR_PLAN_IMAGE, wx.BITMAP_TYPE_ANY)
        self.bitmap_img = img.ConvertToBitmap()
        
        self.floor_plan_img = wx.StaticBitmap(self, -1, self.bitmap_img, (10, 5), (self.bitmap_img.GetWidth(), self.bitmap_img.GetHeight()))
        self.floor_plan_img.Bind(wx.EVT_MOTION, self.imgctrl_on_mousemove)

        self.status_bar = wx.StatusBar(self, -1, wx.STB_ELLIPSIZE_END, "defaultstatusbar");
        self.status_bar.SetStatusText("X={0}, Y={1}".format(0,0))
        self.SetStatusBar(self.status_bar)

        self.anchors = dict()
        self.tag = None
        self.overlay = wx.Overlay()
        self.previous_loc_updates = list()
        self.loc_update_index = 0

        worker = LocationTrackerWorker(self, device_manager, anchor_names, tag_name)
        worker.start()

        self.Show()
        self.Bind(LOC_RECEIVED_EVNT, self.on_location_received)
    
    def on_location_received(self, evt):
        x_pos, y_pos = evt.get_position()
        device_name = evt.get_alias()
        device_type = evt.get_type()
        quality = evt.get_quality()

        if quality > QUALITY_THRESHOLD:
            if device_type == DeviceType.ANCHOR:
                # Set anchor location
                x_pixel, y_pixel = self.convert_to_ui_coordinates(x_pos, y_pos)
                self.anchors[device_name] = (x_pixel, y_pixel, x_pos, y_pos)
                self.draw_tracking_overlay()
            else:
                x_norm, y_norm = self.get_normalized_location(x_pos, y_pos, quality)
                x_pixel, y_pixel = self.convert_to_ui_coordinates(x_norm, y_norm)
                
                if SKIP_LOCATION_UPDATES == 0 or self.loc_update_index == 0:
                    self.tag = (x_pixel, y_pixel, x_pos, y_pos)
                    self.draw_tracking_overlay()
                
                self.loc_update_index += 1
                if self.loc_update_index >= SKIP_LOCATION_UPDATES:
                    self.loc_update_index = 0
        else:
            print("Ignored x={0}, y={1}, due to poor quality={2}".format(x_pos, y_pos, quality))

    def get_normalized_location(self, x, y, quality):
        # Look at given number of  past loc updates to calculate average
        self.previous_loc_updates.append((x, y, quality))
        if len(self.previous_loc_updates) > MAX_PREVIOUS_LOCATION_UPDATES:
            del self.previous_loc_updates[0]
        
        # Calculate weighted average, using quality as the weight
        x_values = np.array([x for x,y,q in self.previous_loc_updates])
        y_values = np.array([y for x,y,q in self.previous_loc_updates])
        q_values = np.array([q for x,y,q in self.previous_loc_updates])

        x_avg = np.average(x_values, weights=q_values)
        y_avg = np.average(y_values, weights=q_values)

        return (x_avg, y_avg)

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

    def imgctrl_on_mousemove(self, event):
        ctrl_pos = event.GetPosition()
        pos = self.floor_plan_img.ScreenToClient(ctrl_pos)
        screen_pos = self.GetScreenPosition()
        relative_pos_x = pos[0] + screen_pos[0]
        relative_pos_y = pos[1] + screen_pos[1]
        self.status_bar.SetStatusText("X={0}, Y={1}".format(relative_pos_x,relative_pos_y))
        self.draw_tracking_overlay()

    def draw_tracking_overlay(self):
        mdc = wx.ClientDC(self)
        dc = wx.BufferedDC(mdc)
        # Draw floor plan
        dc.DrawBitmap(self.bitmap_img, 10, 5)
        
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
        x_pixel_start, x_pixel_end = X_UI_RANGE
        img_x = x-(ICON_IMG_WIDTH/2)
        img_x = x_pixel_start if img_x < x_pixel_start else img_x
        img_x = x_pixel_end if img_x > x_pixel_end else img_x

        img_y = y-(ICON_IMG_HEIGHT/2)
        dc.DrawBitmap(icon_bitmap, img_x , img_y)

        # Draw text: Name and position
        label = "{0} (x={1} mm, y={2} mm)".format(name, x_mm, y_mm)
        tw, th = dc.GetTextExtent(label)
        lbl_x = img_x + ICON_IMG_WIDTH if img_x < (x_pixel_end + x_pixel_start)/2 else img_x - tw
        lbl_y = img_y+ICON_IMG_HEIGHT
        dc.DrawText(label, lbl_x, lbl_y)
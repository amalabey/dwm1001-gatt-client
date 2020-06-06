import wx
from dwm1001 import DwmDeviceManager
from LocationTrackerFrame import LocationTrackerFame

if __name__ == '__main__':
    app = wx.App()
    device_manager = DwmDeviceManager()
    frame = LocationTrackerFame(device_manager, ["Red", "Green", "Blue"], "Tag")
    app.MainLoop()

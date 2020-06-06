from enum import Enum
from dwm1001 import DwmDevice
import threading
import wx

class DeviceType(Enum):
    ANCHOR = 1
    TAG = 2

LOC_RECEIVED_EVNT_TYPE = wx.NewEventType()
LOC_RECEIVED_EVNT = wx.PyEventBinder(LOC_RECEIVED_EVNT_TYPE, 1)
class LocationReceivedEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, alias, type, x_pos, y_pos):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._alias = alias
        self._type = type
        self._x_pos = x_pos
        self._y_pos = y_pos

    def get_position(self):
        return (self._x_pos, self._y_pos)

    def get_alias(self):
        return self._alias

    def get_type(self):
        return self._type

class LocationTrackerWorker(threading.Thread):
    def __init__(self, parent, device_manager, anchor_names, tag_name):
        threading.Thread.__init__(self)
        self._parent = parent
        self._device_manager = device_manager
        self._anchor_names = anchor_names
        self._tag_name = tag_name
        self._mac_address_mapping = {name:None for name in anchor_names}
        self._mac_address_mapping[tag_name] = None

    def run(self):
        # We need to find the mac addresses of all anchors and tags
        self._device_manager.set_discovery_callback(self.dwm_node_discovered)
        self._device_manager.start_discovery()
        self._device_manager.run()

        # We need to get anchor positions
        self._device_manager.set_discovery_callback(None)
        for anchor_name in self._anchor_names:
            print("Finding location of {0}".format(anchor_name))
            if anchor_name in self._mac_address_mapping:
                mac_address = self._mac_address_mapping[anchor_name]
                device = DwmDevice(mac_address=mac_address, manager=self._device_manager, 
                    location_callback=self.dwm_anchor_location_received, subscribe=False)
                device.connect()
                self._device_manager.run()
            else:
                print("Device: {0} is not discovered yet".format(anchor_name))


        # Subscribe to tag position so that we can show live view
        if self._tag_name in self._mac_address_mapping:
            mac_address = self._mac_address_mapping[self._tag_name]
            device = DwmDevice(mac_address=mac_address, manager=self._device_manager, 
                location_callback=self.dwm_tag_location_received, subscribe=True)
            device.connect()
            self._device_manager.run()
        else:
            print("Device: {0} is not discovered yet".format(self._tag_name))
    
    def dwm_node_discovered(self, device_manager, device):
        print("Discovered [%s] %s" % (device.mac_address, device.alias()))
        alias = device.alias()
        if alias in self._mac_address_mapping:
            self._mac_address_mapping[alias] = device.mac_address
        
        # Check if we collected macs for all nodes
        if None not in self._mac_address_mapping.values():
            device_manager.stop()

    def dwm_anchor_location_received(self, device_manager, device, x_pos, y_pos, quality):
        print("X = {0}m , Y = {1}m, Quality= {2}, mac={3}".format(x_pos/1000, y_pos/1000, quality, device.mac_address))

        if self._parent != None:
            evt = LocationReceivedEvent(LOC_RECEIVED_EVNT_TYPE, -1, device.alias(), DeviceType.ANCHOR, x_pos, y_pos)
            wx.PostEvent(self._parent, evt)
        else:
            print("ERR:Parent object not available")

        if device.subscribe != True:
            device_manager.stop()

    def dwm_tag_location_received(self, device_manager, device, x_pos, y_pos, quality):
        if self._parent != None:
            evt = LocationReceivedEvent(LOC_RECEIVED_EVNT_TYPE, -1, device.alias(), DeviceType.TAG, x_pos, y_pos)
            wx.PostEvent(self._parent, evt)
        else:
            print("ERR:Parent object not available")


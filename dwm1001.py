#!/usr/bin/python3
import argparse
import dbus
import gatt
import struct

class DwmDeviceManager(gatt.DeviceManager):
    def __init__(self, adapter_name='hci0', discovery_callback=None):
        self.discovery_callback = discovery_callback
        super(DwmDeviceManager, self).__init__(adapter_name=adapter_name)

    def device_discovered(self, device):
        if self.discovery_callback != None:
            self.discovery_callback(device)

def dwm_node_discovered(device):
    print("Discovered [%s] %s" % (device.mac_address, device.alias()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true", \
        help="Discover active DWM bluetooth devices")
    parser.add_argument("--adapter", type=str, default= "hci0",  \
        help="Bluetooth adapter to use")
    args = parser.parse_args()

    if args.discover != None:
        print("Discovering available DWM devices via bluetooth: {0}".format(args.adapter))
        manager = DwmDeviceManager(adapter_name='hci0', discovery_callback=dwm_node_discovered)
        manager.start_discovery() # todo: Need to filter by service uuid='680c21d9-c946-4c1f-9c11-baa1c21329e7'
        manager.run()

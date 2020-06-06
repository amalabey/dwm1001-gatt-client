#!/usr/bin/python3
import argparse
import dbus
import gatt
import struct

DWM_SERVICE_UUID = '680c21d9-c946-4c1f-9c11-baa1c21329e7'
DWM_LOCATION_CHARACTERISTIC_ID = '003bbdf2-c634-4b3d-ab56-7ec889b89a37'

class DwmDeviceManager(gatt.DeviceManager):
    def __init__(self, adapter_name='hci0', discovery_callback=None):
        self.discovery_callback = discovery_callback
        super(DwmDeviceManager, self).__init__(adapter_name=adapter_name)

    def set_discovery_callback(self, discovery_callback):
        self.discovery_callback = discovery_callback

    def device_discovered(self, device):
        if self.discovery_callback != None:
            self.discovery_callback(self, device)

class DwmDevice(gatt.Device):
    def __init__(self, mac_address, manager, location_callback=None, subscribe=False):
        self.subscribe = subscribe
        self.location_callback = location_callback
        super(DwmDevice, self).__init__(mac_address=mac_address, manager=manager)

    def services_resolved(self):
        super().services_resolved()
        self._read_location()

    def characteristic_value_updated(self, characteristic, value):
        self._decode_location(value)

    def _read_location(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == DWM_SERVICE_UUID)

        location_data_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == DWM_LOCATION_CHARACTERISTIC_ID)
        
        if self.subscribe == True:
            location_data_characteristic.enable_notifications()

        location_data_characteristic.read_value()
    
    def _decode_location(self, location_data):
        encoded_bytes = [int(v) for v in location_data]

        # LOCATION ENCODING: <1 byte - Type><4 bytes-x pos><4 bytes-y pos><4 bytes-z pos><1 byte-quality>
        if len(encoded_bytes) >= 14:
            x_pos = self._get_pos(encoded_bytes[1:5])
            y_pos = self._get_pos(encoded_bytes[5:9])
            quality = encoded_bytes[13]
            if self.location_callback != None:
                self.location_callback(self.manager, self, x_pos, y_pos, quality)
        else:
            print("Invalid location data received: length={0}".format(len(encoded_bytes)))

    def _get_pos(self, encoded_location):
        pos_bytes = bytearray(encoded_location)
        pos, = struct.unpack('<i', pos_bytes)
        return pos


def dwm_node_discovered(device_manager, device):
    print("Discovered [%s] %s" % (device.mac_address, device.alias()))

def dwm_location_received(device_manager, device, x_pos, y_pos, quality):
    print("X = {0}m , Y = {1}m, Quality= {2}, mac={3}".format(x_pos/1000, y_pos/1000, quality, device.mac_address))
    if device.subscribe != True:
        device_manager.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true", help="Discover active DWM bluetooth devices")
    parser.add_argument("--adapter", type=str, default= "hci0", help="Bluetooth adapter to use")
    parser.add_argument("--readlocation", action="store_true", help="Read location from the dwm device")
    parser.add_argument("--continous", action="store_true", help="Continously read location from the device")
    parser.add_argument("--mac", type=str, help="Target device mac address")

    args = parser.parse_args()

    if args.discover == True:
        print("Discovering available DWM devices via bluetooth: {0}".format(args.adapter))
        manager = DwmDeviceManager(adapter_name=args.adapter, discovery_callback=dwm_node_discovered)
        # todo: Need to filter by service uuid='680c21d9-c946-4c1f-9c11-baa1c21329e7'
        manager.start_discovery()
        manager.run()
    elif args.readlocation == True:
        print("Reading location data from: {0}".format(args.mac))
        manager = DwmDeviceManager(adapter_name=args.adapter, discovery_callback=dwm_node_discovered)
        if args.continous:
            device = DwmDevice(mac_address=args.mac, manager=manager, location_callback=dwm_location_received, subscribe=True)
        else:
            device = DwmDevice(mac_address=args.mac, manager=manager, location_callback=dwm_location_received, subscribe=False)

        device.connect()
        manager.run()
    

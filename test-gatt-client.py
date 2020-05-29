import gatt
import struct

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()
        self.read_location()

    def characteristic_value_updated(self, characteristic, value):
        #print("locationdata: %s" % value.decode("utf-8"))
        self.decode_location(value)

    def read_location(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == '680c21d9-c946-4c1f-9c11-baa1c21329e7')

        location_data_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == '003bbdf2-c634-4b3d-ab56-7ec889b89a37')
        location_data_characteristic.enable_notifications()
        location_data = location_data_characteristic.read_value()
        self.decode_location(location_data)
    
    def decode_location(self, location_data):
        encoded_bytes = [int(v) for v in location_data]

        loc_type = encoded_bytes[0:1]
        x_pos = self.get_pos(encoded_bytes[1:5])
        y_pos = self.get_pos(encoded_bytes[5:9])
        quality = encoded_bytes[12]

        if quality == 0:
            print("Type = {0}, X = {1} , Y = {2}, Quality= {3}".format(loc_type, x_pos, y_pos, quality))

    def get_pos(self, encoded_location):
        pos_bytes = bytearray(encoded_location)
        pos = struct.unpack('<i', pos_bytes)
        return pos

device = AnyDevice(mac_address='c2:e2:ca:93:6b:ef', manager=manager)
device.connect()

manager.run()
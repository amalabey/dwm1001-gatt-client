import gatt

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

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))

        self.read_location()

    def read_location(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == '680c21d9-c946-4c1f-9c11-baa1c21329e7')

        location_data_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == '003bbdf2-c634-4b3d-ab56-7ec889b89a37')

        location_data = location_data_characteristic.read_value()
        print("Location Data: [%s]" % (location_data))
        print("Location data length: %d" % len(location_data))


device = AnyDevice(mac_address='c2:e2:ca:93:6b:ef', manager=manager)
device.connect()

manager.run()
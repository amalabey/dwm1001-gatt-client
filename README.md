# Setup

follow (instructions)[https://github.com/getsenic/gatt-python] to setup gatt, dbus for python in linux.


## Experiment: Read all gatt characteristics of a Tag
Example output:
```
[c2:e2:ca:93:6b:ef] Connected
[c2:e2:ca:93:6b:ef] Resolved services
[c2:e2:ca:93:6b:ef]  Service [680c21d9-c946-4c1f-9c11-baa1c21329e7]
[c2:e2:ca:93:6b:ef]    Characteristic [0eb2bc59-baf1-4c1c-8535-8a0204c69de5]
[c2:e2:ca:93:6b:ef]    Characteristic [f4a67d7d-379d-4183-9c03-4b6ea5103291]
[c2:e2:ca:93:6b:ef]    Characteristic [ed83b848-da03-4a0a-a2dc-8b401080e473]
[c2:e2:ca:93:6b:ef]    Characteristic [5955aa10-e085-4030-8aa6-bdfac89ac32b]
[c2:e2:ca:93:6b:ef]    Characteristic [9eed0e27-09c0-4d1c-bd92-7c441daba850]
[c2:e2:ca:93:6b:ef]    Characteristic [5b10c428-af2f-486f-aee1-9dbd79b6bccb]
[c2:e2:ca:93:6b:ef]    Characteristic [28d01d60-89de-4bfa-b6e9-651ba596232c]
[c2:e2:ca:93:6b:ef]    Characteristic [17b1613e-98f2-4436-bcde-23af17a10c72]
[c2:e2:ca:93:6b:ef]    Characteristic [1e63b1eb-d4ed-444e-af54-c1e965192501]
[c2:e2:ca:93:6b:ef]    Characteristic [80f9d8bc-3bff-45bb-a181-2d6a37991208]
[c2:e2:ca:93:6b:ef]    Characteristic [7bd47f30-5602-4389-b069-8305731308b6]
[c2:e2:ca:93:6b:ef]    Characteristic [f0f26c9b-2c8c-49ac-ab60-fe03def1b40c]
[c2:e2:ca:93:6b:ef]    Characteristic [a02b947e-df97-4516-996a-1882521e0ead]
[c2:e2:ca:93:6b:ef]    Characteristic [003bbdf2-c634-4b3d-ab56-7ec889b89a37]
[c2:e2:ca:93:6b:ef]    Characteristic [3f0afd88-7770-46b0-b5e7-9fc099598964]
[c2:e2:ca:93:6b:ef]  Service [00001801-0000-1000-8000-00805f9b34fb]
```


## GUI Demo
Install wxpython:
```
pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04/ wxPython
```
Install depencies:
```
sudo apt-get install git curl libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0
```

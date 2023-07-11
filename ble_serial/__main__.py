import asyncio, logging
from threading import Thread
from ble_serial.bleak.backends.characteristic import BleakGATTCharacteristic
from ble_serial.bluetooth.ble_interface import BLE_interface
import socket
from .parser import DBParser

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
addr = ("localhost", 42069)
p = DBParser()

def start_plotter():
    import os
    os.system("rlplot")

Thread(target=start_plotter).start()

def receive_callback(handle: BleakGATTCharacteristic, value: bytes):
    print("Received:", value)
    p.add_data(handle.handle, value)
    d = p.pop_data()
    while d != None:
        print(d)
        client_socket.sendto(f"{d[1]};{d[0]}".encode(), addr)
        d = p.pop_data()

async def hello_sender(ble: BLE_interface):
    while True:
        await asyncio.sleep(3.0)
        print("Sending...")
        ble.queue_send(b"Hello world\n")

async def main():
    READ_UUID = ['00009a66-0000-1000-8000-00805f9b34fb']

    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = 'D973F2E1-B19E-11E2-9E96-0800200C9A66'
    DEVICE = "02:80:E1:00:00:AA"

    ble = BLE_interface(ADAPTER, SERVICE_UUID)
    ble.set_receiver(receive_callback)

    try:
        await ble.connect(DEVICE, "public", 16.0)
        await ble.setup_chars(WRITE_UUID, READ_UUID, "r")

        await ble.send_loop()
    finally:
        await ble.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(main())

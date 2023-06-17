from array import array
import asyncio, logging
from threading import Thread

from ble_serial.bluetooth.ble_interface import BLE_interface
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
addr = ("localhost", 42069)

def start_plotter():
    import os
    #os.system("cd t-c-plotter && bin/plotter")
    os.system("cd raylib-plotter && ./bin/rlplot")

#Thread(target=start_plotter).start()

def receive_callback(value: bytes):
    b = array("h")
    b.frombytes(value)
    bs = b.tolist()
    for i, b in enumerate(bs):
        if b != 0:
            logging.info(f"Sending: {b};{i}")
            client_socket.sendto(f"{b};{i}".encode(), addr)
    print("Received:", value)

async def hello_sender(ble: BLE_interface):
    while True:
        await asyncio.sleep(3.0)
        print("Sending...")
        ble.queue_send(b"Hello world\n")

async def main():
    # None uses default/autodetection, insert values if needed
    READ_UUID = ['00009a66-0000-1000-8000-00805f9b34fb']

    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = 'D973F2E1-B19E-11E2-9E96-0800200C9A66'
    #READ_UUID = 'D973F2E0-B19E-11E2-9E96-0800200C9A66'
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
    logging.basicConfig(level=logging.NOTSET)
    asyncio.run(main())

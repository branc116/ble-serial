import asyncio, logging
from threading import Thread
from ble_serial.bleak.backends.characteristic import BleakGATTCharacteristic
from ble_serial.bluetooth.ble_interface import BLE_interface
import socket
from .parser import DBParser

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
addr = ("127.0.0.1", 42069)
p = DBParser()
f = open("out.csv", "w+")

class stataus:
    def __init__(self) -> None:
        self.last_rcevid: int = 0
        self.lps: int = 0
        self.lps_r: int = 0

st = stataus()

def receive_callback(handle: BleakGATTCharacteristic, value: bytes):
    print("Received:", value)
    p.add_data(handle.handle, value)
    d = p.pop_data()
    while d != None:
        print(d)
        #f.write(f"{d[1]},")
        if d[0] == 1307:
            if d[1] > st.last_rcevid + 1:
                st.lps += int(d[1]) - int(st.last_rcevid) - int(1)
                st.lps_r += int(d[1]) - int(st.last_rcevid) - int(1)
            st.last_rcevid = int(d[1])
        client_socket.sendto(f"{d[1]};{d[0]} ".encode(), addr)
        d = p.pop_data()
    #f.write(f"{st.lps}\n")
    client_socket.sendto(f"{st.lps};10 {st.lps_r};11 ".encode(), addr)
    #print(f"LOST PACKETS: {st.lps}")

    #f.flush()


# nc -ulkp 42069 | rlplot

async def hello_sender(ble: BLE_interface):
    while True:
        await asyncio.sleep(3.0)
        print("Sending...")
        ble.queue_send(b"Hello world\n")

async def main():
    st.lps_r = 0
    try:
        READ_UUID = ['00009a66-0000-1000-8000-00805f9b34fb']

        ADAPTER = "hci0"
        SERVICE_UUID = None
        WRITE_UUID = 'D973F2E1-B19E-11E2-9E96-0800200C9A66'
        DEVICE = "02:80:E1:00:00:AA"

        ble = BLE_interface(ADAPTER, SERVICE_UUID)
        ble.set_receiver(receive_callback)

        await ble.disconnect();
    except BaseException:
        print("E2!\n")
        return
    finally:
        pass

    try:
        await ble.connect(DEVICE, "public", 16.0)
        await ble.setup_chars(WRITE_UUID, READ_UUID, "r")
        await ble.send_loop()
    except asyncio.exceptions.CancelledError:
        await ble.disconnect()
        print("asio EXITING!\n")
        print("asio EXITING!\n")
        print("asio EXITING!\n")
        print("asio EXITING!\n")
        exit(-1)
    except BaseException as be:
        print(f"{type(be)} E1!\n")
        logging.error(str(be))
    finally:
        await ble.disconnect()

if __name__ == "__main__":
    while True:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())


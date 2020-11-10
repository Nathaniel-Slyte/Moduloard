import asyncio
import platform
import Interface
from bleak import discover, BleakClient

from myqueue import DATA_QUEUE

BPClist = []
MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
UUID_NORDIC_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NORDIC_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

table = ""

def UARTDataReceived(sender, data):
    global table
    i = 0
    while i < len(data) :
        # print(data[i] -1)
        if int(data[i]) == 0:
            print(table)
            print("LA BAS", id(DATA_QUEUE))
            DATA_QUEUE.put(table)
            i = len(data)
            table = ""
        else :
            table += str(data[i]-1) + ","
        i += 1

async def Snif():
    devices = await discover(timeout= 2.0)
    for d in devices:
        print(d)
        if (d.name == "BPC"):
            BPClist.append(d.address)

async def ConnectUART(address, loop):
    
    disconnected_event = asyncio.Event()

    def disconnected_callback(client):
        print("Disconnected callback called!")
        disconnected_event.set()

    async with BleakClient(address, loop=loop, disconnected_callback=disconnected_callback) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        await client.start_notify(UUID_NORDIC_RX, UARTDataReceived)
        while True :
            await asyncio.sleep(2.0, loop=loop)
            # await client.write_gatt_char(UUID_NORDIC_TX, bytearray(b"0"), True)

async def GetUUID(address: str, loop):

    async with BleakClient(address, loop = loop) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        for service in client.services:
            if (service.description == "Nordic UART Service"):

                print("[Service] {0}: {1}".format(service.uuid, service.description))
                for char in service.characteristics:
                    if "notify" in char.properties:
                        UUID_NORDIC_RX = char.uuid
                    if "write" in char.properties:
                        UUID_NORDIC_TX = char.uuid
                        try:
                            value = bytes(await client.read_gatt_char(char.uuid))
                        except Exception as e:
                            value = str(e).encode()
                    else:
                        value = None
                    print(
                        "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                            char.uuid,
                            char.handle,
                            ",".join(char.properties),
                            char.description,
                            value,
                        )
                    )


def Main():
    # loop = asyncio.get_event_loop()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    try:
        while len(BPClist) == 0 :
            loop.run_until_complete(Snif())
        print("Found BPC, address : {}".format(BPClist[0]))

        loop.run_until_complete(GetUUID(BPClist[0], loop))
        loop.run_until_complete(ConnectUART(BPClist[0], loop))
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    Main()
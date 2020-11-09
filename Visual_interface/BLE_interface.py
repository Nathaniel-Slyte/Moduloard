import asyncio
import platform
import Interface
from bleak import discover, BleakClient

BPClist = []
MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
UUID_NORDIC_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NORDIC_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

pos = 0

def UARTDataReceived(sender, data):
    # ###############################
    # A refaire, c'est de la merde.
    # Renvoyer toute la matrice dans la queue sous la forme d'un string et la parse de l'autre côté
    global pos
    if pos >= (Interface.NB_ROW * Interface.NB_COLOMN):
        pos = 0
    data = data.decode()
    data = data.split(",")
    for i in data:
        if i != "":
            Interface.data_queue[pos] = i
            print("RX> {0}".format(i))
            pos += 
    
    # print("RX> {0}".format(str(data)))

async def Snif():
    devices = await discover(timeout= 2.0)
    for d in devices:
        print(d)
        if (d.name == "BPC"):
            BPClist.append(d.address)

async def ConnectUART(address, loop):
    async with BleakClient(address, loop=loop) as client:
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

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    while len(BPClist) == 0 :
        loop.run_until_complete(Snif())
    print("Found BPC, address : {}".format(BPClist[0]))
    # loop.run_until_complete(PrintServices(BPClist[0]))
    loop.run_until_complete(GetUUID(BPClist[0], loop))
    loop.run_until_complete(ConnectUART(BPClist[0], loop))
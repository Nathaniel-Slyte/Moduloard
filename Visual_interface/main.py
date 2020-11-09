import asyncio
import logging
import platform
from bleak import discover, BleakClient

BPClist = []
MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
UUID_NORDIC_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NORDIC_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"


def uart_data_received(sender, data):
    print("RX> {0}".format(data))

async def snif():
    devices = await discover(timeout= 2.0)
    for d in devices:
        print(d)
        if (d.name == "BPC"):
            BPClist.append(d.address)

async def connect(address):
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

async def receiveData(address, loop):
    async with BleakClient(address, loop=loop) as client:
        print("Connected")
        await client.start_notify(UUID_NORDIC_RX, uart_data_received)
        while True :
            await asyncio.sleep(2.0, loop=loop)

async def print_services(address: str):
    async with BleakClient(address) as client:
        print("Connected")
        svcs = await client.get_services()
        print("Services:", svcs)

async def run(address, debug=False):

    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        for service in client.services:
            if (service.description == "Nordic UART Service"):

                print("[Service] {0}: {1}".format(service.uuid, service.description))
                for char in service.characteristics:
                    if "notify" in char.properties:
                        UUID_NORDIC_RX = char.uuid
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
                    # for descriptor in char.descriptors:
                    #     value = await client.read_gatt_descriptor(descriptor.handle)
                    #     print(
                    #         "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                    #             descriptor.uuid, descriptor.handle, bytes(value)
                    #         )
                    #     )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while len(BPClist) == 0 :
        loop.run_until_complete(snif())
    print("Found BPC, address : {}".format(BPClist[0]))
    # loop.run_until_complete(connect(BPClist[0]))
    # loop.run_until_complete(print_services(BPClist[0]))
    loop.set_debug(True)
    loop.run_until_complete(run(BPClist[0]))
    loop.run_until_complete(receiveData(BPClist[0], loop))
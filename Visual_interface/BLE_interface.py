import asyncio
from bleak import discover, BleakClient
from queue import Queue

from myqueue import DATA_QUEUE


class Device:
    def __init__(self, address: str, queue_init):
        self.DATA_QUEUE         = queue_init
        print(id(self.DATA_QUEUE))
        self.UUID_NORDIC_TX     = ""
        self.UUID_NORDIC_RX     = ""
        self.table              = ""
        self.address            = address

        self.disconnected_event = asyncio.Event()
        self.loop               = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)


    def Connect (self):
        try:
            self.loop.run_until_complete(self.UARTUUID())
            self.loop.run_until_complete(self.ConnectUART())
        except (KeyboardInterrupt, SystemExit):
            pass
    
    def disconnected_callback(self,client):
            print("Disconnected callback called!")
            self.disconnected_event.set()

    async def UARTUUID(self):

        async with BleakClient(self.address, loop = self.loop) as client:
            x = await client.is_connected()
            # print("Connected: {0}".format(x))

            for service in client.services:
                if (service.description == "Nordic UART Service"):

                    # print("[Service] {0}: {1}".format(service.uuid, service.description))
                    for char in service.characteristics:
                        if "notify" in char.properties:
                            self.UUID_NORDIC_RX = char.uuid
                        if "write" in char.properties:
                            self.UUID_NORDIC_TX = char.uuid
                            
                        # print("\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(char.uuid, char.handle, ",".join(char.properties), char.description,))

    async def ConnectUART(self):

        async with BleakClient(self.address, loop=self.loop, disconnected_callback=self.disconnected_callback) as client:
            x = await client.is_connected()
            print("Connected: {0}".format(x))

            await client.start_notify(self.UUID_NORDIC_RX, self.UARTDataReceived)
            print("Notify enable")
            while True :
                await asyncio.sleep(1.0, loop=self.loop)
                # await client.write_gatt_char(UUID_NORDIC_TX, bytearray(b"0"), True)
    
    def UARTDataReceived(self, sender, data):
        i = 0
        while i < len(data) :
            # print(data[i] -1)
            if int(data[i]) == 0:
                print(self.table)
                # print("LA BAS", id(DATA_QUEUE))
                if len(self.table.split(',')) >= 21*12-1:
                    self.DATA_QUEUE.put(self.table)
                i = len(data)
                self.table = ""
            else :
                self.table += str(data[i]-1) + ","
            i += 1


async def Snif(address_list):
    devices = await discover(timeout= 1.0)
    for d in devices:
        #print(d)
        if (d.name == "BPC"):
            address_list.append(d.address)


def GetAddress():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    BPClist = []

    i = 0
    while i < 5 :
            loop.run_until_complete(Snif(BPClist))
            i += 1
    i = 0
    BPClist = list(set(BPClist))
    while i < len(BPClist):
        print("Found BPC, address : {}".format(BPClist[i]))
        i +=1
    return BPClist


def main(address, my_queue):
    device1 = Device(address, my_queue)
    device1.Connect()


if __name__ == '__main__':
    # Main()
    address = GetAddress()
    try:
        print("Create a class")
        # device1 = Device(address[0])
        print("start Connection")
        # device1.Connect()
    except (KeyboardInterrupt, SystemExit):
        pass

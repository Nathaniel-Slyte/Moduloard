import asyncio
from bleak import discover, BleakClient
import queue
# from queue import Queue


class Device:
    def __init__(self, loop, address: str):
        self.DATA_QUEUE         = queue.Queue(maxsize=10)
        self.MESSAGE_QUEUE      = queue.Queue(maxsize=10)
        self.UUID_NORDIC_TX     = ""
        self.UUID_NORDIC_RX     = ""
        self.X                  = 0
        self.Y                  = 0
        self.table              = ""
        self.address            = address
        self.active             = True

        self.disconnected_event = asyncio.Event()
        self.loop               = loop
        # self.loop               = asyncio.new_event_loop()
        # asyncio.set_event_loop(self.loop)



    async def Connect (self):
        try:
            await self.UARTUUID()
            await self.ConnectUART()
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
            while self.active :
                await asyncio.sleep(1.0, loop=self.loop)
                # await client.write_gatt_char(self.UUID_NORDIC_TX, bytearray(b"MUCA!"), True)
                try :
                    item = self.MESSAGE_QUEUE.get(block = False)
                except queue.Empty:
                    pass
                else :
                    self.MESSAGE_QUEUE.task_done()
                    await client.write_gatt_char(self.UUID_NORDIC_TX, bytearray(item), True)
    

    def UARTDataReceived(self, sender, data):
        i = 0
        while i < len(data) :

            if int(data[i]) == 0:
                print("my addresse : {}".format(self.address))
                if len(self.table.split(',')) >= 21*12-1:
                    try:
                        self.DATA_QUEUE.put(self.table, block = False)
                    except queue.Full:
                        self.Dequeue()
                        self.DATA_QUEUE.put(self.table, block = False)
                i = len(data)
                self.table = ""

            else :
                self.table += str(data[i]-1) + ","

            i += 1

#### START SCREEN FUNCTIONS ####

    def Dequeue(self):
        # print("Je fonctionne à 60 FPS avec l'addresse {}".format(self.address))
        try :
            item = self.DATA_QUEUE.get(block = False)
        except queue.Empty:
            return "0"
        else :
            self.DATA_QUEUE.task_done()
            return item
    
    def UpdatePos(self, X, Y):
        self.X = X
        self.Y = Y

    def AddMessageQueue(self, message):
        self.MESSAGE_QUEUE.put(message, block = False)

    def StopDevice(self):
        self.active = False


################################# END CLASS DEVICE #################################

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


async def main(loop ,address, my_queue):

    try:
        device = Device(loop, address, my_queue)
        print ("device created : {}".format(address))
        device.Connect()
        print ("device connected : {}".format(address))
    except (KeyboardInterrupt, SystemExit):
        pass



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

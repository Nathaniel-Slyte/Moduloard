import pygame 
import BLE_interface
import asyncio

from queue import Queue
from datetime import datetime



NB_ROW          = 21
NB_COLOMN       = 12
SIZE_PIXEL      = 40

DEVICE_QUEUE    = []
DEVICE          = []
PIXELS          = []

def Dequeue(device : int):
    item = DEVICE_QUEUE[device].get()
    # DEVICE_QUEUE.task_done()
    return item

def DataParser(data : str):
    data = data.split(",")
    data.pop()
    return data


def PixelsInit(screen, device : int):
    rgb = 0
    table = ""
    while rgb < (NB_ROW*NB_COLOMN):
        table += str(0) + ","
        PIXELS.append(pygame.Surface((SIZE_PIXEL,SIZE_PIXEL)))
        rgb+=1
    DEVICE_QUEUE[device].put(table)
    data_table = DataParser(table)
    SetPixels(screen, data_table)


def SetPixels(screen, data_table):
    posX = 0
    posY = 0
    while posY < NB_ROW:
        while posX < NB_COLOMN:

            pos = posY * NB_COLOMN + posX                                       # Position in the X Y matrix
            rgb = int(data_table[pos])                                          # RGB value for pixel
            PIXELS[pos].fill((rgb, rgb, rgb))                                   # set color of the pixel (3x rgb because grey) 
            screen.blit(PIXELS[pos], (posX * SIZE_PIXEL, posY * SIZE_PIXEL))    # update color of the pixel
            
            posX+=1
        posY+=1
        posX =0
    print ("Pixels set !")

def UpdatePixels(screen, device :int):
    raw_table = Dequeue(device)
    # if not raw_table:
    #     return False
    data_table = DataParser(raw_table)
    SetPixels(screen, data_table)
    
    return True





async def clock():
    while True:
        print('The time:', datetime.now())
        await asyncio.sleep(1)





def main():

    # Initialize pygame module
    pygame.init()

    # create a surface on screen that has the size of 240 x 180
    my_screen = pygame.display.set_mode((NB_COLOMN * SIZE_PIXEL* len(DEVICE_QUEUE) , NB_ROW * SIZE_PIXEL))
    
    # define a variable to control the main loop
    running = True
    PixelsInit(my_screen, 0)
    
    print("Entered Main Pygame")

    # main loop
    while running:
        state = UpdatePixels(my_screen, 0)
        # if state == True :
        pygame.display.flip() # Update values on screen
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
     


if __name__ == '__main__':
    print("Interface file connected")
    loop = asyncio.get_event_loop()
    address = BLE_interface.GetAddress()

    for i in address:
        DEVICE_QUEUE.append(Queue(maxsize=10))

    # DEVICE_QUEUE = Queue(maxsize=10)
    # print(id(DEVICE_QUEUE))
    try:
        pygame_task = loop.run_in_executor(None,main)
        # for i in range(len(address)):
        #     DEVICE.append(asyncio.ensure_future(BLE_interface.main(loop, address[i], DEVICE_QUEUE[i])))
        loop.create_task(clock())
        loop.create_task(BLE_interface.main(loop, address[0], DEVICE_QUEUE[0]))
        # loop.create_task(BLE_interface.main(loop, address[1], DEVICE_QUEUE[1]))

            
    except (KeyboardInterrupt, SystemExit):
        loop.stop()
        # pass



    # print("Connection")
    # device1 = BLE_interface.Device(address[0], DEVICE_QUEUE)
    # threading.Thread(target=device1.Connect(), daemon=True).start()
    # except (KeyboardInterrupt, SystemExit):
    #     pass
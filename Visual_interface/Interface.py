import pygame 
import BLE_interface
import asyncio

from pygame.locals import *
from queue import Queue
from datetime import datetime

FPS = 30

NB_ROW          = 21
NB_COLOMN       = 12
SIZE_PIXEL      = 8
SCREEN_LENGTH   = 1280
SCREEN_WIDTH    = 720

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





def main():

    # Initialize pygame module
    pygame.init()
    
    FramePerSec = pygame.time.Clock()

    # Initiate the pygame screen
    my_screen = pygame.display.set_mode((SCREEN_LENGTH , SCREEN_WIDTH))
    
    # define a variable to control the main loop
    running = True
    PixelsInit(my_screen, 0)
    
    print("Entered Main Pygame")

    # main loop
    while running:
        state = UpdatePixels(my_screen, 0)
        # if state == True :
        pygame.display.update() # Update values on screen
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
                pygame.quit()
                sys.exit()
                
        FramePerSec.tick(FPS)
     


if __name__ == '__main__':
    print("Interface file connected")
    loop = asyncio.get_event_loop()
    address = BLE_interface.GetAddress()

    for i in address:
        DEVICE_QUEUE.append(Queue(maxsize=10))

    try:
        pygame_task = loop.run_in_executor(None,main)

        for i in range(len(address)):
            DEVICE.append(BLE_interface.Device(loop, address[i], DEVICE_QUEUE[i]))
            print ("device created : {}".format(address[i]))

        for i in range(len(address)):
            loop.create_task(DEVICE[i].Connect())
        # loop.create_task(DEVICE[0].Connect())
        # loop.create_task(DEVICE[1].Connect())

        loop.run_forever()
            
    except (KeyboardInterrupt, SystemExit):
        loop.stop()
        # pass


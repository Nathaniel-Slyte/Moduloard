import pygame 
import BLE_interface
import asyncio
import sys

from pygame.locals import *
from queue import Queue
from datetime import datetime

FPS = 30

NB_ROW          = 21
NB_COLOMN       = 12
SIZE_PIXEL      = 16
SCREEN_LENGTH   = 1280
SCREEN_WIDTH    = 720

DEVICE          = []

# try:
#     DEVICE[device].PixelsSet(pixels)
# except: # catch *all* exceptions
#     e = sys.exc_info()[0]
#     print("Error: {}".format(e) )

def DataParser(data : str):
    data = data.split(",")
    data.pop()
    return data

def SetPixels(screen, data_table, X, Y):
    print("X: {} Y: {}".format(X,Y))
    pixel = pygame.Surface((SIZE_PIXEL,SIZE_PIXEL))
    
    for y in range(NB_ROW):
        for x in range(NB_COLOMN):

            pos = y * NB_COLOMN + x                               # Position in the X Y matrix
            rgb = int(data_table[pos])                                          # RGB value for pixel
            pixel.fill((rgb, rgb, rgb))                                         # set color of the pixel (3x rgb because grey)
            screen.blit(pixel, (X + x * SIZE_PIXEL, Y + y * SIZE_PIXEL))          # update color of the pixel

    print ("Pixels set !")

def UpdatePixels(screen, device :int):
    raw_table = DEVICE[device].Dequeue()
    if raw_table == "0":
        return False
    else :
        # print(raw_table)
        data_table = DataParser(raw_table)
        SetPixels(screen, data_table, DEVICE[device].X, DEVICE[device].Y)
        # SendMessage("Message received !", device)
        return True

def SendMessage(message: str, device: int):
    message = message.encode('utf-8')
    DEVICE[device].AddMessageQueue(message)

def StopAllDevices():
    for i in range(len(DEVICE)):
        DEVICE[i].StopDevice()

def DetectPos():
    print("Start to update positions !")
    DEVICE[0].UpdatePos(150 , 150  )
    DEVICE[1].UpdatePos(DEVICE[0].X + SIZE_PIXEL*NB_COLOMN + 40, DEVICE[0].Y )

def main():

    # Initialize pygame module
    pygame.init()
    
    FramePerSec = pygame.time.Clock()

    # Initiate the pygame screen
    my_screen = pygame.display.set_mode((SCREEN_LENGTH , SCREEN_WIDTH))

    running = True
    DetectPos()

    # main loop
    while running:
        try:
            for i in range(len(DEVICE)):  
                state = UpdatePixels(my_screen, i)
            pygame.display.update() # Update values on screen
        except:
            e = sys.exc_info()[0]
            print("Error: {}".format(e) )
            print("Can not update !")

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

                StopAllDevices()
                pygame.quit()
                sys.exit()
                
        FramePerSec.tick(FPS)
     


if __name__ == '__main__':
    print("Interface file connected")
    loop = asyncio.get_event_loop()
    address = BLE_interface.GetAddress()

    try:

        for i in range(len(address)):
            DEVICE.append(BLE_interface.Device(loop, address[i]))
            print ("device created : {}".format(address[i]))

        pygame_task = loop.run_in_executor(None,main)

        for i in range(len(address)):
            loop.create_task(DEVICE[i].Connect())

        loop.run_forever()
            
    except (KeyboardInterrupt, SystemExit):
        try:
            StopAllDevices()
        except:
            pass
        loop.stop()
        # pass


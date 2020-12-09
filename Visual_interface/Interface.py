import pygame 
import BLE_interface
import asyncio
import sys

from pygame.locals import *
from queue import Queue
from datetime import datetime

pygame.init()

FPS = 30

NB_ROW          = 21
NB_COLOMN       = 12
SIZE_PIXEL      = 16
SCREEN_WIDTH   = 1280
SCREEN_HEIGHT    = 720

DEVICE          = []

GREY            = (120,120,120)
GREY_LIGHT      = (170,170,170)  
GREY_DARK       = (80,80,80) 
WHITE           = (255,255,255)


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
            
            if rgb >255:
                rgb = 255
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

def InterfaceInit(screen):
    pygame.draw.rect(screen,GREY,(SCREEN_WIDTH-300, 0, 300, SCREEN_HEIGHT))
    


def main():

    # Initialize pygame data
    FramePerSec = pygame.time.Clock()
    pygame.display.set_caption("Moduloard Interface")

    # Initiate the pygame screen
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))

    running = True
    try:
        DetectPos()
    except:
        pass

    # set interface
    InterfaceInit(SCREEN)


    smallfont = pygame.font.SysFont('Corbel',35) 
    text_calib = smallfont.render('Calibration' , True , WHITE) 
    text_gain = smallfont.render('Set gain' , True , WHITE) 

    # main loop
    while running:

        mouse = pygame.mouse.get_pos()

        # event handling, gets all event from the event queue
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:
                if SCREEN_WIDTH-220 <= mouse[0] <= SCREEN_WIDTH-60 and 100 <= mouse[1] <= 160:
                    try:
                        for i in range(len(DEVICE)):
                            SendMessage("New Calibration !", i)
                    except:
                        pass

                if SCREEN_WIDTH-220 <= mouse[0] <= SCREEN_WIDTH-60 and 180 <= mouse[1] <= 240:
                    try:
                        for i in range(len(DEVICE)):
                            SendMessage("SET random gain !", i)
                    except:
                        pass

            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

                StopAllDevices()
                pygame.quit()
                sys.exit()

        # Button management Calibration        
        if SCREEN_WIDTH-220 <= mouse[0] <= SCREEN_WIDTH-60 and 100 <= mouse[1] <= 160: 
            pygame.draw.rect(SCREEN,GREY_LIGHT,[SCREEN_WIDTH-220,100,160,60]) 
        else: 
            pygame.draw.rect(SCREEN,GREY_DARK,[SCREEN_WIDTH-220,100,160,60]) 
        SCREEN.blit(text_calib , (SCREEN_WIDTH-210,120)) 

        # Button management Gain       
        if SCREEN_WIDTH-220 <= mouse[0] <= SCREEN_WIDTH-60 and 180 <= mouse[1] <= 240: 
            pygame.draw.rect(SCREEN,GREY_LIGHT,[SCREEN_WIDTH-220,180,160,60]) 
        else: 
            pygame.draw.rect(SCREEN,GREY_DARK,[SCREEN_WIDTH-220,180,160,60]) 
        SCREEN.blit(text_gain , (SCREEN_WIDTH-210,200)) 

        # Touch interface management
        try:
            for i in range(len(DEVICE)):  
                state = UpdatePixels(SCREEN, i)
            pygame.display.update() # Update values on screen
        except:
            e = sys.exc_info()[0]
            print("Error: {}".format(e) )
            print("Can not update !")

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


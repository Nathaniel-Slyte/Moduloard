import pygame 
import BLE_interface
import asyncio
import sys
import time

from pygame.locals import *
from queue import Queue
from datetime import datetime

pygame.init()

# South == 0
# East  == 1
# North == 2
# West  == 3
CARDINAL = ("South\n", "East\n", "North\n", "West\n") 

FPS = 30

NB_ROW          = 21
NB_COLOMN       = 12
SIZE_PIXEL      = 12
SCREEN_WIDTH    = 1820 # 1280
SCREEN_HEIGHT   = 880 # 720

DEVICE          = []

GREY            = (120,120,120)
GREY_LIGHT      = (170,170,170)  
GREY_DARK       = (80,80,80) 
WHITE           = (255,255,255)
BLACK           = (0,0,0)


def DataParser(data : str):
    data = data.split(",")
    data.pop()
    return data

def SetPixels(screen, data_table, X, Y):
    # print("X: {} Y: {}".format(X,Y))
    pixel = pygame.Surface((SIZE_PIXEL,SIZE_PIXEL))
    
    for y in range(NB_ROW):
        for x in range(NB_COLOMN):

            pos = y * NB_COLOMN + x                               # Position in the X Y matrix
            rgb = int(data_table[pos])                                          # RGB value for pixel
            
            if rgb >255:
                rgb = 255
            pixel.fill((rgb, rgb, rgb))                                         # set color of the pixel (3x rgb because grey)
            screen.blit(pixel, (X + x * SIZE_PIXEL, Y + y * SIZE_PIXEL))          # update color of the pixel

    # print ("Pixels set !")

def CleanPixels(screen, X, Y):
    # print("X: {} Y: {}".format(X,Y))
    pixel = pygame.Surface((SIZE_PIXEL,SIZE_PIXEL))

    for y in range(NB_ROW):
        for x in range(NB_COLOMN):
            pixel.fill(BLACK)                                               # set color of the pixel (3x rgb because grey)
            screen.blit(pixel, (X + x * SIZE_PIXEL, Y + y * SIZE_PIXEL))    # update color of the pixel

    # print ("Pixels set !")

def UpdatePixels(screen, device :int):
    raw_table = DEVICE[device].Dequeue()
    if raw_table == "0":
        return False
    else :
        # print(raw_table)
        data_table                  = DataParser(raw_table)
        DEVICE[device].data_matrix  = data_table
        CleanPixels(screen, DEVICE[device].X, DEVICE[device].Y)
        SetPixels(screen, data_table, DEVICE[device].X, DEVICE[device].Y)
        # SendMessage("Message received !", device)
        return True

################ CONTROL ################

def SendMessage(message: str, device: int):
    message = message.encode('utf-8')
    DEVICE[device].AddMessageQueue(message)

def StopAllDevices():
    for i in range(len(DEVICE)):
        DEVICE[i].StopDevice()

def InterfaceInit(screen):
    pygame.draw.rect(screen,GREY,(SCREEN_WIDTH-300, 0, 300, SCREEN_HEIGHT))
    pygame.draw.rect(screen,BLACK,(0, 0, SCREEN_WIDTH-300, SCREEN_HEIGHT))

################ CARDINAL ################

def AddressToPos(address: str):
    pos = -1
    for i in range(len(DEVICE)):
        if DEVICE[i].address == address:
            pos = i
            break
    print ("Position : {}".format(pos))
    return pos


def CardinalCheck(caller: str, cardinal: int):
    done = False
    for i in range(len(DEVICE)):
        done = DEVICE[i].CardinalSet(caller, cardinal)
        if done:
            break


def CardinalCall():
    for i in range(len(DEVICE)):
        for j in range(4):
            SendMessage(CARDINAL[j], i)
            print("Message {} send to device {}".format(CARDINAL[j], i))
            time.sleep(2)
            CardinalCheck(DEVICE[i].address, j)

def PosSetting(current_device : int, post_device, cardinal : int):
    if cardinal != 4 :
        if cardinal == 0 :
            DEVICE[current_device].UpdatePos(DEVICE[post_device].X, DEVICE[post_device].Y + SIZE_PIXEL*NB_ROW + 20)
        if cardinal == 1 :
            DEVICE[current_device].UpdatePos(DEVICE[post_device].X - SIZE_PIXEL*NB_COLOMN - 20, DEVICE[post_device].Y)
        if cardinal == 2 :
            DEVICE[current_device].UpdatePos(DEVICE[post_device].X, DEVICE[post_device].Y - SIZE_PIXEL*NB_ROW - 20)
        if cardinal == 3 :
            DEVICE[current_device].UpdatePos(DEVICE[post_device].X + SIZE_PIXEL*NB_COLOMN + 20, DEVICE[post_device].Y)
    
    # Send the recursive loop to each cadinal position
    if DEVICE[current_device].south != 0 :
        # Check if the cardinal pos doesn't come back to the old device
        next_pos = AddressToPos(DEVICE[current_device].south)
        if next_pos != post_device:
            # go to the next device
            PosSetting(next_pos, current_device, 0)

    if DEVICE[current_device].east != 0 :
        next_pos = AddressToPos(DEVICE[current_device].east)
        if next_pos != post_device:
            PosSetting(next_pos, current_device, 1)

    if DEVICE[current_device].north != 0 :
        next_pos = AddressToPos(DEVICE[current_device].north)
        if next_pos != post_device:
            PosSetting(next_pos, current_device, 2)

    if DEVICE[current_device].west != 0 :
        next_pos = AddressToPos(DEVICE[current_device].west)
        if next_pos != post_device:
            PosSetting(next_pos, current_device, 3)
    

def DetectPos():
    print("Start to update positions !")
    CardinalCall()
    for i in range(len(DEVICE)):
        print("I'm {} and my cardinal are : South: {}    East: {}    North:{}    West:{}".format(DEVICE[i].address, DEVICE[i].south, DEVICE[i].east, DEVICE[i].north, DEVICE[i].west))
    try:
        DEVICE[0].UpdatePos(500 , 300)
        PosSetting(0, 0, 4) # 0 correspond to the first device position in the list, 4 correspond to the cardinal position which it come from, the 4 mean it come from no one (cardinal are between 0 and 3)
    except:
        print("PosSetting failled")
    # DEVICE[1].UpdatePos(DEVICE[0].X + SIZE_PIXEL*NB_COLOMN + 40, DEVICE[0].Y )
    
################ MAIN ################

def main():

    # Initialize pygame data
    FramePerSec     = pygame.time.Clock()
    pygame.display.set_caption("Moduloard Interface")

    # Initiate the pygame screen
    SCREEN          = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))

    running         = True
    # try:
    #     DetectPos()
    # except:
    #     pass

    # set interface
    InterfaceInit(SCREEN)


    smallfont       = pygame.font.SysFont('Corbel',35) 
    text_calib      = smallfont.render('Calibrate' , True , WHITE) 
    text_gain       = smallfont.render('Set gain' , True , WHITE)
    text_arrow_r    = smallfont.render('>' , True , WHITE)
    text_arrow_l    = smallfont.render('<' , True , WHITE)
    text_arrow_u    = smallfont.render('U' , True , WHITE)
    text_arrow_d    = smallfont.render('D' , True , WHITE) 

    selected_matrix = 0

    # main loop
    while running:

        mouse = pygame.mouse.get_pos()

        # event handling, gets all event from the event queue
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:

                # Calibration button
                if SCREEN_WIDTH-220 <= mouse[0] <= SCREEN_WIDTH-60 and 100 <= mouse[1] <= 160:
                    try:
                        DetectPos()
                        for i in range(len(DEVICE)):
                            SendMessage("Enabling\n", i)
                        # for i in range(len(DEVICE)):
                        #     # SendMessage("New Calibration !", i)
                        #     SendMessage("East\n", 0) # |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||--
                    except:
                        pass
                
                # set gain button 
                if SCREEN_WIDTH-220 <= mouse[0] <= SCREEN_WIDTH-60 and 180 <= mouse[1] <= 240:
                    try:
                        for i in range(len(DEVICE)):
                            SendMessage("SET random gain !", i)
                    except:
                        pass
                
                # touch button Up
                if SCREEN_WIDTH-170 <= mouse[0] <= SCREEN_WIDTH-110 and 300 <= mouse[1] <= 360:
                    try:
                        CleanPixels(SCREEN, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                        DEVICE[selected_matrix].UpdatePos(DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y - 20)
                        SetPixels(SCREEN, DEVICE[selected_matrix].data_matrix, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                    except:
                        pass

                # touch button Down
                if SCREEN_WIDTH-170 <= mouse[0] <= SCREEN_WIDTH-110 and 440 <= mouse[1] <= 500:
                    try:
                        CleanPixels(SCREEN, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                        DEVICE[selected_matrix].UpdatePos(DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y + 20)
                        SetPixels(SCREEN, DEVICE[selected_matrix].data_matrix, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                    except:
                        pass

                # touch button Left
                if SCREEN_WIDTH-205 <= mouse[0] <= SCREEN_WIDTH-145 and 370 <= mouse[1] <= 430:
                    try:
                        CleanPixels(SCREEN, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                        DEVICE[selected_matrix].UpdatePos(DEVICE[selected_matrix].X - 20, DEVICE[selected_matrix].Y)
                        SetPixels(SCREEN, DEVICE[selected_matrix].data_matrix, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                    except:
                        pass

                # touch button Right
                if SCREEN_WIDTH-135 <= mouse[0] <= SCREEN_WIDTH-75 and 370 <= mouse[1] <= 430:
                    try:
                        CleanPixels(SCREEN, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                        DEVICE[selected_matrix].UpdatePos(DEVICE[selected_matrix].X + 20, DEVICE[selected_matrix].Y)
                        SetPixels(SCREEN, DEVICE[selected_matrix].data_matrix, DEVICE[selected_matrix].X, DEVICE[selected_matrix].Y)
                    except:
                        pass

                
                # Interface selection
                for i in range(len(DEVICE)):
                    if DEVICE[i].X <= mouse[0] <= DEVICE[i].X + NB_COLOMN * SIZE_PIXEL and DEVICE[i].Y <= mouse[1] <= DEVICE[i].Y + NB_ROW * SIZE_PIXEL:
                        try:
                            print(f"INTERFACE {i} !")
                            selected_matrix = i
                        except:
                            pass

            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

                StopAllDevices()
                pygame.quit()
                sys.exit()

        ############ BUTTON VISUAL ############

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



        # Button management Up     
        if SCREEN_WIDTH-170 <= mouse[0] <= SCREEN_WIDTH-110 and 300 <= mouse[1] <= 360: 
            pygame.draw.rect(SCREEN,GREY_LIGHT,[SCREEN_WIDTH-170,300,60,60]) 
        else: 
            pygame.draw.rect(SCREEN,GREY_DARK,[SCREEN_WIDTH-170,300,60,60]) 
        SCREEN.blit(text_arrow_u , (SCREEN_WIDTH-150,320)) 

        # Button management Down     
        if SCREEN_WIDTH-170 <= mouse[0] <= SCREEN_WIDTH-110 and 440 <= mouse[1] <= 500: 
            pygame.draw.rect(SCREEN,GREY_LIGHT,[SCREEN_WIDTH-170,440,60,60]) 
        else: 
            pygame.draw.rect(SCREEN,GREY_DARK,[SCREEN_WIDTH-170,440,60,60]) 
        SCREEN.blit(text_arrow_d , (SCREEN_WIDTH-150,460)) 

        # Button management Left
        if SCREEN_WIDTH-205 <= mouse[0] <= SCREEN_WIDTH-145 and 370 <= mouse[1] <= 430: 
            pygame.draw.rect(SCREEN,GREY_LIGHT,[SCREEN_WIDTH-205,370,60,60]) 
        else: 
            pygame.draw.rect(SCREEN,GREY_DARK,[SCREEN_WIDTH-205,370,60,60]) 
        SCREEN.blit(text_arrow_l , (SCREEN_WIDTH-185,385)) 

        # Button management Right    
        if SCREEN_WIDTH-135 <= mouse[0] <= SCREEN_WIDTH-75 and 370 <= mouse[1] <= 430: 
            pygame.draw.rect(SCREEN,GREY_LIGHT,[SCREEN_WIDTH-135,370,60,60]) 
        else: 
            pygame.draw.rect(SCREEN,GREY_DARK,[SCREEN_WIDTH-135,370,60,60]) 
        SCREEN.blit(text_arrow_r , (SCREEN_WIDTH-115,385)) 




        # Touch interface management
        try:
            # pygame.draw.rect(SCREEN,BLACK,(0, 0, SCREEN_WIDTH-300, SCREEN_HEIGHT))
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

        for i in range(len(address)):
            loop.create_task(DEVICE[i].Connect())

        pygame_task = loop.run_in_executor(None,main)

        loop.run_forever()
            
    except (KeyboardInterrupt, SystemExit):
        try:
            StopAllDevices()
        except:
            pass
        loop.stop()
        # pass


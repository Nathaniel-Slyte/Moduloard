import queue, threading
import pygame 
import BLE_interface

from myqueue import DATA_QUEUE

NB_ROW     = 21
NB_COLOMN  = 12
SIZE_PIXEL = 40
pixels     = []

def AddQueue(table:str):
    DATA_QUEUE.put(table)
    print("Added in queue")

def Dequeue():
    print("ICI", id(DATA_QUEUE))
    item = DATA_QUEUE.get()
    # data_queue.task_done()
    return item

def DataParser(data : str):
    data = data.split(",")
    data.pop()
    return data


def PixelsInit(screen):
    rgb = 0
    table = ""
    while rgb < (NB_ROW*NB_COLOMN):
        table += str(0) + ","
        pixels.append(pygame.Surface((SIZE_PIXEL,SIZE_PIXEL)))
        rgb+=1
    DATA_QUEUE.put(table)
    data_table = DataParser(table)
    SetPixels(screen, data_table)


def SetPixels(screen, data_table):
    posX = 0
    posY = 0
    while posY < NB_ROW:
        while posX < NB_COLOMN:

            pos = posY * NB_COLOMN + posX                                       # Position in the X Y matrix
            rgb = int(data_table[pos])                                          # RGB value for pixel
            pixels[pos].fill((rgb, rgb, rgb))                                   # set color of the pixel (3x rgb because grey) 
            screen.blit(pixels[pos], (posX * SIZE_PIXEL, posY * SIZE_PIXEL))    # update color of the pixel
            
            posX+=1
        posY+=1
        posX =0
    print ("Pixels set !")

def UpdatePixels(screen):
    raw_table = Dequeue()
    # if not raw_table:
    #     return False
    data_table = DataParser(raw_table)
    SetPixels(screen, data_table)
    
    return True


def main():

    # Initialize pygame module
    pygame.init()

    # create a surface on screen that has the size of 240 x 180
    my_screen = pygame.display.set_mode((NB_COLOMN * SIZE_PIXEL , NB_ROW * SIZE_PIXEL))
    
    # define a variable to control the main loop
    running = True
    PixelsInit(my_screen)
    

    # main loop
    while running:

        state = UpdatePixels(my_screen)
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
    threading.Thread(target=BLE_interface.Main, daemon=True).start()
    main()
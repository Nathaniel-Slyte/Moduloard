import pygame

NB_ROW     = 12
NB_COLOMN  = 21
SIZE_PIXEL = 40

data_queue = [] # c'est une liste ça, pas une queue ###############################
pixels     = []


def DataParser(data : str):
    ###############################
    # Parse une array de la queue
    # me sors une matrice de valeur pour les pixels


def PixelsInit():
    rgb = 0
    while rgb < (NB_ROW*NB_COLOMN):
        data_queue.append(rgb)
        pixels.append(pygame.Surface((SIZE_PIXEL,SIZE_PIXEL)))
        rgb+=1

def UpdatePixels(screen):
    posX = 0
    posY = 0
    while posX < NB_ROW:
        while posY < NB_COLOMN:
            pixels[posX * NB_ROW + posY].set_alpha(128)                                                                                                 # alpha level (transparency)
            ###############################
            # penser à mettre niveau de gris avec fonction externe (chercher internet)
            pixels[posX * NB_ROW + posY].fill((data_queue[posX * NB_ROW + posY],data_queue[posX * NB_ROW + posY],data_queue[posX * NB_ROW + posY]))     # set color of the pixel  
            screen.blit(pixels[posX * NB_ROW + posY], (posX * SIZE_PIXEL, posY * SIZE_PIXEL))                                                           # update color of the pixel
            posY+=1
        posX+=1
        posY =0

def main():

    # Initialize pygame module
    pygame.init()
    PixelsInit()

    # create a surface on screen that has the size of 240 x 180
    my_screen = pygame.display.set_mode((NB_ROW * SIZE_PIXEL, NB_COLOMN * SIZE_PIXEL))
    
    # define a variable to control the main loop
    running = True
    

    # main loop
    while running:

        UpdatePixels(my_screen)
        pygame.display.flip() # Update values on screen

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
     


if __name__ == '__main__':
    main()
    print("Interface file connected")
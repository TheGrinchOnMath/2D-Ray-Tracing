import pygame, os, sys, ctypes

pygame.init()

screen = pygame.display.set_mode()
screenx, screeny = screen.get_size()
pygame.display.set_mode((screenx, screeny), pygame.FULLSCREEN | pygame.HWSURFACE)

def path_fiddler(dir:list):
    temp = os.getcwd
    for n in dir:
        temp = os.path.join(temp, dir)
    result = ""
    for element in (temp):
        if element == "\\" or element == "/":
            result += element
        result += element
    return result

running = True

# add some functions to make the actual gui work such as buttons and stuff (use fractions of screen dimensions for scalability) (this is going to be pain)

# add a function that does the render part (meaning you could put a picture in the background to make the creation of stuff more useful)

# add a file handler function that can take the input from a box you fill in with overwrite confirmation perhaps, and that handles reading and writing to json stuff

# add a function that handles the actual shape creation and manipulation, with tools such as rotate (needs work to find equations for ellipses that have been twisted), move around, 
# some way of snapping to points and lines, some way of showing when stuff is aligned, and more stuff i have not yet thought of.

class Mirror:
    def __init__(self, type, start, end, ):
    



def main():
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running == False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE | pygame.HWSURFACE)
        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
    
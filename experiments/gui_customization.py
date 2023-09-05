import pygame, os, sys, ctypes

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE | pygame.HWSURFACE)
if sys.platform == "win32": #for windows systems
    HWND = pygame.display.get_wm_info()['window']
    SW_MAXIMIZE = 3
    ctypes.windll.user32.ShowWindow(HWND, SW_MAXIMIZE)
    screenx, screeny = screen.get_size()
elif sys.platform == "linux":
    screen = pygame.display.set_mode()
    screenx, screeny = screen.get_size()
    pygame.display.set_mode((screenx, screeny), pygame.RESIZABLE | pygame.HWSURFACE)
# pygame.RESIZABLE makes the window resizable
else:
    screen = pygame.display.set_mode()
    screenx, screeny = screen.get_size()
    pygame.display.set_mode((screenx, screeny), pygame.RESIZABLE | pygame.HWSURFACE)



def path_fiddler(dir):
    result = ""
    for element in (os.path.join(os.getcwd(), dir)):
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


def main():
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running == False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE | pygame.HWSURFACE)
        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
    
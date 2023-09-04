import pygame, os, cv2, sys

pygame.init()

RAYS = 500 # <-- this variable sets the amount of rays initially emitted from the cursor's position
REFLECT_CTR = 0 # <-- this variable keeps track of how many reflections have been calculated 
                #     (could be used to stop the physics after a set number of reflections)

def path_fiddler(dir):
    result = ""
    for n in (os.path.join(os.getcwd(), dir)):
        if n == ("\\" or "//"):
            result += n
        result += n
    return result

def opencv_image_interpreter():
    dir = path_fiddler(os.path.join("assets", "image.png"))
    img = cv2.imread(dir, cv2.IMREAD_GRAYSCALE)
    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 3, True)
        n = approx.ravel()
    return n

def json_reader():
    # this should hold the data for reading the json file containing
    # the wall data
    pass

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

display = pygame.Surface((screenx, screeny))

running = True

class Line:
    def __init__(self, startpos, endpos):
        self.startpos = startpos
        self.endpos = endpos
        self.vector = pygame.Vector2((startpos[1] + endpos[0] - startpos[0] - endpos[1]), (startpos[1] + endpos[0] - startpos[0] - endpos[1]))
        self.type = "line"

class Ellipse:
    def __init__(self, startpos, endpos, focusA, focusB, eccentricity):
        self.startpos = startpos
        self.endpos = endpos
        self.focusA = focusA
        self.focusB = focusB
        self.eccentricity = eccentricity
        self.type = "ellipse"

    def normal(self, pos):

        # add some code here that calculates the vector perpendicular
        # to the tangent to the point of reflection
        
        pass

class Circle:
    def __init__(self, startpos, endpos, center, radius):
        self.startpos = startpos
        self.endpos = endpos
        self.center = center
        self.radius = radius
        self.type = "circle"

def collision(wall):
    # do line-line intersection here (therefore only ellipse and circle operations are needed in addition)
    if wall.type == "ellipse":      # add a logical operation to check if the ray goes through the real bit of the ellipse
        pass
    elif wall.type == "circle":
        # same for the circle

        pass
    # this function calculates intersections between the different equations
    # such as lines, ellipses and circles
    pass

def main():
    while running:
        for event in pygame.event.get:
            if event.type == pygame.QUIT:
                running == False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE | pygame.HWSURFACE)
            if event.type == pygame.MOUSEBUTTONUP:
                refresh = True
                mx, my = pygame.mouse.get_pos()
                mousepos = (mx, my)
        render(refresh, mousepos)
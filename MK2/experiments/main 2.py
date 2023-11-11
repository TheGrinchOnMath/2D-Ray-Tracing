import pygame, os, cv2, sys, ctypes, random, math
from experiments.lib import *
import numpy as np

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

def physics_calculator(input, mirrors): #input is structured as follows: [originx, originy, vectorx, vectory]
    # consider storing the line equation for the rays in addition to what we already have, cuz i use both line equation parameters and vectors...
    pos = pygame.Vector2(input[0], input[1])
    vect = pygame.Vector2(input[2], input[3])
    slope = input[3] / input[2]
    heightAtOrigin = None # add formula for finding this based on the inputs
    mark = 1000000
    cpos = None
    for mirror in mirrors: # check all mirrors, check intersection, find closest mirror and store ID
        collision = mirror.intersect(pos, vect, slope, heightAtOrigin)
        if collision is not None:
            cpos = collision
            dist = collision - pos # start is the origin of the ray at position n of the array (arrays start at 0, mind)
            if dist < mark:
                mark = dist
                id = mirror.id
                vect = None # vect is the directional vector of the incident ray that is being calculated
    for mirror in mirrors: # get the right mirror and use its data to determine the reflection
        if mirror.id == id:
            if mirror.type == "Ellipse" or mirror.type == "Arc":
                normal = mirror.find_normal(cpos)
            elif mirror.type == "Line":
                normal = mirror.normal
            nvect = pygame.Vector2.reflect(vect, normal)
        continue
    ray_out = [cpos, nvect]
    pos_out = [pos, cpos]

    return ray_out, pos_out # ray_out is the ray data from the reflection, pos_out is both ends of the calculated ray

class Ellipse:
    def __init__(self, startpos, endpos, offset_x, offset_y, width, height):
        self.startpos = startpos
        self.endpos = endpos
        self.a_squared = pow(offset_x, 2)
        self.b_squared = pow(offset_y, 2)
        self.ab = offset_x * offset_y
        self.height_squared = pow(height, 2)
        self.width_squared = pow(width, 2)

    def intersect(self, rayPos, rayVector, slope, heightAtOrigin): # take a list containing position, vector and line equation parameters
        delta = self.a_squared * pow(slope, 2) + self.b_squared - pow((self.offset_x * slope + (heightAtOrigin - self.offset_y)), 2)
        if delta <= 0:
            pos = None
        if delta > 0:
            posx_1 = (self.b_squared * self.offset_x - self.a_squared * slope * (heightAtOrigin - self.offset_y) + math.sqrt(delta) / self.a_squared* pow(slope, 2) + self.b_squared)
            posx_2 = (self.b_squared * self.offset_x - self.a_squared * slope * (heightAtOrigin - self.offset_y) - math.sqrt(delta) / self.a_squared* pow(slope, 2) + self.b_squared)
            posy_1 = slope * posx_1 + heightAtOrigin
            posy_2 = slope * posx_2 + heightAtOrigin
        # insert condition to check if collision is supposed to happen and which intersection is the correct one
        # equation of tangent normal vector to an ellipse at a given point is the bisector of AP and BP 
        # this is big as it is not hard to do, given the formula for the bisector having been reworked.
        return pos # pygame.Vector2

        

class Mirror:
    def __init__(self, type, startpos, endpos): # add data for calculations with ellipse and arc, investigate *args and **kwargs
        self.type = type
        self.startpos = startpos
        self.endpos = endpos
        self.id = random.randint(1, 1000)

    def intersect(self, pos, vector):
        if self.type == "Line":
            x1, y1 = self.startpos
            x2, y2 = self.endpos
            x3, y3 = pos
            x4, y4 = pos + vector

            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            numerator = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
            if denominator == 0:
                return None
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
            t = numerator / denominator
            if 1 > t > 0 and u > 0:
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                collidePos = pygame.math.Vector2(x, y)
                return collidePos
            
        if self.type == "Arc":
            # add the math for the line-arc intersection equation
            pass
        
        if self.type == "Ellipse":
            # add the path for the line-ellipse intersection equation
            pass
                    
    def draw(self, color):
        if self.type == "Line":
            pygame.draw.line(display, color, self.start_pos, self.end_pos, 3)
        if self.type == "Ellipse":
            pass
            

display = pygame.Surface((screenx, screeny))

running = True



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
        
import pygame, os, cv2, sys, ctypes, random, math, multiprocessing
from lib import *
import numpy as np
import concurrent.futures

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
    collisionPos = None
    for mirror in mirrors: # check all mirrors, check intersection, find closest mirror and store ID
        collision = mirror.intersect(pos, vect, slope, heightAtOrigin)
        if collision is not None:
            collisionPos = collision
            dist = math.sqrt(pow((collision[0] - pos[0]), 2) + pow((collision[1] - pos[1]), 2)) # start is the origin of the ray at position n of the array (arrays start at 0, mind)
            if dist < mark:
                mark = dist
                mirrorId = id(mirror)
                vect = None # vect is the directional vector of the incident ray that is being calculated
    for mirror in mirrors: # get the right mirror and use its data to determine the reflection
        if id(mirror) == mirrorId:
            normal = mirror.normalVector(collisionPos)
            rVect = pygame.Vector2.reflect(vect, normal)
        continue
    ray_out = [collisionPos, rVect]
    pos_out = [pos, collisionPos]

    return ray_out, pos_out # ray_out is the ray data from the reflection, pos_out is both ends of the calculated ray


class Mirror:
    def __init__(self, type, startpos, endpos, **kwargs): # add data for calculations with ellipse and arc, investigate *args and **kwargs
        self.type = type
        self.startpos = pygame.Vector2(startpos)
        self.endpos = pygame.Vector2(endpos)
        
        if type == "Line":
            self.normal = pygame.Vector2((endpos[1] - startpos[1]), (startpos[0] - endpos[0]))

        if type == "Ellipse":
            for key, value in kwargs.items():
                if key == "offset":
                    self.offset = value # offset from origin
                if key == "dimensions":
                    self.dimensions = value # (width, height) the values of a and b
                    
            
        self.a_squared = pow(self.offset[0], 2)
        self.b_squared = pow(self.offset[1], 2)
        self.ab = self.offset[0] * self.offset[1]
        self.height_squared = pow(self.dimensions[1], 2)
        self.width_squared = pow(self.dimensions[0], 2)
        self.focusA = None
        self.focusB = None   # add calculations here

        if type == "Arc":
            for key, value in kwargs.items():
                if key == "radius":
                    self.radius = value
                if key == "center":
                    self.center = value

    def intersect(self, rayOrigin, rayVector, slope, heightAtOrigin):
        intersect = None
        if self.type == "Line":
            x1, y1 = self.startpos
            x2, y2 = self.endpos
            x3, y3 = rayOrigin
            x4, y4 = rayOrigin + rayVector

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
            
        if self.type == "Ellipse":
            condition = False # add the bit that checks if there is supposed to be an intersection at all, and which intersection to regard as being the case
            if condition is True:    
                delta = self.a_squared * pow(slope, 2) + self.b_squared - pow((self.offset_x * slope + (heightAtOrigin - self.offset_y)), 2)
                if delta > 0:
                    posx_1 = (self.b_squared * self.offset_x - self.a_squared * slope * (heightAtOrigin - self.offset_y) + math.sqrt(delta) / self.a_squared* pow(slope, 2) + self.b_squared)
                    posx_2 = (self.b_squared * self.offset_x - self.a_squared * slope * (heightAtOrigin - self.offset_y) - math.sqrt(delta) / self.a_squared* pow(slope, 2) + self.b_squared)
                    # this calculates the x coordinate of the intersection between the ray and the ellipse
                    posy_1 = slope * posx_1 + heightAtOrigin
                    posy_2 = slope * posx_2 + heightAtOrigin

            # insert condition to check if collision is supposed to happen and which intersection is the correct one
            # a temporary plug could be to set the intersections to be above or below a x or y coordinate
            return intersect # pygame.Vector2
    
        if self.type == "Arc":
            delta = pow(self.radius, 2) * (pow(slope, 2) + 1) - pow((2 * slope * self.offset[0] + heightAtOrigin - self.offset[1]), 2)
            if delta > 0:
                posx_1 = (self.offset[0] - (slope*(heightAtOrigin - self.offset[1])) + math.sqrt(delta)) / (pow(slope, 2) + 1)
                posx_2 = (self.offset[0] - (slope*(heightAtOrigin - self.offset[1])) - math.sqrt(delta)) / (pow(slope, 2) + 1)
                
                posy_1 = slope * posx_1 + heightAtOrigin
                posy_2 = slope * posx_2 + heightAtOrigin

            return intersect

    def normalVector(self, intersection):
        if self.type == "Line":
            normal = self.normal

        if self.type == "Ellipse":
            AP = pygame.Vector2(intersection - self.focusA)
            BP = pygame.Vector2(intersection - self.focusB)
            normal = pygame.Vector2.normalize(AP * AP.magnitude() + BP * BP.magnitude())
        
        if self.type == "Arc":
            pass # add the bit that does the arc normal vector calculation here, it is -CP where C is center and P is intersection

        return normal
            
                    
    def draw(self, color): # this needs work. the line is easy, but the ellipses might be a little harder. need to rethink the structure of this one
        if self.type == "Line":
            pygame.draw.line(display, color, self.start_pos, self.end_pos, 3)
        if self.type == "Ellipse":
            pass
        if self.type == "Arc":
            pass
            

display = pygame.Surface((screenx, screeny))

running = True


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
  

def multiProcessor():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(printList, arr)
        # add code that unwraps the numpy array here
        print(result)

     # this function is to contain code that takes the ray data workload and distributes it on X processes
         # then returns the calculated datasets
         # would inputting the array with the ray data work?
         # it may be necessary to use the old structure to test the current code
         # i also need to work on the gui, to be able to design shapes with ease
arr = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])

def printList(list):
    return list

if __name__ == "__main__":
    print(multiProcessor())
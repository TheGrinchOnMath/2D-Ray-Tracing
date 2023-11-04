#====LICENSES====#
"""
    MIT License

    Copyright (c) 2020 000Nobody

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
#===============#

#===IMPORTS===#
import math, ctypes, sys, cv2, os, pygame
from ctypes.wintypes import *
from pygame.locals import *
from pygame.math import *
#=============#


pygame.init() # starts pygame, place before any code that uses the pygame library
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE | pygame.HWSURFACE | pygame.FULLSCREEN)
#creates a fullscreen pygame window, and stores pixel dimensions in variables
screenx, screeny = screen.get_size()

""" Variables:
change the variables in the DIR variable to the folders that lead to the image, structure : "dir1", "dir2", "image.png"

NUM_RAYS is the number of rays that leave the mouse position
MAX_REFLECTIONS is the maximum number of reflections
"""

DIR = ["assets", "Penrose_unilluminable_room.png"]
NUM_RAYS = 1000
MAX_REFLECTIONS = 250

#======DO=NOT=CHANGE======#
WINDOW_SIZE = (screenx, screeny)
display = pygame.Surface(WINDOW_SIZE)
mirrors = []
rays = []
running = True

def path_fiddler(dir:list): # this function takes the current working directory of the file and adds the specified folders and file to it, 
    temp = ""               # then modifies the resulting string to double any slashes or backslashes, so that string interpretation is correct
    result = ""               
    for element in dir:
        temp = os.path.join(temp, element)
    for n in (os.path.join(os.getcwd(), temp)):
        if n == ("\\" or "/"):
            result += n
        result += n
    return result

def cv2_img_detect(dir, screenx, screeny): #edge finding using OpenCV
    img = cv2.imread(path_fiddler(dir), cv2.IMREAD_GRAYSCALE)
    resize = cv2.resize(img, (screenx, screeny))
    # converts image into grayscale and resizes it to the screen dimensions

    _, threshold = cv2.threshold(resize, 110, 255, cv2.THRESH_BINARY)
    # Converting image to a binary image
    # ( black and white only image).

    contours, _= cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Detecting contours in image.

    for cnt in contours :
        approx = cv2.approxPolyDP(cnt, 1, True)
    
        # Used to flatten (reduce to one dimension) the array containing
        # the co-ordinates of the vertices.
        n = approx.ravel() 
    return n



  
class Ray:
    def __init__(self, reflections, vector, origin): # initialize variables for the ray objects. first 3 vars are what define the ray
        self.reflections = reflections               # the 4th and 5th are for efficiency
        self.vector = vector
        self.origin = origin
        self.deleted = False
        self.reflected = False

    def checkCollision(self, mirror): # uses line-line intersection formulas from wikipedia: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        x1, y1 = mirror.start_pos     # set variables from mirror start and end positions
        x2, y2 = mirror.end_pos

        x3, y3 = self.origin        # set variables from ray origin to point in the direction of the ray
        x4 = self.origin[0] + self.vector[0]
        y4 = self.origin[1] + self.vector[1]

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        numerator = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        if denominator == 0:
            return None
        
        t = numerator / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if 1 > t > 0 and u > 0:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            collidePos = pygame.math.Vector2(x, y)
            return collidePos
        
    def delete(self): #removes the used objects from memory in an attempt to increase efficiency
        if self.deleted:
            self.kill()
            del self

class Mirror:
    def __init__(self, start_pos, end_pos, color = "white"):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color

        self.slope_x, self.slope_y= end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]

        self.vector = pygame.math.Vector2(self.slope_x, self.slope_y)     

        self.length = math.sqrt(self.slope_x ** 2 + self.slope_y ** 2)

    def draw(self):
        pygame.draw.line(display, self.color, self.start_pos, self.end_pos, 3)

def drawRays(rays, mirrors, color = (200, 200, 20)): # core function of the program, iterates through every ray and for every ray every wall, checks for collision, 
    # finds the closest wall if there is a collision and draws the rays to the display surface
    for ray in rays:
        if ray.reflected == False: # avoids rays being calculated twice
            closest = 10000 # maximum length of rays
            closest_point = None # no collision
            for mirror in mirrors:
                intersect_point = ray.checkCollision(mirror) # finds intersection point between ray and mirror
                if intersect_point is not None:
                    ray.reflected = True
                    ray_dist_x, ray_dist_y = ray.origin[0] - intersect_point[0], ray.origin[1] - intersect_point[1]
                    distance = math.sqrt(ray_dist_x ** 2 + ray_dist_y ** 2) # distance from ray origin to mirror
                    if distance < closest: # this part is where the distance gets reduced so that the closest wall is the one that gets reflected
                        normal_vector = pygame.Vector2(-(mirror.slope_y), mirror.slope_x) # putting the normal vector creation breaks the calculations and rays then pass through walls
                        closest = distance
                        closest_point = intersect_point
            if closest_point is not None:
                ray_vector = ray.vector
                new_vector = ray_vector.reflect(normal_vector)
                if ray.origin != closest_point and ray.reflections <= MAX_REFLECTIONS:
                    pygame.draw.line(display, color, ray.origin, closest_point)
                    rays.append(Ray((ray.reflections + 1), new_vector, closest_point))
    for ray in rays:
        ray.delete() # deletes all ray objects so as not to saturate memory

def generateMirrors(n): # generates all the mirror objects
    mirrors.clear()
    mirrors.append(Mirror((0, 0), (screenx, 0))) # first 4 mirrors are the ones on the edges of the screen so that no rays go on forever and break the code
    mirrors.append(Mirror((0, 0), (0, screeny)))
    mirrors.append(Mirror((screenx, 0), (screenx, screeny)))
    mirrors.append(Mirror((0, screeny), (screenx, screeny)))
    mirrors.append(Mirror((n[-2], n[-1]), (n[0], n[1])))
    mirrors.append(Mirror((n[-4], n[-3]), (n[-2], n[-1])))
    i = 0
    for j in n: # creates mirrors from the list of coords created by opencv
        if(i % 2 == 0) and len(n) - 4 >= i:
            if n[i] == n[-4]:
                pass
            else:
                mirrors.append(Mirror((n[i], n[i + 1]), (n[i + 2], n[i + 3])))
        i = i + 1



def draw(): # creates the first set of rays, draws the mirrors, draws the rays and the reflections
    display.fill((10, 10, 10))
    rays.clear()
    for i in range(0, NUM_RAYS):
        angle = 2 * math.pi * (i / NUM_RAYS)
        ray_vector = pygame.Vector2(math.cos(angle), math.sin(angle))
        rays.append(Ray(0, ray_vector, (mx, my)))

    for mirror in mirrors:
        mirror.draw()

    drawRays([ray for ray in rays], [mirror for mirror in mirrors])

    screen.blit(display, (0, 0)) 

    pygame.display.update() # this makes the display visible on the pygame window

generateMirrors(cv2_img_detect(DIR, screenx, screeny)) # calls the generatemirrors function and the cv2 image detection function

while running: # main loop, one cycle per frame, handles IO and rendering
    mx, my = pygame.mouse.get_pos() # mouse position on screen
    for event in pygame.event.get(): # cycles through events (screen resize, quit events, peripheral inputs)
        if event.type == QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
             screen = pygame.display.set_mode(event.size, pygame.RESIZABLE | pygame.HWSURFACE)
           
    draw() # calls the draw function and therefore the drawrays function
pygame.quit()
sys.exit()
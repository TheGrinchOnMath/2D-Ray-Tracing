"""LICENSES:

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

import math
import ctypes
import sys
import cv2
import os
from ctypes.wintypes import *
import pygame
from pygame.locals import *
from pygame.math import *

wallVar = 3
# Reading image
# str(input("Input file with containing folder with structure; folder/file:"))

def path_fiddler(dir):
    result = ""
    for element in (os.path.join(os.getcwd(), dir)):
        if element == "\\" or element == "/":
            result += element
        result += element
    return result

dir = path_fiddler("assets/image.png")
img2 = cv2.imread(dir, cv2.IMREAD_COLOR)
img = cv2.imread(dir, cv2.IMREAD_GRAYSCALE)

#img2 = cv2.imread("C:\\Users\\kille\\Desktop\\vscode git repository\\visual-studio-code-repository\\Obsidian\\school\\TM\\TM code\\image.png", cv2.IMREAD_COLOR)
# Reading same image in another 
# variable and converting to gray scale.
#img = cv2.imread("C:\\Users\\kille\\Desktop\\vscode git repository\\visual-studio-code-repository\\Obsidian\\TM\\TM code\\image.png", cv2.IMREAD_GRAYSCALE)
# Converting image to a binary image
# ( black and white only image).
_, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
  
# Detecting contours in image.
contours, _= cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# Going through every contours found in the image.
for cnt in contours :
  
    approx = cv2.approxPolyDP(cnt, wallVar, True)  # 0.009 * cv2.arcLength(cnt, True)
  
    # Used to flatted the array containing
    # the co-ordinates of the vertices.
    n = approx.ravel() 
    
pygame.init()
# creates a fullscreen window after checking the display size
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

NUM_RAYS = 5000
WINDOW_SIZE = (screenx, screeny)
MAX_REFLECTIONS = 50
display = pygame.Surface(WINDOW_SIZE)
mirrors = []
rays = []
running = True
  
class Ray:
    def __init__(self, reflections, vector, origin):
        self.reflections = reflections
        self.vector = vector
        self.origin = origin
        self.deleted = False
        self.reflected = False

    def checkCollision(self, mirror):
        x1, y1 = mirror.start_pos     # set variables from wall start and end positions
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
    def delete(self):
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

def drawRays(rays, mirrors, color = (200, 200, 20)):
    for ray in rays:
        if ray.reflected == False:
            closest = 10000 # maximum length of rays
            closest_point = None
            for mirror in mirrors:
                intersect_point = ray.checkCollision(mirror)
                if intersect_point is not None:
                    ray.reflected = True
                    ray_dist_x, ray_dist_y = ray.origin[0] - intersect_point[0], ray.origin[1] - intersect_point[1]
                    distance = math.sqrt(ray_dist_x ** 2 + ray_dist_y ** 2)
                    if distance < closest:
                        mirror_vector = pygame.Vector2(mirror.slope_x, mirror.slope_y)
                        normal_vector = pygame.Vector2(-(mirror_vector[1]), mirror_vector[0])
                        closest = distance
                        closest_point = intersect_point
            if closest_point is not None:
                ray_vector = ray.vector
                new_vector = ray_vector.reflect(normal_vector)
                if ray.origin != closest_point and ray.reflections < MAX_REFLECTIONS:
                    pygame.draw.line(display, color, ray.origin, closest_point)
                    rays.append(Ray((ray.reflections + 1), new_vector, closest_point))
    for ray in rays:
        ray.delete()

def generateMirrors():
    mirrors.clear()
    mirrors.append(Mirror((0, 0), (screenx, 0)))
    mirrors.append(Mirror((0, 0), (0, screeny)))
    mirrors.append(Mirror((screenx, 0), (screenx, screeny)))
    mirrors.append(Mirror((0, screeny), (screenx, screeny)))
    i = 0
    mirrors.append(Mirror((n[-2], n[-1]), (n[0], n[1])))
    mirrors.append(Mirror((n[-4], n[-3]), (n[-2], n[-1])))
    for j in n:
        if(i % 2 == 0) and len(n) - 4 >= i:
            if n[i] == n[-4]:
                pass
            else:
                mirrors.append(Mirror((n[i], n[i + 1]), (n[i + 2], n[i + 3])))
        i = i + 1



def draw():
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

    pygame.display.update()
generateMirrors()

while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
             screen = pygame.display.set_mode(event.size, pygame.RESIZABLE | pygame.HWSURFACE)

        elif event.type == pygame.MOUSEBUTTONUP:
            pass
            
    draw()
pygame.quit()
sys.exit()    
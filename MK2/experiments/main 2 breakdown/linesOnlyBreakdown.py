import pygame, cv2, os, random
import numpy as np

#----Variables----#
RAYS = 1
REFLECTIONS = 5 # this is the max amount of reflections of a ray. deduce this by 1
path = ["MK2", "files", "assets", "penrose_unilluminable_room.png"] 
# ^^ path to the image that will be used with opencv
mirrors = [] # list containing the mirror objects

class Mirror:
    def __init__(self, startPos:tuple, endPos:tuple):
        self.startPos = startPos    # one end of the mirror
        self.endPos = endPos        # the other end of the mirror
        self.normal = (endPos[1] - startPos[1], startPos[0] - endPos[0])
        # ^^ the vector normal to the mirror segment

    def intersect(self, rayOrigin, rayVector): # calculates the intersection between the mirror and the ray
        a1, a2 = self.startpos
        b1, b2 = self.endpos
        p1, p2 = rayOrigin
        v1, v2 = rayVector
        denominator = v2*(b1-a1) - v1*(b2-a2) # common denominator to the equations for n and m
        if denominator == 0:
            return None # this is to avoid divide by zero error
        m = ((b2-a2)*(p1-a1) - (b1-a1)*(p2-a2)) / denominator
        n = (v2*(p1-a1)-v1*(p2-a2)) / denominator
        if 1 > n > 0 and m > 0: # conditions for ray and segment lines
            x = p1 + m*v1
            y = p2 + m*v2
            collidePos = (x, y)
            return collidePos # intersection between the ray and the wall segment
        else:
            return None # if there is no intersection
        
    def draw(self, color): # draws the mirror onto the pygame window
        pygame.draw.line(screen, color, self.startPos, self.endPos, 2)

def path_fiddler(dir:list): 
    # this function takes a list of folders and the file to be used
    # as strings, and returns the full path to the file with syntax appropriate for the relevant operating system
    temp = "" # temporary, for use whilst concatenating the directories in the dir variable
    result = "" # will contain the final string that is returned by this function
    for element in dir: # creates a string containing the path from CWD to file
        temp = os.path.join(temp, element)
    
    for char in (os.path.join(os.getcwd(), temp)):
        # this loop iterates through the string, and adds an extra backslash to escape the first one
        # this avoids issues with backslashes being interpreted as syntax symbols such as \n or \t
        if char == ("\\" or "/"):
            result += char 
        result += char
    return result

def openCVImageInterpreter(path):
    # this function takes the system path to the image and returns a list of coordinates
    # that represent the contours of the image
    # \/ \/ this opens the image, resizes it to the window dimensions
    # and closes it automatically once the operations are complete
    with cv2.imread(path, cv2.IMREAD_GRAYSCALE).resize((screenx, screeny)) as img:
        _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 1, True)
        n = approx

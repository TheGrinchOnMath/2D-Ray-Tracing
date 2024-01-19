#!/usr/bin/env python
# coding: utf-8
import os, pygame, sys, cv2


def read_file(path:str, type:str): # returns either the json data or the contour coords list from the image processing
    if type == "json":
        with read_file(path, "r") as fi:
            try:
                print(fi)
            except:
                print("something went wrong when accessing:", path)
    elif type == "image":
        with cv2.imread(path, cv2.IMREAD_GRAYSCALE) as img:
            try:
                _, thresh = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
                cont, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in cont:
                    approx = cv2.approxPolyDP(cnt, 3, True)
                    n = approx.ravel()
                    print(n)
                    return n
            except:
                print("something went wrong with the image")
    else:
        raise SyntaxError("wrong file type specified, please specify either [image] or [json]")
    

def write_file(path):
    try:
        if os.path.exists(path):
            print("this file already exists. Overwrite?\n")
            if str(input()) == ("y" or "yes" or "Y" or "Yes"):
                print("ok, attempting to overwrite file...")
                with open(path, "w") as write_file:
                    pass
                    #add code here to write data to file. This could be a config file, the OG data file, the bit where the GUI does the saving


                # add here a way to make sure the code is allowed to actually delete the file (check the path and file type, do not write outside of saves folder maybe)
    except PermissionError:
        print("could not write file due to lack of permissions, aborting...")
        
            
def path_fiddler(dirs:list): # dirs has to be all folders leading from current working directory to the end file, so that the path can be used for file operations
    CWD = os.getcwd()
    out = CWD
    for element in dirs:
        os.path.join(out, element)
    temp = ""
    for i in out:
        if i == "\\":
            temp += i
        temp += i
    return temp


class Mirror:
    idIterator = itertools.count()
    def __init__(self, type, startpos, endpos, **kwargs): # add data for calculations with ellipse and arc, investigate *args and **kwargs
        self.type = type
        self.startpos = pygame.Vector2(startpos)
        self.endpos = pygame.Vector2(endpos)
        self.ID = next(Mirror.idIterator)
        
        if type == "Line":
            self.normal = pygame.Vector2((endpos[1] - startpos[1]), (startpos[0] - endpos[0]))
        """
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
        """
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
        """    
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
        """
    def normalVector(self, intersection):
        if self.type == "Line":
            normal = self.normal

        if self.type == "Ellipse":
            AP = pygame.Vector2(intersection - self.focusA)
            BP = pygame.Vector2(intersection - self.focusB)
            normal = pygame.Vector2.normalize(AP * AP.magnitude() + BP * BP.magnitude())
        
        if self.type == "Arc":
           normal = -1 * (pygame.Vector2((intersection[0] - self.center[0]), (intersection[1] - self.center[1])))
        return normal
            
                    
    def draw(self, color): # this needs work. the line is easy, but the ellipses might be a little harder. need to rethink the structure of this one
        if self.type == "Line":
            pygame.draw.line(display, color, self.start_pos, self.end_pos, 3)
        if self.type == "Ellipse":
            pass
        if self.type == "Arc":
            pass







"""

what variables do i want to use?
I need:
> ray origin and directing vector
> Line_Wall start and end, normal vector
> Ellipse_Wall start, end, line_wall for step 1 collision checking. Some kind of variables for step 2 collision checking
that define the curvature of the ellipses. when creating, first determine the A, B coordinates and 
the sum of distances ||AP|| + ||BP||
>Circle_Wall start, end, radius, offset, line that defines which bit exists


I need to figure out the best way to convert one definition of line/circle/ellipse into another.
mainly vector + point notation to explicit cartesian notation.
I need the equation for the line tangent to the point(s) of intersection of an ellipse


"""
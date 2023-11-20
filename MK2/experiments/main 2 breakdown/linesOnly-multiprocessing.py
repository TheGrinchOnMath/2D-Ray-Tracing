import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame, math, cv2, sys, concurrent.futures, random
import numpy as np

RAYS = 1
MAX_REFLECTIONS = 5
dirs = ["MK2", "files", "assets", "penrose_unilluminable_room.png"]

pygame.init()
display = pygame.display.set_mode((0, 0), pygame.HWSURFACE | pygame.FULLSCREEN)
screenx, screeny = display.get_size()
screen = pygame.Surface((screenx, screeny))

class Mirror:
    def __init__(self, type, startpos, endpos, **kwargs): # add data for calculations with ellipse and arc, investigate *args and **kwargs
        self.type = type
        self.startpos = startpos
        self.endpos = endpos
        self.normal = pygame.Vector2(((startpos[1] - endpos[1]), (endpos[0] - startpos[0])))
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

    def intersect(self, rayOrigin, rayVector):
        a1, a2 = self.startpos
        b1, b2 = self.endpos
        p1, p2 = rayOrigin
        v1, v2 = rayVector.normalize()

        denominator = v2 * (a1 - b1) - v1 * (a2 - b2)
        if denominator == 0:
            return None
        
        m = ((b2 -a2) * (p1 - a1) - (b1 - a1) * (p2 - a2)) / denominator
        n = (v2 * (p1 - a1) + v1 * (p2 - a2)) / denominator
        if 1 > n > 0 and m > 0:
            x = p1 + m * v1
            y = p2 + m * v2
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
        """
        if self.type == "Ellipse":
            AP = pygame.Vector2(intersection - self.focusA)
            BP = pygame.Vector2(intersection - self.focusB)
            normal = pygame.Vector2(AP * AP.magnitude() + BP * BP.magnitude()).normalize()
        
        if self.type == "Arc":
           normal = -1 * (pygame.Vector2((intersection[0] - self.center[0]), (intersection[1] - self.center[1])).normalize)
           """
        
        return normal
         
                    
    def draw(self, color): # this needs work. the line is easy, but the ellipses might be a little harder. need to rethink the structure of this one
        if self.type == "Line":
            pygame.draw.line(screen, color, self.startpos, self.endpos, 3)

mirrors = []
mousePos = (screenx / 2, screeny / 2)

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


def opencv_image_interpreter(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    resize = cv2.resize(img, (screenx, screeny))
    _, threshold = cv2.threshold(resize, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.5, True)
        n = approx.ravel()
    return n

def reflector(startRayData):
    mark = 100000
    result = None
    data = startRayData
    start = (data[0], data[1])
    vect = pygame.Vector2(data[2], data[3])
    output = None
    for mirror in mirrors:
        result = mirror.intersect(start, vect)
        if result is not None:
            print("\t", result)
            dist = math.sqrt((result[0] - start[0])**2 +(result[1] - start[1])**2)
            if dist < mark:
                mark = dist
                intersect = result
                ID = id(mirror)
    if result is not None:
        for mirror in mirrors:
            if ID == id(mirror):
                newVector = pygame.math.Vector2.reflect(vect, mirror.normalVector(intersect))
                output = [start[0], start[1], intersect[0], intersect[1], newVector[0], newVector[1]]
    return output

def processor(startRayArr):
    global counter
    output = np.empty((RAYS, 6))

    with concurrent.futures.ProcessPoolExecutor() as executor:
        out = executor.map(reflector, startRayArr) # input needs to be list of lists, not ndarray
    for index, d in enumerate(out):
        output[index] = d
    return output

def render(rayArr, mirrors, reset):
    global counter
    if reset is True:
        counter = 0
        screen.fill((5, 5, 5))
        outArr = np.empty((RAYS, 4))
        for i in range(0, RAYS):
            angle = 2 * np.pi * (i / RAYS)
            v_x = np.cos(angle)
            v_y = np.sin(angle)

            mx, my = pygame.mouse.get_pos()
            if i < RAYS:
                outArr[i:i+1] = [mx, my, v_x, v_y]
            else:
                outArr[i] = [mx, my, v_x, v_y] 

    elif reset is False:
        for mirror in mirrors:
            mirror.draw((255, 255, 255))
        reflectArr = processor(rayArr)
        outArr = np.empty((RAYS, 4))
        color = randomColor()
        for i in range(RAYS):
            iData = reflectArr[i]
            pygame.draw.line(screen, color, (iData[0], iData[1]), (iData[2], iData[3]), 2)
            outArr[i] = [iData[2], iData[3], iData[4], iData[5]]

        display.blit(screen, (0, 0))
        pygame.display.update()
    counter += 1
    return outArr
def randomColor():
    r = random.randint(1, 255)
    g = random.randint(1, 255)
    b = random.randint(1, 255)
    return (r, g, b)

def generateMirrors(fileType, filePath): # could be improved to check for extensions and act accordingly
    global mirrors
    path = path_fiddler(filePath)
    
    mirrors.append(Mirror("Line", (0, 0), (screenx, 0)))
    mirrors.append(Mirror("Line", (0, 0), (0, screeny)))
    mirrors.append(Mirror("Line", (screenx, 0), (screenx, screeny)))
    mirrors.append(Mirror("Line", (0, screeny), (screenx, screeny)))

    if fileType == "JSON":
        pass # this is not implemented yet, this should call a function that takes a json file and creates the mirrors based on that
    if fileType == "Image":
        result = opencv_image_interpreter(path)
        mirrors.append(Mirror("Line", ( result[-2], result[-1]), (result[0], result[1])))
        mirrors.append(Mirror("Line", (result[-4], result[-3]), (result[-2], result[-1])))
        i = 0
        for _ in result:
            if (i % 2 == 0) and len(result) - 4 >= i:
                if result[i] == result[-4]:
                    pass
                else:
                    mirrors.append(Mirror("Line", (result[i], result[i + 1]), (result[i + 2], result[i + 3])))
            i += 1

generateMirrors("Image", dirs)
    
running = True

def main():
    global running, counter
    mouseMoved = False
    mousePos = (screenx / 2, screeny / 2)
    rays = render(mousePos, RAYS, True)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                rays = render(rays, mirrors, True)
        if counter <= MAX_REFLECTIONS:
            rays = render(rays, mirrors, False)

if __name__ == "__main__":
    
    main()
    
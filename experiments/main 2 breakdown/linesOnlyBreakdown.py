import pygame, cv2, os, random, math, sys
import numpy as np

#----Variables----#
RAYS = 100
REFLECTIONS = 5 # this is the max amount of reflections of a ray. deduce this by 1
path = ["MK2", "files", "assets", "penrose_unilluminable_room.png"] 
# ^^ path to the image that will be used with opencv
mirrors = [] # list containing the mirror objects


pygame.init()
display = pygame.display.set_mode((0, 0), pygame.HWSURFACE | pygame.FULLSCREEN)
screenx, screeny = display.get_size()
screen = pygame.Surface((screenx, screeny))

class Mirror:
    def __init__(self, startPos:tuple, endPos:tuple):
        self.startPos = startPos    # one end of the mirror
        self.endPos = endPos        # the other end of the mirror
        self.normal = pygame.Vector2(endPos[1] - startPos[1], startPos[0] - endPos[0])
        # ^^ the vector normal to the mirror segment

    def intersect(self, rayOrigin, rayVector): # calculates the intersection between the mirror and the ray
        a1, a2 = self.startPos
        b1, b2 = self.endPos
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

def pathFiddler(dir:list): 
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
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = img.resize((screenx, screeny))
    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 1, True)
        n = approx.ravel()
    return n

def reflector(rayArr):
    global counter
    output = []
    mark = 100000
    result = None
    collision = None
    intersect = None
    data = rayArr
    start = (data[0], data[1])
    vect = pygame.Vector2(data[2], data[3])
    for mirror in mirrors:
        result = mirror.intersect(start, vect)
        if result is not None:
            collision = result
            dist = math.sqrt((start[0] - collision[0])**2 +(start[1] - collision[1])**2)
        else:
            result = mirror.intersect(start, vect)
            if result is not None:
                collision = result
                dist = math.sqrt((start[0] - collision[0])**2 +(start[1] - collision[1])**2)
                if dist < mark:
                    mark = dist
                    intersect = result
                    normal = mirror.normal
    if intersect is not None:
        new = pygame.Vector2.reflect(vect, normal)
        output = [start[0], start[1], intersect[0], intersect[1], new[0], new[1]]
        # pygame.draw.line(screen, (255, 0, 0), collision, collision + mirror.normal.normalize() * screenx / 10, 3)
    if output == []:
        output = reflector(data)
    return output

def render(rayArr, reset):
    global counter
    
    outArr = np.empty((RAYS, 4))
    if reset is True:

        counter = 0
        screen.fill((5, 5, 5))
        for i in range(0, RAYS):
            angle = 2 * np.pi * (i / RAYS)
            v_x = np.cos(angle)
            v_y = np.sin(angle)

            mx, my = pygame.mouse.get_pos()
            if i < RAYS:
                outArr[i:i+1] = [mx, my, v_x, v_y]
            else:
                outArr[i] = [mx, my, v_x, v_y] 

    if reset is False:
        for mirror in mirrors:
            mirror.draw("White")
        
        tempArr = distributor(rayArr)

        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        for i in range(RAYS):
            data = tempArr[i]
            pygame.draw.line(screen, color, (data[0], data[1]), (data[2], data[3]))
            outArr[i] = [data[2], data[3], data[4], data[5]]
        
        display.blit(screen, (0, 0))
    pygame.display.flip()
    counter += 1
    return outArr

def generateMirrors(fileType, filePath): # could be improved to check for extensions and act accordingly
    global mirrors
    pathFiddled = pathFiddler(filePath)
    
    mirrors.append(Mirror((0, 0), (screenx, 0)))
    mirrors.append(Mirror((0, 0), (0, screeny)))
    mirrors.append(Mirror((screenx, 0), (screenx, screeny)))
    mirrors.append(Mirror((0, screeny), (screenx, screeny)))

    if fileType == "JSON":
        pass # this is not implemented yet, this should call a function that takes a json file and creates the mirrors based on that
    if fileType == "Image":
        result = openCVImageInterpreter(pathFiddled)
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

generateMirrors("Image", path)

def distributor(rayArr):
    output = np.empty((RAYS, 6))
    errors = 0
    for i in range(RAYS):
        out = reflector(rayArr[i])
        try:
            output[i] = out
        except ValueError:
            print("something went wrong while inputting data into the array")
            errors += 1
    print(errors)
    return output

counter = 0
running = True
rays = render(np.empty((RAYS, 4)), True)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            rays = render(rays, True)
    if counter <= REFLECTIONS:
        rays = render(rays, False)
pygame.quit()
sys.exit()
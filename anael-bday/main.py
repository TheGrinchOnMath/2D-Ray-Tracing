import cv2
import random
import sys
import pygame
import os
import numpy as np

RAYS = 10
REFLECT_CAP = 10
CWD = os.getcwd()
ASSETSPATH = ["anael-bday", "assets"]
IMAGE = "penrose_unilluminable_room.png"
BGCOLOR = (10, 10, 10)
ASSETSPATH.append(IMAGE)
mirrors = []


pygame.init()
display = pygame.display.set_mode(
    (0, 0), pygame.HWSURFACE | pygame.FULLSCREEN, pygame.GL_DOUBLEBUFFER
)
screenx, screeny = display.get_size()
screen = pygame.Surface((screenx, screeny))
mousePos = (screenx / 2, screeny / 2)


def pathFiddler(dir: list):
    # this function takes a list of folders and the file to be used
    # as strings, and returns the full path to the file with syntax appropriate for the relevant operating system
    temp = ""  # temporary, for use whilst concatenating the directories in the dir variable
    nult = ""  # will contain the final string that is returned by this function
    for element in dir:  # creates a string containing the path from CWD to file
        temp = os.path.join(temp, element)

    for char in os.path.join(os.getcwd(), temp):
        # this loop iterates through the string, and adds an extra backslash to escape the first one
        # this avoids issues with backslashes being interpreted as syntax symbols such as \n or \t
        if char == ("\\" or "/"):
            nult += char
        nult += char
    return nult


PATH = pathFiddler(ASSETSPATH)


class Mirror:
    # this variable is the thickness of the ray when drawn
    size = 3

    def __init__(self, startPos: tuple, endPos: tuple):
        self.startPos = startPos
        self.endPos = endPos
        self.normVect = pygame.Vector2(endPos[1] - startPos[1], startPos[0] - endPos[0])

    def intersect(self, rayOrigin, rayVect):
        # variables to match equation
        Vect1 = pygame.Vector2(self.startPos, self.endPos)
        Vect2 = pygame.Vector2(self.startPos, rayOrigin)

        # in older iterations I set the equations myself, but since they use cross products, the cpython implementation is faster
        denominator = Vect1.cross(rayVect)

        # case in which the ray and the mirror are parralel
        if denominator == 0:
            return None

        m = Vect2.cross(Vect1)
        n = Vect2.cross(rayVect)

        # this line is a ternary operation: return the collision or None
        return rayOrigin + m * rayVect if 1 > n > 0 and m > 0 else None

    def draw(self, color, screen):
        pygame.draw.line(screen, color, self.startPos, self.endPos, self.size)


def rayPhysicsHandler(rayArr):
    output = []
    mark = 10_000
    nult = None
    data = rayArr
    startPos = (data[0], data[1])
    vect = pygame.Vector2(data[2], data[3])
    intersect = None
    for mirror in mirrors:
        nult = mirror.intersect(startPos, vect)
        if nult is not None:
            dist = pygame.Vector2(startPos, nult).magnitude()
            if dist < mark:
                mark = dist
                intersect = nult
                normal = mirror.normVect
        else:
            return output

    if intersect is not None:
        newVector = pygame.Vector2.reflect(vect, normal)
        output = [startPos, intersect, newVector]


def render(rayMatrix, net):
    global counter
    output = np.empty((RAYS, 4))
    if net is True:
        counter = 0
        screen.fill(BGCOLOR)
        for i in range(RAYS):
            # find angle in radians using fraction of 2pi
            angle = 2 * np.pi * (i / RAYS)
            vect = pygame.Vector2(np.cos(angle), np.sin(angle))
            startPos = mousePos

            if i < RAYS:
                try:
                    output[i : i + 1] = [startPos[0], startPos[1], vect[0], vect[1]]
                except ValueError:
                    print(startPos, vect)
            else:
                output[i] = [startPos[0], startPos[1], vect[0], vect[1]]

    else:
        for mirror in mirrors:
            mirror.draw("white", screen)

    temp = distributor(rayMatrix)

    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    for i in range(RAYS):
        data = temp[i]
        pygame.draw.line(screen, color, (data[0], data[1]), (data[2], data[3]))
        output[i] = [data[2], data[3], data[4], data[5]]

    display.blit(screen, (0, 0))
    pygame.display.flip()
    counter += 1
    return output


def distributor(rayMatrix):
    output = np.empty((RAYS, 6))
    errors = 0
    for i in range(RAYS):
        out = rayPhysicsHandler(rayMatrix[i])
        try:
            output[i] = out
        except ValueError:
            errors += 1
    print(f"error count for frame: {errors}")
    return output


def generateMirrors(PATH):
    global mirrors

    # read image with cv2, nize it to fit display
    img = cv2.imread(PATH, cv2.IMREAD_GRAYSCALE)
    

    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        accuracy = 0.03 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 1, True)
        n = approx.ravel()

    mirrors.append(Mirror((0, 0), (screenx, 0)))
    mirrors.append(Mirror((0, 0), (0, screeny)))
    mirrors.append(Mirror((screenx, 0), (screenx, screeny)))
    mirrors.append(Mirror((0, screeny), (screenx, screeny)))

    mirrors.append(Mirror((n[-2], n[-1]), (n[0], n[1])))
    mirrors.append(Mirror((n[-4], n[-3]), (n[-2], n[-1])))
    for i in range(len(n)):
        if (i % 2 == 0) and len(n) - 4 >= i:
            if n[i] == n[-4]:
                pass
            else:
                mirrors.append(Mirror((n[i], n[i + 1]), (n[i + 2], n[i + 3])))


generateMirrors(PATH)


def main():
    global mousePos
    rayMatrix = render(np.empty((RAYS, 4)), True)

    quit = False
    while not quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and event.key == pygame.K_LCTRL:
                    quit = True

                if event.key == pygame.K_SPACE:
                    mousePos = pygame.mouse.get_pos()
                    rayMatrix = render(np.empty((RAYS, 4)), True)
        if counter <= REFLECT_CAP:
            rayMatrix = render(rayMatrix, False)

    sys.exit()


main() if __name__ == "__main__" else None

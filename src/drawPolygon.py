import cv2
#import random
import sys
import pygame
import os
import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor

CORE_COUNT = os.cpu_count()

RAYS = 1000
REFLECT_CAP = 1 # fixed, to simulate light stopping at walls
CWD = os.getcwd()
ASSETSPATH = ["assets"]
IMAGE = "penrose_unilluminable_room.png"
BGCOLOR = (10, 10, 10)
ASSETSPATH.append(IMAGE)
mirrors = []
frame_counter = 0

RAY_COLOR = (255, 255, 100)


pygame.init()
display = pygame.display.set_mode((0, 0), pygame.HWSURFACE | pygame.FULLSCREEN)
screenx, screeny = display.get_size()
screen = pygame.Surface((screenx, screeny))
mirror_screen = pygame.Surface((screenx, screeny))
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


def cv2EdgeFind(PATH):
    # read image with cv2, nize it to fit display
    img_temp = cv2.imread(PATH, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img_temp, (screenx, screeny))

    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 1, True)
        n = approx.ravel()
    return n


class Mirror:
    # this variable is the thickness of the ray when drawn
    size = 3
    display.fill(BGCOLOR)

    def __init__(self, startPos: tuple, endPos: tuple):
        self.startPos = startPos
        self.endPos = endPos
        self.normVect = pygame.Vector2(endPos[1] - startPos[1], startPos[0] - endPos[0])

    def intersect(self, rayOrigin, rayVector):
        a1, a2 = self.startPos
        b1, b2 = self.endPos
        p1, p2 = rayOrigin
        v1, v2 = rayVector

        denominator = v2 * (b1 - a1) - v1 * (b2 - a2)
        if denominator == 0:
            return None

        m = ((b2 - a2) * (p1 - a1) - (b1 - a1) * (p2 - a2)) / denominator
        n = (v2 * (p1 - a1) - v1 * (p2 - a2)) / denominator

        if 1 > n > 0 and m > 0:
            x = a1 + n * (b1 - a1)
            y = a2 + n * (b2 - a2)
            collidePos = (x, y)
            return collidePos
        else:
            return None

    def draw(self, color, screen):
        pygame.draw.line(screen, color, self.startPos, self.endPos, self.size)


def rayPhysicsHandler(rayArr):
    output = []
    mark = 100000
    closest = None
    result = None
    data = rayArr
    startPos = (data[0], data[1])
    vect = pygame.Vector2(data[2], data[3])
    for mirror in mirrors:
        result = mirror.intersect(startPos, vect)
        if result is not None:
            collision = result
            dist = np.sqrt(
                (startPos[0] - collision[0]) ** 2 + (startPos[1] - collision[1]) ** 2
            )
            if dist < mark and dist > 0.0000001:
                mark = dist
                closest = collision
                normal = mirror.normVect

    if closest is not None:
        newVector = vect.reflect(normal)
        output = [
            startPos[0],
            startPos[1],
            closest[0],
            closest[1],
            newVector[0],
            newVector[1],
        ]
    return output


def render(rayMatrix, reset):
    global counter, frame_counter
    output = np.empty((RAYS, 4))
    if reset is True:
        counter = 0
        display.fill(BGCOLOR)
        mirror_screen.fill(BGCOLOR)
        for i in range(RAYS):
            # find angle in radians using fraction of 2pi
            angle = 2 * np.pi * (i / RAYS)
            vect = pygame.Vector2(np.cos(angle), np.sin(angle))
            startPos = mousePos
            if i < RAYS:
                output[i : i + 1] = [startPos[0], startPos[1], vect[0], vect[1]]
            else:
                output[i] = [startPos[0], startPos[1], vect[0], vect[1]]

    else:
        for mirror in mirrors:
            mirror.draw("white", screen)

        newMatrix = distributor(rayMatrix)

        # color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        li = []
        for i in range(RAYS):
            startPos_x, startPos_y, intersect_x, intersect_y, vector_x, vector_y = (
                newMatrix[i]
            )
            li.append((intersect_x, intersect_y))
            #pygame.draw.line(screen, RAY_COLOR, (startPos_x, startPos_y), (intersect_x, intersect_y))
            output[i] = [intersect_x, intersect_y, vector_x, vector_y]

        pygame.draw.polygon(screen, RAY_COLOR, li)

        display.blit(screen, (0, 0))


    pygame.draw.circle(display, "orange", mousePos, 5)
    pygame.display.flip()
    counter += 1
    frame_counter += 1
    return output


def distributor(rayMatrix):
    output = np.empty((RAYS, 6))
    errors = 0

    with ProcessPoolExecutor(max_workers=CORE_COUNT) as executor:
        _out = executor.map(rayPhysicsHandler, rayMatrix)
    
    for i in enumerate(_out):
        try:
            output[i[0]] = i[1]
        except ValueError:
            errors += 1
    """
    for i in range(RAYS):
        out = rayPhysicsHandler(rayMatrix[i])
        try:
            output[i] = out
        except ValueError:
            errors += 1
            """
    print(
        f"error count for frame no ({frame_counter}): {errors}"
    ) if errors > 0 else None
    return output


def generateMirrors(PATH):
    global mirrors

    n = cv2EdgeFind(PATH)

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
print(f"mirror count: {len(mirrors)}")


def main():
    global mousePos
    time_current = time.perf_counter()
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
        time_new = time.perf_counter()
        print(f"Time for frame({frame_counter}): {time_new - time_current:0.4f} seconds")
        time_current = time_new

    sys.exit()


main() if __name__ == "__main__" else None
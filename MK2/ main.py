from lib import IO
import pygame
import numpy as np
import os

# -----VARIABLES-----#
RAYS = 1
ALPHA = 100
IMAGE = "penrose_unilluminable_room.png"
MAX_REFLECTIONS = 1
path = IO.pathFiddler(["MK2", "assets", IMAGE])
# -------------------#
# ALPHA sets the transparency of each ray higher is more opaque, for a maximum of 255
counter = 0
# initialize pygame modules
pygame.init()
# create pygame window, get display size
screen = pygame.display.set_mode(
    (0, 0), pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF
)
displayDimensions = screen.get_size()
print(displayDimensions)


# parent class. contains all shared attributes of all 3 classes
class Mirror:
    def __init__(self, startPos: tuple, endPos: tuple, color):
        self.startPos = startPos
        self.endPos = endPos
        self.color = color


class segmentMirror(Mirror):
    def __init__(self, startPos, endPos):
        super().__init__(
            startPos, endPos, color="white"
        )  # init super class with variables
        self.vector = pygame.Vector2(
            self.endPos[0] - self.startPos[0], self.endPos[1] - self.startPos[1]
        )

    def draw(self, screen: pygame.surface):
        pygame.draw.line(screen, self.color, self.startPos, self.endPos, 2)

    # using the dot product to benefit from compiled functions and less memory use
    def rayIntersect(self, rayOrigin:tuple, rayVector:pygame.Vector2):
        # check if ray and wall are parralel (Save a little bit of time)
        if rayVector.normalize() != self.vector.normalize():
            # create vector between origin and wall start position
            Origin_WallStart_Vector = pygame.Vector2(
                rayOrigin[0] - self.startPos[0], rayOrigin[1] - self.startPos[1]
            )

            # calculate denominator common to m and n
            commonDenominator = pygame.Vector2.dot(self.vector, rayVector)

            if commonDenominator != 0:
                # calculate numerators for ray and mirror
                rayNumerator = (
                    self.vector.dot(Origin_WallStart_Vector) / commonDenominator
                )
                mirrorNumerator = (
                    Origin_WallStart_Vector.dot(rayVector) / commonDenominator
                )

                # check for conditions
                if 1 > mirrorNumerator > 0 and rayNumerator > 0:
                    x = rayOrigin[0] + rayNumerator * rayVector[0]
                    y = rayOrigin[1] + rayNumerator * rayVector[1]

                    # return computed values
                    return (x, y)
                else:
                    return None
            else:
                return None
        else:
            return None

    def normal(self):
        normal = pygame.Vector2(-self.vector[1], self.vector[0])
        return normal


# ray-segment intersection. needs to be as precise as possible
# rayArr needs to contain : a tuple, and a pygame.vector2 object
def rayIntersectionCheck(rayArr, mirrors):
    # if no intersection found (shouldnt happen), return none
    output = None
    # declare tracker variables
    # distanceTracker has to be very high, as it tracks the distance between the ray start and the mirror,
    # and therefore gets decremented
    distanceTracker = 100000
    # mirrorTracker stores the object that intersects at the smallest distance
    mirrorTracker = None
    # extract rayOrigin and rayArr from function call
    rayOrigin = (rayArr[0], rayArr[1])
    rayVector = pygame.Vector2(rayArr[2], rayArr[3])
    for mirror in mirrors:
        # check twice if the intersection is happening
        intersection = mirror.rayIntersect(rayOrigin, rayVector)
        if (
            intersection is not None
            and mirror.rayIntersect(rayOrigin, rayVector) is not None
        ):
            print("intersection!")
            distance = np.sqrt(
                np.square(intersection[0] - rayOrigin[0])
                + np.square(intersection[1] - rayOrigin[1])
            )
            if distance < distanceTracker:
                distanceTracker = distance
                mirrorTracker = mirror

    # get normal for stored mirror
    if mirrorTracker is not None:
        normal = mirrorTracker.normal()
        # reflect vector from normal
        reflectedVector = rayVector.reflect(normal)
        output = [
            rayOrigin[0],
            rayOrigin[1],
            intersection[0],
            intersection[1],
            reflectedVector[0],
            reflectedVector[1],
        ]

    return output


# generates the mirror objects and adds them to a list
def initMirrors(path: str, type: str):
    # declare mirror list
    mirrors = []

    # declare screenx, screeny
    screenx, screeny = displayDimensions

    # generate mirrors that go along the edges of the display
    mirrors.append(segmentMirror((0, 0), (screenx, 0)))
    mirrors.append(segmentMirror((0, 0), (0, screeny)))
    mirrors.append(segmentMirror((screenx, 0), (screenx, screeny)))
    mirrors.append(segmentMirror((0, screeny), (screenx, screeny)))
    # if the generation has been set to use opencv
    if type == "image":
        # call the cv2 function and get an array of positions
        posList = IO.openWithCV2(path)

        # iterate through the array from opencv
        mirrors.append(
            segmentMirror((posList[-2], posList[-1]), (posList[0], posList[1]))
        )
        mirrors.append(
            segmentMirror((posList[-4], posList[-3]), (posList[-2], posList[-1]))
        )

        for i in range(0, len(posList), 2):
            if len(posList) - 4 >= i:
                mirrors.append(
                    segmentMirror(
                        (posList[i], posList[i + 1]), (posList[i + 2], posList[i + 3])
                    )
                )
        return mirrors

    elif type == "json":
        print("not implemented")
        return

    else:
        print('wrong type passed. please pass "image", or "json".')
        return


# generates an array based on a given position and number of starting rays
def initRays(pos: tuple, numRays: int):
    if numRays < 0:
        print("wrong value: numRays is negative, aborting...")
        return None
    elif len(pos) != 2:
        print("wrong value: pos is of wrong dimension, aborting...")
        return None
    else:
        # generate empty array
        arr = np.empty((numRays, 4))

        # create rays
        for i in range(0, numRays):
            # generate angle
            angle = 2 * np.pi * i / numRays

            # special condition for edge case with numpy array indexing
            if i < numRays:
                arr[i : i + 1] = [pos[0], pos[1], np.cos(angle), np.sin(angle)]
            # set array at given index
            else:
                arr[i] = [pos[0], pos[1], np.cos(angle), np.sin(angle)]
        return arr

def handler(reset, array):
    global counter
    # declare an empty array for calculations and physics
    if reset:
        print("\n\n\n\n")
        # reset reflections counter
        counter = 0
        # cover the display in black (remove old stuff)
        screen.fill("black")

        # set the output to be a fresh set of rays
        outArray = initRays(pygame.mouse.get_pos(), RAYS)
    else:
        outArray = np.empty((RAYS, 2))
        # create surface to paint onto
        raySurface = pygame.Surface(displayDimensions, pygame.SRCALPHA)
        templateSurface = pygame.Surface(displayDimensions, pygame.SRCALPHA)
        templateSurface.set_alpha(ALPHA)
        templateSurface.lock()
        # iterate through the numpy array
        for i in range(RAYS):
            color = "yellow"

            # copy template surface
            tempSurface = templateSurface.copy
            # check intersections for the ray
            rayResult = rayIntersectionCheck(array[i], [mirror for mirror in mirrors])
            # draw the ray
            pygame.draw.line(
                tempSurface,
                color,
                (rayResult[0], rayResult[1]),
                (rayResult[2], rayResult[3]),
                1.5,
            )
            # draw the surface onto the raySurface, delete the temporary surface
            raySurface.blit(tempSurface, (0, 0))
            del tempSurface

            outArray[i] = rayResult[2:5]

        screen.blit(raySurface, (0, 0))
        pygame.display.update

mirrors = initMirrors(path, "image")
print(mirrors[0].normal())
def main():
    # declare while condition variable (gives ability to break main loop from inside it)
    running = True
    # set starting position to be in the middle of the screen
    startMousePos = (displayDimensions[0] / 2, displayDimensions[1] / 2)
    pygame.mouse.set_pos(startMousePos)

    # generate first set of rays and return array
    startArr = initRays(startMousePos, RAYS)
    rayArr = startArr

    # main event loop, gets broken by setting running to false
    while running:
        # cycle through pygame events
        for event in pygame.event.get():
            # catch alt+f4 / click x button events
            if event.type == pygame.QUIT:
                # close the while loop
                running = False
            # catch the user changing the length and with of the pygame window
            if event.type == pygame.VIDEORESIZE:
                # set the screen to the new dimensions
                screen.set_mode(
                    event.size, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
                )
            # catch the left mouse click release
            if event.type == pygame.MOUSEBUTTONUP:
                # generate rays with fresh set of rays
                rayArr = handler(True, rayArr)

        if counter <= MAX_REFLECTIONS:
            rayArr = handler(False, rayArr)

    for mirror in mirrors:
        mirror.draw()


if __name__ == "__main__":
    main()

print(mirrors[0].rayIntersect(()))
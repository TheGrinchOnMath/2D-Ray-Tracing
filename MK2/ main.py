from lib import *


import pygame
import numpy as np


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
    def rayIntersect(self, rayOrigin, rayVector):
        # check if ray and wall are parralel (Save a little bit of time)
        if rayVector.normalize_ip() == self.vector.normalize_ip():
            # create vector between origin and wall start position
            Origin_WallStart_Vector = pygame.Vector2(rayOrigin - self.startPos)

            # calculate denominator common to m and n
            commonDenominator = self.vector.dot(rayVector)

            # calculate numerators for ray and mirror
            rayNumerator = self.vector.dot(Origin_WallStart_Vector) / commonDenominator
            mirrorNumerator = Origin_WallStart_Vector.dot(rayVector) / commonDenominator

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

    def normal(self):
        normal = self.vector.rotate(90)
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
    rayOrigin = rayArr[0]
    rayVector = rayArr[1]
    for mirror in mirrors:
        # check twice if the intersection is happening
        intersection = mirror.rayIntersect(rayOrigin, rayVector)
        if (
            intersection is not None
            and mirror.rayIntersect(rayOrigin, rayVector) is not None
        ):
            distance = np.sqrt(
                np.square(intersection[0] - rayOrigin[0])
                + np.square(intersection[1] - rayOrigin[1])
            )
            if distance < distanceTracker:
                distanceTracker = distance
                mirrorTracker = mirror

    # get normal for stored mirror
    normal = mirrorTracker.normal()
    reflectedVector = rayVector.reflect(normal)
    newRayOutput = [intersection, reflectedVector]
    renderOutput = [rayOrigin, intersection]

    output = renderOutput.append(reflectedVector)
    return output

def initRays(pos:tuple, numRays:int):
    if numRays < 0:
        print("wrong value: numRays is negative, aborting...")
        return None
    elif  len(pos) != 2:
        print("wrong value: pos is of wrong dimension, aborting...")
        return None
    else:
        # generate empty array
        arr = np.empty((numRays, 2))

        # create rays
        for i in range(0, numRays):
            # generate angle
            angle = 2 * np.pi * i / numRays

            # calculate x and y component of vector, create vector2
            vector = pygame.Vector2(np.cos(angle), np.sin(angle))

            if i < numRays:
                arr[i:i+1] = [pos, vector]
            else:
                arr[i] = [pos, vector]
        return arr









pygame.init()

print(pygame.Vector2.epsilon)